# DEPRECATED: This file is a legacy placeholder and is not actively used in the rescue shell.
# Please refer to gaia_rescue.py for the current implementation.

import logging
from datetime import datetime
from llama_cpp import Llama

from app.config import Config
from app.cognition.inner_monologue import process_thought
from app.utils.project_manager import ProjectManager
from app.memory.status_tracker import GAIAStatus
from app.utils.code_analyzer import CodeAnalyzer
from app.utils.background.background_tasks import BackgroundTask
from app.utils.background.task_queue import TaskQueue
from app.memory.conversation.manager import ConversationManager
from app.behavior.persona_manager import PersonaManager
from app.behavior.persona_adapter import PersonaAdapter
from app.memory.session_manager import SessionManager
from app.commands.self_analysis_trigger import run_self_analysis
from app.models.vector_store import VectorStoreManager
from app.models.document import DocumentProcessor
from app.ethics.ethical_sentinel import EthicalSentinel
from app.cognition.self_reflection import run_self_reflection
from app.ethics.core_identity_guardian import CoreIdentityGuardian
from app.utils.context import get_context_for_task

logger = logging.getLogger("GAIA")

class AIManager:
    def __init__(self, config, minimal=False):
        self.config = config
        if minimal:
            logger.warning("⚠️ GAIA initialized in MINIMAL (rescue) mode.")
            self.project_manager = ProjectManager(config)
            return

        self.persona_manager = PersonaManager(self.config.personas_dir)
        self.vector_store_manager = VectorStoreManager(config=self.config)
        self.doc_processor = DocumentProcessor(self.vector_store_manager)
        self.code_analyzer = CodeAnalyzer(config=self.config)
        self.background_processor = BackgroundTask(self)
        self.self_reflection = run_self_reflection(config)
        self.conversation_manager = ConversationManager(config=self.config)
        self.session_manager = SessionManager(self.config)
        self.project_manager = ProjectManager(config)
        self.identity_guardian = CoreIdentityGuardian(config)
        self.ethical_sentinel = EthicalSentinel(self.identity_guardian)
        self.llm = None
        self.current_persona_name = None
        self.current_persona = None
        self.status = {"initialized": False}
        self.task_queue = TaskQueue()
        self.initialized = False

    def generate_response(self, user_prompt: str) -> str:
        if not self.llm:
            logger.warning("🛑 LLM not loaded.")
            return "I'm still initializing..."

        if not self.current_persona:
            logger.warning("🛑 No active persona set.")
            return "I'm missing my persona setup."

        persona = self.current_persona
        instructions = persona.instructions if hasattr(persona, "instructions") else []
        traits = persona.traits if hasattr(persona, "traits") else {}

        gil_response = self.initiative_loop.check_topics_and_generate(user_prompt)
        if gil_response:
            logger.info("🔁 [GIL] Responding to active initiative topic")
            return gil_response

        if not self.ethical_sentinel.run_full_safety_check(traits, instructions, user_prompt):
            return "⚠️ Request denied due to safety or identity constraints."

        logger.info("🧠 Invoking inner_monologue for prompt generation")
        return process_thought(
            task_type="chat",
            persona=self.current_persona_name or "unknown",
            instructions=instructions,
            payload=user_prompt,
            identity_intro=self.identity_guardian.identity.get("preamble", ""),
            llm=self.llm,
            reflect=True,
            context=get_context_for_task("chat", config=self.config),
            config=self.config
        )

    def initialize(self):
        logger.info("Initializing AIManager components...")
        try:
            project_name = self.config.default_project_name
            persona_name = self.config.default_persona_name

            self.project_manager.set_active_project(project_name)
            logger.info(f"📁 Project initialized: {self.project_manager.active_project}")

            loaded_persona = self.persona_manager.set_persona(persona_name)
            if not loaded_persona:
                raise RuntimeError("Failed to load current persona.")
            self.current_persona = PersonaAdapter(loaded_persona, self.config)
            self.current_persona_name = self.persona_manager.get_current_persona_name()
            logger.info(f"✅ Persona loaded: {self.current_persona_name}")

            if not hasattr(self.current_persona, "traits") or not hasattr(self.current_persona, "instructions"):
                logger.debug(f"[DEBUG] Loaded persona keys: {self.current_persona.__dict__.keys()}")
                raise RuntimeError("PersonaAdapter missing required attributes.")

            self.session_manager.initialize_session(persona_name)
            logger.info("✅ Session initialized")

            self.doc_processor.load_and_preprocess_data(self.config.core_docs_path)
            logger.info("✅ Core docs loaded and embedded")

            try:
                self.llm = Llama(
                    model_path=self.config.model_path,
                    n_gpu_layers=self.config.n_gpu_layers,
                    n_ctx=self.config.max_tokens,
                    n_batch=self.config.n_batch,
                    use_mlock=True,
                    verbose=True
                )
                logger.info("🧠 Hermes (llama.cpp) model loaded successfully.")

                self.vector_store_manager.initialize_store()
                self.vector_store = self.vector_store_manager.vector_store
                logger.info("✅ Vector store initialized and assigned.")

            except Exception as e:
                logger.exception(f"❌ Failed to load Hermes model: {e}")

            self.status["initialized"] = True
            self.initialized = True
            logger.info(f"🎯 Initialization complete. Persona: {self.current_persona_name}, Project: {self.project_manager.active_project}")
            self.initiative_loop.start()
            return True
        except Exception as e:
            logger.exception(f"❌ AIManager failed to initialize: {e}")
            return False

    def set_persona(self, persona_name):
        persona = self.persona_manager.set_persona(persona_name)
        if persona:
            self.current_persona = PersonaAdapter(persona, self.config)
            self.current_persona_name = persona_name
            logger.info(f"✅ Persona switched to: {persona_name}")
            return True
        logger.warning(f"⚠️ Failed to switch to persona: {persona_name}")
        return False

    def get_persona(self):
        return self.current_persona

    def summarize_conversation(self):
        logger.info("Triggering conversation summarization...")
        return self.background_processor.process_conversation_task({"action": "summarize"})

    def embed_documents(self, doc_paths):
        logger.info("Embedding documents via DocumentProcessor...")
        return self.doc_processor.embed_documents(doc_paths)

    def analyze_codebase(self):
        logger.info("Initiating code analysis task...")
        return self.code_analyzer.analyze_codebase()

    def handle_intent(self, intent: str, message: str = None) -> str:
        if intent == "create_behavior":
            return "Sure! Let's define a new persona together."
        elif intent == "trigger_code_analysis":
            logger.info("🧠 Running self-analysis triggered by user.")
            return run_self_analysis(self)
        return "I'm not sure what to do with that yet — want to rephrase or try another request?"

    def update_background_status(self):
        self.background_status = {
            "status": "running",
            "last_check": datetime.utcnow().isoformat(),
            "active_tasks": self.task_queue.list_tasks() if hasattr(self.task_queue, "list_tasks") else []
        }

    def shutdown(self):
        logger.info("Shutting down AIManager...")
        self.vector_store_manager.persist()
        logger.info("Shutdown complete.")
