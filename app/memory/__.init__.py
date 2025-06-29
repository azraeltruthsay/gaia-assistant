"""
app.memory

This package contains GAIA’s memory-related systems:
- Short-term runtime state tracking (status_tracker)
- Session-level continuity and persistence (session_manager)
- Conversation summarization and logging (conversation/*)
- Structured task memory and prioritization (priority_manager)
- Emerging support for log summarization and seed management

Modules here serve GAIA's ability to recall, contextualize, prioritize, and reflect on past experience.
"""

from .status_tracker import GAIAStatus
from .session_manager import SessionManager
from .priority_manager import GAIAPriorityManager
from .conversation.manager import (
    log_conversation,
    archive_conversation,
    summarize_conversation
)

__all__ = [
    "GAIAStatus",
    "SessionManager",
    "GAIAPriorityManager",
    "log_conversation",
    "archive_conversation",
    "summarize_conversation"
]
