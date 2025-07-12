import json
import logging
import re
from app.models.model_pool import model_pool

logger = logging.getLogger("GAIA.CognitiveDispatcher")

def dispatch(prompt: str, persona_instructions: str) -> dict:
    """
    Analyzes the prompt and dispatches it to the appropriate model with a dynamic context window.

    Returns:
        A dictionary containing the selected model, the response, and the token budget.
    """
    lite_model = model_pool.acquire_model("lite")
    if not lite_model:
        logger.error("Could not acquire Lite model for initial analysis.")
        return None

    try:
        # New, more direct prompt
        analysis_prompt = f"You are a JSON output agent. Analyze the following prompt and respond with ONLY a single JSON object with two keys: 'complexity' (simple, moderate, or complex) and 'required_context' (minimal, medium, or full).\n\nPrompt: {prompt}"
        
        analysis_response_raw = lite_model.create_completion(prompt=analysis_prompt, max_tokens=128) # Corrected variable name
        analysis_response_text = analysis_response_raw["choices"][0]["text"].strip()

        try:
            # Use regex to find the JSON object in the response
            json_match = re.search(r"\{.*\}", analysis_response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group(0))
            else:
                raise json.JSONDecodeError("No JSON object found in response", analysis_response_text, 0)

        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Could not decode JSON from lite model. Error: {e}. Response: {analysis_response_text}")
            analysis = {"complexity": "simple", "required_context": "minimal"}

        complexity = analysis.get("complexity", "simple")
        required_context = analysis.get("required_context", "minimal")

        token_budget = {
            "minimal": 1024,
            "medium": 2048,
            "full": 4096
        }.get(required_context, 1024)

        if complexity == "simple":
            selected_model_name = "lite"
            selected_model = lite_model
        else:
            model_pool.release_model("lite")
            selected_model_name = "prime"
            selected_model = model_pool.acquire_model("prime")

        if not selected_model:
            logger.error(f"Could not acquire {selected_model_name} model.")
            return None

        return {
            "model_name": selected_model_name,
            "model": selected_model,
            "token_budget": token_budget,
            "persona_instructions": persona_instructions
        }

    except Exception as e:
        logger.error(f"Error in cognitive dispatch: {e}", exc_info=True)
        return None
    finally:
        model_pool.release_model("lite")
        model_pool.release_model("prime")