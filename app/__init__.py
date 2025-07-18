import logging
from flask import Flask
# from app.models.ai_manager import AIManager
from app.memory.session_manager import SessionManager
from app.web.routes import web_bp, set_ai_manager
from app.web.project_routes import projects_bp  # ✅ NEW

# Optional: You could eventually pull this from a config file/env
PORT = 6414
DEBUG_MODE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GAIA_WEB")

# Shared config object (singleton style)
from app.config import Config
config = Config()

#def create_app():
#    app = Flask(__name__)
#
#    logger.info("🧪 Entered create_app()")
#    ai_manager = AIManager(config=config)
#
#    if not ai_manager.initialize():
#        raise RuntimeError("Failed to initialize AIManager")
#
#    logger.info("✅ AIManager initialized successfully.")
#    app.config["AI_MANAGER"] = ai_manager  # 🔧 For use in /api/projects/list
#
#    # Attach to route module
#    set_ai_manager(ai_manager)
#
#    # Perform session syncing, etc.
#    session_manager: SessionManager = ai_manager.session_manager
#    session_manager.sync_personas_with_behavior()
#
#    # Register web routes
#    app.register_blueprint(web_bp)
#    app.register_blueprint(projects_bp)  # ✅ NEW
#
#    # Final debug info
#    logger.info("🚀 GAIA Web App initialized successfully")
#    logger.info(f"🧠 Active persona: {ai_manager.current_persona}\n")
#    logger.info("🧬 Tier I Identity Guardian and Knowledge Index loaded")
#
#    return app
#
#def start_app():
#    app = create_app()
#    logger.info("🧪 Entered start_app()")
#    logger.info(f"🌐 Starting Flask app on port {config.PORT}")
#    app.run(debug=config.DEBUG_MODE, host='0.0.0.0', port=config.PORT)
