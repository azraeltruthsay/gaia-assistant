"""Thin wrappers that add debug logging around llama-cpp calls."""
import logging, time
logger = logging.getLogger("GAIA.LLM")

def safe_generate(llm, *args, **kwargs):
    """Call llm.create_completion with context-size diagnostics."""
    ctx_size = getattr(llm, "n_ctx", getattr(llm, "ctx_size", "?"))
    logger.info("LLM call: ctx_size=%s  max_tokens=%s",
                ctx_size, kwargs.get("max_tokens"))
    start = time.perf_counter()
    try:
        return llm.create_completion(*args, **kwargs)
    finally:
        logger.info("LLM call completed in %.2fs",
                    time.perf_counter() - start)