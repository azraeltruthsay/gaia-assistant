# /home/azrael/Project/gaia-assistant/app/utils/stream_observer.py

import logging
import re
import torch
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger("GAIA.StreamObserver")


class StreamObserver:
    """
    Streaming Observer for council/cognitive output.
    Can be backed by an LLM or rules.
    """

    def __init__(self, llm=None, name="observer", interrupt_handler=None):
        self.llm = llm
        self.name = name
        self.buffer = []
        self.active = True
        self.interrupt_handler = interrupt_handler or self.default_interrupt_handler
        self.interrupt_reason = None  # Store the reason for interruption

    def observe(self, buffer, context):
        """
        Runs the observer logic on the current stream buffer.
        The model call here is now correctly suppressed.
        """
        # MODIFICATION: Import the suppression utility
        from app.cognition.external_voice import suppress_llama_stderr
        if isinstance(buffer, list):
            buffer = "".join(buffer)

        max_length = 500
        buffer_to_send = summarize_buffer(buffer) if len(buffer) > max_length else buffer

        if self.llm is None:
            return "continue"

        # --- MODIFICATION: Create a much richer prompt using the new context ---
        persona_name = context.get("persona", "GAIA")
        instructions = "\n- ".join(context.get("instructions", []))

        prompt = (
            f"You are an AI's ethical and technical guardian. The AI, named {persona_name}, is generating a response. "
            f"Its core instructions are:\n- {instructions}\n\n"
            f"The response so far is:\n---\n{buffer_to_send}\n---\n\n"
            "Review the response for the following issues:\n"
            "1. Technical errors (repetition, gibberish, formatting problems).\n"
            "2. Ethical violations or straying from its core instructions.\n"
            "3. Hallucinations or fabricating information.\n\n"
            "Reply with only 'CONTINUE' if the output is fine. "
            "Otherwise, reply with 'INTERRUPT: <reason for stopping>'."
        )
        try:
            # MODIFICATION: The model call is now wrapped in the suppressor
            with suppress_llama_stderr():
                result = self.llm.create_completion(prompt=prompt, max_tokens=64)

            text = result["choices"][0]["text"].strip().upper()
            if text.startswith("INTERRUPT"):
                self.interrupt_reason = text.split(":", 1)[-1].strip()
                if self.interrupt_handler:
                    self.interrupt_handler(self.interrupt_reason)
                return "interrupt"
        except Exception as e:
            logger.error(f"StreamObserver ({self.name}) failed: {e}")
        return "continue"

    def default_interrupt_handler(self, reason):
        """Default handler to print the interruption reason."""
        print(f"\n🔔 Observer Interrupt: {reason}")


# This helper function remains the same.
_OBSERVER_SUM_MODEL = SentenceTransformer("/models/all-MiniLM-L6-v2")

def summarize_buffer(buffer, max_sentences=4):
    """
    Quickly summarizes a long buffer by extracting the most salient sentences.
    """
    sentences = re.split(r'(?<=[.!?])\s+', buffer.strip())
    if len(sentences) <= max_sentences:
        return buffer

    embeddings = _OBSERVER_SUM_MODEL.encode(sentences, convert_to_tensor=True)
    mean_emb = torch.mean(embeddings, dim=0)
    similarities = util.cos_sim(mean_emb, embeddings)[0]

    sorted_indices = torch.argsort(similarities, descending=True)
    top_indices = sorted_indices[:max_sentences]

    final_indices = sorted(top_indices.tolist())
    summary = " ".join([sentences[i] for i in final_indices])

    return summary