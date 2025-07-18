# === model_pool.py (extended) ===

from llama_cpp import Llama
from app.config import Config
import logging
from app.behavior.persona_manager import PersonaManager # New import
from app.behavior.persona_adapter import PersonaAdapter # New import
from sentence_transformers import SentenceTransformer # ✅ FIXED: Added the missing import

logger = logging.getLogger("GAIA.ModelPool")

class ModelPool:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.models = {}
        self.model_status = {}  # new: track each model's current role
        self.persona_manager = PersonaManager(self.config.PERSONAS_DIR)  # Initialize PersonaManager
        self.active_persona_obj = None  # Store the active PersonaAdapter object

    def load_models(self):
        try:
            logger.info("🔹 Loading Prime model")
            self.models["prime"] = Llama(
                model_path=self.config.model_path,
                n_gpu_layers=self.config.n_gpu_layers,
                n_ctx=self.config.max_tokens,
                stream=True,
                verbose=False,
            )
            logger.info(f"✅ Prime loaded: {self.models['prime']}")
            self.model_status["prime"] = "idle"
        except Exception as e:
            logger.error(f"❌ Failed to load Prime model: {e}")

        if self.config.lite_model_path:
            try:
                logger.info("🔹 Loading Lite model")
                self.models["lite"] = Llama(
                    model_path=self.config.lite_model_path,
                    n_gpu_layers=self.config.n_gpu_layers,
                    n_ctx=self.config.max_tokens // 2,
                    stream=False,
                    verbose=False,
                )
                logger.info(f"✅ Lite loaded: {self.models['lite']}")
                self.model_status["lite"] = "idle"
            except Exception as e:
                logger.warning(f"⚠️ Failed to load Lite model: {e}")

        # Load the embedding model into the pool
        try:
            logger.info("🔹 Loading Embedding model")
            # This now correctly uses the EMBEDDING_MODEL_PATH from the config
            self.models["embed"] = SentenceTransformer(self.config.EMBEDDING_MODEL_PATH)
            logger.info(f"✅ Embedding model loaded: {self.models['embed']}")
            self.model_status["embed"] = "idle"
        except Exception as e:
            logger.error(f"❌ Failed to load Embedding model: {e}")

    def get(self, name: str):
        model = self.models.get(name)
        if model is None:
            logger.error(f"❌ Requested model '{name}' not found in pool! Pool keys: {list(self.models.keys())}")
        return model

    def list_models(self):
        return list(self.models.keys())

    def set_status(self, name: str, status: str):
        if name in self.models:
            self.model_status[name] = status
            logger.info(f"🔄 Model '{name}' status set to '{status}'")

    def get_idle_model(self, exclude=[]):
        for name, status in self.model_status.items():
            if status == "idle" and name not in exclude:
                return name
        return None

    def acquire_model(self, name: str):
        if name in self.models:
            self.set_status(name, "busy")
            return self.models[name]
        return None

    def release_model(self, name: str):
        if name in self.models:
            self.set_status(name, "idle")

    def get_active_persona(self) -> PersonaAdapter:
        """Returns the currently active PersonaAdapter object."""
        return self.active_persona_obj
    
    def set_persona(self, persona):
        """
        Make the given persona object discoverable to code that calls
        `model_pool.get_active_persona()` or inspects `model_pool.persona_name`.
        """
        if isinstance(persona, dict):
            self.active_persona_obj = PersonaAdapter(persona, self.config)
        elif isinstance(persona, PersonaAdapter):
            self.active_persona_obj = persona
        else:
            logger.error(f"Invalid persona type: {type(persona)}")
            return

        # Best-effort human label
        self.persona_name = getattr(self.active_persona_obj, "name", getattr(self.active_persona_obj, "id", "unknown"))
        logging.getLogger(__name__).debug("🔄 Active persona set to %s", self.persona_name)

# Global instance
model_pool = ModelPool()
model_pool.load_models()  # This will now also load the default persona
model_pool.config.model_pool = model_pool # Attach the model_pool instance to its own config object
