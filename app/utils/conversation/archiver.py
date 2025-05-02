"""
conversation/archiver.py

Handles saving and loading archived conversations in Markdown format.
Manages storage, file formatting, and retrieval operations.
"""

import os
import datetime
import logging
from typing import List, Optional

logger = logging.getLogger("GAIA")

class ConversationArchiver:
    def __init__(self, archives_dir: str):
        """
        Initialize the archiver.

        Args:
            archives_dir: Directory to save and load conversation archives
        """
        self.archives_dir = archives_dir
        os.makedirs(self.archives_dir, exist_ok=True)

    def archive_conversation(self, session_id: str, conversation_history: List[dict], summary: str, keywords: List[str]) -> str:
        """
        Archive the conversation to a markdown file.

        Args:
            session_id: ID of the current session
            conversation_history: List of message dictionaries
            summary: Generated summary text
            keywords: List of extracted keywords

        Returns:
            Archive ID (filename without extension)
        """
        archive_id = f"{session_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = f"{archive_id}.md"
        filepath = os.path.join(self.archives_dir, filename)

        markdown_content = self._format_conversation_as_markdown(conversation_history, summary, keywords)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Conversation archived to {filepath}")
        except Exception as e:
            logger.error(f"Error saving archive {filename}: {e}")

        return archive_id

    def load_archived_conversation(self, archive_id: str) -> Optional[str]:
        """
        Load an archived conversation by its ID.

        Args:
            archive_id: Archive ID (without extension)

        Returns:
            Content of the archived conversation or None if not found
        """
        filepath = os.path.join(self.archives_dir, f"{archive_id}.md")

        if not os.path.exists(filepath):
            logger.warning(f"Archive not found: {archive_id}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading archive {archive_id}: {e}")
            return None

    def _format_conversation_as_markdown(self, conversation_history: List[dict], summary: str, keywords: List[str]) -> str:
        """
        Format the conversation history into a markdown string.

        Args:
            conversation_history: List of message dictionaries
            summary: Summary text
            keywords: List of keyword phrases

        Returns:
            Markdown-formatted conversation
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        markdown = f"# Conversation Archive - {timestamp}\n\n"
        markdown += f"## Summary\n\n{summary}\n\n"

        if keywords:
            markdown += f"**Keywords**: {', '.join(keywords)}\n\n"

        markdown += "## Conversation\n\n"

        for msg in conversation_history:
            role_display = "**User**" if msg["role"] == "user" else "**GAIA**"
            msg_time = datetime.datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
            markdown += f"{role_display} ({msg_time}):\n\n{msg['content']}\n\n---\n\n"

        return markdown
