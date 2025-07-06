import os
import json
from pathlib import Path
import logging

logger = logging.getLogger("GAIA.Config")

BASE_DIR = Path(__file__).parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
PROJECTS_DIR = KNOWLEDGE_DIR / "projects"
PERSONAS_DIR = KNOWLEDGE_DIR / "personas"
LOGS_DIR = BASE_DIR / "logs"
TS_DIR = KNOWLEDGE_DIR / "logs" / "thoughtstreams"
ARTIFACTS_DIR = KNOWLEDGE_DIR / "artifacts"
VECTORDB_DIR = KNOWLEDGE_DIR / "vectordb"
COREDOCS_DIR = KNOWLEDGE_DIR / "core_docs"
SYSTEM_REF_DIR = KNOWLEDGE_DIR / "system_reference"
REFLECTIONS_DIR = KNOWLEDGE_DIR / "reflections"
CONSTANTS_PATH = BASE_DIR / "app" / "gaia_constants.json"

class Config:
    def __init__(self, persona=None, override_path=None):
        self._load_constants(override_path)
        self.BASE_DIR = BASE_DIR
        self.KNOWLEDGE_DIR = KNOWLEDGE_DIR
        self.PERSONAS_DIR = PERSONAS_DIR
        self.PROJECTS_DIR = PROJECTS_DIR
        self.LOGS_DIR = LOGS_DIR
        self.TS_DIR = TS_DIR
        self.ARTIFACTS_DIR = ARTIFACTS_DIR
        self.VECTORDB_DIR = VECTORDB_DIR
        self.COREDOCS_DIR = COREDOCS_DIR
        self.SYSTEM_REF_DIR = SYSTEM_REF_DIR
        self.REFLECTIONS_DIR = REFLECTIONS_DIR
        self.persona_name = persona or self.constants.get("persona_defaults", {}).get("name", "prime")
        self.identity = self.constants.get("identity", "GAIA - Artisanal Intelligence")
        self.identity_intro = self.constants.get("identity_intro", "")
        self.temperature = self.constants.get("temperature", 0.7)
        self.top_p = self.constants.get("top_p", 0.95)
        self.max_tokens = self.constants.get("max_tokens", 512)
        self.n_gpu_layers = self.constants.get("n_gpu_layers", 0)
        self.SHARED_DIR = "app/shared"
        self.SESSIONS_FILE = os.path.join(self.SHARED_DIR, "sessions.json")
        self.TOPIC_CACHE_FILE = os.path.join(self.SHARED_DIR, "topic_cache.json")
        self.LAST_ACTIVITY_FILE = os.path.join(self.SHARED_DIR, "last_activity.timestamp")
        self.primitives = self.constants.get("primitives", ["read", "write", "vector_query", "shell"])
        self.SAFE_EXECUTE_FUNCTIONS = self.constants.get("SAFE_EXECUTE_FUNCTIONS", [])
        self.reflection_guidelines = self.constants.get("reflection_guidelines", [])
        self.reflection_max_iterations = self.constants.get("reflection_max_iterations", 3)
        self.reflection_confidence_threshold = self.constants.get("reflection_confidence_threshold", 90)
        self.persona_defaults = self.constants.get("persona_defaults", {})
        self.AUTO_WRITE = self.constants.get("AUTO_WRITE", False)
        self.prompt_config = self.constants.get("prompt_config", {})
        self.n_threads = self.constants.get("n_threads", 4)
        self.model_path = self.constants.get("model_paths", {}).get("Prime", None)
        self.lite_model_path = self.constants.get("model_paths", {}).get("Lite", None)
        self.EMBEDDING_MODEL_PATH = self.constants.get("model_paths", {}).get("Embedding", os.getenv("EMBEDDING_MODEL_PATH"))
        self.status_file = self.constants.get("status_file", None)
        self.llm_backend = self.constants.get("llm_backend", None)
        self.lite_backend = self.constants.get("lite_backend", None)
        self.OBSERVER_TOKEN_THRESHOLD = self.constants.get("OBSERVER_TOKEN_THRESHOLD", 10)
        self.LOGICAL_STOP_PUNCTUATION = self.constants.get("LOGICAL_STOP_PUNCTUATION", [".", "!", "?", "\n"])
        self.identity_file_path = self.SYSTEM_REF_DIR / "core_identity.json"

        # Compatibility shims
        self.MAX_TOKENS = self.max_tokens
        self.RESPONSE_BUFFER = self.constants.get("response_buffer", 256)

    def _load_constants(self, override_path=None):
        path = Path(override_path) if override_path else CONSTANTS_PATH
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.constants = json.load(f)
            logger.info(f"Loaded GAIA constants from {path}")
        except Exception as e:
            logger.error(f"Failed to load GAIA constants: {e}")
            self.constants = {}
    def reload(self, override_path=None):
        self._load_constants(override_path)
        logger.info("GAIA Config reloaded.")
    def get_persona_instructions(self):
        return (
            self.constants.get("persona_defaults", {}).get("instructions")
            or self.identity_intro
            or "Assist with integrity and care."
        )
    def as_dict(self):
        return {
            "identity": self.identity,
            "identity_intro": self.identity_intro,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "primitives": self.primitives,
            "SAFE_EXECUTE_FUNCTIONS": self.SAFE_EXECUTE_FUNCTIONS,
            "reflection_guidelines": self.reflection_guidelines,
            "persona_name": self.persona_name,
            "persona_defaults": self.persona_defaults,
            "AUTO_WRITE": self.AUTO_WRITE,
            "prompt_config": self.prompt_config,
            "n_threads": self.n_threads,
            "llm_backend": self.llm_backend,
            "lite_backend": self.lite_backend,
            "paths": {
                "KNOWLEDGE_DIR": str(self.KNOWLEDGE_DIR),
                "PERSONAS_DIR": str(self.PERSONAS_DIR),
                "PROJECTS_DIR": str(self.PROJECTS_DIR),
                "LOGS_DIR": str(self.LOGS_DIR),
                "TS_DIR": str(self.TS_DIR),
                "ARTIFACTS_DIR": str(self.ARTIFACTS_DIR),
                "VECTORDB_DIR": str(self.VECTORDB_DIR),
                "COREDOCS_DIR": str(self.COREDOCS_DIR),
                "SYSTEM_REF_DIR": str(self.SYSTEM_REF_DIR),
                "REFLECTIONS_DIR": str(self.REFLECTIONS_DIR),
            },
        }

def load_constants():
    try:
        with open(CONSTANTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[GAIA Config] Error loading gaia_constants.json: {e}")
        return {}

constants = load_constants()