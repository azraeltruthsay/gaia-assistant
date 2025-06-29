# /home/azrael/Project/gaia-assistant/gaia_rescue.py

import os
import logging
import subprocess
import code
import json
import sys
import importlib
from datetime import datetime
from pathlib import Path
from typing import Optional

# --- Core GAIA Components ---
from app.config import Config
from app.models.model_pool import model_pool
from app.behavior.persona_adapter import PersonaAdapter
from app.behavior.persona_manager import PersonaManager
from app.cognition.agent_core import AgentCore
from app.utils.vector_indexer import embed_gaia_reference, vector_query
from app.utils import gaia_rescue_helper as helper
from app.memory.conversation.manager import ConversationManager

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GAIA.Rescue")
logging.getLogger("llama_index").setLevel(logging.WARNING)
logging.getLogger("llama_cpp").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)

# --- MinimalAIManager (remains the same) ---
class MinimalAIManager:
    """A lightweight manager for the rescue shell, providing core primitives."""

    def __init__(self):
        self.config = model_pool.config
        self.llm = model_pool.get("prime")
        self.lite_llm = model_pool.get("lite")
        self.embed_model = model_pool.get("embed")
        self.status = {"boot_time": datetime.utcnow().isoformat()}
        self.active_persona = None
        self.helper = helper
        self.conversation_manager = ConversationManager(
            config=self.config,
            llm=self.llm,
            embed_model=self.embed_model
        )
        # MODIFICATION: Instantiate the PersonaManager service
        self.persona_manager = PersonaManager(self.config.PERSONAS_DIR)
        # MODIFICATION: AIManager is now responsible for holding the active persona state
        self.active_persona: Optional[PersonaAdapter] = None

    def initialize(self):
        """Initializes the manager with a fallback persona."""
        try:
            # MODIFICATION: Change 'dev_persona' to 'dev' to load from the 'dev' directory.
            persona_data = self.persona_manager.load_persona_data('dev')

            if not persona_data:
                # A simple fallback if the file is missing or fails to load
                logger.error("❌ Failed to load 'dev_persona'. Using emergency fallback.")
                persona_data = {
                    "name": "gaia-dev-emergency",
                    "description": "Emergency fallback persona.",
                    "template": "You are GAIA-Dev, operating in a minimal rescue shell.",
                    "instructions": ["Your primary persona file could not be loaded. Operate with extreme caution."]
                }

            # The AIManager creates and holds the active PersonaAdapter instance
            self.active_persona = PersonaAdapter(persona_data, self.config)
            logger.info(f"✅ Loaded dev persona '{self.active_persona.name}' via PersonaManager.")
        except Exception as e:
            logger.error(f"❌ Persona loading failed during initialization: {e}", exc_info=True)

    def reload(self, module_name: str):
        """Hot-reloads a specified Python module."""
        try:
            if module_name.endswith(".py"):
                module_name = module_name[:-3]
            if module_name.startswith("app/"):
                module_name = module_name.replace("/", ".")

            module_path = module_name.replace("app.", "app/").replace(".", "/") + ".py"
            if not os.path.exists(module_path):
                logger.error(f"❌ Cannot reload: File not found at '{module_path}'")
                return

            module = importlib.import_module(module_name)
            importlib.reload(module)
            if "gaia_rescue_helper" in module_name:
                self.helper = importlib.import_module("app.utils.gaia_rescue_helper")
            logger.info(f"✅ Reloaded module: {module_name}")
        except Exception as e:
            logger.error(f"❌ Failed to reload {module_name}: {e}")

    def read(self, filepath: str):
        """Reads and prints the content of a file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            logger.info(f"📄 Contents of {filepath}:\n---\n{content}\n---")
        except Exception as e:
            logger.error(f"❌ Could not read file: {e}")

    def write(self, filepath: str, content: str):
        """Writes content to a file, creating a backup first."""
        try:
            if os.path.exists(filepath):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{filepath}.bak.{timestamp}"
                os.rename(filepath, backup_path)
                logger.info(f"🗃️  Backup created: {backup_path}")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"✅ Written to {filepath}")
        except Exception as e:
            logger.error(f"❌ Could not write file: {e}")

    def execute(self, command: str):
        """
        Executes a safe shell command and prints its output.
        Only commands listed in SAFE_EXECUTE_FUNCTIONS are allowed.
        """
        safe_commands = self.config.SAFE_EXECUTE_FUNCTIONS
        is_safe = any(command.strip().startswith(f) for f in safe_commands)

        if not is_safe:
            logger.error(
                f"❌ Unsafe command blocked: '{command}'. Only commands from SAFE_EXECUTE_FUNCTIONS are allowed.")
            return

        try:
            result = subprocess.run(
                command, shell=True, check=True, capture_output=True, text=True, timeout=10
            )
            output_log = f"🖥️ Command Output:\n---\n{result.stdout.strip()}\n---"
            if result.stderr:
                output_log += f"\n⚠️ Command Error Output:\n---\n{result.stderr.strip()}\n---"
            logger.info(output_log)
            self.status["last_exec"] = {"success": True, "command": command, "stdout": result.stdout.strip(),
                                        "stderr": result.stderr.strip()}
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Command failed with exit code {e.returncode}:\n---\n{e.stderr.strip()}\n---")
            self.status["last_exec"] = {"success": False, "command": command, "returncode": e.returncode,
                                        "stdout": e.stdout.strip(), "stderr": e.stderr.strip()}
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Command timed out after 10 seconds: '{command}'")
            self.status["last_exec"] = {"success": False, "command": command, "error": "Timeout"}
        except Exception as e:
            logger.error(f"❌ An unexpected error occurred during command execution: {e}")
            self.status["last_exec"] = {"success": False, "command": command, "error": str(e)}


# --- Main Chat Loop (Heavily Simplified) ---
def rescue_chat_loop():
    """
    Starts an interactive chat session by using the central AgentCore.
    This loop is now only responsible for presentation (input/print).
    """
    print("\n💬 Entering GAIA Rescue chat mode. Type 'exit' to leave.")
    print("👉 Use '<<<' and '>>>' on new lines to enter multi-line input.\n")

    # The AgentCore now holds all the complex logic.
    agent_core = AgentCore(ai)

    while True:
        try:
            user_input = input("You > ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("\n👋 Exiting chat mode.")
                break

            if user_input == "<<<":
                print("🔽 Multi-line input mode. Type >>> on a new line to send.")
                lines = []
                while True:
                    line = input()
                    if line.strip() == ">>>":
                        break
                    lines.append(line)
                user_input = "\n".join(lines)

            if not user_input:
                continue

            print("GAIA > ", end="", flush=True)

            # The core of the loop: iterate through events from the agent
            for event in agent_core.run_turn(user_input):
                if event["type"] == "token":
                    print(event["value"], end="", flush=True)
                elif event["type"] == "interruption_start":
                    print(f"\n\n--- 🔔 INTERRUPT: {event['reason']} ---")
                    print("🤔 Engaging self-reflection to generate a corrected response...\n")
                elif event["type"] == "correction_start":
                    print("GAIA (Corrected) > ", end="", flush=True)
                elif event["type"] == "action_start":
                    print("\n\n--- ⚡ ACTIONS DETECTED ---")
                elif event["type"] == "action_reflect":
                    print(f"🤔 Reflecting on: {event['command']}")
                elif event["type"] == "action_blocked":
                    print(f"⚠️ Action blocked by self-reflection: {event['reason']}")
                elif event["type"] == "action_executing":
                    print(f"Executing: {event['command']}")
                elif event["type"] == "action_failure":
                    print(f"❌ Action failed: {event['command']}\n   Error: {event['error']}")
                elif event["type"] == "action_end":
                    print("--- ✅ ACTIONS COMPLETE ---")

            print() # Final newline for the next prompt

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting chat mode.")
            break
        except Exception as e:
            logger.error(f"Error during rescue chat loop: {e}", exc_info=True)
            print(f"\n❌ An error occurred: {e}")


# --- Main Execution Block ---
if __name__ == "__main__":
    ai = MinimalAIManager()
    ai.initialize()

    print("""
    🧠 GAIA Rescue Shell initialized.

    This is a minimal, robust shell for diagnostics and direct interaction.
    GAIA's chat and cognitive functions are available.

    • Type `rescue_chat_loop()` to begin an interactive chat.
    • Use `ai.read('path/to/file')` or `ai.write(...)` for file operations.
    • Use `ai.execute('ls -l')` for safe shell commands.
    • Use `ai.helper.<func>()` for utilities like `create_codebase_overview`.
    • Use `ai.conversation_manager.reset()` to clear chat history.
    • Type `reload("app.utils.gaia_rescue_helper")` to hot-reload the helper module.
    • Press Ctrl+D or type `exit()` to leave the rescue shell.

    """)

    code.interact(local={
        "ai": ai,
        "rescue_chat_loop": rescue_chat_loop,
        "status": lambda: print(ai.status),
        "reload": ai.reload,
        "vector_query": vector_query,
        "embed_reference": embed_gaia_reference
    })