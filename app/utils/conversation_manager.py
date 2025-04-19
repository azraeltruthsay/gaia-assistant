"""
Conversation Manager for GAIA D&D Campaign Assistant.
Handles tracking, summarizing, and archiving conversations.
"""

import os
import re
import json
import uuid
import logging
import datetime
from typing import List, Dict, Any, Optional, Tuple

# Get the logger
logger = logging.getLogger("GAIA")

class ConversationManager:
    """Manages conversation history, summarization, and archiving."""
    
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
        self.conversation_history = []
        self.summaries = []
        
        # Create archives directory if it doesn't exist
        self.archives_dir = os.path.join(config.data_path, "../conversation_archives")
        os.makedirs(self.archives_dir, exist_ok=True)
        
        # Load existing summaries index if it exists
        self.summaries_index_path = os.path.join(self.archives_dir, "summaries_index.json")
        if os.path.exists(self.summaries_index_path):
            try:
                with open(self.summaries_index_path, 'r', encoding='utf-8') as f:
                    self.summaries = json.load(f)
            except Exception as e:
                logger.error(f"Error loading summaries index: {e}")
                self.summaries = []
        
        # Max message count before summarization/archiving
        self.max_active_messages = 30
        
        logger.info("Conversation Manager initialized")
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The sender of the message ('user' or 'assistant')
            content: The message content
        """
        timestamp = datetime.datetime.now().isoformat()
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        
        self.conversation_history.append(message)
        
        # Check if we need to summarize and archive
        if len(self.conversation_history) >= self.max_active_messages:
            self.summarize_and_archive()
    
    def get_active_context(self) -> str:
        """
        Get the active conversation context for prompting.
        
        Returns:
            Formatted conversation history as a string
        """
        context = []
        
        # Add the latest summary if available
        if self.summaries:
            latest_summary = self.summaries[-1]
            context.append(f"Previous conversation summary: {latest_summary['summary']}\n")
        
        # Format conversation history
        for msg in self.conversation_history:
            role_display = "User" if msg["role"] == "user" else "GAIA"
            context.append(f"{role_display}: {msg['content']}")
        
        return "\n\n".join(context)
    
    def summarize_and_archive(self) -> None:
        """Summarize the current conversation and archive it."""
        if not self.conversation_history:
            return
        
        # Create a summary of the conversation
        summary = self._generate_summary()
        
        # Archive the conversation
        archive_id = self._archive_conversation(summary)
        
        # Add to summaries index
        summary_entry = {
            "id": archive_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": summary,
            "keyword_phrases": self._extract_keywords()
        }
        
        self.summaries.append(summary_entry)
        
        # Save the updated summaries index
        try:
            with open(self.summaries_index_path, 'w', encoding='utf-8') as f:
                json.dump(self.summaries, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving summaries index: {e}")
        
        # Clear the active conversation history
        self.conversation_history = []
        
        logger.info(f"Conversation summarized and archived with ID: {archive_id}")
    
    def _generate_summary(self) -> str:
        """
        Generate a summary of the current conversation.
        
        Returns:
            A concise summary of the conversation
        """
        if not self.llm:
            # Fallback summary method if no LLM is available
            return self._generate_basic_summary()
        
        try:
            # Format the conversation for summarization
            conversation_text = self._format_conversation_for_summarization()
            
            # Generate summary with the LLM
            prompt = f"""Please provide a concise summary (2-3 sentences) of the following D&D campaign conversation between a user and GAIA (an AI assistant).
            Focus on key plot points, character development, or world-building elements discussed.
            
            CONVERSATION:
            {conversation_text}
            
            SUMMARY:"""
            
            summary = self.llm(prompt).strip()
            
            # Clean up the summary
            summary = re.sub(r'^(Summary:|SUMMARY:)', '', summary, flags=re.IGNORECASE).strip()
            
            return summary
        except Exception as e:
            logger.error(f"Error generating summary with LLM: {e}")
            return self._generate_basic_summary()
    
    def _generate_basic_summary(self) -> str:
        """
        Generate a basic summary without using an LLM.
        
        Returns:
            A simple summary based on message count and first/last messages
        """
        if not self.conversation_history:
            return "Empty conversation"
        
        user_msg_count = sum(1 for msg in self.conversation_history if msg["role"] == "user")
        gaia_msg_count = sum(1 for msg in self.conversation_history if msg["role"] == "assistant")
        
        first_user_msg = next((msg["content"] for msg in self.conversation_history if msg["role"] == "user"), "")
        if first_user_msg:
            # Truncate to first sentence or first 50 chars
            first_user_msg = re.split(r'[.!?]', first_user_msg)[0]
            if len(first_user_msg) > 50:
                first_user_msg = first_user_msg[:47] + "..."
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return f"Conversation on {timestamp} with {user_msg_count} user messages and {gaia_msg_count} GAIA responses, starting with user query about '{first_user_msg}'"
    
    def _format_conversation_for_summarization(self) -> str:
        """
        Format the conversation history for summarization.
        
        Returns:
            Formatted conversation as a string
        """
        formatted = []
        for msg in self.conversation_history:
            role_display = "User" if msg["role"] == "user" else "GAIA"
            formatted.append(f"{role_display}: {msg['content']}")
        
        return "\n\n".join(formatted)
    
    def _extract_keywords(self) -> List[str]:
        """
        Extract keyword phrases from the conversation.
        
        Returns:
            List of extracted keyword phrases
        """
        # Simple keyword extraction
        all_text = " ".join([msg["content"] for msg in self.conversation_history])
        
        # Extract proper nouns and potential keywords
        # This is a simple heuristic approach - could be improved with NLP
        potential_keywords = re.findall(r'\b[A-Z][a-zA-Z\']+(?:\s+[A-Z][a-zA-Z\']+)*\b', all_text)
        
        # Filter out common words and keep unique keywords
        common_words = {"I", "You", "He", "She", "It", "We", "They", "The", "A", "An", "This", "That", "These", "Those"}
        keywords = []
        seen = set()
        
        for keyword in potential_keywords:
            if keyword not in seen and keyword not in common_words:
                keywords.append(keyword)
                seen.add(keyword)
                
                # Limit to reasonable number of keywords
                if len(keywords) >= 10:
                    break
        
        return keywords
    
    def _archive_conversation(self, summary: str) -> str:
        """
        Archive the current conversation to a markdown file.
        
        Args:
            summary: Generated summary of the conversation
            
        Returns:
            Archive ID (filename without extension)
        """
        # Generate archive ID and filename
        archive_id = f"{self.current_session_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = f"{archive_id}.md"
        filepath = os.path.join(self.archives_dir, filename)
        
        # Format conversation as markdown
        markdown_content = self._format_conversation_as_markdown(summary)
        
        # Save to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Conversation archived to {filepath}")
        except Exception as e:
            logger.error(f"Error saving archive: {e}")
        
        return archive_id
    
    def _format_conversation_as_markdown(self, summary: str) -> str:
        """
        Format the conversation history as markdown.
        
        Args:
            summary: Generated summary of the conversation
            
        Returns:
            Formatted markdown string
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create markdown header
        markdown = f"# Conversation Archive - {timestamp}\n\n"
        markdown += f"## Summary\n\n{summary}\n\n"
        
        if self._extract_keywords():
            markdown += f"**Keywords**: {', '.join(self._extract_keywords())}\n\n"
        
        markdown += "## Conversation\n\n"
        
        # Add each message
        for msg in self.conversation_history:
            role_display = "**User**" if msg["role"] == "user" else "**GAIA**"
            msg_time = datetime.datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
            markdown += f"{role_display} ({msg_time}):\n\n{msg['content']}\n\n---\n\n"
        
        return markdown
    
    def find_relevant_context(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Find relevant archived conversations based on a query.
        
        Args:
            query: The query to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant context entries
        """
        if not self.summaries:
            return []
        
        # Extract keywords from the query
        query_words = re.findall(r'\b[a-zA-Z\']+\b', query.lower())
        
        # Simple relevance scoring
        scored_summaries = []
        for summary in self.summaries:
            score = 0
            
            # Check summary text
            summary_text = summary["summary"].lower()
            for word in query_words:
                if word in summary_text:
                    score += 1
            
            # Check keywords
            for keyword in summary.get("keyword_phrases", []):
                keyword_lower = keyword.lower()
                for word in query_words:
                    if word in keyword_lower:
                        score += 2  # Keywords get higher weight
            
            if score > 0:
                scored_summaries.append((score, summary))
        
        # Sort by relevance score
        scored_summaries.sort(reverse=True, key=lambda x: x[0])
        
        # Return top results
        return [item[1] for item in scored_summaries[:max_results]]
    
    def get_archived_conversation(self, archive_id: str) -> Optional[str]:
        """
        Retrieve an archived conversation by ID.
        
        Args:
            archive_id: The ID of the archived conversation
            
        Returns:
            The conversation content as a string, or None if not found
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
    
    def get_relevant_context_for_query(self, query: str) -> str:
        """
        Get relevant context from archived conversations for a query.
        
        Args:
            query: The query to find context for
            
        Returns:
            Relevant context as a formatted string
        """
        relevant_items = self.find_relevant_context(query)
        
        if not relevant_items:
            return ""
        
        context_parts = []
        
        for item in relevant_items:
            context_parts.append(f"From previous conversation ({item['id']}):\n{item['summary']}")
        
        return "\n\n".join(context_parts)
    def summarize_and_archive_for_background(self):
        """
        Prepare the current conversation for background processing.
        Similar to summarize_and_archive but delegates processing to background tasks.
        
        Returns:
            Dictionary with archive information
        """
        if not self.conversation_history:
            return None
        
        # Generate a basic summary for immediate feedback
        summary = self._generate_basic_summary()
        
        # Create a unique archive ID
        archive_id = f"{self.current_session_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = f"{archive_id}.md"
        filepath = os.path.join(self.archives_dir, filename)
        
        # Format raw conversation as markdown
        markdown_content = self._format_conversation_as_markdown(summary)
        
        # Save raw conversation
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Raw conversation archived to {filepath}")
        except Exception as e:
            logger.error(f"Error saving archive: {e}")
            return None
    
        # Add to summaries index with basic summary
        summary_entry = {
            "id": archive_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": summary,
            "keyword_phrases": self._extract_keywords(),
            "status": "pending_processing"
        }
    
        self.summaries.append(summary_entry)
    
        # Save the updated summaries index
        try:
            with open(self.summaries_index_path, 'w', encoding='utf-8') as f:
                json.dump(self.summaries, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving summaries index: {e}")
        
        # Clear the active conversation history
        self.conversation_history = []
        
        logger.info(f"Conversation prepared for background processing with ID: {archive_id}")
        
        return {
            "id": archive_id,
            "filepath": filepath,
            "summary": summary
        }

# Add this method to the ConversationManager class

    def update_archive_status(self, archive_id, new_status, new_summary=None):
        """
        Update the status of an archived conversation after background processing.
        
        Args:
            archive_id: ID of the archive to update
            new_status: New status string (e.g., 'processed', 'failed')
            new_summary: Optional improved summary from structured processing
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Find the summary entry
            for summary in self.summaries:
                if summary["id"] == archive_id:
                    summary["status"] = new_status
                    if new_summary:
                        summary["summary"] = new_summary
                    
                    # Save the updated summaries index
                    with open(self.summaries_index_path, 'w', encoding='utf-8') as f:
                        json.dump(self.summaries, f, indent=2)
                    
                    logger.info(f"Updated archive {archive_id} status to {new_status}")
                    return True
            
            logger.warning(f"Archive {archive_id} not found in summaries index")
            return False
        except Exception as e:
            logger.error(f"Error updating archive status: {e}")
            return False
    
    # Add this method to the ConversationManager class
    
    def get_archive_statistics(self):
        """
        Get statistics about archived conversations.
        
        Returns:
            Dictionary with archive statistics
        """
        try:
            total_archives = len(self.summaries)
            processed_archives = sum(1 for s in self.summaries if s.get("status") == "processed")
            pending_archives = sum(1 for s in self.summaries if s.get("status") == "pending_processing")
            failed_archives = sum(1 for s in self.summaries if s.get("status") == "failed")
            
            # Count keywords
            all_keywords = []
            for summary in self.summaries:
                all_keywords.extend(summary.get("keyword_phrases", []))
            
            # Get most common keywords
            keyword_counts = {}
            for keyword in all_keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_archives": total_archives,
                "processed_archives": processed_archives,
                "pending_archives": pending_archives,
                "failed_archives": failed_archives,
                "top_keywords": top_keywords
            }
        except Exception as e:
            logger.error(f"Error getting archive statistics: {e}")
            return {
                "total_archives": 0,
                "processed_archives": 0,
                "pending_archives": 0,
                "failed_archives": 0,
                "top_keywords": []
            }
    
    # Add this method to the ConversationManager class
    
    def get_related_archives(self, query, max_results=5):
        """
        Find archives related to a specific query using keywords.
        
        Args:
            query: Query string to match against archives
            max_results: Maximum number of results to return
            
        Returns:
            List of related archive entries
        """
        # Extract keywords from the query
        query_words = re.findall(r'\b[a-zA-Z\']+\b', query.lower())
        
        # Score archives based on keyword matches
        scored_archives = []
        for archive in self.summaries:
            score = 0
            
            # Match against summary
            summary = archive.get("summary", "").lower()
            for word in query_words:
                if word in summary:
                    score += 1
            
            # Match against keywords
            keywords = [k.lower() for k in archive.get("keyword_phrases", [])]
            for word in query_words:
                if any(word in keyword for keyword in keywords):
                    score += 2
            
            if score > 0:
                scored_archives.append((score, archive))
        
        # Sort by score and return top results
        scored_archives.sort(reverse=True, key=lambda x: x[0])
        return [archive for _, archive in scored_archives[:max_results]]