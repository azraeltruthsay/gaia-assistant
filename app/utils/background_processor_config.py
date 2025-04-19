"""
Configuration module for the Background Processor.
Defines settings for idle-time processing and task management.
"""

import os
import logging

# Get the logger
logger = logging.getLogger("GAIA")

class BackgroundProcessorConfig:
    """Configuration class for background processing settings."""
    
    def __init__(self):
        """Initialize configuration from environment variables with defaults."""
        # Idle thresholds
        self.idle_threshold = int(os.environ.get("BG_IDLE_THRESHOLD", "300"))  # 5 minutes in seconds
        self.long_idle_threshold = int(os.environ.get("BG_LONG_IDLE_THRESHOLD", "1800"))  # 30 minutes
        
        # Task priorities
        self.conversation_priority = int(os.environ.get("BG_CONVERSATION_PRIORITY", "10"))
        self.embedding_priority = int(os.environ.get("BG_EMBEDDING_PRIORITY", "20"))
        self.lora_priority = int(os.environ.get("BG_LORA_PRIORITY", "30"))
        
        # Retry settings
        self.max_retries = int(os.environ.get("BG_MAX_RETRIES", "3"))
        self.retry_delay_base = int(os.environ.get("BG_RETRY_DELAY_BASE", "2"))  # Exponential backoff base
        
        # Processing limits
        self.max_concurrent_tasks = int(os.environ.get("BG_MAX_CONCURRENT_TASKS", "1"))
        self.max_processing_time = int(os.environ.get("BG_MAX_PROCESSING_TIME", "300"))  # 5 minutes per task
        
        # Resource management
        self.max_memory_usage = float(os.environ.get("BG_MAX_MEMORY", "0.75"))  # 75% of available memory
        self.max_cpu_usage = float(os.environ.get("BG_MAX_CPU", "0.5"))  # 50% of CPU
        
        # Processing strategies
        self.overnight_processing = os.environ.get("BG_OVERNIGHT", "false").lower() == "true"
        self.overnight_start_hour = int(os.environ.get("BG_OVERNIGHT_START", "22"))  # 10:00 PM
        self.overnight_end_hour = int(os.environ.get("BG_OVERNIGHT_END", "6"))  # 6:00 AM
        
        # LoRA fine-tuning settings
        self.enable_lora = os.environ.get("BG_ENABLE_LORA", "false").lower() == "true"
        self.lora_learning_rate = float(os.environ.get("BG_LORA_LR", "0.0001"))
        self.lora_batch_size = int(os.environ.get("BG_LORA_BATCH", "4"))
        self.lora_r_rank = int(os.environ.get("BG_LORA_R", "8"))
        self.lora_alpha = int(os.environ.get("BG_LORA_ALPHA", "16"))
        
        # Directory settings
        self.structured_archives_dir = os.environ.get("BG_STRUCTURED_DIR", "structured_archives")
        self.lora_adapters_dir = os.environ.get("BG_LORA_ADAPTERS_DIR", "lora_adapters")
        
        # Task processing timeouts (in seconds)
        self.conversation_timeout = int(os.environ.get("BG_CONV_TIMEOUT", "120"))  # 2 minutes
        self.embedding_timeout = int(os.environ.get("BG_EMBED_TIMEOUT", "60"))  # 1 minute
        self.lora_timeout = int(os.environ.get("BG_LORA_TIMEOUT", "1800"))  # 30 minutes
        
        # Create required directories
        self._create_directories()
        
        logger.info("Background Processor Configuration loaded")
        
    def _create_directories(self):
        """Create required directories if they don't exist."""
        try:
            os.makedirs(self.structured_archives_dir, exist_ok=True)
            if self.enable_lora:
                os.makedirs(self.lora_adapters_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating background processor directories: {e}")
    
    def get_pretty_config(self):
        """Return a formatted string of the current configuration."""
        return f"""
        Background Processor Configuration:
        ----------------------------------
        Idle Threshold: {self.idle_threshold} seconds
        Long Idle Threshold: {self.long_idle_threshold} seconds
        
        Task Priorities:
        - Conversation: {self.conversation_priority}
        - Embedding: {self.embedding_priority}
        - LoRA: {self.lora_priority}
        
        Resource Limits:
        - Max Memory Usage: {self.max_memory_usage * 100}%
        - Max CPU Usage: {self.max_cpu_usage * 100}%
        - Max Processing Time: {self.max_processing_time} seconds
        
        Overnight Processing: {self.overnight_processing}
        - Start Hour: {self.overnight_start_hour}:00
        - End Hour: {self.overnight_end_hour}:00
        
        LoRA Fine-tuning:
        - Enabled: {self.enable_lora}
        - Learning Rate: {self.lora_learning_rate}
        - Batch Size: {self.lora_batch_size}
        - r Rank: {self.lora_r_rank}
        - Alpha: {self.lora_alpha}
        
        Directories:
        - Structured Archives: {self.structured_archives_dir}
        - LoRA Adapters: {self.lora_adapters_dir}
        """