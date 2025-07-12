import re
from app.utils.gaia_rescue_helper import sketch
from app.cognition.thought_seed import generate_thought_seed

# This is a placeholder for a more robust execution module
# In a real scenario, this would be a class with methods for each command
# and would handle the security and validation of the commands.
from app.utils.chat_logger import log_chat_entry

def route_output(response_text, ai_manager, session_id, destination="cli"):
    """
    Parses the structured output from the LLM and routes each part to the
    appropriate handler based on the destination.
    """
    # Default to the full string as the response if no prefixes are found
    response_to_user = response_text

    # --- Plan Block ---
    plan_match = re.search(r"PLAN:(.*?)(EXECUTE:|RESPONSE:|THOUGHT_SEED:|$)", response_text, re.DOTALL)
    if plan_match:
        plan_content = plan_match.group(1).strip()
        if plan_content:
            sketch("Execution Plan", plan_content)

    # --- Execute Block ---
    execute_commands = re.findall(r"EXECUTE:(.+?)(?=\nPLAN:|EXECUTE:|RESPONSE:|THOUGHT_SEED:|$)", response_text, re.DOTALL)
    for command in execute_commands:
        command = command.strip()
        if command:
            print(f"[Output Router] Executing for destination '{destination}': {command}")
            # In a real scenario, this would call a secure execution handler
            # ai_manager.execute(command)

    # --- Thought Seed Block ---
    thought_seed_match = re.search(r"THOUGHT_SEED:(.*?)(PLAN:|EXECUTE:|RESPONSE:|$)", response_text, re.DOTALL)
    if thought_seed_match:
        seed_content = thought_seed_match.group(1).strip()
        if seed_content:
            generate_thought_seed(prompt=seed_content, context={"source": "self_reflection", "destination": destination}, config=ai_manager.config, llm=ai_manager.llm)

    # --- Response Block ---
    response_match = re.search(r"RESPONSE:(.*)", response_text, re.DOTALL)
    if response_match:
        response_to_user = response_match.group(1).strip()

    # Route the final user-facing response to the correct destination
    if destination == "cli":
        # For the CLI, we typically print the response to the console
        # This will be handled by the calling function, which will stream the response
        pass
    elif destination == "web_chat":
        # TODO: Implement web chat output (e.g., WebSocket)
        pass
    elif destination == "council_chat":
        # TODO: Implement council chat output
        pass
    elif destination == "discord_chat":
        # TODO: Implement Discord chat output (e.g., webhook)
        pass

    # The calling function will be responsible for streaming this to the user
    return response_to_user
