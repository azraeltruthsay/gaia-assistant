"""
GAIA Archives API Routes

Exposes endpoints to list and retrieve archived conversations (.md and .log).
Integrates with ConversationManager via AIManager.

Routes:
    GET /api/archives             - List all available archive files
    GET /api/archives/<archive>  - Return the content of a specific archive
"""

import os
import logging
from flask import Blueprint, jsonify, current_app

logger = logging.getLogger("GAIA")
archives_bp = Blueprint('archives', __name__)

@archives_bp.route('/api/archives', methods=['GET'])
def list_archives():
    """
    Return a list of all archived conversation files (.md and .log).
    """
    try:
        ai_manager = current_app.config.get('AI_MANAGER')
        if not ai_manager:
            logger.error("❌ AI Manager not available in /api/archives")
            return jsonify({'error': 'AI Manager not initialized'}), 503

        archive_dir = ai_manager.conversation_manager.archiver.archives_dir
        if not os.path.exists(archive_dir):
            logger.warning(f"⚠️ Archive directory missing: {archive_dir}")
            return jsonify({'archives': []})

        files = sorted([
            f for f in os.listdir(archive_dir)
            if f.endswith(".md") or f.endswith(".log")
        ])

        logger.info(f"📁 Archive list requested: {len(files)} files found")
        return jsonify({'archives': files})

    except Exception as e:
        logger.error(f"🔥 Error listing archives: {e}", exc_info=True)
        return jsonify({'error': 'Failed to list archives'}), 500


@archives_bp.route('/api/archives/<archive_id>', methods=['GET'])
def get_archive(archive_id):
    """
    Return the content of a specific archived conversation by ID.
    """
    try:
        ai_manager = current_app.config.get('AI_MANAGER')
        if not ai_manager:
            logger.error("❌ AI Manager not available in /api/archives/<archive_id>")
            return jsonify({'error': 'AI Manager not initialized'}), 503

        # Strip .md if it's passed with extension
        archive_id = archive_id.replace(".md", "")
        content = ai_manager.conversation_manager.archiver.load_archived_conversation(archive_id)

        if content:
            logger.info(f"📜 Archive '{archive_id}' successfully retrieved")
            return jsonify({'content': content})
        else:
            logger.warning(f"⚠️ Archive not found: {archive_id}")
            return jsonify({'error': 'Archive not found'}), 404

    except Exception as e:
        logger.error(f"🔥 Error loading archive '{archive_id}': {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve archive'}), 500
