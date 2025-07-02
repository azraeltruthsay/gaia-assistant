# /home/azrael/Project/gaia-assistant/gaia_rescue.py
"""GAIA minimal rescue shell — hardening patch 2025-06-29."""

import argparse
import code
import importlib
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import faulthandler

# ── Core GAIA components ───────────────────────────────────────────────────────
from app.behavior.persona_adapter import PersonaAdapter
from app.behavior.persona_manager import PersonaManager
from app.cognition.agent_core import AgentCore
from app.config import Config
from app.memory.conversation.manager import ConversationManager
from app.models.model_pool import model_pool
from app.utils import gaia_rescue_helper as helper
from app.utils.vector_indexer import embed_gaia_reference, vector_query

# ── Crash-trace + logging setup ────────────────────────────────────────────────
faulthandler.enable()  # dumps C-level traceback on seg-fault
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger("GAIA.Rescue")

# Silence noisy deps
for noisy in (
    "llama_index",
    "llama_cpp",
    "transformers",
    "sentence_transformers",
    "huggingface_hub",
):
    logging.getLogger(noisy).setLevel(logging.WARNING)

# ── MinimalAIManager  ──────────────────────────────────────────────────────────
class MinimalAIManager:
    """Lightweight manager for GAIA rescue shell."""

    def __init__(self):
        self.config = model_pool.config
        self.llm = model_pool.get("prime")
        self.lite_llm = model_pool.get("lite")
        self.embed_model = model_pool.get("embed")
        self.status = {"boot_time": datetime.utcnow().isoformat()}
        self.helper = helper
        self.conversation_manager = ConversationManager(
            config=self.config, llm=self.llm, embed_model=self.embed_model
        )

        # Persona plumbing
        self.persona_manager = PersonaManager(self.config.PERSONAS_DIR)
        self.active_persona: Optional[PersonaAdapter] = None

    # --------------------------------------------------------------------- init
    def initialize(self) -> None:
        """Load the ‘dev’ persona or fall back to an emergency stub."""
        try:
            data = self.persona_manager.load_persona_data("dev") or {}
            if not data:
                logger.error("❌ Could not load 'dev' persona; using fallback.")
                data = {
                    "name": "gaia-dev-emergency",
                    "description": "Emergency fallback persona.",
                    "template": (
                        "You are GAIA-Dev, operating in a minimal rescue shell."
                    ),
                    "instructions": [
                        "Primary persona file is missing. Operate with caution."
                    ],
                }

            self.active_persona = PersonaAdapter(data, self.config)
            logger.info(
                "✅ Loaded dev persona '%s' via PersonaManager.",
                self.active_persona.name,
            )
        except Exception as exc:  # pragma: no cover
            logger.exception("Persona init failed: %s", exc)

    # ------------------------------------------------------------------- reload
    def reload(self, module_name: str) -> None:
        """Hot-reload a module; helpful during tinkering."""
        try:
            if module_name.endswith(".py"):
                module_name = module_name[:-3]
            if module_name.startswith("app/"):
                module_name = module_name.replace("/", ".")

            module_path = (
                module_name.replace("app.", "app/").replace(".", "/") + ".py"
            )
            if not os.path.exists(module_path):
                logger.error("❌ File not found: %s", module_path)
                return

            module = importlib.import_module(module_name)
            importlib.reload(module)

            if "gaia_rescue_helper" in module_name:
                self.helper = importlib.import_module(
                    "app.utils.gaia_rescue_helper"
                )
            logger.info("✅ Reloaded module: %s", module_name)
        except Exception as exc:  # pragma: no cover
            logger.exception("Reload failed: %s", exc)

    # --------------------------------------------------------------------- I/O
    def read(self, filepath: str) -> None:
        """Log file contents to console."""
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                content = fh.read()
            logger.info("📄 %s\n---\n%s\n---", filepath, content)
        except Exception as exc:
            logger.error("❌ Read error: %s", exc)

    def write(self, filepath: str, content: str) -> None:
        """Write file with timestamped backup."""
        try:
            if os.path.exists(filepath):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup = f"{filepath}.bak.{ts}"
                os.rename(filepath, backup)
                logger.info("🗃️  Backup created: %s", backup)

            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(content)
            logger.info("✅ Wrote %s", filepath)
        except Exception as exc:
            logger.error("❌ Write error: %s", exc)

    # ------------------------------------------------------------- safe execute
    def execute(self, command: str) -> None:
        """Run a whitelisted shell command."""
        safe_cmds = self.config.SAFE_EXECUTE_FUNCTIONS
        if not any(command.strip().startswith(c) for c in safe_cmds):
            logger.error(
                "❌ Unsafe command blocked: %s (allowed: %s)",
                command,
                safe_cmds,
            )
            return

        try:
            res = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            out = res.stdout.strip()
            err = res.stderr.strip()
            if out:
                logger.info("🖥️  STDOUT\n---\n%s\n---", out)
            if err:
                logger.warning("⚠️  STDERR\n---\n%s\n---", err)
            self.status["last_exec"] = {
                "success": True,
                "command": command,
                "stdout": out,
                "stderr": err,
            }
        except subprocess.CalledProcessError as exc:
            logger.error("❌ Exit code %s\n%s", exc.returncode, exc.stderr)
        except subprocess.TimeoutExpired:
            logger.error("❌ Command timed out after 10 s: %s", command)
        except Exception as exc:  # pragma: no cover
            logger.exception("Exec failed: %s", exc)


