import json
import logging
import re
from app.models.model_pool import model_pool

logger = logging.getLogger("GAIA.CognitiveDispatcher")

def dispatch(prompt: str, persona_instructions: str) -> dict:
    """
    Analyzes the prompt and dispatches it to the appropriate model with a dynamic context window.
    Acquires the selected model and returns it. The caller is responsible for releasing the model.

    Returns:
        A dictionary containing the selected model name, the acquired model instance, token budget, and persona instructions.
    """
    lite_model = model_pool.acquire_model("lite")
    if not lite_model:
        logger.error("Could not acquire Lite model for initial analysis.")
        return None

    try:
        # Improved, more explicit analysis prompt to encourage valid JSON output
        analysis_prompt = (
            "You are GAIA's cognitive dispatcher. Your task is to analyze the following user prompt and respond ONLY with a valid JSON object. "
            "The JSON must have two keys: 'complexity' (with value 'simple', 'moderate', or 'complex') and 'required_context' (with value 'minimal', 'medium', or 'full'). "
            "Do not include any explanation, commentary, or extra text. Example: {\"complexity\": \"moderate\", \"required_context\": \"medium\"}. "
            f"Prompt: {prompt}"
        )
        
        analysis_response_raw = lite_model.create_completion(prompt=analysis_prompt, max_tokens=128)
        analysis_response_text = analysis_response_raw["choices"][0]["text"].strip()

        try:
            # Enhanced JSON extraction to find the first valid JSON object
            json_match = re.search(r"(?s)\{.*?\}", analysis_response_text)
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

        selected_model_name = "lite"
        selected_model = lite_model

        if complexity != "simple":
            # Complex task: switch to prime model
            prime_model = model_pool.acquire_model("prime")
            if prime_model:
                # Successfully acquired prime, so we can release lite
                model_pool.release_model("lite")
                selected_model_name = "prime"
                selected_model = prime_model
            else:
                # Failed to get prime, so we'll just use the lite model
                logger.warning("Could not acquire Prime model, falling back to Lite model for complex task.")
        
        return {
            "model_name": selected_model_name,
            "model": selected_model,
            "token_budget": token_budget,
            "persona_instructions": persona_instructions
        }

    except Exception as e:
        logger.error(f"Error in cognitive dispatch: {e}", exc_info=True)
        # Release any models we might have acquired before the error
        model_pool.release_model("lite")
        model_pool.release_model("prime") # It might have been acquired
        return None
