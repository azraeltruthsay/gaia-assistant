# intent_detection.py

def detect_intent(user_input):
    """
    Lightweight intent detection based on user input.

    Args:
        user_input (str): The user's latest message.

    Returns:
        str: Detected intent string ('create_behavior', 'normal_chat', etc.)
    """
    lowered = user_input.lower()

    # Very simple pattern matching
    create_behavior_phrases = [
        "create a behavior",
        "make a behavior",
        "start behavior creation",
        "define your personality",
        "generate your default personality",
        "begin behavior creation mode"
    ]

    for phrase in create_behavior_phrases:
        if phrase in lowered:
            return "create_behavior"

    return "normal_chat"
