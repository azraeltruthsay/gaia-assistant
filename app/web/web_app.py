import logging
import threading
from flask.logging import default_handler

from app import create_app, init_ai
from app.config import Config

# Build Flask app and config
config = Config()
app = create_app()

logger = logging.getLogger("GAIA_WEB")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(default_handler)


def start_app():
    logger.info("🧪 Entered start_app()")

    

    def boot_ai():
        logger.info("🧵 Background initialization thread started")
        init_ai(app)

    threading.Thread(target=boot_ai).start()

    logger.info(f"🌐 Starting Flask app on port {config.PORT}")
    app.run(debug=config.DEBUG_MODE, host='0.0.0.0', port=config.PORT)


if __name__ == "__main__":
    start_app()
