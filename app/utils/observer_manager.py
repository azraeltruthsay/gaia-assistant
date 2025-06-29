# === observer_manager.py ===

from app.models.model_pool import model_pool
from app.utils.stream_observer import StreamObserver
from app.utils.role_manager import RoleManager
import logging

logger = logging.getLogger("GAIA.ObserverManager")

def assign_observer(current_responder, stream_channel="active_response"):
    observer_name = model_pool.get_idle_model(exclude=[current_responder])
    if not observer_name:
        logger.warning(f"⚠️ No idle observer available. {current_responder} will self-monitor.")
        # Self-observing StreamObserver, no LLM (no-ops are handled in StreamObserver)
        return StreamObserver(llm=None, name=current_responder)

    observer_llm = model_pool.get(observer_name)
    model_pool.set_status(observer_name, "observing")
    RoleManager.add_observer(observer_name)
    logger.info(f"👂 Assigned observer: {observer_name}")
    return StreamObserver(llm=observer_llm, name=observer_name)


def default_interrupt_eval(model, stream_text):
    prompt = f"You are monitoring output. Does this contain hallucinations, contradictions, or tone drift?\n\n{stream_text}\n\nReply with:\n- CONTINUE\n- INTERRUPT: <reason>"
    result = model.create_completion(prompt=prompt, max_tokens=64)
    return result["choices"][0]["text"].strip()


def default_interrupt_handler(reason):
    print(f"🔔 Observer Interrupt: {reason}")
