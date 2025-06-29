import logging
from app.utils.prompt_builder import build_prompt
from app.config import Config
from app.behavior.persona_adapter import PersonaAdapter
from app.cognition.thought_seed import maybe_generate_seed

logger = logging.getLogger("GAIA.InnerMonologue")


def _prepare_context_for_prompt_builder(initial_context: dict, config: Config, current_input: str, task_type: str):
    """Helper to ensure the context dictionary is fully populated for build_prompt."""
    context = initial_context if initial_context is not None else {}

    # Ensure essential elements are present, prioritizing existing context values
    context["user_input"] = current_input
    context["task_type"] = task_type

    if config:
        context["identity"] = context.get("identity", config.identity)
        context["identity_intro"] = context.get("identity_intro", config.identity_intro)
        context["primitives"] = context.get("primitives", config.primitives)
        context["reflection_guidelines"] = context.get("reflection_guidelines", config.reflection_guidelines)

        # This part relies on model_pool being attached to config
        if hasattr(config, 'model_pool') and config.model_pool and config.model_pool.get_active_persona():
            active_persona_obj = config.model_pool.get_active_persona()
            context["persona"] = context.get("persona", active_persona_obj.name)
            context["instructions"] = context.get("instructions", active_persona_obj.instructions)
            context["persona_template"] = context.get("persona_template", active_persona_obj.template)
            context["persona_traits"] = context.get("persona_traits", active_persona_obj.traits)
        else: # Fallback if model_pool or active persona not ready
            context["persona"] = context.get("persona", config.persona_name)
            context["instructions"] = context.get("instructions", config.get_persona_instructions())

    return context


def process_thought_stream(thought, model, config=None, source="unknown", interrupt_check=None, stream_callback=None,
                           context=None):
    """
    Model-powered streaming thought pipeline.
    Streams tokens from model and invokes callbacks/interruption.
    """
    if not model:
        logger.error("No LLM model provided for process_thought_stream.")
        return iter([])

    if config is None:
        config = Config()

    full_context = _prepare_context_for_prompt_builder(context, config, thought, "chat")

    messages = build_prompt(
        context=full_context,
    )

    temperature = config.temperature
    max_tokens = config.max_tokens
    top_p = config.top_p

    if hasattr(model, "reset"):
        try:
            model.reset()
        except Exception as e:
            logger.warning(f"Model reset failed: {e}")

    stream = model.create_chat_completion(
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        stream=True
    )
    full_response = ""
    for output in stream:
        token = output.get("choices", [{}])[0].get("delta", {}).get("content", "")
        if not token:
            continue
        full_response += token
        if interrupt_check and interrupt_check():
            logger.warning("🔴 Stream interrupted by check condition.")
            break
        if stream_callback:
            stream_callback(token)

    # --- MODIFIED: Prevent recursive thought seed generation ---
    if full_context.get("task_type") != "thought_seed":
        try:
            seed_context = {
                "user_input": thought,
                "gaia_response": full_response,
                "persona_name": full_context.get("persona", "unknown"),
                "source": source
            }
            maybe_generate_seed(thought, seed_context, config, llm=model)
        except Exception as e:
            logger.error(f"❌ Error attempting to generate thought seed in stream: {e}", exc_info=True)
    # --- END MODIFIED ---

    return full_response


def process_thought(task_type, persona, instructions, payload, llm, config, context=None, identity_intro="",
                    reflect=True):
    """
    Non-streaming, model-powered pipeline for generating monologue or pipeline thoughts.
    """
    logger.info(f"🧠 Generating {task_type} response... (reflect={reflect})")

    if config is None:
        config = Config()

    initial_context_from_args = {
        "persona": persona,
        "instructions": instructions,
        "identity_intro": identity_intro,
        "reflect": reflect
    }
    if context:
        initial_context_from_args.update(context)

    full_context = _prepare_context_for_prompt_builder(initial_context_from_args, config, payload, task_type)

    messages = build_prompt(
        context=full_context,
        add_history=False,
        add_monologue=False
    )

    if hasattr(llm, "reset"):
        try:
            llm.reset()
        except Exception as e:
            logger.warning(f"LLM context reset failed or unsupported: {e}")

    temperature = config.temperature
    max_tokens = config.max_tokens
    top_p = config.top_p

    completion = llm.create_chat_completion(
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        stream=False
    )

    output = completion["choices"][0]["message"]["content"].strip()

    # --- MODIFIED: Prevent recursive thought seed generation ---
    if task_type != "thought_seed":
        try:
            seed_context = {
                "user_input": payload,
                "gaia_response": output,
                "persona_name": full_context.get("persona", "unknown"),
                "source": task_type
            }
            maybe_generate_seed(payload, seed_context, config, llm=llm)
        except Exception as e:
            logger.error(f"❌ Error attempting to generate thought seed in process_thought: {e}", exc_info=True)
    # --- END MODIFIED ---

    logger.info(f"✅ Monologue/thought generated: {len(output)} chars")
    return output


def quick_thought(prompt, config, llm, persona="gaia-lite"):
    """
    Ultra-fast, minimal context, Lite-model response pipeline.
    """
    logger.info("⚡ Entering quick_thought() mode")

    if config is None:
        config = Config()

    initial_context = {
        "persona": persona,
        "instructions": "Respond concisely using minimal context. Avoid excessive explanation.",
        "identity_intro": getattr(config, "identity_intro_lite", config.identity_intro),
        "reflect": False
    }
    full_context = _prepare_context_for_prompt_builder(initial_context, config, prompt, "quick")

    return process_thought(
        task_type="quick",
        persona=full_context["persona"],
        instructions=full_context["instructions"],
        payload=prompt,
        identity_intro=full_context["identity_intro"],
        reflect=False,
        context=full_context,
        llm=llm,
        config=config
    )


def generate_response(
        user_input,
        config,
        llm,
        stream_output=False,
        log_tokens=False,
        interrupt_check=None,
        lite_llm=None,
        model_selector=None,
        stream_callback=None,
        **kwargs
):
    """
    Main entrypoint for manager pipeline: routes to streaming or non-streaming, supports model selection.
    """
    logger.info("🧠 Generating response via inner monologue pipeline")

    if config is None:
        config = Config()

    initial_context = {
        "identity_intro": kwargs.get("identity_intro") or getattr(config, "identity_intro", ""),
        "persona": getattr(config, "persona_name", "gaia-dev"),
        "task_type": "chat"
    }

    if 'context' in kwargs and isinstance(kwargs['context'], dict):
        initial_context.update(kwargs['context'])

    full_context = _prepare_context_for_prompt_builder(initial_context, config, user_input,
                                                       initial_context["task_type"])

    def default_model_selector(text, config, lite, full):
        if lite and "?" in text and len(text) < 200:
            logger.debug("🧠 Default selector: Routing to Lite LLM")
            return lite
        logger.debug("🧠 Default selector: Routing to Prime LLM")
        return full

    selected_llm = (
        model_selector(user_input, config, lite_llm, llm)
        if model_selector
        else default_model_selector(user_input, config, lite_llm, llm)
    )

    if stream_output:
        output = process_thought_stream(
            thought=user_input,
            model=selected_llm,
            config=config,
            source="chat",
            interrupt_check=interrupt_check,
            stream_callback=stream_callback,
            context=full_context
        )
    else:
        output = process_thought(
            task_type=full_context["task_type"],
            persona=full_context["persona"],
            instructions=full_context["instructions"],
            payload=user_input,
            identity_intro=full_context["identity_intro"],
            reflect=full_context.get("reflect", True),
            context=full_context,
            llm=selected_llm,
            config=config
        )

    return output