import faulthandler, os
# ensure logs dir exists
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
# open a file to record native stack traces
fh = open(os.path.join(log_dir, "faulthandler.log"), "w")
faulthandler.enable(fh, all_threads=True)

import argparse
import code
import importlib
import logging
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, Any

import faulthandler

# GAIA internal modules
from app.behavior.persona_adapter import PersonaAdapter
from app.behavior.persona_manager import PersonaManager
from app.cognition.agent_core import AgentCore
from app.cognition import topic_manager
from app.config import Config
from app.ethics.core_identity_guardian import CoreIdentityGuardian
from app.ethics.ethical_sentinel import EthicalSentinel
import app.utils.gaia_rescue_helper as helper
from app.memory.session_manager import SessionManager
from app.models.model_pool import model_pool
from app.utils.vector_indexer import embed_gaia_reference, vector_query

faulthandler.enable()  # dumps C‑level traceback on seg‑fault

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
config = Config()
LOG_DIR = config.LOGS_DIR
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    handlers=[
        logging.StreamHandler(),                     # stdout (CLI)
        logging.FileHandler(f"{LOG_DIR}/gaia_cli.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("GAIA.Rescue")

# Silence noisy deps that spam INFO
for noisy in ("llama_index", "llama_cpp", "transformers", "sentence_transformers", "huggingface_hub"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

# =============================================================================
#  MinimalAIManager – a super‑light wrapper around GAIA’s cognition stack
# =============================================================================
class MinimalAIManager:
    """Lightweight manager for GAIA rescue shell."""

    # --------------------------------------------------------------------- init
    def __init__(self):
        # ------------------------------------------------------------------ cfg
        self.config: Config = model_pool.config  # reuse global Config instance
        # Back‑compat shim for legacy UPPER‑CASE attrs consumed by older helpers
        self.config.MAX_TOKENS = getattr(self.config, "max_tokens", 4096)
        self.config.RESPONSE_BUFFER = self.config.constants.get("RESPONSE_BUFFER", 512)

        # ---------------------------------------------------------------- models
        self.llm = model_pool.get("prime")
        self.lite_llm = model_pool.get("lite")
        self.embed_model = model_pool.get("embed")

        # ---------------------------------------------------------------- state
        self.status: Dict[str, Any] = {"boot_time": datetime.utcnow().isoformat()}
        self.helper = helper  # hot‑reloadable helper limb
        self.topic_cache_path = "app/shared/topic_cache.json"

        # ------------------------------------------------------------- ethics
        self.identity_guardian = CoreIdentityGuardian(config=self.config)
        self.ethical_sentinel = EthicalSentinel(identity_guardian=self.identity_guardian)

        # ---------------------------------------------------------------- sess
        self.session_manager = SessionManager(config=self.config, llm=self.llm, embed_model=self.embed_model)
        
        # ---------------------------------------------------------------- pool / persona
        self.model_pool = model_pool  # reuse already‑loaded pool
        self.persona_manager = PersonaManager(self.config.PERSONAS_DIR)
        persona = self.persona_manager.load_persona_data("dev")
        if persona and hasattr(self.model_pool, "set_persona"):
            try:
                self.model_pool.set_persona(persona)
            except Exception:  # pragma: no cover – not fatal in rescue mode
                logger.warning("ModelPool.set_persona() failed; continuing without persona binding.")

    # --------------------------------------------------------------------- init
    def initialize(self, persona_name: str = "dev") -> None:
        """Load the specified persona or fall back to an emergency stub."""
        try:
            data = self.persona_manager.load_persona_data(persona_name) or {}
            if not data:
                logger.error("❌ Could not load '%s' persona; using fallback.", persona_name)
                data = {
                    "name": "gaia-dev-emergency",
                    "description": "Emergency fallback persona.",
                    "template": "You are GAIA‑Dev, operating in a minimal rescue shell.",
                    "instructions": [
                        "Primary persona file is missing. Operate with caution.",
                    ],
                }
            self.active_persona = PersonaAdapter(data, self.config)
            logger.info("✅ Loaded %s persona '%s' via PersonaManager.", "default" if persona_name == "dev" else "", self.active_persona.name)
        except Exception as exc:  # pragma: no cover
            logger.exception("Persona init failed: %s", exc)

    # ------------------------------------------------------------------- reload
    def reload(self, module_name: str) -> None:
        """Hot‑reload a module; handy while tinkering inside the shell."""
        try:
            if module_name.endswith(".py"):
                module_name = module_name[:-3]
            if module_name.startswith("app/"):
                module_name = module_name.replace("/", ".")

            module_path = module_name.replace("app.", "app/").replace(".", "/") + ".py"
            if not os.path.exists(module_path):
                logger.error("❌ File not found: %s", module_path)
                return

            module = importlib.import_module(module_name)
            importlib.reload(module)

            if "gaia_rescue_helper" in module_name:
                self.helper = importlib.import_module("app.utils.gaia_rescue_helper")
            logger.info("✅ Reloaded module: %s", module_name)
        except Exception as exc:  # pragma: no cover
            logger.exception("Reload failed: %s", exc)

    # --------------------------------------------------------------------- I/O
    def read(self, filepath: str) -> None:
        """Log file contents to console."""
        try:
            with open(filepath, "r", encoding="utf‑8") as fh:
                content = fh.read()
            logger.info("📄 %s\n---\n%s\n---", filepath, content)
        except Exception as exc:  # pragma: no cover
            logger.error("❌ Read error: %s", exc)

    def write(self, filepath: str, content: str) -> None:
        """Write file with timestamped backup."""
        try:
            if os.path.exists(filepath):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup = f"{filepath}.bak.{ts}"
                os.rename(filepath, backup)
                logger.info("🗃️  Backup created: %s", backup)

            with open(filepath, "w", encoding="utf‑8") as fh:
                fh.write(content)
            logger.info("✅ Wrote %s", filepath)
        except Exception as exc:  # pragma: no cover
            logger.error("❌ Write error: %s", exc)

    # --------------------------------------------------------- safe execute
    def execute(self, command: str) -> None:
        """Run a whitelisted shell command."""
        safe_cmds = self.config.SAFE_EXECUTE_FUNCTIONS
        if not any(command.strip().startswith(c) for c in safe_cmds):
            logger.error("❌ Unsafe command blocked: %s (allowed: %s)", command, safe_cmds)
            return

        try:
            res = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, timeout=10)
            out, err = res.stdout.strip(), res.stderr.strip()
            if out:
                logger.info("🖥️  STDOUT\n---\n%s\n---", out)
            if err:
                logger.warning("⚠️  STDERR\n---\n%s\n---", err)
            self.status["last_exec"] = {"success": True, "command": command, "stdout": out, "stderr": err}
        except subprocess.CalledProcessError as exc:
            logger.error("❌ Exit code %s\n%s", exc.returncode, exc.stderr)
        except subprocess.TimeoutExpired:
            logger.error("❌ Command timed out after 10 s: %s", command)
        except Exception as exc:  # pragma: no cover
            logger.exception("Exec failed: %s", exc)

    # ----------------------------------------------------------- topic helpers
    def add_topic(self, topic: Dict[str, Any]) -> None:
        """Primitive to add a new topic to GAIA's internal thought cache."""
        topic_manager.add_topic(self.topic_cache_path, topic)

    def resolve_topic(self, topic_id: str) -> bool:
        """Primitive to mark a topic as resolved."""
        return topic_manager.resolve_topic(self.topic_cache_path, topic_id)

    def update_topic(self, topic_id: str, updates: Dict[str, Any]) -> bool:
        """Primitive to update an existing topic's metadata."""
        return topic_manager.update_topic(self.topic_cache_path, topic_id, updates)


# =============================================================================
#  Interactive chat loop
# =============================================================================

def rescue_chat_loop(ai: MinimalAIManager, session_id: str) -> None:
    """Interactive chat session that streams AgentCore events for a given session."""
    print(f"\n💬 Entering GAIA Rescue chat mode for session: '{session_id}'\n👉 Use '<<<' and '>>>' on new lines for multi‑line input.\n")

    # Pass the sentinel to the agent core
    agent_core = AgentCore(ai, ethical_sentinel=ai.ethical_sentinel)

    while True:
        try:

            prompt = input("You > ").strip()
            if prompt.lower() in {"exit", "quit"}:
                print("\n👋 Exiting chat mode.")
                break

            if prompt == "<<<":
                print("🔽 Multi‑line mode (type >>> to send).")
                lines = []
                while (line := input()) != ">>>":
                    lines.append(line)
                prompt = "\n".join(lines)

            if not prompt:
                continue

            print("GAIA > ", end="", flush=True)

            t_loop_start = time.perf_counter()
            logger.info(f"gaia_rescue: starting run_turn for prompt")
            for event in agent_core.run_turn(prompt, session_id=session_id):
                et, val = event["type"], event.get("value")
                if et == "token":
                    print(val, end="", flush=True)
                elif et == "interruption_start":
                    print(f"\n\n--- 🔔 INTERRUPT: {event['reason']} ---")
                    print("🤔 Engaging self‑reflection to generate a corrected response…\n")
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
            t_loop_end = time.perf_counter()
            logger.info(f"gaia_rescue: run_turn loop took {t_loop_end - t_loop_start:.2f}s")
            print()  # newline for next prompt

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting chat mode.")
            break
        except Exception as exc:  # pragma: no cover
            logger.exception("Chat loop error: %s", exc)
            print(f"\n❌ Error: {exc}")

    # Setup file logging
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, "gaia_rescue.log"), mode="a")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)

