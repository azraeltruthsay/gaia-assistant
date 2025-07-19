"""
external_voice.py — handles all inbound/outbound chat traffic for GAIA
(streaming, observer hooks, basic logging).  This module is the *sole*
entry and exit for chat-based interactions.
"""
from __future__ import annotations

import contextlib
import json
import logging
import os
import queue
import sys
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

from app.config import Config
from app.utils.prompt_builder import build_prompt
from app.utils.stream_observer import StreamObserver

logger = logging.getLogger("GAIA.ExternalVoice")

cfg = Config()
LLAMA_LOG_PATH = os.path.join(cfg.LOGS_DIR, "llama_cpp.log")
CHAT_LOG_PATH = os.path.join(cfg.LOGS_DIR, "chat_session.log")
os.makedirs(cfg.LOGS_DIR, exist_ok=True)


# --------------------------------------------------------------------------- #
# stderr suppression helper (llama.cpp progress bars)
# --------------------------------------------------------------------------- #
@contextlib.contextmanager
def suppress_llama_stderr() -> None:
    """
    Temporarily redirect C-level stderr (llama.cpp progress bars) to a file so
    they don't pollute the interactive CLI.
    """
    original_fd = sys.stderr.fileno()
    saved_fd = os.dup(original_fd)
    try:
        with open(LLAMA_LOG_PATH, "a", encoding="utf-8") as fh:
            os.dup2(fh.fileno(), original_fd)
            yield
    finally:
        os.dup2(saved_fd, original_fd)
        os.close(saved_fd)


# --------------------------------------------------------------------------- #
# ExternalVoice
# --------------------------------------------------------------------------- #
class ExternalVoice:
    def __init__(
        self,
        model,
        model_pool,
        config: Config,
        thought: Optional[str] = None,
        messages: Optional[List[Dict]] = None,
        context: Optional[Dict] = None,
        session_id: str = "shell",
        source: str = "web",
        observer: Optional[StreamObserver] = None,
    ) -> None:
        self.model = model
        self.model_pool = model_pool
        self.config = config
        self.thought = thought
        self.messages = messages
        self.context = context or {}
        self.session_id = session_id
        self.source = source
        self.observer = observer

        self.logical_stop_punct = self.config.LOGICAL_STOP_PUNCTUATION
        self.observer_threshold = self.config.OBSERVER_TOKEN_THRESHOLD

    # --------------------------------------------------------------------- #
    # streaming
    # --------------------------------------------------------------------- #
    def stream_response(self, user_input: Optional[str] = None):
        """Generator that yields tokens (or events) from the LLM stream."""
        if user_input:
            self.thought = user_input

        active_persona = self.model_pool.get_active_persona()

        # ---- Build persona instructions block safely -------------------- #
        persona_instructions = ""
        if active_persona:
            tmpl = getattr(active_persona, "template", "")
            instr = getattr(active_persona, "instructions", [])
            if isinstance(instr, list):
                instr_block = "\n".join(instr)
            else:  # already a str
                instr_block = str(instr)
            persona_instructions = f"{tmpl}\n\n{instr_block}".strip()

        prompt_context = {
            "config": self.config,
            "persona_instructions": persona_instructions,
            "session_id": self.session_id,
            "history": self.context.get("history", []),
            "user_input": self.thought,
        }

        self.messages = build_prompt(context=prompt_context)

        # ---- Direct model stream (no worker thread) -------------------- #
        logger.info("ExternalVoice: starting create_chat_completion stream directly")
        t_start = time.perf_counter()
        try:
            token_stream = self.model.create_chat_completion(
                messages=self.messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                stream=True,
            )
            t_end = time.perf_counter()
            logger.info(f"ExternalVoice: create_chat_completion stream took {t_end - t_start:.2f}s")

            buffer: List[str] = []
            since_check = 0

            for item in token_stream:
                if self.observer and self.observer.interrupted:
                    reason = getattr(self.observer, "interrupt_reason", "observer interrupt")
                    logger.info(f"ExternalVoice: interruption detected from observer: {reason}")
                    yield {"event": "interruption", "data": reason}
                    break

                token = item["choices"][0]["delta"].get("content", "")
                if not token:
                    continue

                buffer.append(token)
                yield token

                since_check += 1
                need_check = (
                    since_check >= self.observer_threshold
                    or any(p in token for p in self.logical_stop_punct)
                )

                if self.observer and need_check:
                    current = "".join(buffer)
                    logger.debug("ExternalVoice: invoking observer.observe")
                    t_obs_start = time.perf_counter()
                    decision = self.observer.observe(current, prompt_context)
                    t_obs_end = time.perf_counter()
                    logger.info(f"ExternalVoice: observer.observe took {t_obs_end - t_obs_start:.2f}s")
                    since_check = 0
                    if decision == "interrupt":
                        reason = getattr(self.observer, "interrupt_reason", "observer interrupt")
                        logger.info(f"ExternalVoice: interruption triggered immediately: {reason}")
                        yield {"event": "interruption", "data": reason}
                        break
        except Exception as e:
            logger.error(f"Error during model stream: {e}", exc_info=True)
            raise

    # --------------------------------------------------------------------- #
    # convenience helpers
    # --------------------------------------------------------------------- #
    def generate_full_response(self, user_input: Optional[str] = None) -> str:
        chunks: List[str] = []
        for item in self.stream_response(user_input):
            if isinstance(item, dict) and item.get("event") == "interruption":
                chunks.append(f"\n\n--- {item['data']} ---")
                break
            chunks.append(str(item))
        return "".join(chunks)

    @classmethod
    def from_thought(cls, model, thought: str, **kw):
        return cls(model=model, thought=thought, **kw)

    @classmethod
    def from_messages(cls, model, messages: List[Dict], **kw):
        return cls(model=model, messages=messages, **kw)

    @classmethod
    def one_shot(cls, model, prompt: str, **kw) -> str:
        """Non-streamed convenience wrapper."""
        messages = build_prompt(context={"user_input": prompt})
        with suppress_llama_stderr():
            res = model.create_chat_completion(
                messages=messages,
                max_tokens=kw.get("max_tokens", 52),
                temperature=kw.get("temperature", 0.7),
                top_p=kw.get("top_p", 0.95),
            )
        return res["choices"][0]["message"]["content"]
