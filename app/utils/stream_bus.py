"""
Stream Bus Utility (council/cognitive ready)
- Streams LLM responses chunk-by-chunk (token, sub-token, or fixed char/window)
- Accepts an observer_fn callback for live interruption/interjection (e.g., Lite model or council observer)
- Easy to extend for streaming to UI, logs, or multi-model monitoring
"""

import logging

logger = logging.getLogger("GAIA.StreamBus")

def publish_stream(
    response_iterable,
    output_fn,
    observer_fn=None,
    chunk_size=8,
    flush_every=1
):
    """
    Streams tokens/chunks from a model response iterator, with observer hooks.
    Params:
        response_iterable: iterable (string, generator, or LLM stream) of output tokens/chunks
        output_fn: function to call with each output chunk (e.g., print or web UI update)
        observer_fn: callback(buffer, context) -> "continue" or "interrupt" (optional)
        chunk_size: number of characters per emitted chunk (if input is a string)
        flush_every: flush output every N chunks (for UI/log responsiveness)
    Returns:
        The full streamed response as a string.
    """
    buffer = []
    full_response = ""
    chunk_buffer = ""

    if isinstance(response_iterable, str):
        # Convert string to chunked stream
        def chunker(text, n):
            for i in range(0, len(text), n):
                yield text[i:i + n]
        response_iterable = chunker(response_iterable, chunk_size)

    for i, chunk in enumerate(response_iterable):
        if not chunk:
            continue
        chunk_buffer += chunk
        full_response += chunk
        if (i + 1) % flush_every == 0 or "\n" in chunk:
            output_fn(chunk_buffer, end="", flush=True)
            buffer.append(chunk_buffer)
            chunk_buffer = ""
            # Observer check (for interruption/interjection)
            if observer_fn is not None:
                decision = observer_fn("".join(buffer))
                if decision == "interrupt":
                    output_fn("\n[⛔ Interrupted by observer]\n")
                    logger.warning("⛔ Streaming interrupted by observer.")
                    break
    # Flush any remaining buffer
    if chunk_buffer:
        output_fn(chunk_buffer, end="", flush=True)
        full_response += chunk_buffer

    logger.info("✅ Stream completed.")
    return full_response

_output_listeners = []

def add_output_listener(fn):
    _output_listeners.append(fn)

def publish_stream(token, **kwargs):
    for fn in _output_listeners:
        fn(token, **kwargs)
