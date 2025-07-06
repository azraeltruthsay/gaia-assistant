
"""
Prompt Builder (robust, persona/context-aware)
- Assembles the LLM prompt with identity, persona, context, constraints, history, and memory.
- Actively manages the token budget to prevent context overflow.
- Implements a tiered context strategy for reliability.
"""

import logging
import os
from typing import List, Dict

# We need a tokenizer to count tokens for budget management.
# This assumes a utility function exists. If not, we can create a simple one.
from app.utils.tokenizer import count_tokens

logger = logging.getLogger("GAIA.PromptBuilder")

# Define the path where session-specific summary files are stored.
SUMMARY_DIR = "app/shared/summaries"


def _build_prompt_core(
    config,
    persona_instructions: str,
    session_id: str,
    history: List[Dict],
    user_input: str
) -> List[Dict]:
    """
    Builds a tiered, budget-aware prompt for LLM inference.

    This function is the core of maintaining the agent's identity and memory.
    It ensures the final prompt fits within the model's context window by
    intelligently including a long-term summary and recent conversation history.

    Tier 0: Persona Instructions (Immutable Core Identity)
    Tier 1: Evolving Summary (Long-term Memory)
    Tier 2: Recent History (Short-term Memory)
    Tier 3: User Input (The Current Task)

    Args:
        config: The application's configuration object (for MAX_TOKENS, etc.).
        persona_instructions: The full, pre-formatted system prompt containing identity and tools.
        session_id: The unique ID for the current conversation.
        history: The recent, verbatim conversation history from the SessionManager.
        user_input: The user's latest message.

    Returns:
        A list of message dictionaries formatted for the LLM.
    """
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    summary_file_path = os.path.join(SUMMARY_DIR, f"{session_id}.summary")

    # --- Tier 0 & 3: The immutable parts of the prompt ---
    core_prompt = {"role": "system", "content": persona_instructions}
    user_prompt = {"role": "user", "content": user_input}

    # --- Calculate the token budget ---
    # Start with the total context window and subtract the essentials.
    fixed_tokens = count_tokens(core_prompt['content']) + count_tokens(user_prompt['content'])
    # The response buffer is a safety margin for the model to generate its answer.
    remaining_budget = config.MAX_TOKENS - fixed_tokens - config.RESPONSE_BUFFER
    logger.debug(
        f"Token Budgeting: Total={config.MAX_TOKENS}, "
        f"Fixed={fixed_tokens}, ResponseBuffer={config.RESPONSE_BUFFER} -> "
        f"Remaining Budget={remaining_budget}"
    )

    # --- Tier 1: Load and budget for the Evolving Summary (Long-Term Memory) ---
    summary_content = ""
    if os.path.exists(summary_file_path):
        try:
            with open(summary_file_path, 'r', encoding='utf-8') as f:
                summary_content = f.read().strip()
        except IOError as e:
            logger.error(f"Could not read summary file {summary_file_path}: {e}")

    summary_prompt = {}
    if summary_content:
        # Frame the summary so the model understands its purpose.
        formatted_summary = f"[This is a summary of the conversation so far to provide long-term context.]\n{summary_content}"
        summary_prompt = {"role": "system", "content": formatted_summary}
        summary_tokens = count_tokens(summary_prompt['content'])

        # Deduct the summary's token count from our budget.
        remaining_budget -= summary_tokens
        logger.debug(f"Budget after including summary ({summary_tokens} tokens): {remaining_budget}")

    # --- Tier 2: Add Recent History (Short-Term Memory) until the budget is full ---
    history_to_include = []
    # Iterate backwards to get the most recent messages first.
    for message in reversed(history):
        msg_tokens = count_tokens(message['content'])
        if msg_tokens <= remaining_budget:
            # Add to the beginning of the list to maintain chronological order.
            history_to_include.insert(0, message)
            remaining_budget -= msg_tokens
        else:
            # Stop when we run out of space.
            logger.debug("History budget exhausted. Trimming older messages.")
            break

    # --- Assemble the final prompt in the correct order ---
    final_prompt = [core_prompt]
    if summary_prompt:
        final_prompt.append(summary_prompt)
    final_prompt.extend(history_to_include)
    final_prompt.append(user_prompt)

    final_token_count = config.MAX_TOKENS - remaining_budget - config.RESPONSE_BUFFER
    logger.info(
        f"Final prompt assembled for session '{session_id}'. "
        f"Messages: {len(final_prompt)}, "
        f"Estimated Tokens: ~{final_token_count}/{config.MAX_TOKENS}"
    )

    return final_prompt

# Older modules (external_voice, a few tests) still call
#     build_prompt(context=ctx_dict)
# where ctx_dict = {
#     "config": cfg,
#     "persona_instructions": system_str,
#     "session_id": sid,
#     "history": history_list,
#     "user_input": user_msg,
# }
# The wrapper below quietly converts that call into the new positional form.

def build_prompt(*args, **kwargs):
    """
    Compatibility wrapper.

    Accepts either:
        build_prompt(config, persona_instructions, session_id, history, user_input)
    or the legacy:
        build_prompt(context=<dict>)
    """
    if "context" in kwargs:
        ctx = kwargs.pop("context")
        # ── tolerant defaults for legacy callers ─────────────────
        from app.config import Config
        cfg   = ctx.get("config", Config())
        instr = ctx.get("persona_instructions")
        if instr is None:                       # synthesise if missing
            tmpl = ctx.get("persona_template", "")
            raw  = ctx.get("instructions", [])
            instr = f"{tmpl}\n\n" + ("\n".join(raw) if isinstance(raw, list) else str(raw))
        sid   = ctx.get("session_id", "system")
        hist  = ctx.get("history", [])
        user  = ctx.get("user_input", "")
        return _build_prompt_core(cfg, instr, sid, hist, user)
    # Fall back to the new signature (positional or keyword)
    return _build_prompt_core(*args, **kwargs)


# Maintain the alias from the original file for backward compatibility.
build_chat_prompt = build_prompt
