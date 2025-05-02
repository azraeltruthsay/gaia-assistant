# create_behavior_trigger.py

from app.behavior.creation_manager import BehaviorCreationManager
from flask import current_app

def trigger_behavior_creation(vectordb_client):
    """
    Manually trigger a new behavior creation session.

    This is useful for development, testing, or initializing GAIA's core personality.
    It creates a new BehaviorCreationManager instance and starts the flow.

    Args:
        vectordb_client: A vector DB client instance (e.g., from AIManager).

    Returns:
        str: First prompt from the behavior creation process.
    """
    behavior_manager = BehaviorCreationManager(vectordb_client)
    current_app.config['BEHAVIOR_MANAGER'] = behavior_manager
    return behavior_manager.start_behavior_creation()