# =============================================================================
#  CLI entry‑point
# =============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GAIA Rescue Shell")
    parser.add_argument("--session-id", type=str, default="cli_default_session", help="Session ID to use/continue.")
    parser.add_argument("--persona", type=str, default="dev", help="Persona to load (default: dev).")
    args = parser.parse_args()
    SESSION_ID = args.session_id

    ai = MinimalAIManager()
    ai.initialize(args.persona)

    print(
        "\n🧠 GAIA Rescue Shell initialized.\n"
        f"   Session ID: {SESSION_ID}\n\n"
        "Diagnostics & direct interaction available.\n\n"
        "• rescue_chat_loop()         – start interactive chat for the current session\n"
        "• ai.read('path') / ai.write – file ops\n"
        "• ai.execute('ls -l')        – safe shell\n"
        "• ai.helper.*                – helper utilities\n"
        f"• ai.session_manager.reset_session('{SESSION_ID}') – clear this session's history\n"
        "• reload('app.utils.gaia_rescue_helper') – hot‑reload helper\n"
        "• exit() or Ctrl‑D           – quit\n"
    )

    code.interact(
        local={
            "ai": ai,
            "rescue_chat_loop": lambda: rescue_chat_loop(ai, SESSION_ID),
            "status": lambda: print(ai.status),
            "reload": ai.reload,
            "vector_query": vector_query,
            "embed_reference": embed_gaia_reference,
        }
    )