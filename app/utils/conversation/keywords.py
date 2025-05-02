"""
conversation/keywords.py

Handles keyword extraction from conversation history.
Lightweight heuristics for identifying important terms.
"""

import re
from typing import List

class ConversationKeywordExtractor:
    def __init__(self):
        """
        Initialize the keyword extractor.
        """
        self.common_words = {"I", "You", "He", "She", "It", "We", "They", "The", "A", "An", "This", "That", "These", "Those"}

    def extract_keywords(self, conversation_history: List[dict], limit: int = 10) -> List[str]:
        """
        Extract keyword phrases from conversation history.

        Args:
            conversation_history: List of message dictionaries
            limit: Maximum number of keywords to return

        Returns:
            List of extracted keyword phrases
        """
        all_text = " ".join([msg["content"] for msg in conversation_history])
        potential_keywords = re.findall(r'\b[A-Z][a-zA-Z\']*(?:\s+[A-Z][a-zA-Z\']*)*\b', all_text)

        keywords = []
        seen = set()

        for keyword in potential_keywords:
            cleaned_keyword = keyword.strip()
            if cleaned_keyword and cleaned_keyword not in seen and cleaned_keyword not in self.common_words:
                keywords.append(cleaned_keyword)
                seen.add(cleaned_keyword)
            if len(keywords) >= limit:
                break

        return keywords
