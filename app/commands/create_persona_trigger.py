import logging
from flask import current_app
from app.behavior.creation_manager import PersonaCreationManager

logger = logging.getLogger("GAIA.Commands")

def trigger_persona_creation(vectordb_client):
    """
    Manual or test-mode function to trigger GAIA's persona creation logic.
    Stores a PersonaCreationManager instance in Flask's app context.
    """
    manager = PersonaCreationManager(vectordb_client)
    current_app.config["persona_creator"] = manager
    manager.start_persona_creation()

def create_code_analyzer_persona(vectordb_client):
    """
    Programmatically create a 'code_analyzer' persona using predefined traits.
    Will mount under /personas/code_analyzer/ using docker volume structure.
    """
    creator = PersonaCreationManager(vectordb_client)

    traits = {
        "verbosity": "short",
        "humor": "none",
        "formality": "technical"
    }

    instructions = {
        "analysis_focus": (
            "Prioritize clarity, summarization, and tagging of functions, \
            imports, and module structure. Avoid unnecessary commentary."
        )
    }

    success = creator.generate_persona_from_traits(
        name="code_analyzer",
        tone="precise and analytical",
        context="source code inspection and modular AI design",
        traits=traits,
        instructions=instructions
    )

    if success:
        logger.info("✅ Code Analyzer persona created and stored.")
    else:
        logger.error("❌ Failed to create Code Analyzer persona.")

    return success
