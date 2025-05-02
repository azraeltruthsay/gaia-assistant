"""
GAIA Primary Web Routes (core API endpoints)
Cleaned, logged, and annotated for stability and maintainability.
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
from app.utils.helpers import sanitize_filename, clean_response, get_file_extension

# Behavior + intent detection
from app.intent_detection import detect_intent
from app.behavior.creation_manager import BehaviorCreationManager
from app.commands.create_behavior_trigger import trigger_behavior_creation

logger = logging.getLogger("GAIA")
web_bp = Blueprint('web', __name__)

ALLOWED_EXTENSIONS = {'txt', 'rtf', 'docx', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@web_bp.route('/')
def index():
    """Serve main page."""
    return render_template('index.html')


@web_bp.route('/api/status')
def status():
    """Healthcheck + readiness probe."""
    try:
        logger.info("🩺 /api/status requested")
        ai_manager = current_app.config.get('AI_MANAGER')
        init_error = current_app.config.get('INIT_ERROR')

        if init_error:
            logger.warning(f"Startup error reported: {init_error}")
            return jsonify({'initialized': False, 'error': init_error})

        if not ai_manager or not getattr(ai_manager, 'initialized', False):
            return jsonify({'initialized': False, 'error': 'AI components not fully initialized yet'})

        return jsonify({'initialized': True})

    except Exception as e:
        logger.error(f"Error in /api/status: {e}", exc_info=True)
        return jsonify({'initialized': False, 'error': 'Internal error'}), 500


@web_bp.route('/api/query', methods=['POST'])
def query():
    """Main chat interface for campaign world queries."""
    ai_manager = current_app.config.get('AI_MANAGER')
    behavior_manager = current_app.config.get('BEHAVIOR_MANAGER')

    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503

    try:
        data = request.get_json()
        query_text = data.get('query', '').strip()

        if not query_text:
            return jsonify({'error': 'No query provided'}), 400

        logger.info(f"📨 User query received: {query_text}")

        if query_text.lower() in {"cancel", "stop", "nevermind", "abort"}:
            if behavior_manager and behavior_manager.awaiting_user_response:
                behavior_manager.awaiting_user_response = False
                behavior_manager.filled_fields = {}
                behavior_manager.current_field = None
                return jsonify({"response": "🔝 Behavior creation has been canceled."})
            return jsonify({"response": "🔝 Request canceled."})

        if behavior_manager and behavior_manager.awaiting_user_response:
            response = behavior_manager.process_user_response(query_text)
        else:
            intent = detect_intent(query_text)
            if intent == "create_behavior":
                response = trigger_behavior_creation(ai_manager.vector_store_manager)
            else:
                response = ai_manager.process_query(query_text)

        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Query processing error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@web_bp.route('/api/documents')
def list_documents():
    """List available markdown docs (core + artifact)."""
    ai_manager = current_app.config.get('AI_MANAGER')
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503

    try:
        core_docs = []
        artifacts = []

        if os.path.exists(ai_manager.config.data_path):
            for fname in os.listdir(ai_manager.config.data_path):
                if fname.endswith('.md'):
                    fpath = os.path.join(ai_manager.config.data_path, fname)
                    core_docs.append({
                        'name': fname,
                        'modified': datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d %H:%M:%S'),
                        'size': os.path.getsize(fpath)
                    })

        if os.path.exists(ai_manager.config.output_path):
            for fname in os.listdir(ai_manager.config.output_path):
                if fname.endswith('.md'):
                    fpath = os.path.join(ai_manager.config.output_path, fname)
                    artifacts.append({
                        'name': fname,
                        'modified': datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d %H:%M:%S'),
                        'size': os.path.getsize(fpath)
                    })

        return jsonify({'core_documentation': core_docs, 'artifacts': artifacts})
    except Exception as e:
        logger.error(f"Error listing documents: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@web_bp.route('/api/document/<filename>')
def get_document(filename):
    """Load markdown content of one document."""
    ai_manager = current_app.config.get('AI_MANAGER')
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503

    try:
        paths = [
            os.path.join(ai_manager.config.data_path, filename),
            os.path.join(ai_manager.config.output_path, filename)
        ]

        for path in paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return jsonify({'content': f.read()})

        return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving document {filename}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@web_bp.route('/api/switch_project', methods=['POST'])
def switch_project():
    """Switch active GAIA project (e.g., dnd-campaign, code-assistant)."""
    try:
        ai_manager = current_app.config.get('AI_MANAGER')
        if not ai_manager:
            return jsonify({'success': False, 'error': 'AI Manager not available'}), 503

        project_name = request.args.get('name')
        if not project_name:
            return jsonify({'success': False, 'error': 'No project name provided'}), 400

        # Adjust project-specific config
        project_base = os.path.join('/app/projects', project_name)
        raw_data = os.path.join(project_base, 'raw-data')
        core_docs = os.path.join(project_base, 'core-documentation')

        # Update config paths
        ai_manager.config.data_path = core_docs
        ai_manager.config.raw_data_path = raw_data
        ai_manager.config.output_path = os.path.join(project_base, 'converted_raw')

        # Reprocess content
        ai_manager.doc_processor.process_raw_data()
        documents = ai_manager.doc_processor.load_and_preprocess_data(core_docs)
        ai_manager.vector_store = ai_manager.vector_store_manager.create_vector_store(documents)

        logger.info(f"🔄 Project switched to: {project_name}")
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"❌ Error switching project: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
