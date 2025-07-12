import json
import logging
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
        analysis_prompt = f"Analyze this prompt for complexity and required context. Respond with a JSON object containing: {{'complexity': 'simple|moderate|complex', 'required_context': 'minimal|medium|full'}}.\n\nPrompt: {prompt}"
        analysis_response = lite_model.create_completion(prompt=analysis_prompt, max_tokens=128)
        
        try:
            analysis = json.loads(analysis_response["choices"][0]["text"].strip())
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Could not decode JSON from lite model. Error: {e}. Response: {analysis_response}")
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