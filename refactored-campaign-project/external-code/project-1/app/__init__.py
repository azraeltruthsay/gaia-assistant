"""
GAIA D&D Campaign Assistant application package.
"""

import os
import logging
from flask import Flask

from app.config import Config
from app.models.ai_manager import AIManager
from app.web.routes import web_bp
from app.web.error_handlers import errors_bp

# Get the logger
logger = logging.getLogger("GAIA")

def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config: Optional custom configuration object
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
                
    # Use provided config or create default
    if config is None:
        config = Config()
    
    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(errors_bp)
    
    # Store initialization error if any
    app.config['INIT_ERROR'] = None
    
    # Configure the app
    app.config['UPLOAD_FOLDER'] = config.raw_data_path
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit uploads to 16MB
    
    # Create directories if they don't exist
    for path in [config.data_path, config.raw_data_path, config.output_path, config.vector_db_path]:
        os.makedirs(path, exist_ok=True)
    
    # Set AI manager to None initially
    app.config['AI_MANAGER'] = None
    
    return app

def init_ai(app, config=None):
    """
    Initialize the AI components.
    
    Args:
        app: Flask application
        config: Optional custom configuration object
        
    Returns:
        True if initialization is successful, False otherwise
    """
    if config is None:
        config = Config()
    
    try:
        # Initialize AI manager
        ai_manager = AIManager(config)
        success = ai_manager.initialize()
        
        if success:
            app.config['AI_MANAGER'] = ai_manager
            logger.info("AI Manager initialized successfully")
            return True
        else:
            app.config['INIT_ERROR'] = "Failed to initialize AI components"
            logger.error("Failed to initialize AI components")
            return False
    except Exception as e:
        error_message = f"Error initializing AI: {str(e)}"
        app.config['INIT_ERROR'] = error_message
        logger.error(error_message, exc_info=True)
        return False