"""
GAIA Additional Routes - Future Features and Archive Support
These routes are not deprecated — they are intended for full production use when ready.
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, current_app, jsonify, request

logger = logging.getLogger("GAIA")
future_bp = Blueprint("future", __name__)

@future_bp.route('/api/structured_archives')
def list_structured_archives():
    """(Future) List all structured archives."""
    ai_manager = current_app.config.get('AI_MANAGER')
    if not ai_manager or not ai_manager.conversation_manager:
        return jsonify({'error': 'Conversation manager not initialized'}), 503

    try:
        archives = []
        structured_dir = ai_manager.conversation_manager.structured_archives_dir

        if os.path.exists(structured_dir):
            for filename in os.listdir(structured_dir):
                if filename.endswith('_structured.md'):
                    file_path = os.path.join(structured_dir, filename)
                    archive_id = filename.replace('_structured.md', '')
                    mtime = os.path.getmtime(file_path)

                    summary = ""
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for line in lines[:10]:
                                if line.startswith('##') and 'Summary' in line:
                                    idx = lines.index(line)
                                    if len(lines) > idx + 1:
                                        summary = lines[idx + 1].strip()
                                    break
                    except Exception as e:
                        logger.warning(f"Could not extract summary from {filename}: {e}")

                    archives.append({
                        'id': archive_id,
                        'timestamp': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'summary': summary
                    })

        return jsonify({'archives': archives})
    except Exception as e:
        logger.error(f"Error listing structured archives: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@future_bp.route('/api/structured_archive/<archive_id>', methods=['GET'])
def get_structured_archive(archive_id):
    """(Future) Get a specific structured archive."""
    ai_manager = current_app.config.get('AI_MANAGER')
    if not ai_manager or not ai_manager.conversation_manager:
        return jsonify({'error': 'Conversation manager not initialized'}), 503

    try:
        file_path = os.path.join(
            ai_manager.conversation_manager.structured_archives_dir,
            f"{archive_id}_structured.md"
        )

        if not os.path.exists(file_path):
            return jsonify({'error': 'Structured archive not found'}), 404

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({'content': content})
    except Exception as e:
        logger.error(f"Error getting structured archive: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
