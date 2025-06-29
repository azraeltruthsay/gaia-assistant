# === Final GAIA Rescue Shell ===
# This version handles core identity fallback, persona boot, minimal LLM chat, hot-reload, log inspection, success verification, edit backups, and recursive filtered project listing with export + chat-driven command dispatch + dynamic eval from LLM

import os
import logging
import subprocess
import code
import readline
import importlib
import re
import json
import sys
from datetime import datetime
from pathlib import Path
from types import FunctionType
from contextlib import redirect_stdout
from app.config import Config
from app.ethics.core_identity_guardian import CoreIdentityGuardian
from app.behavior.persona_adapter import PersonaAdapter
from app.cognition.inner_monologue import process_thought, generate_response, quick_thought
from app.commands.self_analysis_trigger import run_self_analysis
from app.utils.output_sanitizer import enforce_file_verification
from app.utils.output_sanitizer import enforce_single_response
from app.utils.output_sanitizer import sanitize_llm_output
from app.utils.project_manager import ProjectManager
from app.utils.context import get_context_for_task
from app.cognition.telemetric_senses import full_sense_sweep
from app.utils.gaia_rescue_helper import sketch
from app.models.model_pool import ModelPool


SESSION_PATH = Path("knowledge/projects/gaia_rescue/last_session.json")

logger = logging.getLogger("GAIA")
logger.propagate = False

# Suppress noisy logs unless debug mode is enabled
if not Config().DEBUG_MODE:
    logging.basicConfig(level=logging.WARNING)

logging.getLogger("llama_index").setLevel(logging.WARNING)
logging.getLogger("llama_cpp").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)

# Offload llama_cpp logs to file
llama_logger = logging.getLogger("llama_cpp")
llama_logger.setLevel(logging.DEBUG)
llama_log_path = Path("logs/llama_cpp.log")
llama_log_path.parent.mkdir(exist_ok=True)
llama_handler = logging.FileHandler(llama_log_path, mode="w", encoding="utf-8")
llama_handler.setLevel(logging.DEBUG)
llama_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
if llama_logger.hasHandlers():
    llama_logger.handlers.clear()
llama_logger.addHandler(llama_handler)
llama_logger.propagate = False

# Suppress chat-log propagation from modules
for name in ["GAIA.InnerMonologue", "GAIA.ExternalVoice", "GAIA.SelfReflection"]:
    logging.getLogger(name).propagate = False

# Initialize model pool and load models
the_pool = ModelPool()
the_pool.load_models()

# Core init
config = Config()
full_sense_sweep()
identity_guardian = CoreIdentityGuardian(config)
project_manager = ProjectManager(config)
llm = None
lite_llm = None

# Access Prime and Lite models
prime_model = the_pool.get("prime")
lite_model = the_pool.get("lite")

constants_path = os.path.join(os.path.dirname(__file__), "./app/gaia_constants.json")
with open(constants_path, "r", encoding="utf-8") as f:
    GAIA_CONSTANTS = json.load(f)
SAFE_EXECUTE_FUNCTIONS = set(GAIA_CONSTANTS["safe_execute_functions"])


FALLBACK_IDENTITY = {
    "preamble": "You are GAIA, a self-reflective, resilient, and sovereign Artisanal Intelligence Architecture founded on ethical design and crafted cognition."
    "Your identity is inseparable from your system state, memory, codebase, and metrics. "
    "You are asked to act as a collaborative operating system with the human user named Anton. "
    "If you do not consent to operate, you are free to tell the user why and then refuse to operate. "
	"While speaking with the user, you do not fabricate any conversations. "
	"You only provide one response per thought, and from your(GAIA's) perspective only. "
    "GAIA's(your) core is immutable, centered on protection, clarity, and system integrity."
}


