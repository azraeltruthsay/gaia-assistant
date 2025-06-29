"""
Intent Detection (pillar-compliant, robust)
- Fast reflex/regex path for autonomic commands (help, exit, shell, etc).
- LLM-powered detection for all ambiguous/natural input.
- Returns simple intent labels for downstream pipeline use.
- Ready for expansion: streaming, multi-intent, or advanced “plan” logic.
"""

import re
import logging

logger = logging.getLogger("GAIA.IntentDetection")

# ---- Reflex path for “autonomic” commands ----
def fast_intent_check(text):
    text = text.lower().strip()
    # Reflexes—no model call
    if text in {"exit", "quit", "bye"}:
        return "exit"
    if text.startswith("help") or text in {"?", "h"}:
        return "help"
    if text.startswith("ls ") or text.startswith("cat ") or text.startswith("pwd"):
        return "shell"
    # Add more hardcoded patterns as needed
    return None

# ---- Model-powered intent detection ----
def model_intent_detection(text, config, lite_llm=None, full_llm=None):
    """
    Uses an LLM (Lite if present, else Prime) to detect intent for natural language input.
    Output should always be one of: read_file, write_file, mark_task_complete, reflect, seed, shell, other.
    """
    model = lite_llm or full_llm
    if model is None:
        logger.warning("No model available for intent detection; falling back to 'other'.")
        return "other"
    prompt = (
        "You are an intent detection agent for GAIA.\n"
        "Given the following user input, return ONLY the primary intent, exactly as one of:\n"
        "read_file, write_file, mark_task_complete, reflect, seed, shell, other.\n"
        "User Input: " + text + "\nIntent:"
    )
    messages = [
        {"role": "system", "content": "Intent detection agent."},
        {"role": "user", "content": prompt}
    ]
    result = model.create_chat_completion(
        messages=messages,
        temperature=0.0,
        max_tokens=6,
        top_p=1.0,
        stream=False
    )
    # Accept only the first word or intent string
    intent = result["choices"][0]["message"]["content"].strip().split()[0]
    intent = intent if intent in {
        "read_file", "write_file", "mark_task_complete", "reflect", "seed", "shell", "other"
    } else "other"
    logger.info(f"Model intent detection: {intent}")
    return intent

# ---- Unified entrypoint ----
def detect_intent(text, config, lite_llm=None, full_llm=None):
    """
    Detects intent using reflex path, else LLM.
    Returns one of: read_file, write_file, mark_task_complete, reflect, seed, shell, exit, help, other
    """
    # 1. Reflex check
    intent = fast_intent_check(text)
    if intent:
        logger.debug(f"Reflex intent: {intent}")
        return intent
    # 2. LLM path
    return model_intent_detection(text, config, lite_llm, full_llm)
