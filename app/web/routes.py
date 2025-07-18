import os
import logging
from flask import Blueprint, request, jsonify, current_app, render_template

#from app.models.ai_manager import AIManager
from app.cognition.nlu.intent_detection import detect_intent
from app.memory.session_manager import SessionManager
from app.ethics.core_identity_guardian import CoreIdentityGuardian
from app.ethics.ethical_sentinel import EthicalSentinel
from app.utils.knowledge_index import KnowledgeIndex
from app.utils.helpers import get_tier_from_path
from app.utils.verifier import verify_prompt_safety
from app.memory.status_tracker import GAIAStatus


logger = logging.getLogger("app")
web_bp = Blueprint("web", __name__)

ai_manager = None

def set_ai_manager(manager):
    global ai_manager
    ai_manager = manager

@web_bp.route("/")
def index():
    return render_template("index.html")

@web_bp.route("/status")
def status():
    return jsonify({
        "status": "GAIA running",
        "initialized": ai_manager.status.get("initialized", False),
        "persona": ai_manager.current_persona.name if ai_manager.current_persona else "unknown",
        "project": ai_manager.project_manager.active_project
    })

@web_bp.route("/api/status", methods=["GET"])
def api_status():
    return status()

@web_bp.route("/api/chat", methods=["POST"])
def chat():
    try:
        logger.info("[CHAT] Received /api/chat request")
        logger.debug(f"[CHAT] Request JSON: {request.json}")

        user_input = request.json.get("message", "").strip()
        context = request.json.get("context", "default")
        history = request.json.get("history", [])
        meta = request.json.get("meta", {})

        if not user_input:
            logger.warning("[CHAT] No user input received.")
            return jsonify({"error": "Empty message"}), 400

        logger.info(f"[CHAT] Processing input: {user_input}")
        logger.debug(f"[CHAT] Context: {context}, Meta: {meta}, History Length: {len(history)}")

        intent = detect_intent(user_input)
        logger.info(f"[CHAT] Detected intent: {intent}")

        response = ai_manager.generate_response(user_input)
        logger.debug(f"[CHAT] Generated response: {response}")

        return jsonify({"response": response})

    except Exception as e:
        logger.exception("[CHAT] Exception in /api/chat handler")
        return jsonify({"error": str(e)}), 500


@web_bp.route("/api/projects/list", methods=["GET"])
def get_projects_alias():
    from flask import current_app
    ai_manager = current_app.config.get("AI_MANAGER")
    if not ai_manager:
        return jsonify({"error": "AI Manager not initialized"}), 503
    return jsonify(ai_manager.project_manager.list_available_projects())  # 🔧 FIXED

@web_bp.route("/api/project/<name>", methods=["POST"])
def switch_project(name):
    try:
        ai_manager.project_manager.set_project(name)
        return jsonify({"status": "ok", "active_project": name})
    except Exception as e:
        logger.error(f"Error switching project: {e}")
        return jsonify({"error": str(e)}), 500

@web_bp.route("/api/personas", methods=["GET"])
def list_personas():
    try:
        personas = ai_manager.persona_manager.list_available_personas()
        return jsonify(personas)
    except Exception as e:
        logger.error(f"Error listing personas: {e}")
        return jsonify({"error": str(e)}), 500

@web_bp.route("/api/persona/<name>", methods=["POST"])
def switch_persona(name):
    try:
        ai_manager.persona_manager.load_persona(name)
        ai_manager.session_manager.set_persona(name)
        return jsonify({"status": "ok", "current_persona": name})
    except Exception as e:
        logger.error(f"Error switching persona: {e}")
        return jsonify({"error": str(e)}), 500

@web_bp.route("/api/archives", methods=["GET"])
def get_archives():
    try:
        archives = ai_manager.session_manager.list_archives()
        return jsonify(archives)
    except Exception as e:
        logger.error(f"Error fetching archives: {e}")
        return jsonify({"error": str(e)}), 500

@web_bp.route("/api/conversations/archived", methods=["GET"])
def get_conversations_archived():
    return get_archives()

@web_bp.route("/api/archive/<archive_id>", methods=["GET"])
def get_archive(archive_id):
    try:
        archive = ai_manager.session_manager.load_archive(archive_id)
        return jsonify(archive)
    except Exception as e:
        logger.error(f"Error loading archive {archive_id}: {e}")
        return jsonify({"error": str(e)}), 500

@web_bp.route("/api/archive/<archive_id>", methods=["DELETE"])
def delete_archive(archive_id):
    try:
        ai_manager.session_manager.delete_archive(archive_id)
        return jsonify({"status": "deleted", "archive_id": archive_id})
    except Exception as e:
        logger.error(f"Error deleting archive {archive_id}: {e}")
        return jsonify({"error": str(e)}), 500

@web_bp.route("/api/background/status", methods=["GET"])
def background_status():
    try:
        status = ai_manager.background_processor.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error fetching background status: {e}")
        return jsonify({"error": str(e)}), 500
