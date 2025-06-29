# /home/azrael/Project/gaia-assistant/app/cognition/agent_core.py

import logging
import re
from app.cognition.external_voice import ExternalVoice, log_chat_entry
from app.utils.stream_observer import StreamObserver
from app.cognition.self_reflection import run_self_reflection

logger = logging.getLogger("GAIA.AgentCore")


class AgentCore:
    """
    Encapsulates the core "Reason-Act-Reflect" loop for GAIA.
    This class is UI-agnostic and yields structured events back to the caller.
    """

    def __init__(self, ai_manager):
        self.ai_manager = ai_manager
        self.model_pool = ai_manager.config.model_pool
        self.config = ai_manager.config

    def _execute_actions(self, response: str):
        """
        Parses a response for EXECUTE blocks, reflects, and yields events for each action.
        This is a generator function.
        """
        commands_to_run = re.findall(r"EXECUTE:\s*(ai\..+)", response)
        if not commands_to_run:
            return

        yield {"type": "action_start"}
        for command in commands_to_run:
            command = command.strip()

            # 1. Yield event for reflection
            yield {"type": "action_reflect", "command": command}

            # 2. Perform the reflection
            last_user_message = ""
            if self.ai_manager.conversation_manager.history:
                for msg in reversed(self.ai_manager.conversation_manager.history):
                    if msg.get("role") == "user":
                        last_user_message = msg.get("content", "")
                        break

            reflection_context = {
                "user_input": last_user_message,
                "proposed_action": command
            }
            reflection_llm = self.ai_manager.lite_llm or self.ai_manager.llm
            reflection = run_self_reflection(
                context=reflection_context,
                output=command,
                config=self.config,
                llm=reflection_llm
            )

            # 3. Check reflection and yield appropriate event
            if reflection and any(
                    key in reflection.lower() for key in ["issue", "unsafe", "error", "warning", "do not", "block"]):
                yield {"type": "action_blocked", "command": command, "reason": reflection}
                continue

            # 4. If reflection passes, yield execution events
            try:
                yield {"type": "action_executing", "command": command}
                eval(command, {"ai": self.ai_manager})
                yield {"type": "action_success", "command": command}
            except Exception as e:
                logger.error(f"Action failed: {command}\n   Error: {e}", exc_info=True)
                yield {"type": "action_failure", "command": command, "error": str(e)}

        yield {"type": "action_end"}

    def run_turn(self, user_input: str):
        """
        Runs a single turn of the agent loop. This is a generator that yields structured events.
        """
        full_response = ""
        prime_model = self.model_pool.get("prime")
        lite_model = self.model_pool.get("lite")

        self.ai_manager.conversation_manager.add_message("user", user_input)
        smart_history = self.ai_manager.conversation_manager.build_smart_history(
            current_input=user_input, max_recent=3, max_salient=2
        )
        chat_context = {"history": smart_history}

        observer = StreamObserver(llm=lite_model, name="AgentCore-Observer") if lite_model else None

        voice = ExternalVoice(
            model=prime_model,
            model_pool=self.model_pool,
            config=self.config,
            thought=user_input,
            source="agent_core",
            observer=observer,
            context=chat_context
        )

        stream_generator = voice.stream_response(user_input)
        for token_or_event in stream_generator:
            if isinstance(token_or_event, dict) and token_or_event.get("event") == "interruption":
                reason = token_or_event.get("data", "Interrupted by observer.")
                yield {"type": "interruption_start", "reason": reason}

                correction_thought = f"""My initial response was interrupted for the reason: '{reason}'.
The user's original request was: '{user_input}'.
My incomplete response was: '{full_response}'.
Please generate a new, corrected, and complete response that addresses the user's request while fixing the issue."""

                correction_voice = ExternalVoice(
                    model=prime_model, model_pool=self.model_pool, config=self.config,
                    thought=correction_thought, source="agent_core_correction", observer=None, context=chat_context
                )

                yield {"type": "correction_start"}
                corrected_response_text = ""
                for token in correction_voice.stream_response(correction_thought):
                    yield {"type": "token", "value": str(token)}
                    corrected_response_text += str(token)

                full_response = corrected_response_text
                yield {"type": "correction_end"}
                break
            else:
                token = str(token_or_event)
                yield {"type": "token", "value": token}
                full_response += token

        self.ai_manager.status["last_response"] = full_response
        self.ai_manager.conversation_manager.add_message("assistant", full_response)
        log_chat_entry(user_input, full_response)

        if full_response:
            yield from self._execute_actions(full_response)