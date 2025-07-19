# /home/azrael/Project/gaia-assistant/app/utils/stream_observer.py

import logging
import re
import threading

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
        self.llm_check_triggered = False
        self.interrupted = False
        self._lock = threading.Lock()

    def observe(self, buffer, context):
        """
        Runs the observer logic on the current stream buffer.
        """
        if self.interrupted:
            return "interrupt"

        if isinstance(buffer, list):
            buffer = "".join(buffer)

        # --- Tier 1: Fast, rule-based check on every call ---
        if self.fast_check(buffer):
            self.interrupted = True
            return "interrupt"

        # --- Tier 2: Slower, LLM-based check ---
        if self.llm and len(buffer) > 250 and not self.llm_check_triggered:
            self.llm_check_triggered = True
            self._threaded_slow_check(buffer, context)

        return "continue"

    def fast_check(self, buffer: str) -> bool:
        """
        Performs fast, rule-based checks for obvious errors.
        Returns True if an interruption is needed.
        """
        buffer_lower = buffer.lower()
        if "error" in buffer_lower or "exception" in buffer_lower:
            self.interrupt_reason = "Potential error detected in output."
            self.interrupt_handler(self.interrupt_reason)
            return True
        return False

    def _threaded_slow_check(self, buffer: str, context: dict):
        """
        Performs the expensive LLM check in a separate thread.
        """
        from app.cognition.external_voice import suppress_llama_stderr
        from app.config import constants

        buffer_to_send = buffer[:500]
        user_input = context.get("user_input", "")
        observer_instruction = constants.get('TASK_INSTRUCTIONS', {}).get("observer", "")
        prompt = f"{observer_instruction}\n\nUser's Request: {user_input}\n\nResponse to review:\n---\n{buffer_to_send}\n---"

        logger.info(f"StreamObserver ({self.name}): Performing non-blocking LLM check.")
        try:
            with suppress_llama_stderr():
                result = self.llm.create_completion(prompt=prompt, max_tokens=64, temperature=0.1)

            text = result["choices"][0]["text"].strip().upper()
            if text.startswith("INTERRUPT"):
                with self._lock:
                    self.interrupt_reason = text.split(":", 1)[-1].strip()
                    self.interrupted = True
                    self.interrupt_handler(self.interrupt_reason)
        except Exception as e:
            logger.error(f"StreamObserver ({self.name}) LLM check failed: {e}")

    def default_interrupt_handler(self, reason: str):
        """Default handler to print the interruption reason."""
        print(f"\n🔔 Observer Interrupt: {reason}")

