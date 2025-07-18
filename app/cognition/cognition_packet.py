"""
CognitionPacket – dynamic state for GAIA’s self-reflection loop.

Schema:
  prompt:         str            # original user prompt
  persona:        str            # active persona ID
  identity:       dict           # core identity fields
  instructions:   List[str]      # system prompts
  history:        List[dict]     # recent chat messages

  reflection_count: int           # increments each iteration
  thoughts:         List[dict]    # chain-of-thought entries
  scratch:         Dict[str, Any] # dynamic slots: dataA...dataE
  user_approval:    bool          # flag for shell cmd approval
"""

from __future__ import annotations
from typing import Any, Dict, List
import json

class CognitionPacket:
    def __init__(self,
                 prompt: str,
                 persona: str,
                 identity: Dict[str, Any],
                 instructions: List[str],
                 history: List[Dict[str, Any]]):
        # Fixed fields
        self.prompt = prompt
        self.persona = persona
        self.identity = identity
        self.instructions = instructions
        self.history = history

        # Reflection state
        self.reflection_count = 0
        self.thoughts: List[Dict[str, Any]] = []

        # Scratch slots
        self.scratch: Dict[str, Any] = { f"data{c}": None for c in "ABCDE" }

        # User approval for shell commands (default: no)
        self.user_approval = False

        # Final output flag
        self._finalized = False

    def to_json(self) -> str:
        """Serialize packet to JSON for the LLM prompt."""
        return json.dumps({
            "prompt": self.prompt,
            "persona": self.persona,
            "identity": self.identity,
            "instructions": self.instructions,
            "history": self.history,
            "reflection_count": self.reflection_count,
            "thoughts": self.thoughts,
            "scratch": self.scratch,
            "user_approval": self.user_approval,
        }, indent=2)

    def append_thought(self, text: str, confidence: float | None = None) -> None:
        """Add a new thought to the chain-of-thought."""
        self.reflection_count += 1
        entry = {"step": self.reflection_count, "text": text}
        if confidence is not None:
            entry["confidence"] = confidence
        self.thoughts.append(entry)

    def request_scratch(self, slot: str, value: Any) -> None:
        """Populate a scratch slot (e.g. 'dataA')."""
        if slot in self.scratch:
            self.scratch[slot] = value

    def has_shell_action(self) -> bool:
        """Detect if the last thought or plan contains a shell action."""
        # Implementation detail: scan last thought text for 'EXECUTE:'
        if not self.thoughts:
            return False
        return "EXECUTE:" in self.thoughts[-1]["text"]

    def get_shell_action(self) -> str | None:
        """Extract the shell command from the last thought (if any)."""
        text = self.thoughts[-1]["text"]
        # naive parse: after 'EXECUTE: ' until end of line
        if "EXECUTE:" in text:
            return text.split("EXECUTE:",1)[1].strip()
        return None

    def mark_final(self) -> None:
        """Flag the packet as finalized; loop should exit."""
        self._finalized = True

    def is_finalized(self) -> bool:
        return self._finalized