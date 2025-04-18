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
    
    # Maximum number of conversation history items to keep
    MAX_HISTORY_LENGTH = 50
    
    # Text splitting parameters
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 100
    
    def __init__(self):
        """Initialize configuration from environment variables with defaults."""
        # Path configuration
        self.data_path = os.environ.get("DATA_PATH", "./app/campaign-data/core-documentation/")
        self.raw_data_path = os.environ.get("RAW_DATA_PATH", "./app/campaign-data/raw-data/")
        self.output_path = os.environ.get("OUTPUT_PATH", "./app/campaign-data/converted_raw/")
        self.vector_db_path = os.environ.get("VECTOR_DB_PATH", "./app/chroma_db")
        self.core_instructions_file = os.environ.get("CORE_INSTRUCTIONS_FILE", "./app/gaia_instructions.txt")
        self.model_path = os.environ.get("MODEL_PATH", "/app/model.gguf")
        
        # Code analysis configuration
        self.code_path = os.environ.get("CODE_PATH", "./app/")
        self.external_code_path = os.environ.get("EXTERNAL_CODE_PATH", "./external-code/")
        
        # Model configuration
        self.n_gpu_layers = int(os.environ.get("N_GPU_LAYERS", "0"))
        self.n_batch = int(os.environ.get("N_BATCH", "512"))
        self.n_ctx = int(os.environ.get("N_CTX", "2048"))
        self.n_threads = int(os.environ.get("N_THREADS", "6"))
        
        # UI configuration
        self.skip_tts_selection = os.environ.get("SKIP_TTS_SELECTION", "false").lower() == "true"
        
        # Create directories if they don't exist
        for path in [self.data_path, self.raw_data_path, self.output_path, 
                    self.vector_db_path, self.external_code_path]:
            os.makedirs(path, exist_ok=True)
            
    def get_pretty_config(self):
        """Return a formatted string of the current configuration."""
        return f"""
        GAIA Configuration:
        -------------------
        Data Path: {self.data_path}
        Raw Data Path: {self.raw_data_path}
        Output Path: {self.output_path}
        Vector DB Path: {self.vector_db_path}
        Instructions File: {self.core_instructions_file}
        Model Path: {self.model_path}
        
        Code Analysis:
        Code Path: {self.code_path}
        External Code Path: {self.external_code_path}
        
        Model Settings:
        GPU Layers: {self.n_gpu_layers}
        Batch Size: {self.n_batch}
        Context Window: {self.n_ctx}
        Threads: {self.n_threads}
        
        UI Settings:
        Skip TTS Selection: {self.skip_tts_selection}
        """