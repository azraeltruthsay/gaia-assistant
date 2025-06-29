"""
Project management routes for GAIA web interface.
Defines routes for managing different project contexts.
"""

import logging
from flask import Blueprint, request, jsonify, current_app

# Get the logger
logger = logging.getLogger("GAIA")

# Create the blueprint
projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/projects', methods=['GET'])
def list_projects():
    """List all available projects."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager or not hasattr(ai_manager, 'project_manager'):
        return jsonify({'error': 'Project manager not initialized'}), 503
    
    try:
        projects = ai_manager.project_manager.list_projects()
        
        return jsonify({
            'success': True,
            'projects': projects
        })
    except Exception as e:
        logger.error(f"Error listing projects: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/current', methods=['GET'])
def get_current_project():
    """Get information about the current project."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager or not hasattr(ai_manager, 'project_manager'):
        return jsonify({'error': 'Project manager not initialized'}), 503
    
    try:
        project = ai_manager.project_manager.get_current_project()
        
        return jsonify({
            'success': True,
            'project': project
        })
    except Exception as e:
        logger.error(f"Error getting current project: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/switch/<project_id>', methods=['POST'])
def switch_project(project_id):
    """Switch to a different project."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager or not hasattr(ai_manager, 'project_manager'):
        return jsonify({'error': 'Project manager not initialized'}), 503
    
    try:
        # Switch project
        success = ai_manager.project_manager.switch_project(project_id)
        
        if not success:
            return jsonify({'error': f'Failed to switch to project {project_id}'}), 400
        
        # Reload core instructions for AI manager
        ai_manager.core_instructions = ai_manager.project_manager.get_project_instructions()
        
        # Update vector store path
        if ai_manager.vector_store:
            ai_manager.vector_store_manager.config = ai_manager.config
            # Reload vector store
            ai_manager.vector_store = ai_manager.vector_store_manager.load_vector_store()
        
        return jsonify({
            'success': True,
            'message': f'Switched to project {project_id}',
            'project': ai_manager.project_manager.get_current_project()
        })
    except Exception as e:
        logger.error(f"Error switching projects: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/list', methods=['GET'])
def list_projects_alias():
    return list_projects()

@projects_bp.route('/api/projects/create', methods=['POST'])
def create_project():
    """Create a new project."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager or not hasattr(ai_manager, 'project_manager'):
        return jsonify({'error': 'Project manager not initialized'}), 503
    
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        project_id = data.get('id')
        if not project_id:
            return jsonify({'error': 'Project ID is required'}), 400
        
        # Create project
        success = ai_manager.project_manager.create_project(project_id, data)
        
        if not success:
            return jsonify({'error': f'Failed to create project {project_id}'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Created project {project_id}',
            'project': ai_manager.projects[project_id]
        })
    except Exception as e:
        logger.error(f"Error creating project: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/update/<project_id>', methods=['PUT'])
def update_project(project_id):
    """Update an existing project."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager or not hasattr(ai_manager, 'project_manager'):
        return jsonify({'error': 'Project manager not initialized'}), 503
    
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update project
        success = ai_manager.project_manager.update_project(project_id, data)
        
        if not success:
            return jsonify({'error': f'Failed to update project {project_id}'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Updated project {project_id}',
            'project': ai_manager.projects[project_id]
        })
    except Exception as e:
        logger.error(f"Error updating project: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/delete/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager or not hasattr(ai_manager, 'project_manager'):
        return jsonify({'error': 'Project manager not initialized'}), 503
    
    try:
        # Delete project
        success = ai_manager.project_manager.delete_project(project_id)
        
        if not success:
            return jsonify({'error': f'Failed to delete project {project_id}'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Deleted project {project_id}'
        })
    except Exception as e:
        logger.error(f"Error deleting project: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500