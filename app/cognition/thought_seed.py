"""
Thought Seed System (GAIA pillar-compliant)
- Generates, stores, reviews, and processes thought seeds.
"""

# /home/azrael/Project/gaia-assistant/app/cognition/thought_seed.py

import os
import json
from pathlib import Path
from datetime import datetime
from app.config import Config
import logging
# unified reflection engine
from app.cognition.self_reflection import run_self_reflection
from app.utils.thoughtstream import write as ts_write
logger = logging.getLogger("GAIA.ThoughtSeed")

SEEDS_DIR = Path("./knowledge/seeds")
SEEDS_DIR.mkdir(parents=True, exist_ok=True)


def generate_thought_seed(prompt, context=None, config=None, llm=None):  # <--- llm parameter added
    """
    Generate a model-powered thought seed.
    """
    # Local import to break circular dependency

    if config is None:
        config = Config()

    # Ensure LLM is available. If not passed, try to get from config's model_pool.
    # This assumes model_pool is correctly attached to config.
    if llm is None:
        if hasattr(config, 'model_pool') and config.model_pool is not None:
            llm = config.model_pool.get("prime")
        else:
            logger.error("❌ No LLM provided and model_pool not available in config for thought seed generation.")
            return None  # Return None or raise an error if LLM is critical

    if context is None:
        context = {}

    seed_obj = None  # Initialize seed_obj to None
    try:
        # --- MODIFICATION START ---
        # Construct a more direct and less verbose prompt for the seed.
        user_input = context.get("user_input", prompt)
        gaia_response = context.get("gaia_response", "")

        seed_prompt = (
            f"Review the following exchange:\n\n"
            f"User: {user_input}\n"
            f"GAIA: {gaia_response}\n\n"
            "Based on this exchange, generate a concise, actionable 'seed thought' for future reflection. "
            "A seed thought is a single sentence describing a possible next step, a question to investigate, or an insight to remember. Do not act on it, just generate the thought."
        )
        # --- MODIFICATION END ---
        seed_text = process_thought(
            task_type="thought_seed",
            persona=config.persona_name,
            instructions="Generate only a thought seed. Do not act or execute.",
            payload=seed_prompt,
            identity_intro=config.identity_intro,
            reflect=False,
            context=context,
            llm=llm,  # <--- Pass the LLM here
            config=config
        )
        seed_obj = {
            "created": datetime.utcnow().isoformat(),
            "context": context,
            "prompt": prompt,
            "seed": seed_text.strip(),
            "reviewed": False,
            "action_taken": False,
            "result": None
        }
        # Store to disk
        fname = f"seed_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(SEEDS_DIR / fname, "w", encoding="utf-8") as f:
            json.dump(seed_obj, f, indent=2)
        logger.info(f"Thought seed generated and saved: {fname}")
    except Exception as e:
        logger.error(f"❌ Error generating thought seed: {e}", exc_info=True)
    return seed_obj  # Return seed_obj, which might be None on error


def list_unreviewed_seeds():
    seeds = []
    for f in SEEDS_DIR.glob("seed_*.json"):
        try:  # Add try-except for file reading
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                if not data.get("reviewed"):
                    seeds.append((f, data))
        except Exception as e:
            logger.error(f"❌ Error reading thought seed file {f}: {e}", exc_info=True)
    return seeds


def review_and_process_seeds(config=None, llm=None, auto_act=False):  # <--- llm parameter added
    """
    Load unreviewed seeds, use model to decide whether to act, then process as appropriate.
    """
    # Local import to break circular dependency

    if config is None:
        config = Config()

    # Ensure LLM is available. If not passed, try to get from config's model_pool.
    if llm is None:
        if hasattr(config, 'model_pool') and config.model_pool is not None:
            llm = config.model_pool.get("prime")
        else:
            logger.error("❌ No LLM provided and model_pool not available in config for seed review.")
            return False  # Indicate failure

    seeds = list_unreviewed_seeds()
    for f, data in seeds:
        review_prompt = (
            f"Here is a thought seed generated earlier:\nSeed: {data['seed']}\n"
            f"Context: {data['context']}\nShould GAIA act on this seed now? Answer yes or no, and explain."
        )
    try:
            messages = [
                {"role": "system", "content": "You are a decision-making assistant. Answer with 'yes' or 'no' and a brief explanation."},
                {"role": "user", "content": review_prompt},
            ]
            result = llm.create_chat_completion(
                messages=messages,
                temperature=0.3,
                top_p=0.7,
                max_tokens=256,
                stream=False
            )
            decision = result["choices"][0]["message"]["content"].strip()
            should_act = "yes" in decision.lower()
            data["reviewed"] = True
            data["reviewed_at"] = datetime.utcnow().isoformat()
            data["review_decision"] = decision
            if should_act and auto_act:
                action_result = "Not implemented yet"
                data["action_taken"] = True
                data["action_result"] = action_result
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=2)
            logger.info(f"Thought seed reviewed: {f.name} — Decision: {decision}")
    except Exception as e:
            logger.error(f"❌ Error reviewing thought seed {f.name}: {e}", exc_info=True)
    return True


def maybe_generate_seed(prompt, context, config, llm=None):  # <--- llm parameter added
    """
    Decides (based on config/heuristics) whether to generate a thought seed.
    """
    # Add conditions as needed—by default, always generate for demonstration.
    generate_thought_seed(prompt, context, config, llm=llm)  # <--- Pass llm here
    # If you want config-driven or conditional behavior, check here.


def maybe_review_seeds(config, llm=None):  # <--- llm parameter added
    """
    Decides (based on config/heuristics) whether to review/process seeds now.
    """
    # Add conditions as needed—by default, always review for demonstration.
    review_and_process_seeds(config=config, llm=llm, auto_act=False)  # <--- Pass llm here
    # Set auto_act=True if you want seeds to trigger actions directly.