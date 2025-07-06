# Persistent Memory Guide for Gemini

This document outlines how to interact with GAIA's persistent memory. GAIA's memory is designed to be long-term and session-aware, allowing for continuous conversations and context retention.

## Key Concepts

*   **Sessions:** All conversations are tied to a session ID. The `rescue_chat_loop` in `gaia_rescue.py` automatically handles session management.
*   **History:** The `SessionManager` stores the full conversation history for each session. This history is used by the `PromptBuilder` to construct the context for the LLM.
*   **Reflection:** The agent now uses a `reflect_and_refine` loop to improve its reasoning and actions. This process is logged to the `thoughtstream` for debugging and analysis.

## Interacting with Memory

*   **Continuing a Conversation:** To continue a previous conversation, simply start the `rescue_chat_loop` with the same session ID.
*   **Viewing Session History:** You can inspect the session history by interacting with the `ai.session_manager` object in the `gaia_rescue.py` interactive shell.
*   **Resetting a Session:** To start a fresh conversation, you can reset the session using `ai.session_manager.reset_session('your_session_id')`.

## Best Practices

*   **Be Specific:** When interacting with the agent, provide clear and specific instructions. This will help the agent better understand your intent and generate more accurate responses.
*   **Provide Context:** If you are referencing a previous conversation, be sure to provide enough context for the agent to understand the reference.
*   **Use the `thoughtstream`:** The `thoughtstream` is a valuable tool for understanding the agent's reasoning process. You can find the `thoughtstream` logs in the `knowledge/logs/thoughtstreams` directory.
