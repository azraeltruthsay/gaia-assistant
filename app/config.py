"""
Configuration module for GAIA D&D Campaign Assistant.
Manages environment variables and settings.
"""

import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/gaia.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GAIA")

class Config:
    """Configuration class to manage environment variables and settings."""

    # Global limits and constants
    MAX_HISTORY_LENGTH = int(os.environ.get("MAX_HISTORY_LENGTH", 50))
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", 100))
    PORT = int(os.environ.get("PORT", 7860))  # <-- added to fix Flask startup
    DEBUG_MODE = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    def __init__(self):
        """Initialize configuration from environment variables with defaults."""

        # Data and document paths
        self.data_path = os.environ.get("DATA_PATH", "./campaign-data/core-documentation/")
        self.raw_data_path = os.environ.get("RAW_DATA_PATH", "./campaign-data/raw-data/")
        self.output_path = os.environ.get("OUTPUT_PATH", "./campaign-data/converted_raw/")
        self.vector_db_path = os.environ.get("VECTOR_DB_PATH", "./chroma_db")

        # Model settings
        self.model_path = os.environ.get("MODEL_PATH", "./model.gguf")
        self.n_gpu_layers = int(os.environ.get("N_GPU_LAYERS", 0))
        self.n_batch = int(os.environ.get("N_BATCH", 768))
        self.n_ctx = int(os.environ.get("N_CTX", 8192))
        self.n_threads = int(os.environ.get("N_THREADS", 6))

        # Personalities
        self.default_personality_file = os.environ.get("DEFAULT_PERSONALITY_FILE", "./personalities/default_personality.json")
        self.personalities_path = os.environ.get("PERSONALITIES_PATH", "./personalities")


        # Code analysis
        self.code_project_path = os.path.join(
            os.environ.get("PROJECTS_DIR", "./shared"),
            "../projects/code-assistant/files"
        )
        self.task_status_path = os.path.join(self.data_path, "../background_tasks.json")

        # TTS and UI
        self.ENABLE_TTS = os.environ.get("ENABLE_TTS", "True").lower() == "true"
        self.skip_tts_selection = os.environ.get("SKIP_TTS_SELECTION", "true").lower() == "true"
        self.debug_mode = os.environ.get("DEBUG_MODE", "False").lower() == "true"

        # Create required directories if they don't exist
        for path in [self.data_path, self.raw_data_path, self.output_path,
                     self.vector_db_path, self.code_project_path]:
            os.makedirs(path, exist_ok=True)

    def __repr__(self):
        return f"""
        GAIA Configuration:
        -------------------
        Data Path: {self.data_path}
        Raw Data Path: {self.raw_data_path}
        Output Path: {self.output_path}
        Vector DB Path: {self.vector_db_path}
        Personality File: {self.default_personality_file}
        Model Path: {self.model_path}

        Code Analysis:
        Code Path: {self.code_project_path}
        Task Status Path: {self.task_status_path}

        Model Settings:
        GPU Layers: {self.n_gpu_layers}
        Batch Size: {self.n_batch}
        Context Window: {self.n_ctx}
        Threads: {self.n_threads}

        UI Settings:
        TTS Enabled: {self.ENABLE_TTS}
        Skip TTS Selection: {self.skip_tts_selection}
        Debug Mode: {self.debug_mode}

        Text Processing:
        Chunk Size: {self.CHUNK_SIZE}
        Overlap: {self.CHUNK_OVERLAP}

        History:
        Max Entries: {self.MAX_HISTORY_LENGTH}

        Server:
        Port: {self.PORT}
        """
