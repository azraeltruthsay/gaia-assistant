"""
conversation/manager.py

Main orchestrator for conversation management.
Coordinates message history, summarization, keyword extraction, and archiving.
"""

import os
import uuid
import threading
import datetime
import logging
from typing import List, Dict, Any, Optional

from .summarizer import ConversationSummarizer
from .keywords import ConversationKeywordExtractor
from .archiver import ConversationArchiver

logger = logging.getLogger("GAIA")

class ConversationManager:
    def __init__(self, config, llm=None):
        """
        Initialize the Conversation Manager.

        Args:
            config: Configuration object
            llm: Optional language model for summarization
        """
        self.config = config
        self.llm = llm
        self.current_session_id = str(uuid.uuid4())
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_active_messages = getattr(config, 'max_active_messages', 30)
        self.summary_lock = threading.Lock()

        self.summarizer = ConversationSummarizer(llm)
        self.keyword_extractor = ConversationKeywordExtractor()
        self.archiver = ConversationArchiver(
            getattr(config, 'conversation_archives_path', os.path.join(config.data_path, "../conversation_archives"))
        )

        logger.info("Conversation Manager initialized")

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history and log it to raw archive.
    
        Args:
            role: 'user' or 'assistant'
            content: The message content
        """
        timestamp = datetime.datetime.now().isoformat()
        message = {"role": role, "content": content, "timestamp": timestamp}
        self.conversation_history.append(message)
    
        # 🔁 Always append to raw log file for this session
        raw_log_path = os.path.join(
            self.archiver.archives_dir,
            f"{self.current_session_id}_raw.log"
        )
        try:
            with open(raw_log_path, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} [{role.upper()}]: {content}\n")
            logger.debug(f"📩 Appended to raw archive: {role.upper()} at {timestamp}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to append raw archive: {e}")
    
        # 🔁 Archive summary only after N messages
        if len(self.conversation_history) >= self.max_active_messages:
            self.summarize_and_archive()

    def summarize_and_archive(self) -> None:
        """
        Summarize and archive the current conversation history.
        """
        if not self.conversation_history:
            return

        with self.summary_lock:
            summary = self.summarizer.generate_summary(self.conversation_history)
            keywords = self.keyword_extractor.extract_keywords(self.conversation_history)
            archive_id = self.archiver.archive_conversation(
                self.current_session_id, self.conversation_history, summary, keywords
            )

            logger.info(f"Conversation summarized and archived with ID: {archive_id}")
            self.conversation_history.clear()

    def get_active_context(self) -> str:
        """
        Get the current active conversation context.

        Returns:
            Formatted string of conversation history
        """
        context = []
        for msg in self.conversation_history:
            role_display = "User" if msg["role"] == "user" else "GAIA"
            context.append(f"{role_display}: {msg['content']}")

        return "\n\n".join(context)

    def load_archived_conversation(self, archive_id: str) -> Optional[str]:
        """
        Load a past conversation by archive ID.

        Args:
            archive_id: Archive ID (without extension)

        Returns:
            Conversation content or None if not found
        """
        return self.archiver.load_archived_conversation(archive_id)
