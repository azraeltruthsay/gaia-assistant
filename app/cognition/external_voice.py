"""
external_voice.py -- Handles all inbound and outbound external communication for GAIA,
including chat input, output, streaming, observer notifications, and session logging.
This module is the *sole* entry and exit for all chat-based interactions with GAIA.
"""
# /home/azrael/Project/gaia-assistant/app/cognition/external_voice.py

import os
import sys
import logging
import contextlib
import json
import queue
import threading
from datetime import datetime
from app.utils.prompt_builder import build_prompt
from app.cognition import inner_monologue
from app.utils.stream_observer import StreamObserver

logger = logging.getLogger("GAIA.ExternalVoice")

llama_log_path = "/gaia-assistant/logs/llama_cpp.log"
chat_log_path = "/gaia-assistant/logs/chat_session.log"
os.makedirs(os.path.dirname(llama_log_path), exist_ok=True)
os.makedirs(os.path.dirname(chat_log_path), exist_ok=True)


@contextlib.contextmanager
def suppress_llama_stderr():
    """
    A context manager to temporarily redirect C-level stderr to a log file.
    This is necessary to capture the progress bars from llama.cpp, which are
    printed to stderr, without affecting the main application's stdout.
    """
    original_stderr_fd = sys.stderr.fileno()
    saved_stderr_fd = os.dup(original_stderr_fd)

    try:
        # Open the log file and redirect stderr to it
        with open(llama_log_path, 'a', encoding='utf-8') as log_file:
            os.dup2(log_file.fileno(), original_stderr_fd)
            yield
    finally:
        # Restore original stderr and close the saved descriptor
        os.dup2(saved_stderr_fd, original_stderr_fd)
        os.close(saved_stderr_fd)


def log_chat_entry(user_input: str, assistant_output: str):
    """Appends a full user/assistant turn to the session log."""
    timestamp = datetime.now().isoformat()
    with open(chat_log_path, 'a', encoding='utf-8') as log:
        log.write(f"[{timestamp}]\nUser > {user_input}\nGAIA > {assistant_output}\n\n")


class ExternalVoice:
    def __init__(
            self,
            model,
            model_pool,
            config,
            thought: str = None,
            messages: list = None,
            context: dict = None,
            source: str = "web",
            observer: StreamObserver = None
    ):
        self.model = model
        self.model_pool = model_pool
        self.config = config
        self.thought = thought
        self.messages = messages
        self.context = context or {}
        self.source = source
        self.observer = observer
        self.logical_stop_punctuation = self.config.LOGICAL_STOP_PUNCTUATION
        self.observer_token_threshold = self.config.OBSERVER_TOKEN_THRESHOLD

    def stream_response(self, user_input: str = None):
        """
        A generator that yields tokens from the LLM response stream.
        This version uses a worker thread to isolate the noisy C++ library output,
        ensuring the main thread's stdout is not suppressed.
        """
        if user_input:
            self.thought = user_input

        active_persona = self.model_pool.get_active_persona()

        prompt_context = {
            "user_input": self.thought,
            "history": self.context.get("history", [])
        }
        if active_persona:
            prompt_context.update({
                "persona": active_persona.name,
                "instructions": active_persona.instructions,
                "persona_template": active_persona.template,
                "persona_traits": active_persona.traits,
            })

        self.messages = build_prompt(context=prompt_context)

        q = queue.Queue()

        def worker():
            """This function runs in a separate thread."""
            try:
                # The model call and iteration happen here, inside the suppressed context.
                with suppress_llama_stderr():
                    token_stream = self.model.create_chat_completion(
                        messages=self.messages,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                        top_p=self.config.top_p,
                        stream=True,
                    )
                    for chunk in token_stream:
                        q.put(chunk)
            except Exception as e:
                q.put(e)
            finally:
                q.put(None)

        thread = threading.Thread(target=worker)
        thread.start()

        full_response_buffer = []
        token_count_since_last_check = 0

        while True:
            item = q.get()
            if item is None:
                break
            if isinstance(item, Exception):
                raise item

            chunk = item
            token_str = chunk["choices"][0]["delta"].get("content", "")
            if not token_str:
                continue

            full_response_buffer.append(token_str)
            yield token_str

            token_count_since_last_check += 1
            perform_observer_check = token_count_since_last_check >= self.observer_token_threshold or \
                                     any(p in token_str for p in self.logical_stop_punctuation)

            if self.observer and perform_observer_check:
                current_output = "".join(full_response_buffer)
                decision = self.observer.observe(current_output, prompt_context)
                token_count_since_last_check = 0

                if decision == "interrupt":
                    reason = getattr(self.observer, 'interrupt_reason', "Interrupted by observer.")
                    logger.info(f"Stream interrupted by observer. Reason: {reason}")
                    yield {"event": "interruption", "data": reason}
                    break

        thread.join()

    def generate_full_response(self, user_input: str = None) -> str:
        """Generates the full model response by consuming the stream_response generator."""
        output_chunks = []
        for chunk in self.stream_response(user_input):
            if isinstance(chunk, dict) and chunk.get("event") == "interruption":
                output_chunks.append(f"\n\n--- {chunk['data']} ---")
                break
            output_chunks.append(str(chunk))
        return "".join(output_chunks)

    @classmethod
    def from_thought(cls, model, thought: str, **kwargs):
        return cls(model=model, thought=thought, **kwargs)

    @classmethod
    def from_messages(cls, model, messages: list, **kwargs):
        return cls(model=model, messages=messages, **kwargs)

    @classmethod
    def one_shot(cls, model, prompt: str, **kwargs) -> str:
        """Generates a single, non-streamed response."""
        messages = build_prompt(context={"user_input": prompt})
        with suppress_llama_stderr():
            result = model.create_chat_completion(
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 512),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.95),
            )
        return result["choices"][0]["message"]["content"]