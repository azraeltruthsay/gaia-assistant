# /home/azrael/Project/gaia-assistant/app/memory/conversation/summarizer.py

import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer, util # NEW IMPORT

logger = logging.getLogger("GAIA.ConversationSummarizer")

class ConversationSummarizer:
    """
    Uses the LLM to summarize a conversation history.
    Falls back to placeholder text if no LLM is available.
    """

    def __init__(self, llm=None, embed_model=None): # MODIFIED: Added embed_model
        self.llm = llm
        self.embed_model = embed_model # NEW: Store embedding model

    def generate_summary(self, messages: List[dict]) -> str:
        if not messages:
            return "(No messages to summarize)"

        try:
            if not self.llm:
                logger.info("ℹ️ No LLM available for summarization. Returning placeholder summary.")
                return "Summary unavailable (LLM not connected)"

            conversation_text = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages)
            prompt = (
                "You are an AI assistant summarizing a conversation between a user and GAIA. "
                "Provide a clear and concise summary of what was discussed.\n\n" + conversation_text
            )

            logger.debug("🧠 Requesting LLM-based conversation summary...")
            raw = self.llm(prompt)
            # Normalize to a plain string
            if isinstance(raw, dict):
                # Prefer OpenAI-style choices
                choices = raw.get("choices", [])
                if choices and isinstance(choices[0], dict):
                    text = choices[0].get("text")
                    if text is None:
                        text = choices[0].get("message", {}).get("content", "")
                else:
                    # Fallback: serialize full response
                    import json
                    try:
                        text = json.dumps(raw)
                    except Exception:
                        text = str(raw)
            else:
                text = raw
            return text.strip()

        except Exception as e:
            logger.error(f"❌ Failed to summarize conversation: {e}", exc_info=True)
            return "(Error during summarization)"

    def build_smart_history(self, full_history: List[Dict], current_input: str, max_recent: int = 3, max_salient: int = 2) -> List[Dict]: # NEW METHOD
        """
        Builds a context-aware history by combining recent turns with semantically
        relevant turns from the past, using the embedding model.
        """
        if not self.embed_model:
            logger.warning("⚠️ No embedding model available. Smart history is disabled, returning full history.")
            return full_history

        if len(full_history) <= (max_recent * 2):
            return full_history  # Not enough history to need smart selection yet

        # 1. Separate recent history from long-term memory
        recent_history = full_history[-(max_recent * 2):]
        long_term_history = full_history[:-(max_recent * 2)]

        if not long_term_history:
            return full_history

        # 2. Find the most salient turns from long-term memory
        salient_turns_with_similarity = []
        # Group long-term history into pairs of (user, assistant) turns
        # Ensure we only process complete user-assistant pairs for salience
        pairs_to_embed = []
        for i in range(0, len(long_term_history), 2):
            user_turn = long_term_history[i]
            if user_turn.get("role") == "user":
                assistant_turn = long_term_history[i+1] if i+1 < len(long_term_history) and long_term_history[i+1].get("role") == "assistant" else None
                if assistant_turn:
                    pairs_to_embed.append((user_turn, assistant_turn))
                else:
                    # If last user turn without assistant response, include it for embedding
                    pairs_to_embed.append((user_turn, None))

        if not pairs_to_embed:
            return full_history # No complete pairs or single user turn in long-term history

        # Encode current input once
        current_embedding = self.embed_model.encode(current_input, convert_to_tensor=True)

        # Encode all long-term turns and calculate similarity
        for user_t, assistant_t in pairs_to_embed:
            combined_text = user_t["content"] + (f" {assistant_t['content']}" if assistant_t else "")
            turn_embedding = self.embed_model.encode(combined_text, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(current_embedding, turn_embedding).item()
            salient_turns_with_similarity.append((similarity, user_t, assistant_t))

        # 3. Sort by relevance and pick the top N
        salient_turns_with_similarity.sort(key=lambda x: x[0], reverse=True)
        top_salient_pairs = salient_turns_with_similarity[:max_salient]

        # 4. Assemble the new history
        smart_history = []
        if top_salient_pairs:
            smart_history.append({"role": "system", "content": "[Recap of relevant past conversation for context]"})
            # Add the turns in their original chronological order
            # Need to map back to original indices to preserve order
            original_indices = {id(turn): i for i, turn in enumerate(full_history)}
            sorted_top_salient_pairs = sorted(top_salient_pairs, key=lambda x: original_indices[id(x[1])])

            for _, user_turn, assistant_turn in sorted_top_salient_pairs:
                smart_history.append(user_turn)
                if assistant_turn:
                    smart_history.append(assistant_turn)
            smart_history.append({"role": "system", "content": "[Resuming recent conversation]"})

        smart_history.extend(recent_history)
        return smart_history
