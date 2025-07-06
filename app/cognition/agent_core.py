import logging
import re
from typing import Generator, Dict, Any

from app.cognition.external_voice import ExternalVoice
from app.cognition.self_reflection import run_self_reflection, reflect_and_refine
# MODIFICATION: Import the new prompt builder and the correct chat logger
from app.utils.prompt_builder import build_prompt
from app.utils.chat_logger import log_chat_entry
from app.utils.stream_observer import StreamObserver
from app.config import Config
from app.utils.thoughtstream import write as ts_write

logger = logging.getLogger("GAIA.AgentCore")


class AgentCore:
    """
    Encapsulates the core "Reason-Act-Reflect" loop for GAIA.
    This class is UI-agnostic and yields structured events back to the caller.
    It is session-aware and uses a prompt builder to manage context.
    """

    def __init__(self, ai_manager, ethical_sentinel=None):
        self.ai_manager = ai_manager
        self.model_pool = ai_manager.model_pool
        self.config = ai_manager.config
        self.ethical_sentinel = ethical_sentinel
        # The AI Manager now provides the persistent SessionManager
        self.session_manager = ai_manager.session_manager

    def _execute_actions(self, response: str, session_id: str) -> Generator[Dict[str, Any], None, None]:
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

            # 1. Get user context for reflection
            last_user_message = ""
            history = self.session_manager.get_history(session_id)
            for msg in reversed(history):
                if msg.get("role") == "user":
                    last_user_message = msg.get("content", "")
                    break

            reflection_context = {
                "user_input": last_user_message,
                "proposed_action": command
            }

            # 2. Reflect and refine the command
            yield {"type": "action_reflect", "command": command}
            refined_command = reflect_and_refine(
                context=reflection_context,
                output=command,
                config=self.config,
                llm=self.ai_manager.lite_llm or self.ai_manager.llm,
                ethical_sentinel=self.ethical_sentinel
            )

            ts_write({"type": "reflection-action", "in": reflection_context, "out": refined_command}, session_id)

            # 3. Check if the command was blocked
            if "[REDACTED]" in refined_command:
                yield {"type": "action_blocked", "command": command, "reason": refined_command}
                continue

            # 4. Execute the refined command
            try:
                yield {"type": "action_executing", "command": refined_command}
                eval(refined_command, {"ai": self.ai_manager})
                yield {"type": "action_success", "command": refined_command}
            except Exception as e:
                logger.error(f"Action failed: {refined_command}\n   Error: {e}", exc_info=True)
                yield {"type": "action_failure", "command": refined_command, "error": str(e)}

        yield {"type": "action_end"}

    def run_turn(self, user_input: str, session_id: str) -> Generator[Dict[str, Any], None, None]:
        """
        Runs a single turn of the agent loop. This is a generator that yields structured events.
        """
        from app.cognition.nlu.intent_service import detect_intent
        full_response = ""
        prime_model = self.model_pool.get("prime")
        lite_model = self.model_pool.get("lite")

        # MODIFICATION: Add the user's message to the persistent session
        self.session_manager.add_message(session_id, "user", user_input)

        # --- Intent Detection -------------------------------------------
        intent_str = detect_intent(               # returns e.g. "ask_question"
            user_input,
            self.config,
            lite_llm=lite_model,
            full_llm=prime_model,
        )
        intent_result = {"intent": intent_str}    # normalise to dict
        ts_write({"type": "intent_detect", **intent_result}, session_id)

        # MODIFICATION: Use the new PromptBuilder to construct a budget-aware, tiered prompt
        persona_instructions = self.ai_manager.active_persona.get_full_instructions()
        history = self.session_manager.get_history(session_id)

        messages = build_prompt(
            config=self.config,
            persona_instructions=persona_instructions,
            session_id=session_id,
            history=history,
            user_input=user_input
        )

        # --- Pre-generation Planning and Reflection ---
        planning_context = {"user_input": user_input, "intent": intent_result.get("intent"), "history_summary": messages[1]["content"]}
        initial_plan_prompt = f"Based on the user's request and the conversation history, create a concise plan to address their needs. The plan should be a short, high-level outline of the steps to take. User Request: {user_input}"
        
        # Generate the initial plan
        initial_plan = self.ai_manager.llm.create_chat_completion(
            messages=[{"role": "user", "content": initial_plan_prompt}],
            temperature=0.5, top_p=0.8, max_tokens=256, stream=False
        )["choices"][0]["message"]["content"].strip()

        # Refine the plan
        refined_plan = reflect_and_refine(
            context=planning_context,
            output=initial_plan,
            config=self.config,
            llm=lite_model or prime_model,
            ethical_sentinel=self.ethical_sentinel
        )
        ts_write({"type": "reflection-pre", "in": planning_context, "out": refined_plan}, session_id)

        # The context for the observer and voice is now the fully constructed prompt
        chat_context = {"history": messages}

        # Add the refined plan to the messages for the final response generation
        messages.append({"role": "assistant", "content": f"I will proceed with the following plan: {refined_plan}"})

        observer = StreamObserver(llm=lite_model, name="AgentCore-Observer") if lite_model else None

        voice = ExternalVoice(
            model=prime_model,
            model_pool=self.model_pool,
            config=self.config,
            messages=messages,            # pass the list *as messages*
            source="agent_core",
            observer=observer,
            context=chat_context,
            session_id=session_id,
        )

        stream_generator = voice.stream_response()   # no arg needed
        
        for token_or_event in stream_generator:
            if isinstance(token_or_event, dict) and token_or_event.get("event") == "interruption":
                reason = token_or_event.get("data", "Interrupted by observer.")
                yield {"type": "interruption_start", "reason": reason}
                ts_write({"type":"interruption", "reason": reason}, session_id)

                correction_thought = f'''My initial response was interrupted for the reason: '{reason}'.
The user's original request was: '{user_input}'.
My incomplete response was: '{full_response}'.
Please generate a new, corrected, and complete response that addresses the user's request while fixing the issue.'''

                # Re-build the prompt for the correction turn
                correction_messages = build_prompt(
                    config=self.config,
                    persona_instructions=persona_instructions,
                    session_id=session_id,
                    history=history,
                    user_input=correction_thought  # The new input is the correction context
                )

                correction_voice = ExternalVoice(
                    model=prime_model, model_pool=self.model_pool, config=self.config,
                    thought=correction_messages, source="agent_core_correction", observer=None,
                    context={"history": correction_messages}
                )

                yield {"type": "correction_start"}
                corrected_response_text = ""
                for token in correction_voice.stream_response(correction_messages):
                    yield {"type": "token", "value": str(token)}
                    ts_write({"type":"token", "value": str(token)}, session_id)
                    corrected_response_text += str(token)

                full_response = corrected_response_text
                yield {"type": "correction_end"}
                break
            else:
                token = str(token_or_event)
                yield {"type": "token", "value": token}
                ts_write({"type":"token", "value": token}, session_id)
                full_response += token

        self.ai_manager.status["last_response"] = full_response
        # Add the final assistant response to the persistent session
        self.session_manager.add_message(session_id, "assistant", full_response)

        # Use the clean, centralized logger
        log_chat_entry(user_input, full_response)
        ts_write({"type":"turn_end","user":user_input,"assistant":full_response}, session_id)

        # MODIFICATION: Record that a turn has just completed successfully
        self.session_manager.record_last_activity()

        if full_response:
            yield from self._execute_actions(full_response, session_id)
