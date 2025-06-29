"""
llm_analysis.py

Handles code analysis using an LLM (Large Language Model).
"""

import logging
from typing import List, Dict
from app.cognition.inner_monologue import process_thought
from app.config import Config

logger = logging.getLogger("GAIA.LLMAnalysis")

def summarize_chunks(chunks: List[Dict], llm, reflect: bool = True) -> str:
    """
    Generate a natural language summary of code chunks using the provided LLM.
    """
    try:
        cfg = Config()
        persona = "technical summarizer"
        instructions = "Review the provided code functions and summarize their purpose in plain English."

        messages = [chunk["content"] for chunk in chunks if chunk["type"] in ("function", "class")]
        payload = "\n\n".join(messages).strip()

        if not payload:
            logger.warning("LLMAnalysis received an empty code chunk payload. Skipping summarization.")
            return "(Empty prompt — no summary generated.)"

        summary = process_thought(
            task_type="code_summary",
            persona=persona,
            instructions=instructions,
            payload=payload,
            llm=llm,
            reflect=reflect
        )
        return summary

    except Exception as e:
        logger.error(f"❌ LLM summarization failed: {e}", exc_info=True)
        return "(Failed to summarize code.)"
