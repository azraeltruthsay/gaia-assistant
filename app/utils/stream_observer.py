# /home/azrael/Project/gaia-assistant/app/utils/stream_observer.py

import logging
import re

logger = logging.getLogger("GAIA.StreamObserver")


class StreamObserver:
    """
    Streaming Observer for council/cognitive output.
    Employs a tiered checking strategy for efficiency.
    """

    def __init__(self, llm=None, name="observer", interrupt_handler=None):
        self.llm = llm
        self.name = name
        self.buffer = []
        self.active = True
        self.interrupt_handler = interrupt_handler or self.default_interrupt_handler
        self.interrupt_reason = None
        self.llm_check_triggered = False # Ensure LLM check runs only once

    def observe(self, buffer, context):
        """
        Runs the observer logic on the current stream buffer.
        """
        if isinstance(buffer, list):
            buffer = "".join(buffer)

        # --- Tier 1: Fast, rule-based check on every call ---
        if self.fast_check(buffer):
            return "interrupt"

        # --- Tier 2: Slower, LLM-based check on longer buffers ---
        # Only run if the buffer is long enough AND it hasn't run before
        if self.llm and len(buffer) > 250 and not self.llm_check_triggered:
            if self.slow_check(buffer, context):
                return "interrupt"

        return "continue"

    def fast_check(self, buffer: str) -> bool:
        """
        Performs fast, rule-based checks for obvious errors.
        Returns True if an interruption is needed.
        """
        buffer_lower = buffer.lower()
        # Simple check for common error keywords
        if "error" in buffer_lower or "exception" in buffer_lower:
            self.interrupt_reason = "Potential error detected in output."
            self.interrupt_handler(self.interrupt_reason)
            return True
        return False

    def slow_check(self, buffer: str, context: dict) -> bool:
        """
        Performs a more expensive LLM-based check for subtle issues.
        Returns True if an interruption is needed.
        """
        self.llm_check_triggered = True # Mark that this check has now run
        from app.cognition.external_voice import suppress_llama_stderr
        from app.config import constants

        # Use a simple slice instead of expensive summarization
        buffer_to_send = buffer[:500]

        # The prompt is now driven by the config, making it more modular
        observer_instruction = constants.get('TASK_INSTRUCTIONS', {}).get("observer", "")
        prompt = f"{observer_instruction}\n\nResponse to review:\n---\n{buffer_to_send}\n---"

        logger.info(f"StreamObserver ({self.name}): Performing LLM check.")
        try:
            with suppress_llama_stderr():
                result = self.llm.create_completion(prompt=prompt, max_tokens=64, temperature=0.1)

            text = result["choices"][0]["text"].strip().upper()
            if text.startswith("INTERRUPT"):
                self.interrupt_reason = text.split(":", 1)[-1].strip()
                self.interrupt_handler(self.interrupt_reason)
                return True
        except Exception as e:
            logger.error(f"StreamObserver ({self.name}) LLM check failed: {e}")

        return False

    def default_interrupt_handler(self, reason: str):
        """Default handler to print the interruption reason."""
        print(f"\n🔔 Observer Interrupt: {reason}")