# ── Chat loop (presentation only) ─────────────────────────────────────────────
def rescue_chat_loop() -> None:
    """Interactive chat session that streams AgentCore events."""
    print(
        "\n💬 Entering GAIA Rescue chat mode. Type 'exit' to leave."
        "\n👉 Use '<<<' and '>>>' on new lines for multi-line input.\n"
    )

    agent_core = AgentCore(ai)  # core cognitive loop

    while True:
        try:
            prompt = input("You > ").strip()
            if prompt.lower() in {"exit", "quit"}:
                print("\n👋 Exiting chat mode.")
                break

            if prompt == "<<<":  # multi-line entry
                print("🔽 Multi-line mode (type >>> to send).")
                lines = []
                while (line := input()) != ">>>":
                    lines.append(line)
                prompt = "\n".join(lines)

            if not prompt:
                continue

            print("GAIA > ", end="", flush=True)

            for event in agent_core.run_turn(prompt):
                et, val = event["type"], event.get("value")
                if et == "token":
                    print(val, end="", flush=True)
                elif et == "interruption_start":
                    print(f"\n\n--- 🔔 INTERRUPT: {event['reason']} ---")
                    print(
                        "🤔 Engaging self-reflection to generate a corrected response…\n"
                    )
                elif et == "correction_start":
                    print("GAIA (Corrected) > ", end="", flush=True)
                elif et == "action_start":
                    print("\n\n--- ⚡ ACTIONS DETECTED ---")
                elif et == "action_reflect":
                    print(f"🤔 Reflecting on: {event['command']}")
                elif et == "action_blocked":
                    print(f"⚠️ Action blocked: {event['reason']}")
                elif et == "action_executing":
                    print(f"Executing: {event['command']}")
                elif et == "action_failure":
                    print(f"❌ Action failed: {event['error']}")
                elif et == "action_end":
                    print("--- ✅ ACTIONS COMPLETE ---")

            print()  # newline for next prompt

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting chat mode.")
            break
        except Exception as exc:  # pragma: no cover
            logger.exception("Chat loop error: %s", exc)
            print(f"\n❌ Error: {exc}")


# ── Entry-point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ai = MinimalAIManager()
    ai.initialize()

    print(
        """
🧠 GAIA Rescue Shell initialized.

Diagnostics & direct interaction available.

• rescue_chat_loop()         – start interactive chat
• ai.read('path') / ai.write – file ops
• ai.execute('ls -l')        – safe shell
• ai.helper.*                – helper utilities
• ai.conversation_manager.reset() – clear chat history
• reload('app.utils.gaia_rescue_helper') – hot-reload helper
• exit() or Ctrl-D           – quit
"""
    )

    code.interact(
        local={
            "ai": ai,
            "rescue_chat_loop": rescue_chat_loop,
            "status": lambda: print(ai.status),
            "reload": ai.reload,
            "vector_query": vector_query,
            "embed_reference": embed_gaia_reference,
        }
    )
