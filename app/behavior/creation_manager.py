import logging
from typing import Dict, Optional

from app.behavior.persona_writer import PersonaWriter
from app.templates.persona_template import get_blank_persona_template

logger = logging.getLogger("GAIA.CreationManager")

class PersonaCreationManager:
    """
    Interactive or programmatic persona creator. Handles filling templates and passing them to PersonaWriter.
    Can be used by GAIA to self-generate personas.
    """

    def __init__(self, vectordb_client, personas_dir="/personas"):
        self.writer = PersonaWriter(vectordb_client, personas_dir)

    def start_persona_creation(self):
        """Start interactive creation if CLI or TUI available (placeholder for UI integration)."""
        logger.info("🚧 Interactive persona creation not implemented yet.")
        return None

    def process_user_response(self, input_str: str):
        """
        Placeholder for multi-turn chat-driven persona generation workflow.
        Intended for future GAIA-initiated self-invention.
        """
        logger.debug(f"🧠 PersonaCreator received input: {input_str}")
        return "(Persona creation flow not yet active)"

    def create_persona(self, template: Dict, instructions: Optional[Dict[str, str]] = None) -> bool:
        """
        Create a persona from a provided template and optional instruction dictionary.

        Args:
            template: The filled persona template
            instructions: Optional instruction dict

        Returns:
            bool: Whether persona was successfully created
        """
        logger.info(f"✨ Creating persona: {template.get('name', '[unnamed]')}")
        return self.writer.create_persona_from_template(template, instructions)

    def generate_persona_from_traits(self, name: str, tone: str, context: str, traits: Optional[Dict[str, str]] = None, instructions: Optional[Dict[str, str]] = None) -> bool:
        """
        Create a persona using name, tone, context, and trait overrides.

        Args:
            name: Persona identifier
            tone: Primary tone descriptor
            context: Primary usage domain
            traits: Optional traits to override
            instructions: Optional instruction overlays

        Returns:
            bool: True if successful
        """
        template = get_blank_persona_template(name)
        template["tone"] = tone
        template["context"] = context

        if traits:
            template["traits"].update(traits)

        logger.info(f"🧬 Generating persona '{name}' with tone='{tone}' and context='{context}'")
        return self.create_persona(template, instructions)
