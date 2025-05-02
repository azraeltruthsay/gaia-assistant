import os
from flask import Flask
from app.web.routes import web_bp
from app.config import Config  # or whatever your config class is named
from app.web.archives import archives_bp

config = Config()

def create_app():
    # Calculate base directory from this file's location
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')

    # Explicitly assign template and static paths
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(archives_bp)

    return app


def init_ai(app):
    from app.models.ai_manager import AIManager
    from app.behavior.session import SessionManager

    app.logger.info("­ЪДа Creating AIManager...")
    ai_manager = AIManager(config)

    success = ai_manager.initialize()
    
    
    if success:
        app.config['AI_MANAGER_OBJECT'] = ai_manager
        app.config['AI_MANAGER'] = ai_manager
        session_manager = SessionManager(ai_manager)
        app.config['GAIA_SESSION_MANAGER'] = session_manager
        session_manager.sync_behaviors()
        app.logger.info(f"­ЪДа Behavior Profile: {session_manager.report_current_personality()}")
        app.config['GAIA_STATUS'] = {"initialized": True}
        app.logger.info("✅ GAIA_STATUS set to initialized")
        return True
    else:
        app.config['INIT_ERROR'] = "AI failed to initialize"
        return False

