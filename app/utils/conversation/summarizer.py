"""
conversation/summarizer.py

Handles conversation summarization logic for GAIA.
Supports both LLM-driven summarization and basic fallback methods.
"""

import re
import datetime
import logging
from typing import List

logger = logging.getLogger("GAIA")

class ConversationSummarizer:
    def __init__(self, llm=None):
        """
        Initialize the summarizer.

        Args:
            llm: Optional language model for generating summaries.
        """
        self.llm = llm

    def generate_summary(self, conversation_history: List[dict]) -> str:
        """
        Generate a summary of a conversation.

        Args:
            conversation_history: List of message dictionaries

        Returns:
            Summary string
        """
        if not conversation_history:
            return "Empty conversation"

        if not self.llm:
            return self._generate_basic_summary(conversation_history)

        try:
            conversation_text = self._format_conversation(conversation_history)
            prompt = self._enhanced_summary_prompt(conversation_text)
            summary = self.llm(prompt).strip()
            summary = re.sub(r'^(Summary:|SUMMARY:)', '', summary, flags=re.IGNORECASE).strip()
            return summary
        except Exception as e:
            logger.error(f"Error generating summary with LLM: {e}")
            return self._generate_basic_summary(conversation_history)

    def _generate_basic_summary(self, conversation_history: List[dict]) -> str:
        """
        Basic fallback summarization without using an LLM.

        Args:
            conversation_history: List of message dictionaries

        Returns:
            Simple summary string
        """
        first_msg = next((msg["content"] for msg in conversation_history if msg["role"] == "user"), "a general topic")
        first_msg_excerpt = re.split(r'[.!?]', first_msg)[0]
        if len(first_msg_excerpt) > 80:
            first_msg_excerpt = first_msg_excerpt[:77] + "..."

        participant_summary = f"{sum(1 for m in conversation_history if m['role'] == 'user')} user messages and {sum(1 for m in conversation_history if m['role'] == 'assistant')} GAIA responses"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

        return f"Summary of conversation on {timestamp}: {participant_summary}, beginning with discussion about '{first_msg_excerpt}'."

    def _enhanced_summary_prompt(self, conversation_text: str) -> str:
        """
        Create an enhanced summarization prompt for the LLM.

        Args:
            conversation_text: Formatted conversation history

        Returns:
            Full prompt string
        """
        return f"""You are a campaign chronicler AI assisting in summarizing D&D sessions.
Focus on key plot developments, emotional character moments, significant choices, and emerging world lore.
Maintain a tone appropriate for an immersive game master log.
Summarize the following conversation in 2-3 rich, vivid sentences:

{conversation_text}

Summary:"""

    def _format_conversation(self, conversation_history: List[dict]) -> str:
        """
        Format conversation history into a clean string for summarization.

        Args:
            conversation_history: List of message dictionaries

        Returns:
            Formatted conversation string
        """
        formatted = []
        for msg in conversation_history:
            role_display = "User" if msg["role"] == "user" else "GAIA"
            formatted.append(f"{role_display}: {msg['content']}")
        return "\n\n".join(formatted)
