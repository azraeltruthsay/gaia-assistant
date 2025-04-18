#!/usr/bin/env python3
"""
GAIA Web Interface - Web application entry point for the D&D Campaign AI Assistant

This module provides a web-based interface for interacting with the GAIA
D&D Campaign AI Assistant, including asking questions, generating artifacts,
and viewing campaign documentation.
"""

import os
import logging
from threading import Thread

from app import create_app, init_ai
from app.config import Config

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/gaia_web.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GAIA_WEB")

# Create Flask application
app = create_app()

def initialize_ai_in_background():
    """Initialize the AI in a background thread to prevent blocking the web server."""
    try:
        logger.info("Starting AI initialization in background thread")
        config = Config()
        success = init_ai(app, config)
        
        if success:
            logger.info("Background AI initialization completed successfully")
        else:
            logger.error("Background AI initialization failed")
    except Exception as e:
        logger.error(f"Error during background AI initialization: {e}", exc_info=True)
        app.config['INIT_ERROR'] = str(e)

# Start background initialization thread
initialization_thread = Thread(target=initialize_ai_in_background)
initialization_thread.daemon = True
initialization_thread.start()

def start_app():
    """Start the Flask application."""
    try:
        # Start the Flask app
        port = int(os.environ.get('PORT', 7860))
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except Exception as e:
        logger.critical(f"Failed to start web application: {e}", exc_info=True)
        print(f"Critical error: {e}")

if __name__ == "__main__":
    start_app()