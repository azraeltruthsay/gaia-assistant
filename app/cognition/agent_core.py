import logging
import re
import regex as re
import ast
from typing import Generator, Dict, Any

from app.cognition.external_voice import ExternalVoice
from app.cognition.self_reflection import run_self_reflection, reflect_and_refine
# MODIFICATION: Import the new prompt builder and the correct chat logger
from app.utils.prompt_builder import build_prompt
from app.utils.output_router import route_output
from app.utils.chat_logger import log_chat_entry
from app.utils.stream_observer import StreamObserver
from app.config import Config, constants
from app.utils.thoughtstream import write as ts_write
from app.memory.conversation.summarizer import ConversationSummarizer

logger = logging.getLogger("GAIA.AgentCore")
# After this many messages, collapse history into a summary
HISTORY_SUMMARY_THRESHOLD = 20

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

    def _safe_execute(self, code_snippet: str):
        """
        Safely executes a command by parsing it and calling the corresponding
        whitelisted method on the ai_manager.
        """
        # Whitelist of allowed methods on the 'ai' object
        allowed_methods = {
            "read", "write", "execute", "reload",
            "add_topic", "resolve_topic", "update_topic",
        }

        try:
            # Parse the code snippet into an Abstract Syntax Tree
            # We use mode='eval' because we expect a single expression.
            tree = ast.parse(code_snippet, mode='eval')

            # We expect an expression, which contains a Call node
            if not isinstance(tree, ast.Expression) or not isinstance(tree.body, ast.Call):
                raise ValueError("Command must be a single function call.")

            call_node = tree.body

            # Check that the call is on the 'ai' object
            if not isinstance(call_node.func, ast.Attribute) or \
               not isinstance(call_node.func.value, ast.Name) or \
               call_node.func.value.id != 'ai':
                raise ValueError("Command must be a call on the 'ai' object (e.g., ai.read(...)).")

            method_name = call_node.func.attr

            # Check if the method is in our whitelist
            if method_name not in allowed_methods:
                raise ValueError(f"Method '{method_name}' is not allowed.")

            # Get the actual method from the ai_manager
            method_to_call = getattr(self.ai_manager, method_name, None)
            if not callable(method_to_call):
                raise ValueError(f"Method '{method_name}' not found or not callable on ai_manager.")

            # Evaluate the arguments safely using ast.literal_eval
            args = [ast.literal_eval(arg) for arg in call_node.args]
            kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call_node.keywords}

            # Execute the method
            return method_to_call(*args, **kwargs)

        except (ValueError, SyntaxError, AttributeError) as e:
            logger.error(f"Failed to safely execute command: '{code_snippet}'. Error: {e}")
            raise  # Re-raise the exception to be caught by the caller

    def _execute_actions(self, response: str, session_id: str) -> Generator[Dict[str, Any], None, None]:
        """
        Parses a response for EXECUTE blocks, reflects, and yields events for each action.
        This is a generator function.
        """
        # Use a non-greedy regex and assume one command per EXECUTE block
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

            # 4. Execute only valid ai.*(...) snippets from the refined command
            try:
                # Extract a single ai.command(...) call. This regex is more robust
                # for nested parentheses but assumes the command is well-formed.
                match = re.search(r"\b(ai\.[\w_]+\(.*\))", refined_command, re.S)
                if match:
                    code_snippet = match.group(1)
                    yield {"type": "action_executing", "command": code_snippet}
                    # NEW: Call the safe execution method instead of eval()
                    self._safe_execute(code_snippet)
                    yield {"type": "action_success", "command": code_snippet}
                else:
                    logger.warning(f"No executable ai.* snippet found in refined action: {refined_command}")
                    yield {"type": "action_blocked", "command": refined_command, "reason": "no valid ai command"}
            except Exception as e:
                logger.error(f"Action failed executing snippet from: {refined_command}\nError: {e}", exc_info=True)
                yield {"type": "action_failure", "command": refined_command, "error": str(e)}

        yield {"type": "action_end"}

    def run_turn(self, user_input: str, session_id: str, destination: str = "cli_chat") -> Generator[Dict[str, Any], None, None]:
        """
        Runs a single turn of the agent loop. This is a generator that yields structured events.
        """
        from app.cognition.nlu.intent_service import detect_intent
        import time as _time
        t0 = _time.perf_counter()
        full_response = ""
        prime_model = self.model_pool.get("prime")
        lite_model = self.model_pool.get("lite")

        # MODIFICATION: Add the user's message to the persistent session
        self.session_manager.add_message(session_id, "user", user_input)

        # Instrument: Measure prompt building
        t_build_start = _time.perf_counter()
        active_persona = self.ai_manager.active_persona
        persona_instructions = active_persona.get_full_instructions()
        persona_instruction_list = active_persona.instructions

        # --- Cognitive Dispatch -------------------------------------------
        from app.cognition.cognitive_dispatcher import dispatch
        dispatch_result = dispatch(user_input, persona_instructions)

        if not dispatch_result:
            # Handle dispatch failure, maybe by sending a default message
            yield {"type": "token", "value": "I am currently unable to process your request."}
            return

        selected_model_name = dispatch_result["model_name"]
        selected_model = dispatch_result["model"]
        token_budget = dispatch_result["token_budget"]

        # --- Intent Detection -------------------------------------------
        intent_str = detect_intent(               # returns e.g. "ask_question"
            user_input,
            self.config,
            lite_llm=self.model_pool.get("lite"),
            full_llm=self.model_pool.get("prime"),
        )
        intent_result = {"intent": intent_str}    # normalise to dict
        ts_write({"type": "intent_detect", **intent_result}, session_id)

        history = self.session_manager.get_history(session_id)

        # ——— Summarize long histories to stay under token budget ———
        if len(history) > HISTORY_SUMMARY_THRESHOLD:
            logger.info(f"AgentCore: summarizing history of {len(history)} messages")
            summarizer = ConversationSummarizer(llm=self.model_pool.get("prime"), embed_model=self.model_pool.get("embed"))
            summary = summarizer.generate_summary(history)
            history = [
                {
                    "role": "system",
                    "content": f"Summary of prior conversation: {summary}"
                }
            ]

        # --- Pre-generation Planning and Reflection ---
        plan_messages = build_prompt(
            config=self.config,
            persona_instructions=persona_instructions,
            session_id=session_id,
            history=history,
            user_input=user_input,
            task_instruction="initial_planning",
            token_budget=token_budget
        )

        t_build_end = _time.perf_counter()
        logger.info(f"AgentCore: build_prompt for planning took {t_build_end - t_build_start:.2f}s")
        
        # Summarize planning context to respect token budget
        from app.utils.prompt_builder import count_tokens
        from app.memory.conversation.summarizer import ConversationSummarizer
        MAX_PLAN_TOKENS = getattr(self.config, 'max_plan_tokens', 1024)
        plan_token_count = count_tokens(plan_messages)
        if plan_token_count > MAX_PLAN_TOKENS:
            logger.info(f"AgentCore: summarizing planning context of {plan_token_count} tokens (threshold {MAX_PLAN_TOKENS})")
            summarizer = ConversationSummarizer(llm=self.model_pool.get("prime"), embed_model=self.model_pool.get("embed"))
            summary = summarizer.generate_summary(plan_messages)
            plan_messages = [{
                "role": "system",
                "content": f"Summary of prior context: {summary}"
            }]

        t_plan_start = _time.perf_counter()
        initial_plan = selected_model.create_chat_completion(
            messages=plan_messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
        )["choices"][0]["message"]["content"].strip()
        t_plan_end = _time.perf_counter()
        logger.info(f"AgentCore: initial plan generation took {t_plan_end - t_plan_start:.2f}s")

        # Build the prompt for the final response generation
        messages = build_prompt(
            config=self.config,
            persona_instructions=persona_instructions,
            session_id=session_id,
            history=history,
            user_input=user_input,
            token_budget=token_budget
        )
        
        planning_context = {"user_input": user_input, "intent": intent_result.get("intent"), "history_summary": messages[1]["content"] if len(messages) > 1 else ""}

        # Refine the plan
        t_reflect_start = _time.perf_counter()
        refined_plan = reflect_and_refine(
            context=planning_context,
            output=initial_plan,
            config=self.config,
            llm=self.model_pool.get_idle_model(exclude=[selected_model_name]),
            ethical_sentinel=self.ethical_sentinel,
            instructions=persona_instruction_list
        )
        t_reflect_end = _time.perf_counter()
        logger.info(f"AgentCore: reflect_and_refine took {t_reflect_end - t_reflect_start:.2f}s")
        ts_write({"type": "reflection-pre", "in": planning_context, "out": refined_plan}, session_id)

        # The context for the observer and voice is now the fully constructed prompt
        chat_context = {"history": messages}

        # Add the refined plan to the messages for the final response generation
        messages.append({"role": "assistant", "content": f"I will proceed with the following plan: {refined_plan}"})

        observer_model_name = self.model_pool.get_idle_model(exclude=[selected_model_name])
        observer_model = self.model_pool.get(observer_model_name) if observer_model_name else None
        observer = StreamObserver(llm=observer_model, name="AgentCore-Observer") if observer_model else None

        voice = ExternalVoice(
            model=selected_model,
            model_pool=self.model_pool,
            config=self.config,
            thought=user_input,
            messages=messages,            # pass the list *as messages*
            source="agent_core",
            observer=observer,
            context=chat_context,
            session_id=session_id,
        )

        t_stream_start = _time.perf_counter()
        stream_generator = voice.stream_response()   # no arg needed
        
        was_interrupted = False
        for token_or_event in stream_generator:
            if isinstance(token_or_event, dict) and token_or_event.get("event") == "interruption":
                was_interrupted = True
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
                    user_input=correction_thought,  # The new input is the correction context
                    task_instruction="interruption_handling"
                )

                correction_voice = ExternalVoice(
                    model=prime_model, model_pool=self.model_pool, config=self.config,
                    thought=correction_thought, messages=correction_messages, source="agent_core_correction", observer=None,
                    context={"history": correction_messages}
                )

                yield {"type": "correction_start"}
                # Stream the corrected response back to the caller
                corrected_response_text = ""
                for token in correction_voice.stream_response():
                    yield {"type": "token", "value": token}
                    corrected_response_text += token
                full_response = corrected_response_text
                yield {"type": "correction_end"}
                break
            else:
                token = str(token_or_event)
                full_response += token

        t_stream_end = _time.perf_counter()
        logger.info(f"AgentCore: streaming response took {t_stream_end - t_stream_start:.2f}s")

        # Route the output to get the user-facing part
        response_to_user = route_output(full_response, self.ai_manager, session_id, destination=destination)

        # Stream the user-facing response
        for char in response_to_user:
            yield {"type": "token", "value": char}
            ts_write({"type": "token", "value": char}, session_id)

        self.ai_manager.status["last_response"] = full_response
        # Add the final assistant response to the persistent session
        self.session_manager.add_message(session_id, "assistant", full_response)

        # Use the clean, centralized logger
        log_chat_entry(user_input, full_response)
        ts_write({"type":"turn_end","user":user_input,"assistant":full_response}, session_id)

        # MODIFICATION: Record that a turn has just completed successfully
        self.session_manager.record_last_activity()

        # Maybe generate a thought seed for later reflection
        try:
            from app.cognition.thought_seed import maybe_generate_seed
            context = {"user_input": user_input, "gaia_response": full_response}
            maybe_generate_seed(user_input, context, self.config, llm=self.model_pool.get("prime"))
        except Exception as e:
            logger.error(f"Failed to generate thought seed: {e}", exc_info=True)

        if full_response:
            t_exec_start = _time.perf_counter()
            yield from self._execute_actions(full_response, session_id)
            t_exec_end = _time.perf_counter()
            logger.info(f"AgentCore: _execute_actions took {t_exec_end - t_exec_start:.2f}s")
        logger.info(f"AgentCore: run_turn total took {_time.perf_counter() - t0:.2f}s")
