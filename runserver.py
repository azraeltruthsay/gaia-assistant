# /home/azrael/Project/gaia-assistant/runserver.py

from flask import Flask
from app.models.model_pool import model_pool # Import the global model pool
from app.web.routes_chat import bp as chat_bp # Import the chat blueprint

app = Flask(__name__, template_folder="app/templates")
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

# model_pool is a global instance, its __init__ already calls load_models()
# If you explicitly want to ensure models are loaded here, you can uncomment:
# model_pool.load_models()

# Register route blueprints
app.register_blueprint(chat_bp)
# You may also register routes_admin.py, routes_misc.py here if they are part of the minimal core

if __name__ == "__main__":
    print("GAIA Web API is live.")
    print(app.url_map)
    app.run(host="0.0.0.0", port=6414)