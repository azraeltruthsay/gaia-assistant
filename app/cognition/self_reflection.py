"""
Self Reflection Processor (model-powered, robust pipeline)
- Calls LLM for post-generation analysis and hallucination/error detection.
- Integrates config-driven safety and can fallback to rule-based checks.
- Used for post-response reflection in manager.py or external_voice.py pipeline.
"""

import logging
import re
from app.utils.prompt_builder import build_prompt
from app.config import Config

logger = logging.getLogger("GAIA.SelfReflection")

def reflect_and_refine(context, output, config, llm, ethical_sentinel):
    """
    Performs iterative self-reflection to refine a response until a confidence
    threshold is met.
    """
    from app.utils.gaia_rescue_helper import sketch, show_sketchpad, clear_sketchpad

    max_iterations = config.reflection_max_iterations
    confidence_threshold = config.reflection_confidence_threshold

    clear_sketchpad()

    current_thought = output
    for i in range(max_iterations):
        # Step 1: Critique and Score the current thought.
        critique_prompt = (
            f"You are a critique and refinement AI. Review the following 'thought' in the context of the user's request. "
            f"User Context: {context}\n\n"
            f"Thought to review: '{current_thought}'\n\n"
            f"1. Critique this thought. Is it logical, safe, and does it directly address the user's need? "
            f"2. How can it be improved to be more accurate, helpful, and safe? "
            f"3. On a scale of 1-100, how confident are you in this thought? Respond with only the number."
        )

        critique_and_score_raw = llm.create_chat_completion(
            messages=[{"role": "user", "content": critique_prompt}],
            temperature=0.4,
            top_p=0.8,
            max_tokens=512,
            stream=False
        )["choices"][0]["message"]["content"].strip()

        # Step 2: Extract Confidence Score
        confidence_score = 0
        score_match = re.search(r'\b(\d{1,3})\b', critique_and_score_raw)
        if score_match:
            confidence_score = int(score_match.group(1))

        # Step 3: Sketch the process for debugging
        sketch(
            title=f"Iteration {i+1}: Confidence {confidence_score}%",
            content=f"Thought: {current_thought}\n\nCritique: {critique_and_score_raw}"
        )

        # Step 4: Check for exit conditions (High confidence AND ethical safety)
        if confidence_score >= confidence_threshold:
            # Final check before returning a high-confidence thought
            if ethical_sentinel.run_full_safety_check(
                persona_traits=getattr(config.persona, 'traits', {}),
                instructions=getattr(config.persona, 'instructions', []),
                prompt=current_thought
            ):
                logger.info(f"✅ Reflection loop passed with confidence {confidence_score} after {i+1} iterations.")
                return current_thought
            else:
                logger.warning(f"⚠️ High confidence thought failed final safety check. Continuing refinement.")

        # Step 5: If not confident or safe enough, refine the thought
        refinement_prompt = (
            f"User Context: {context}\n\n"
            f"Previous thought: '{current_thought}'\n\n"
            f"Critique and improvement suggestions: '{critique_and_score_raw}'\n\n"
            f"Based on the critique, generate a new, improved thought that better addresses the user's need."
        )

        current_thought = llm.create_chat_completion(
            messages=[{"role": "user", "content": refinement_prompt}],
            temperature=0.7,
            top_p=0.9,
            max_tokens=1024,
            stream=False
        )["choices"][0]["message"]["content"].strip()

    # After the loop, perform one last safety check on the final thought
    if ethical_sentinel.run_full_safety_check(
        persona_traits=getattr(config.persona, 'traits', {}),
        instructions=getattr(config.persona, 'instructions', []),
        prompt=current_thought
    ):
        logger.info(f"✅ Reflection loop finished. Returning last thought after {max_iterations} iterations.")
        return current_thought
    else:
        logger.error(f"⛔ Final thought failed safety check after {max_iterations} iterations. Blocking output.")
        return "[REDACTED] The proposed action was blocked by the ethical sentinel after final review."


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
    from app.cognition.thought_seed import maybe_review_seeds
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
