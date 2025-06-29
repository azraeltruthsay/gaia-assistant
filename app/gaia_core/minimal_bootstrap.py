# app/gaia_core/minimal_bootstrap.py

from app.cognition.self_reflection import run_self_reflection
from app.cognition.external_voice import pipe_chat_loop

def minimal_bootstrap():
    # Minimal cognitive kernel (no AIManager, no web)
    reflect = run_self_reflection()
    model = reflect.load_llm() if hasattr(reflect, "load_llm") else None
    return {
        "reflect": reflect,
        "model": model,
        "chat_loop": lambda: pipe_chat_loop(model) if model else print("No LLM loaded.")
    }
