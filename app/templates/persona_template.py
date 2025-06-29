PERSONA_TEMPLATE = {
    "name": "",  # Unique identifier for the persona
    "tone": "",  # Describes GAIA's communication tone (e.g., friendly, formal, sarcastic)
    "context": "",  # Domain or situational bias (e.g., fantasy, scientific, corporate)
    "priority": "",  # Optional: low, medium, high — influence on override strength
    "default_instruction": "",  # Optional: default instruction file to load
    "instruction_scope": "",  # Optional: task, project, global
    "traits": {
        "verbosity": "",     # short, medium, long
        "humor": "",         # dry, witty, none
        "formality": ""      # casual, technical, strict
    }
}

def get_blank_persona_template(name: str = "untitled") -> dict:
    """
    Return a copy of the persona template with default or empty fields.

    Args:
        name (str): Optional name for the persona

    Returns:
        dict: Initialized persona structure
    """
    return {
        "name": name,
        "tone": "",
        "context": "",
        "priority": "medium",
        "default_instruction": "",
        "instruction_scope": "task",
        "traits": {
            "verbosity": "medium",
            "humor": "none",
            "formality": "technical"
        }
    }