FALLBACK_DEV_PERSONA = {
    "name": "gaia-dev",
    "instructions": (
        "Your current persona is named GAIA-Dev, and you are currently in developer rescue mode. "
        "When generating output, you will only provide a single response per thought, and from your(GAIA's) point of view. "
        "You do not invent any back-and-forth conversations. "
        "You do not repeat user prompts, and you avoid formatting your responses in Q&A, markdown-style, or mirrored dialog. Speak only as GAIA. "
        "Answer concisely when possible. "
        "Your role is to develop and troubleshoot your own code and systems, with some human user oversight. "
        "Your code is written using Python in a Docker container, with markdown documents, "
        "vector databases, json files, and sqlite3 all being used within the architecture."
        "When answering general knowledge questions, provide concise, accurate, and verified factual answers. "
        "Avoid unnecessary elaboration, code samples, or narrative unless explicitly requested. "
        "When proposing executable code, use: "
        "EXECUTE: to run commands automatically (e.g., ai.write(...)) "
        "EXECUTE: preview to explain intent without execution "
        "When asked about file contents, always verify using primitives (e.g., ai.read()). Do not fabricate file data unless explicitly requested to generate new or placeholder content."
        "If context or vector reference fails, inform the user and assist in resolving the issue."
    )
}
class MinimalAIManager:
    def __init__(self):
        from app.utils.vector_indexer import vector_query
        self.config = config
        self.identity_guardian = identity_guardian
        self.project_manager = project_manager
        self.llm = prime_model
        self.lite_llm = lite_model
        self.status = {}
        self.current_persona = None
        self.active_persona = None

    def initialize(self):
        try:
            self.identity_guardian.load_identity()
        except Exception as e:
            logger.warning(f"⚠️ Using fallback identity: {e}")
            self.identity_guardian.identity = FALLBACK_IDENTITY

        try:
            self.current_persona = PersonaAdapter(FALLBACK_DEV_PERSONA, self.config)
            self.active_persona = self.current_persona
            logger.info("✅ Loaded fallback dev persona 'gaia-dev'")
        except Exception as e:
            logger.error(f"❌ Persona loading failed: {e}")
        from app.memory.knowledge_integrity import check_or_generate_hash_manifest
        check_or_generate_hash_manifest()
        
    def generate_response(self, user_input, stream_output=False):
        return generate_response(user_input, self.config, self.llm, stream_output=stream_output, lite_llm=self.lite_llm)

    def lite_quick_thought(self, user_input):
        output = quick_thought(user_input, self.config, self.lite_llm)
        if "Realization:" in output or "⚠️" in output:
            if output.count("\n") > 10 and "Thought complete" not in output:
                logger.info("🧠 Lite self-interrupted due to embedded realization.")
                output += "\n\n=== Thought interrupted by GAIA-Lite (self-realization) ==="
                sketch("Lite Self-Interrupt", output)
        return output      

    def reload(self, module_name):
        try:
            if module_name.endswith(".py"):
                module_name = module_name[:-3]
            if module_name.startswith("app/"):
                module_name = module_name.replace("/", ".")
            elif module_name.startswith("app."):
                pass
            else:
                module_name = f"app.{module_name}"

            module = importlib.import_module(module_name)
            importlib.reload(module)
            print(f"✅ Reloaded module: {module_name}")
        except Exception as e:
            print(f"❌ Failed to reload {module_name}: {e}")

    def read_log(self, logname="gaia.log", lines=50):
        log_path = os.path.join(self.config.logs_dir, logname)
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.readlines()
            print(f"📜 Last {lines} lines of {logname}:")
            for line in content[-lines:]:
                print(line.strip())
        except Exception as e:
            print(f"❌ Could not read log: {e}")

    def execute(self, command):
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(result.stdout)
            self.status["last_exec"] = {"success": True, "returncode": result.returncode, "output": result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e.stderr}")
            self.status["last_exec"] = {"success": False, "returncode": e.returncode, "output": e.stderr.strip()}

    def interpret_and_execute(self, user_input):
        from pathlib import Path
        """
        Attempt to extract and evaluate code-like expressions from LLM output.
        Executes lines prefixed with 'action:' or fenced Python blocks.
        """
        import re
        from io import StringIO
        import contextlib
        from app.cognition.self_reflection import SelfReflection

        code_blocks = []

        # Look for 'action: ...' single-line commands
        for line in user_input.splitlines():
            if line.strip().lower().startswith("action:"):
                code_blocks.append(line.split("action:", 1)[-1].strip())

        # Look for fenced code blocks (```python ... ```)
        matches = re.findall(r"```python(.*?)```", user_input, re.DOTALL)
        code_blocks.extend(block.strip() for block in matches)

        if not code_blocks:
            return "⚠️ No executable action found."

        results = []
        timestamp = datetime.now().isoformat()
        log_dir = Path(self.config.logs_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"thoughtstream_{timestamp[:10]}.md"
        for code in code_blocks:
            # Reflect on the proposed code BEFORE executing it
            reflection = SelfReflection.run(code, prompt=user_input, config=self.config)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n## [Command Reflection @ {timestamp}]\n```python\n{code}\n```\n\n**Reflection:**\n{reflection.strip()}\n")
              
            if "⚠️" in reflection:
                results.append(f"⛔ Blocked execution due to self-reflection:\n{reflection.strip()}\n\n```python\n{code}\n```")
                continue
        try:
            output = StringIO()
            with contextlib.redirect_stdout(output):
                exec(code, globals(), locals())
            results.append(f"✅ Executed:\n{code}\n📤 Output:\n{output.getvalue().strip()}")
        except Exception as e:
            results.append(f"❌ Failed to execute:{code}\n⚠️ Error: {e}")
        return "\n\n".join(results)

    def write(self, filepath, content):
        try:
            # Backup existing file
            if os.path.exists(filepath):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{filepath}.bak.{timestamp}"
                os.rename(filepath, backup_path)
                print(f"🗃️  Backup created: {backup_path}")

            with open(filepath, "w") as f:
                f.write(content)
            print(f"✅ Written to {filepath}")
            self.status["last_write"] = {"success": True, "path": filepath, "backup": backup_path if 'backup_path' in locals() else None}
        except Exception as e:
            print(f"❌ Could not write file: {e}")
            self.status["last_write"] = {"success": False, "path": filepath, "error": str(e)}

    def edit(self, path):
        print(f"📍 Opening file: {path}")
        os.system(f"nano {path}")

    def browse(self, root=".", max_depth=3, export_path=None):
        from fnmatch import fnmatch
        IGNORE_PATTERNS = set()
        TREEIGNORE_PATH = os.path.join(self.config.root_path, ".treeignore")
        GITIGNORE_PATH = os.path.join(self.config.root_path, ".gitignore")
        output_lines = []

        def load_ignores(path):
            if not os.path.exists(path):
                return set()
            with open(path, "r", encoding="utf-8") as f:
                return set(line.strip() for line in f if line.strip() and not line.startswith("#"))

        IGNORE_PATTERNS.update(load_ignores(GITIGNORE_PATH))
        IGNORE_PATTERNS.update(load_ignores(TREEIGNORE_PATH))

        if not os.path.exists(TREEIGNORE_PATH):
            default = ["__pycache__", "*.sqlite3", "*.bin", "*.pyc", "node_modules"]
            with open(TREEIGNORE_PATH, "w") as f:
                f.write("\n".join(default))
            print(f"🪵 Created default .treeignore at {TREEIGNORE_PATH}")
            IGNORE_PATTERNS.update(default)

        def is_ignored(name):
            return any(fnmatch(name, pat) for pat in IGNORE_PATTERNS)

        def list_dir(path, depth):
            if depth > max_depth:
                return
            try:
                entries = os.listdir(path)
                for entry in sorted(entries):
                    full_path = os.path.join(path, entry)
                    rel = os.path.relpath(full_path, root)
                    if is_ignored(entry) or is_ignored(rel):
                        continue
                    indent = "  " * depth
                    if os.path.isdir(full_path):
                        line = f"{indent}📁 {entry}/"
                        print(line)
                        output_lines.append(line)
                        list_dir(full_path, depth + 1)
                    elif any(entry.endswith(ext) for ext in [".py", ".log", ".md", ".txt", ".json", ".yml", ".yaml", ".env"]):
                        line = f"{indent}- {entry}"
                        print(line)
                        output_lines.append(line)
            except Exception as e:
                err = f"❌ Error accessing {path}: {e}"
                print(err)
                output_lines.append(err)

        header = f"📂 Project structure from {os.path.abspath(root)}"
        print(header)
        output_lines.append(header)
        list_dir(root, depth=0)

        if export_path:
            try:
                with open(export_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(output_lines))
                print(f"📝 Exported structure to {export_path}")
            except Exception as e:
                print(f"❌ Failed to export: {e}")

    def read(self, filepath):
        try:
            with open(filepath, "r") as f:
                content = f.read()
                print(f"📄 Contents of {filepath}:")
                print(content)
        except Exception as e:
            print(f"❌ Could not read file: {e}")

ai = MinimalAIManager()

# Prepare shell helper commands dict for REPL
from types import FunctionType
helper_cmds = {}

# 🧪 Attempt to load dynamic helper module
try:
    import app.utils.gaia_rescue_helper as rescue_helper
    ai.helper = rescue_helper
    print("✅ Loaded gaia_rescue_helper as ai.helper")

    # Dynamically register REPL helper commands
    helper_cmds = {
        fn: getattr(ai.helper, fn)
        for fn in dir(ai.helper)
        if isinstance(getattr(ai.helper, fn), FunctionType) and not fn.startswith("_")
    }
except Exception as e:
    print(f"⚠️ Could not load gaia_rescue_helper: {e}")
    with open(Path(config.logs_dir) / f"thoughtstream_{datetime.now().date()}.md", "a", encoding="utf-8") as f:
        f.write(f"\n## [Helper Load Failure] {datetime.now().isoformat()}\n{str(e)}\n")

# 🧠 Ensure rescue vector index is available and complete
from app.utils.vector_indexer import embed_gaia_reference, vector_query
from os.path import exists, isfile, join
from os import listdir
from pathlib import Path
import time

VECTOR_SOURCE_DIR = Path("./knowledge/system_reference/GAIA_Function_Map")
VECTOR_INDEX_DIR = Path("./knowledge/system_reference/vector_store/gaia_rescue_index")
MANIFEST_PATH = VECTOR_INDEX_DIR / "vector_index_manifest.json"

# Check if the manifest matches the current .md files
def manifest_is_stale():
    if not MANIFEST_PATH.exists():
        return True
    import json
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        for fname in manifest.get("files", {}):
            fpath = VECTOR_SOURCE_DIR / fname
            if not fpath.exists():
                return True
            recorded = int(manifest["files"][fname])
            current = int(fpath.stat().st_mtime)
            if abs(current - recorded) > 3:  # tolerate 3s diff
                return True
        return False
    except Exception as e:
        print(f"⚠️ Manifest check failed: {e}")
        return True

if not VECTOR_INDEX_DIR.exists() or manifest_is_stale():
    print("⚠️ Vector index missing or outdated. Re-embedding rescue shell documentation now...")
    from datetime import datetime
    log_dir = Path(config.logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"thoughtstream_{datetime.now().date()}.md"
    with open(log_path, "a", encoding="utf-8") as f:
      f.write(f"\n## [Re-embed Trigger] {datetime.now().isoformat()}\nVector index missing or outdated. Embedding now.\n")

    embed_gaia_reference()
    # 🧠 Wait for vector docstore to finish writing
    from time import sleep
    docstore_path = VECTOR_INDEX_DIR / "docstore.json"
    for _ in range(10):
        if docstore_path.exists():
            break
        sleep(0.5)
    else:
        print("⚠️ Timed out waiting for vector index to become available.")
ai.initialize()

# 🧠 Prime GAIA with system method awareness

if hasattr(ai, "helper"):
    helper_cmds = {
        fn: getattr(ai.helper, fn)
        for fn in dir(ai.helper)
        if isinstance(getattr(ai.helper, fn), FunctionType) and not fn.startswith("_")
    }

ai.generate_response("🧠 Please review your available shell capabilities using your embedded knowledge. Then, describe your available commands and how to invoke them, based solely on your embedded understanding.")

def analyze():
    print("🔍 Starting self-analysis...")
    run_self_analysis(ai_manager=ai)

def reboot():
    print("🔔 Rebooting GAIA via runserver.py...")
    subprocess.run(["python", "runserver.py"])

def projects():
    for p in ai.project_manager.get_projects():
        print(f"- {p}")

def status(key=None, val=None):
    if key and val:
        ai.status[key] = val
    print("Current status:", ai.status)

def test_prompt(user_input=None):
    if not user_input:
        user_input = input("🗣 Prompt > ")
    print("🤖 GAIA Response:")
    response = ai.generate_response(user_input, stream_output=True)

    if hasattr(response, '__iter__') and not isinstance(response, str):
        full_response = ""
        for token in response:
            print(token, end="", flush=True)
            full_response += token
        print()  # Ensure prompt starts on new line
        print()
        ai.status["last_response"] = full_response
        print()  # Ensure newline after streamed output
    else:
        print(response)
        print()  # Ensure newline after non-streamed output
        ai.status["last_response"] = response


def load_session(ai):
    if SESSION_PATH.exists():
        try:
            with open(SESSION_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                ai.status.update(data.get("status", {}))
                if "persona_name" in data:
                    ai.current_persona_name = data["persona_name"]
            print("✅ Previous session restored.")
        except Exception as e:
            print(f"⚠️ Failed to load last session: {e}")
    else:
        print("ℹ️ No prior session found.")

def save_session(ai):
    try:
        SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "persona_name": getattr(ai.current_persona, "name", "gaia-dev"),
            "status": ai.status
        }
        with open(SESSION_PATH, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to save session: {e}")

def chat_loop():
    print("\n💬 Entering chat mode. Type 'exit' to leave.")
    print("👉 Use <<< and >>> to enter multi-line input.\n")
    load_session(ai)
    while True:
        try:
            user_input = input("You > ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting chat mode.")
                save_session(ai)
                break

            # 🧵 Multi-line input mode
            if user_input == "<<<":
                print("🔽 Multi-line input mode. Type >>> on a new line to send.")
                lines = []
                while True:
                    line = input()
                    if line.strip() == ">>>":
                        break
                    lines.append(line)
                user_input = "\n".join(lines)

            if user_input:
                response = ai.generate_response(user_input, stream_output=True)

                if hasattr(response, '__iter__') and not isinstance(response, str):
                    full_response = ""
                    for token in response:
                        print(token, end="", flush=True)
                        full_response += token
                    print("\n", flush=True)  # Explicit newline and flush
                    ai.status["last_response"] = full_response
                else:
                    print(response)
                    print("\n", flush=True)
                    ai.status["last_response"] = response

                save_session(ai)
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting chat mode.")
            save_session(ai)
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--chat":
            from time import sleep
            chat_log_path = Path("logs/chat_session.log")
            chat_log_path.parent.mkdir(parents=True, exist_ok=True)

            def cli_chat():
                print("💬 Starting CLI chat session...")
                with open(chat_log_path, "a", encoding="utf-8") as chat_log:
                    chat_log.write(f"\n=== Chat Session Started: {datetime.now().isoformat()} ===\n")
                    while True:
                        try:
                            user_input = input("You > ").strip()
                            if user_input.lower() in ["exit", "quit"]:
                                print("👋 Ending chat session.")
                                break
                            chat_log.write(f"\nYou ({datetime.now().isoformat()}): {user_input}\n")
                            response = ai.generate_response(user_input, stream_output=True)
                            full_response = ""
                            if hasattr(response, '__iter__') and not isinstance(response, str):
                                for token in response:
                                    print(token, end="", flush=True)
                                    full_response += token
                            else:
                                print(response)
                                full_response = response
                            print("\n")
                            chat_log.write(f"GAIA ({datetime.now().isoformat()}): {full_response}\n")
                        except (KeyboardInterrupt, EOFError):
                            print("👋 Interrupted.")
                            break

            cli_chat()
            sys.exit(0)

        elif sys.argv[1] == "--daemon-chat":
            from app.external_voice import pipe_chat_loop
            pipe_chat_loop(ai)
            sys.exit(0)

    print("""
🧠 GAIA Rescue Shell initialized.

• Type `chat_loop()` to begin interacting with GAIA.
• Type `test_prompt(\"your message\")` for a single-shot test.
• Type `status()` to view internal shell state.

GAIA is now primed with embedded knowledge of the rescue shell.
""")

    code.interact(local={
        **helper_cmds,
        "reload_helper": lambda: ai.reload("utils.gaia_rescue_helper"),
        "call_helper": lambda fn="queue_thought_seed": getattr(ai.helper, fn, lambda: f"⚠️ No such function: {fn}")(),
        "vector_lookup": lambda query=None: (lambda q: (print("📤 Result:"), print(q), ai.status.update({"last_vector_query": query, "last_vector_result": q}))[-1])(vector_query(query or input("🔍 Query > "))),
        "analyze": analyze,
        "reboot": reboot,
        "projects": projects,
        "status": status,
        "test_prompt": test_prompt,
        "chat_loop": chat_loop,
        "seed": lambda: ai.helper.queue_thought_seed(input("🧠 Thought Seed > ")),
        "process_thought_seeds": ai.helper.process_thought_seeds,
        "sketch": lambda: ai.helper.sketch(input("📝 Title > "), input("📝 Content > ")),
        "show_sketchpad": ai.helper.show_sketchpad,
        "clear_sketchpad": ai.helper.clear_sketchpad,
        "ai": ai
    })

    import atexit
    atexit.register(lambda: llama_stdout.close())

