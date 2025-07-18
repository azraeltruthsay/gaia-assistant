Below is a comprehensive patch plan you can hand off to Gemini. It does three things:

1. \*\*Adds \*\*\`\` as a new class in `app/cognition/cognition_packet.py`.
2. \*\*Extends \*\*\`\` to accept a `CognitionPacket` and serialize it into the prompt.
3. \*\*Updates \*\*\`\` to drive the reflection loop using `CognitionPacket` and handle `user_approval` for shell actions.

Each diff is line‑numbered relative to the **current** file (use `git pull` to sync first). Inline comments (`#`) explain each change.

---

```diff
*** a/app/cognition/cognition_packet.py (new file)
@@ 0,0 +1,200 @@
+001 """
+002 CognitionPacket – dynamic state for GAIA’s self-reflection loop.
+003
+004 Schema:
+005   prompt:         str            # original user prompt
+006   persona:        str            # active persona ID
+007   identity:       dict           # core identity fields
+008   instructions:   List[str]      # system prompts
+009   history:        List[dict]     # recent chat messages
+010
+011   reflection_count: int           # increments each iteration
+012   thoughts:         List[dict]    # chain-of-thought entries
+013   scratch:         Dict[str, Any] # dynamic slots: dataA...dataE
+014   user_approval:    bool          # flag for shell cmd approval
+015"""
+016
+017 from __future__ import annotations
+018 from typing import Any, Dict, List
+019 import json
+
+020 class CognitionPacket:
+021     def __init__(self,
+022                  prompt: str,
+023                  persona: str,
+024                  identity: Dict[str, Any],
+025                  instructions: List[str],
+026                  history: List[Dict[str, Any]]):
+027         # Fixed fields
+028         self.prompt = prompt
+029         self.persona = persona
+030         self.identity = identity
+031         self.instructions = instructions
+032         self.history = history
+
+033         # Reflection state
+034         self.reflection_count = 0
+035         self.thoughts: List[Dict[str, Any]] = []
+
+036         # Scratch slots
+037         self.scratch: Dict[str, Any] = { f"data{c}": None for c in "ABCDE" }
+
+038         # User approval for shell commands (default: no)
+039         self.user_approval = False
+
+040         # Final output flag
+041         self._finalized = False
+
+042     def to_json(self) -> str:
+043         """Serialize packet to JSON for the LLM prompt."""
+044         return json.dumps({
+045             "prompt": self.prompt,
+046             "persona": self.persona,
+047             "identity": self.identity,
+048             "instructions": self.instructions,
+049             "history": self.history,
+050             "reflection_count": self.reflection_count,
+051             "thoughts": self.thoughts,
+052             "scratch": self.scratch,
+053             "user_approval": self.user_approval,
+054         }, indent=2)
+
+055     def append_thought(self, text: str, confidence: float | None = None) -> None:
+056         """Add a new thought to the chain-of-thought."""
+057         self.reflection_count += 1
+058         entry = {"step": self.reflection_count, "text": text}
+059         if confidence is not None:
+060             entry["confidence"] = confidence
+061         self.thoughts.append(entry)
+
+062     def request_scratch(self, slot: str, value: Any) -> None:
+063         """Populate a scratch slot (e.g. 'dataA')."""
+064         if slot in self.scratch:
+065             self.scratch[slot] = value
+066
+067     def has_shell_action(self) -> bool:
+068         """Detect if the last thought or plan contains a shell action."""
+069         # Implementation detail: scan last thought text for 'EXECUTE:'
+070         if not self.thoughts:
+071             return False
+072         return "EXECUTE:" in self.thoughts[-1]["text"]
+
+073     def get_shell_action(self) -> str | None:
+074         """Extract the shell command from the last thought (if any)."""
+075         text = self.thoughts[-1]["text"]
+076         # naive parse: after 'EXECUTE: ' until end of line
+077         if "EXECUTE:" in text:
+078             return text.split("EXECUTE:",1)[1].strip()
+079         return None
+
+080     def mark_final(self) -> None:
+081         """Flag the packet as finalized; loop should exit."""
+082         self._finalized = True
+
+083     def is_finalized(self) -> bool:
+084         return self._finalized
*** End of new file
```

```diff
*** a/app/cognition/prompt_builder.py
@@ 1,6 **
-import logging
+import logging
 from pathlib import Path
+from app.cognition.cognition_packet import CognitionPacket  # NEW import
```

````diff
*** a/app/cognition/prompt_builder.py
@@
-    def build_system_prompt(self, messages: list[dict]) -> str:
-        # existing logic ...
+    def build_from_packet(self, packet: CognitionPacket) -> str:
+        """
+        Build the full prompt text by combining system templates with the
+        packet JSON. The LLM sees both the human instructions and the packet.
+        """
+        system = self.build_system_prompt([])  # reuse existing template logic
+        packet_json = packet.to_json()
+        return f"{system}\n\nCognition Packet:\n```json\n{packet_json}\n```"
*** End of prompt_builder patch
````

```diff
*** a/app/cognition/agent_core.py
@@ def run_turn(self, prompt: str, session_id: str) -> Generator:
-        # existing: build messages, call LLM, handle EXECUTE tokens...
+        # ----------------------------------------------
+        # NEW: Initialize CognitionPacket for this turn
+        from app.cognition.cognition_packet import CognitionPacket
+        packet = CognitionPacket(
+            prompt=prompt,
+            persona=self.persona,
+            identity=self.identity_guardian.identity,
+            instructions=self.instructions,
+            history=self.session_manager.get_history(session_id)
+        )
+
+        # Reflection loop
+        while not packet.is_finalized():
+            # 1) build prompt from packet
+            prompt_text = self.prompt_builder.build_from_packet(packet)
+            # 2) invoke LLM
+            output = self.external_voice.create_chat_completion(
+                prompt_text, stream=False
+            )
+            # 3) merge output: either thought(s) or populate directives
+            if "<<<POPULATE" in output:
+                # parse slot and primitive, call primitive, update packet
+                slot, prim = parse_populate(output)
+                value = self.invoke_primitive(prim)
+                packet.request_scratch(slot, value)
+                continue  # re-loop
+            else:
+                # treat as new thought
+                packet.append_thought(output)
+
+            # 4) user approval for shell commands
+            if packet.has_shell_action() and not packet.user_approval:
+                cmd = packet.get_shell_action()
+                response = input(f"GAIA proposes shell: {cmd}\nApprove? (y/N): ")
+                packet.user_approval = response.strip().lower() in ("y","yes")
+                if not packet.user_approval:
+                    raise RuntimeError("User denied shell execution")
+
+            # 5) execute any primitives encapsulated in thoughts
+            self._execute_actions(packet)
+
+            # 6) check confidence or finalization condition
+            # (could extract a confidence field from packet.thoughts[-1])
+            packet.mark_final()
+
+        # Once finalized, stream final response back
+        yield from stream_response(packet.thoughts[-1]["text"])
*** End of agent_core patch
```

---

**Hand this plan off to Gemini** (or apply it yourself): it wires in the `CognitionPacket`, gives GAIA a dynamic workspace, and adds the `user_approval` gate for any shell actions. Let me know once it’s in place and I’ll help you test the dev\_matrix PoC end-to-end!
