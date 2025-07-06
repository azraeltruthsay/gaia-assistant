import logging
import os
from datetime import datetime

def setup_chat_logger():
    """Sets up a dedicated logger for chat history."""
    log_dir = "logs/chat_history"
    os.makedirs(log_dir, exist_ok=True)

    # Use a unique filename for each session
    log_file = os.path.join(log_dir, f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    logger = logging.getLogger("GAIA.ChatHistory")
    logger.setLevel(logging.INFO)

    # Prevent chat logs from appearing in the main console log
    logger.propagate = False

    # Add a file handler only if one doesn't exist
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Initialize the logger when the module is loaded
chat_history_logger = setup_chat_logger()

def log_chat_entry(user_input: str, assistant_output: str):
    """Logs a user and assistant turn to the dedicated session file."""
    if user_input:
        chat_history_logger.info(f"User > {user_input}")
    if assistant_output:
        chat_history_logger.info(f"GAIA > {assistant_output}\n" + "-"*20)
