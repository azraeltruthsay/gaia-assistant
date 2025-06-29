import logging
from app.behavior.creation_manager import PersonaCreationManager

logger = logging.getLogger("GAIA.Commands")

def run_create_persona_command(vectordb_client, persona_data, instructions=None):
    """
    Run a one-shot command to create a new persona from the given data.

    Args:
        vectordb_client: Vector DB client (optional for embedding)
        persona_data (dict): Persona template dict with name, tone, context, traits, etc.
        instructions (dict): Optional overlay instructions {filename: content}

    Returns:
        bool: True if persona was created successfully
    """
    manager = PersonaCreationManager(vectordb_client)
    logger.info(f"⚙️ Running create_persona_command for: {persona_data.get('name', '[unnamed]')}")

    success = manager.create_persona(persona_data, instructions)
    if success:
        logger.info("✅ Persona created successfully.")
    else:
        logger.error("❌ Persona creation failed.")
    return success
