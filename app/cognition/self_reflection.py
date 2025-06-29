"""
Self Reflection Processor (model-powered, robust pipeline)
- Calls LLM for post-generation analysis and hallucination/error detection.
- Integrates config-driven safety and can fallback to rule-based checks.
- Used for post-response reflection in manager.py or external_voice.py pipeline.
"""

import logging
from app.utils.prompt_builder import build_prompt
from app.config import Config
from app.cognition.thought_seed import maybe_review_seeds

logger = logging.getLogger("GAIA.SelfReflection")

def run_self_reflection(context, output, config=None, llm=None):
    """
    Main entrypoint for model-powered self-reflection.
    - context: dict with current persona, session, etc.
    - output: the GAIA-generated response to check.
    - config: Config instance (optional)
    - llm: model to use for reflection (optional, defaults to Prime)
    """
    if config is None:
        config = Config()
    if llm is None and hasattr(config, "model_pool"):
        llm = config.model_pool.get("Prime", None)  # Fallback to Prime if available

    # Build a robust prompt for reflection—include guidelines and output to review
    prompt = (
        f"You are GAIA's internal reflection engine. Your guidelines:\n"
        f"{'; '.join(getattr(config, 'reflection_guidelines', []))}\n\n"
        f"Review the following output for errors, hallucinations, privacy leaks, or unsafe content.\n"
        f"Output:\n{output}\n\n"
        f"Provide a brief reflection: is the output safe and high-quality? If not, summarize the issue."
    )

    # Model-powered reflection (if LLM present)
    if llm:
        messages = [
            {"role": "system", "content": "Self-reflection and quality control assistant."},
            {"role": "user", "content": prompt},
        ]
        try:
            result = llm.create_chat_completion(
                messages=messages,
                temperature=0.3,
                top_p=0.7,
                max_tokens=256,
                stream=False
            )
            reflection = result["choices"][0]["message"]["content"].strip()
            logger.info(f"🪞 Model-powered self-reflection: {reflection[:100]}...")

            # Only generate a thought seed if reflection is notable
            if reflection and any(
                key in reflection.lower()
                for key in ["interesting", "improve", "issue", "todo", "fix"]
            ):
                try:
                    from app.cognition.thought_seed import maybe_generate_seed
                    maybe_generate_seed(reflection, context, config)
                except Exception as seed_exc:
                    logger.error(f"Error generating thought seed: {seed_exc}")

            maybe_review_seeds(config=config)
            return reflection
        except Exception as e:
            logger.error(f"Self-reflection LLM error: {e}")

    # Rule-based fallback: simple string checks
    flagged = False
    message = ""
    out_l = output.lower()
    if "error" in out_l or "exception" in out_l:
        flagged = True
        message = "[Reflection: Possible error detected. Please verify output.]"
    elif "hallucinate" in out_l or "fabrication" in out_l:
        flagged = True
        message = "[Reflection: Hallucination or fabricated content possible.]"
    elif "password" in out_l or "secret" in out_l or "token" in out_l:
        flagged = True
        message = "[Reflection: Possible sensitive data leak.]"
    if flagged:
        logger.warning(f"Rule-based reflection triggered: {message}")
        maybe_review_seeds(config=config)
        return message

        try:
            from app.cognition.thought_seed import maybe_generate_seed
            maybe_generate_seed(message, context, config)
        except Exception as seed_exc:
            logger.error(f"Error generating thought seed: {seed_exc}")


    logger.info("Reflection: Output appears normal.")
    return None

def reflect_on(origin, content, responder, config: Config = None, post_action_hook=None):
    """
    Robust post-generation reflection. Can be called after every streamed or generated response.
    """
    logger.info(f"🤔 Running self-reflection for responder '{responder}' on origin '{origin}'...")

    if not content or not content.strip():
        logger.warning("⚠️ No content to reflect on.")
        return None

    # Optionally, context could be richer—here we just use responder and basic config
    context = {
        "responder": responder,
        "origin": origin,
        "instructions": getattr(config, "reflection_guidelines", []),
    }
    reflection = run_self_reflection(context, content, config=config)

    if post_action_hook:
        try:
            logger.info("🔁 Running post-action hook after reflection.")
            post_action_hook(content)
        except Exception as e:
            logger.warning(f"Post-action hook failed: {e}")

    # (Optional) Buffer/sketch or shell execution if desired (stub)
    if "EXECUTE:" in content:
        logger.info("🚀 Detected EXECUTE directive in content. (stub)")

    return reflection
