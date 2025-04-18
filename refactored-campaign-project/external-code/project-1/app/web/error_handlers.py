"""
Error handlers for GAIA D&D Campaign Assistant web interface.
Defines handlers for various HTTP errors.
"""

import logging
from flask import Blueprint, jsonify, render_template

# Get the logger
logger = logging.getLogger("GAIA")

# Create the blueprint
errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    logger.warning(f"400 Bad Request: {error}")
    return jsonify({
        'error': 'Bad Request',
        'message': 'The server could not understand the request.'
    }), 400

@errors_bp.app_errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    logger.warning(f"404 Not Found: {error}")
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource does not exist.'
    }), 404

@errors_bp.app_errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed errors."""
    logger.warning(f"405 Method Not Allowed: {error}")
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'The method is not allowed for this resource.'
    }), 405

@errors_bp.app_errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 Request Entity Too Large errors."""
    logger.warning(f"413 Request Entity Too Large: {error}")
    return jsonify({
        'error': 'Request Entity Too Large',
        'message': 'The request is larger than the server is willing or able to process.'
    }), 413

@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error errors."""
    logger.error(f"500 Internal Server Error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'The server encountered an internal error and was unable to complete your request.'
    }), 500

@errors_bp.app_errorhandler(Exception)
def handle_exception(error):
    """Handle unhandled exceptions."""
    logger.error(f"Unhandled Exception: {error}", exc_info=True)
    return jsonify({
        'error': 'Server Error',
        'message': 'An unexpected error occurred.'
    }), 500