"""
llm_analysis.py

Handles code analysis using an LLM (Large Language Model).
"""

import re
import json
import logging
from typing import Optional

logger = logging.getLogger("GAIA")


class LLMAnalyzer:
    """Performs LLM-driven analysis of code files."""

    def __init__(self, llm=None):
        """
        Initialize the analyzer.

        Args:
            llm: Optional LLM instance for code analysis
        """
        self.llm = llm

    def analyze_code(self, filepath: str, content: str, language: str) -> dict:
        """
        Analyze code using an LLM and return structured insights.

        Args:
            filepath: Path to the code file
            content: Code content
            language: Detected programming language

        Returns:
            Dictionary containing analysis results
        """
        if not self.llm or not content:
            logger.warning("LLM not available or content empty")
            return {}

        try:
            prompt = self._build_prompt(filepath, content, language)
            response_text = self.llm(prompt)

            json_data = self._extract_json(response_text)

            if json_data:
                return json_data

            # Fallback if no clean JSON was extracted
            return {
                'summary': (response_text[:200] + '...') if len(response_text) > 200 else response_text,
                'components': [],
                'improvements': [],
                'issues': [],
                'complexity_rating': 5  # Default neutral score
            }
        except Exception as e:
            logger.error(f"Error during LLM code analysis: {e}", exc_info=True)
            return {}

    def _build_prompt(self, filepath: str, content: str, language: str) -> str:
        """Builds the LLM prompt for code analysis."""
        return f"""Analyze the following code file and provide structured insights:

File: {filepath}
Language: {language}

```{language}
{content}"""
