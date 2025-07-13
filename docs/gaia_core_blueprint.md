# GAIA Core Blueprint

This document outlines the core architecture and functionality of the GAIA agent. It serves as a single source of truth for understanding how GAIA's cognitive processes work, from handling user input to generating a response.

## 1. Verification Protocol

Items in this blueprint may be marked with a verification tag to indicate that they have been checked against the live codebase. This ensures the documentation remains an accurate reflection of the system's implementation.

The format is as follows:

**`[Verified ✅ | Def: 2025-07-10 | Call: 2025-07-10]`**

*   **`[Verified ✅]`**: A visual confirmation of successful verification.
*   **`Def: YYYY-MM-DD`**: The date when the component's **Definition** (its purpose and parameters as described in the blueprint) was last confirmed to match the source code.
*   **`Call: YYYY-MM-DD`**: The date when a specific **Call** between modules (as described in the Cognitive Flow) was last confirmed to be implemented correctly in the source code, with all parameters honored.

This two-step process ensures that the blueprint is not just a high-level overview, but a truly accurate and verifiable guide to the codebase's architecture.

## 2. Core Components

### 2.1. `gaia_rescue.py`: The Entry Point

The `gaia_rescue.py` script is the primary entry point for interacting with GAIA in a developer-focused "rescue shell."

*   **`MinimalAIManager`**: A lightweight class that initializes and manages all the essential components of GAIA's cognitive stack, including the model pool, configuration, ethical sentinels, and session manager.
*   **`rescue_chat_loop`**: The main interactive loop that handles user input, passes it to the `AgentCore`, and streams the response back to the user.
*   **Command-line Arguments**:
    *   `--session-id`: Specifies the session to use or create.
    *   `--persona`:  Loads a specific persona for GAIA.

### 2.2. `app/cognition/agent_core.py`: The Heart of GAIA

The `AgentCore` class orchestrates the entire cognitive process. Its `run_turn` method is the central function that executes a single turn of the conversation.

*   **`run_turn(user_input, session_id, destination)`**:
    1.  **Intent Detection**: Determines the user's intent (e.g., "ask_question", "run_command").
    2.  **Prompt Building**: Constructs a detailed prompt for the LLM using the `prompt_builder`. This includes persona instructions, conversation history, and the user's input. For planning, it injects an `initial_planning` task instruction.
    3.  **Planning**: Sends the planning prompt to the LLM to generate an initial plan.
    4.  **Reflection and Refinement**: Uses the `reflect_and_refine` function to improve the initial plan.
    5.  **Response Generation**: Constructs a final prompt, including the refined plan, and sends it to the LLM to generate a structured response.
    6.  **Interruption Handling**: If the response generation is interrupted by the `StreamObserver`, it rebuilds the prompt with an `interruption_handling` task instruction and generates a corrected response.
    7.  **Output Routing**: The structured response from the LLM is passed to the `OutputRouter`, which extracts the user-facing message.
    8.  **Action Execution**: If the response contains `EXECUTE:` blocks, the `_execute_actions` method is called to run the specified commands.

### 2.3. `app/config.py`: System-Wide Configuration

The `Config` class loads and provides access to all system-wide settings from `gaia_constants.json`.

*   **`gaia_constants.json`**: A central JSON file that defines:
    *   **`identity` and `identity_intro`**: GAIA's core identity.
    *   **`primitives`**: A list of allowed actions (e.g., "read", "write").
    *   **`SAFE_EXECUTE_FUNCTIONS`**: A whitelist of shell commands that can be executed.
    *   **`reflection_guidelines`**: Rules for the self-reflection process.
    *   **`TASK_INSTRUCTIONS`**: Specific instructions for different cognitive tasks (e.g., "initial_planning", "refinement").
    *   **Model paths, temperature, and other LLM parameters.**

### 2.4. `app/models/model_pool.py`: Managing AI Models [Verified: ❌]

The `ModelPool` class is responsible for loading and managing the different AI models used by GAIA.

*   **`load_models()`**: Loads the "prime", "lite", and "embed" models into memory.
*   **`get(name)`**: Retrieves a specific model from the pool.
*   **`set_persona(persona)`**: Sets the active persona for the models.
*   **`acquire_model(name)`**: Marks a model as "busy" and returns it.
*   **`release_model(name)`**: Marks a model as "idle".
*   **`get_idle_model(exclude)`**: Returns the name of an idle model, optionally excluding a specific model. [Verified ✅ | Def: 2025-07-11]

### 2.5. `app/cognition/cognitive_dispatcher.py`: Dynamic Cognitive Dispatching [Verified: ❌]

The `cognitive_dispatcher.py` module is responsible for analyzing incoming prompts and dispatching them to the most appropriate model with a dynamic context window. [Verified ✅ | Def: 2025-07-11]

*   **`dispatch(prompt, persona_instructions)`**:
    *   Uses the "lite" model to analyze the prompt for complexity and required context.
    *   Based on the analysis, selects either the "lite" or "prime" model to generate the response.
    *   Determines a token budget for the prompt, allowing for a dynamic context window.
    *   Returns the selected model, the response, the token budget, and the persona instructions.

