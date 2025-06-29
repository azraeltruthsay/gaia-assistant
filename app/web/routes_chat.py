# /home/azrael/Project/gaia-assistant/app/web/routes_chat.py

import json
import logging
from flask import Blueprint, request, jsonify, render_template, Response, stream_with_context
from app.cognition.external_voice import ExternalVoice
from app.utils.stream_observer import StreamObserver # Ensure this is imported
from app.models.model_pool import model_pool # Import the global model_pool
from app.config import Config # Import Config to ensure it's available for ExternalVoice if needed

bp = Blueprint("chat", __name__)
logger = logging.getLogger("GAIA.Web.Chat")

@bp.route("/", methods=["GET"])
def index():
    """Serves the main chat HTML page."""
    return render_template("chat.html")

@bp.route("/chat", methods=["POST"])
def chat():
    """
    Receives user input via POST and streams the response from GAIA's ExternalVoice
    as Server-Sent Events (SSE), with observer-based interruption.
    This route uses ExternalVoice as a minimal core, bypassing AIManager.
    """
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    # --- Observer Setup ---
    # Get an idle model to act as the observer (e.g., 'lite')
    observer_model = model_pool.get("lite")
    observer = None
    if observer_model:
        observer = StreamObserver(llm=observer_model, name="WebUI-Observer")
        model_pool.set_status("lite", "observing") # Mark observer model as busy

    # --- Voice (Responder) Setup ---
    # ExternalVoice is the minimal core for this interaction.
    # It directly uses models from the global model_pool and the global config.
    voice = ExternalVoice.from_thought(
        model=model_pool.get("prime"), # Use the Prime model for the main response
        thought=user_input,
        model_pool=model_pool, # Pass the global model_pool for escalation/observer
        config=model_pool.config, # Pass the config from model_pool
        observer=observer  # Pass the observer to the voice
    )
    model_pool.set_status("prime", "responding") # Mark prime model as busy

    def generate_sse_stream():
        """Yields SSE-formatted strings from the voice stream."""
        try:
            for token_or_event in voice.stream_response(user_input):
                if isinstance(token_or_event, dict) and token_or_event.get("event") == "interruption":
                    # This is our special interruption signal. Send a custom SSE event.
                    event_data = json.dumps({"reason": token_or_event.get("data", "Interrupted")})
                    yield f"event: interruption\ndata: {event_data}\n\n"
                    break  # Stop sending more data
                else:
                    # This is a regular token. Send a default 'message' event.
                    # JSON-encoding the token handles special characters like newlines.
                    yield f"data: {json.dumps(str(token_or_event))}\n\n"
        except Exception as e:
            logger.error(f"Error in chat stream: {e}", exc_info=True)
            error_data = json.dumps({"message": "An error occurred during streaming."})
            yield f"event: error\ndata: {error_data}\n\n"
        finally:
            # Ensure models are marked idle after stream finishes or breaks
            model_pool.set_status("prime", "idle")
            if observer_model:
                model_pool.set_status("lite", "idle")


    # Set mimetype to 'text/event-stream' for Server-Sent Events
    return Response(stream_with_context(generate_sse_stream()), mimetype='text/event-stream')