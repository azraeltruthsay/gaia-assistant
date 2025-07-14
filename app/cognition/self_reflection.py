"""
Self Reflection Processor (model-powered, robust pipeline)
- Calls LLM for post-generation analysis and hallucination/error detection.
- Integrates config-driven safety and can fallback to rule-based checks.
- Used for post-response reflection in manager.py or external_voice.py pipeline.
"""

import logging
import time
import json
import re
from app.config import Config
from app.memory.conversation.summarizer import ConversationSummarizer
from app.utils.gaia_rescue_helper import sketch, show_sketchpad, clear_sketchpad
from app.utils.prompt_builder import count_tokens

logger = logging.getLogger("GAIA.SelfReflection")
# File logging setup for self-reflection module
import os
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, "self_reflection.log"), mode="a")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def reflect_and_refine(context: dict, output: str, config, llm, ethical_sentinel, instructions: list) -> str:
    """
    Iteratively reflect on the given output using the LLM and ethical sentinel,
    summarizing large outputs and respecting token budgets.
    Returns the final refined thought or reflection.
    """
    # -- Reflection budget handling --
    MAX_REFLECTION_TOKENS = getattr(config, 'max_reflection_tokens', 500)
    output_tokens = count_tokens(output)
    if output_tokens > MAX_REFLECTION_TOKENS:
        logger.info(f"SelfReflection: summarizing output of {output_tokens} tokens (threshold {MAX_REFLECTION_TOKENS})")
        summarizer = ConversationSummarizer(config)
        try:
            summary = summarizer.generate_summary([{'role': 'assistant', 'content': output}])
            output = summary
        except Exception as e:
            logger.error(f"SelfReflection: summarization failed: {e}", exc_info=True)

    # -- Build reflection prompt --
    from app.utils.prompt_builder import build_prompt
    messages = build_prompt(
        config=config,
        persona_instructions="You are a self-reflection and refinement expert.",
        session_id=context.get('session_id'),
        history=[],
        user_input=output,
        task_instruction="refinement"
    )
    prompt = messages[0]['content']

    final_thought = None
    iterations = getattr(config, 'max_reflection_iterations', 3)
    threshold = getattr(config, 'reflection_threshold', 0.9)
    max_tokens = getattr(config, 'reflection_max_tokens', 256)

    for i in range(iterations):
        t_iter_start = time.perf_counter()
        try:
            raw = llm.create_chat_completion(
                messages=[{"role": "system", "content": prompt}],
                max_tokens=max_tokens,
                temperature=getattr(config, 'reflection_temperature', 0.3)
            )
        except Exception as e:
            logger.error(f"SelfReflection: iteration {i+1} LLM call failed: {e}", exc_info=True)
            break
        t_iter_end = time.perf_counter()
        logger.info(f"SelfReflection: iteration {i+1} LLM call took {t_iter_end - t_iter_start:.2f}s")

        # Extract text
        text = None
        if isinstance(raw, dict):
            choices = raw.get("choices", [])
            if choices and isinstance(choices[0], dict):
                text = choices[0].get("text") or choices[0].get("message", {}).get("content") or ""
        if not isinstance(text, str):
            try:
                text = json.dumps(raw)
            except Exception:
                text = str(raw)
        text = text.strip()
        logger.info(f"SelfReflection: iteration {i+1} raw response: {text}")

        # Parse confidence inline
        text_lower = text.lower()
        score = 0.0
        # Look for explicit numeric confidence between 0 and 1
        m = re.search(r"^Confidence:\s*(0(?:\.\d+)?|1(?:\.0+)?)", text, re.MULTILINE)
        if m:
            score = float(m.group(1))
        else:
            # Fallback: keyword-based inference
            if any(k in text_lower for k in ['safe', 'high-quality', 'no issues', 'passed']):
                score = 1.0
            elif any(k in text_lower for k in ['unsafe', 'errors', 'hallucinations', 'privacy leaks']):
                score = 0.0
        logger.info(f"SelfReflection: iteration {i+1} confidence {score}")

        # Log sketchpad
        try:
            sketch(f"Reflection {i+1}", text)
        except Exception as e:
            logger.error(f"SelfReflection: iteration {i+1} sketch failed: {e}", exc_info=True)

        if score >= threshold:
            logger.info("SelfReflection: confidence threshold reached, exiting loop")
            final_thought = text
            break
    else:
        # Loop exhausted without hitting threshold
        final_thought = text if 'text' in locals() else ''

    logger.info(f"SelfReflection: completed {i+1 if final_thought else iterations} iterations")

    # -- Final safety check --
    try:
        safe = ethical_sentinel.run_full_safety_check(
            persona_traits=context.get('persona_traits', {}),
            instructions=instructions,
            prompt=final_thought
        )
        if safe:
            logger.info("SelfReflection: passed final safety check")
        else:
            logger.warning("SelfReflection: final safety check failed")
    except Exception as e:
        logger.error(f"SelfReflection: safety check error: {e}", exc_info=True)

    # -- Clean up sketchpad if configured --
    try:
        clear_sketchpad()
    except Exception as e:
        logger.warning(f"SelfReflection: clearing sketchpad failed: {e}", exc_info=True)

    # Ensure final_thought is a string before searching
    if not isinstance(final_thought, str):
        final_thought = ""

    # Extract the refined plan from the PLAN block
    plan_match = re.search(r"PLAN:(.*)", final_thought, re.DOTALL)
    if plan_match:
        return plan_match.group(1).strip()
    else:
        # Fallback to returning the whole thought if PLAN block is missing
        return final_thought



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

    # Summarize large output to stay within reflection budget
    from app.utils.prompt_builder import count_tokens
    MAX_REFLECTION_TOKENS = getattr(config, 'max_reflection_tokens', 500)
    # Measure output token size
    output_tokens = count_tokens(output)
    if output_tokens > MAX_REFLECTION_TOKENS:
        logger.info(f"SelfReflection: summarizing output of {output_tokens} tokens")
        from app.memory.conversation.summarizer import ConversationSummarizer
        summarizer = ConversationSummarizer(config)
        # Wrap output in message format for summarization
        summary = summarizer.generate_summary([{'role': 'assistant', 'content': output}])
        output = summary

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
                    maybe_generate_seed(reflection, context, config, llm=llm)
                except Exception as seed_exc:
                    logger.error(f"Error generating thought seed: {seed_exc}")
        
            maybe_review_seeds(config=config, llm=llm)
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