### 2.6. `app/utils/prompt_builder.py`: Crafting the Perfect Prompt

The `prompt_builder.py` module is responsible for constructing the prompts sent to the LLM.

*   **`build_prompt(config, persona_instructions, session_id, history, user_input, task_instruction)`**:
    *   Assembles a tiered prompt that includes the persona, conversation history (summarized if necessary), user input, and an optional task-specific instruction.
    *   Manages the token budget to ensure the prompt does not exceed the model's context window.

### 2.6. `app/cognition/self_reflection.py`: Introspection and Improvement

The `self_reflection.py` module enables GAIA to analyze and improve its own plans and responses.

*   **`reflect_and_refine(context, output, config, llm, ethical_sentinel, instructions)`**:
    *   Takes an initial plan or response and uses the LLM to critique and refine it.
    *   Calls `build_prompt` with the `task_instruction="refinement"` to guide the LLM's reflection.
    *   Extracts the refined plan from a `PLAN:` block in the LLM's response. [Verified ✅ | Def: 2025-07-10 | Call: 2025-07-10]

### 2.7. `app/utils/stream_observer.py`: The Watchful Guardian

The `StreamObserver` monitors the LLM's output in real-time to detect and prevent critical errors.

*   **`observe(buffer, context)`**:
    *   Analyzes the stream of tokens from the LLM.
    *   Uses a "lite" model to check for issues like repetitive gibberish, ethical violations, or hallucinations.
    *   If a problem is detected, it can interrupt the response generation process.
    *   Loads an "observer" task instruction from `gaia_constants.json` to guide its analysis.

### 2.8. `app/utils/output_router.py`: Directing the Flow of Information

The `OutputRouter` is a new component that parses the structured output from the LLM and routes it to the appropriate destination.

*   **`route_output(response_text, ai_manager, session_id, destination)`**:
    *   Parses the response for `PLAN:`, `EXECUTE:`, `RESPONSE:`, and `THOUGHT_SEED:` blocks.
    *   Handles the content of each block accordingly (e.g., sketching the plan, executing commands).
    *   Extracts the user-facing message from the `RESPONSE:` block.
    *   Includes placeholder logic for routing to different destinations like `web_chat`, `council_chat`, and `discord_chat`.

### 2.9. `app/utils/gaia_rescue_helper.py`: The Developer's Toolkit

The `gaia_rescue_helper.py` module provides a set of utility functions that can be used in the rescue shell.

*   **`sketch(title, content)`**: Records information to a "sketchpad" for later review.
*   **`show_sketchpad()`**: Displays the contents of the sketchpad.
*   **`clear_sketchpad()`**: Clears the sketchpad.
*   **Other helper functions for file operations, shell commands, and more.**

### 2.10. Ethics and Memory

*   **`app/ethics/core_identity_guardian.py` and `app/ethics/ethical_sentinel.py`**: These modules work together to ensure that GAIA's behavior remains within ethical boundaries. The `CoreIdentityGuardian` enforces immutable identity rules, while the `EthicalSentinel` monitors system health and cognitive strain.
*   **`app/memory/session_manager.py`**: The `SessionManager` is responsible for persisting conversation history and managing long-term memory.

## 3. The Cognitive Flow in Detail

Here's a step-by-step breakdown of how GAIA processes a user's request in the `dev` persona:

1.  The user enters a prompt in the `rescue_chat_loop`. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
2.  The `rescue_chat_loop` calls `agent_core.run_turn`. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
3.  `run_turn` calls `build_prompt` with the `task_instruction="initial_planning"`. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
4.  `build_prompt` creates a prompt that includes the user's request and instructions to create a plan. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
5.  `run_turn` sends this prompt to the "prime" LLM, which generates an initial plan. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
6.  `run_turn` calls `reflect_and_refine` with the initial plan. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
7.  `reflect_and_refine` calls `build_prompt` with the `task_instruction="refinement"`. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
8.  `build_prompt` creates a prompt that instructs the LLM to critique and improve the plan. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
9.  `reflect_and_refine` sends this prompt to the "lite" LLM, which generates a refined plan. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
10. `run_turn` calls `build_prompt` again, this time without a task instruction, but including the refined plan in the conversation history. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
11. `run_turn` sends this final prompt to the "prime" LLM to generate the response. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
12. As the LLM generates the response, the `StreamObserver` monitors the output for errors. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-12]
13. Once the response is complete, `run_turn` passes it to the `OutputRouter`. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
14. The `OutputRouter` parses the structured response, extracts the user-facing message, and returns it to `run_turn`. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
15. `run_turn` streams the user-facing message to the `rescue_chat_loop`, which prints it to the console. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]
16. If the response includes an `EXECUTE:` block, `run_turn` calls `_execute_actions` to run the command. [Verified ✅ | Def: 2025-07-11 | Call: 2025-07-11]

This detailed, multi-step process ensures that GAIA's responses are well-planned, reflective, and safe.
