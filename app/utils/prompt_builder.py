"""
Prompt Builder (robust, persona/context-aware)
- Assembles the LLM prompt with identity, persona, context, constraints, history, and monologue.
- Supports flexible formatting (chatML, system/user, etc.).
"""

import logging

logger = logging.getLogger("GAIA.PromptBuilder")

def build_prompt(
    context,
    prompt_format="chatml",  # Can expand to support other formats (e.g., openai, json, etc.)
    add_history=True,
    add_monologue=True,
    **kwargs
):
    """
    Builds a prompt for LLM inference from the provided context.
    Params:
        context: dict with all pipeline fields (identity, persona, instructions, etc.)
        prompt_format: 'chatml' by default; other formats can be supported
        add_history: whether to include recent conversation history
        add_monologue: whether to include inner monologue/thoughts
    Returns:
        List of messages or formatted prompt string as required by model.
    """
    if context is None:
        context = {}

    identity = context.get("identity", "")
    identity_intro = context.get("identity_intro", "")
    persona = context.get("persona", "")
    persona_template = context.get("persona_template", "")
    instructions = context.get("instructions", "")
    constraints = context.get("constraints", [])
    primitives = context.get("primitives", [])
    session = context.get("session", "")
    project = context.get("project", "")
    user = context.get("user", "")
    monologue = context.get("monologue", "") if add_monologue else ""
    history = context.get("history", []) if add_history else []
    extra_fields = {k: v for k, v in context.items() if k not in {
        "identity", "identity_intro", "persona", "persona_template", "instructions",
        "constraints", "primitives", "session", "project", "user", "monologue", "history"
    }}

    # === System message / identity/persona framing ===
    prompt_messages = []

    system_parts = []
    if identity:
        system_parts.append(f"Identity: {identity}")
    if identity_intro:
        system_parts.append(f"Identity Intro: {identity_intro}")
    if persona:
        system_parts.append(f"Persona: {persona}")
    if persona_template:
        system_parts.append(f"Persona Template: {persona_template}")
    if instructions:
        system_parts.append(f"Instructions: {instructions}")
    if primitives:
        system_parts.append(f"Primitives available: {', '.join(primitives)}")
    if constraints:
        system_parts.append("Constraints: " + "; ".join(constraints))
    if session or project or user:
        system_parts.append(f"Session: {session} | Project: {project} | User: {user}")
    if monologue:
        system_parts.append(f"Inner Monologue: {monologue}")

    system_msg = "\n".join(system_parts).strip()
    if system_msg:
        prompt_messages.append({"role": "system", "content": system_msg})

    # --- MODIFICATION START ---
    # The history from ConversationManager is already in the correct format.
    # We can just extend the prompt_messages list with it directly.
    if history:
        prompt_messages.extend(history)
    # --- MODIFICATION END ---

    # === Include any additional context fields if present ===
    for key, value in extra_fields.items():
        if value:
            prompt_messages.append({"role": "system", "content": f"{key.capitalize()}: {value}"})

    # (Optional) Add a trailing user message for current prompt if present
    if "user_input" in context:
        prompt_messages.append({"role": "user", "content": context["user_input"]})

    logger.debug(f"Built prompt with {len(prompt_messages)} messages (format: {prompt_format})")
    return prompt_messages

# Maintain alias for compatibility
build_chat_prompt = build_prompt