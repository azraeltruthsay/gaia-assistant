# session_manager.py

import datetime
import os
import re

#    def __init__(self, vectordb_client, personalities_path="/personalities/"):

class SessionManager:
    def __init__(self, ai_manager):
        """
        Initialize the GAIA Session Manager.

        Args:
            vectordb_client: Client for interacting with the vector database.
            personalities_path: Path to the local personalities directory.
        """
        self.vectordb = ai_manager.vector_store_manager
        self.personalities_path = ai_manager.config.personalities_path
        self.session_profile = None
    def initialize_session(self, user_selected_style=None):
        """
        Initializes a new GAIA session.

        Args:
            user_selected_style (str): Optional. User-selected behavior style.

        Returns:
            dict: Session profile containing behavior settings.
        """
        style = user_selected_style or "neutral"
        behavior_modules = self.retrieve_behavior_modules(style)

        self.session_profile = {
            "style": style,
            "behavior_modules": behavior_modules,
            "timestamp": datetime.datetime.now().isoformat()
        }
        return self.session_profile

    def retrieve_behavior_modules(self, style):
        """
        Queries the VectorDB for behavior modules matching the requested style.

        Args:
            style (str): Desired behavior style.

        Returns:
            list: Retrieved behavior documents.
        """
        results = self.vectordb.query(
            filter={
                "type": "behavior",
                "style": style
            },
            top_k=1
        )

        if not results:
            # Fallback if no matching behavior found
            results = self.vectordb.query(
                filter={
                    "type": "behavior",
                    "style": "neutral"
                },
                top_k=1
            )

        return results

    def assemble_prompt(self, conversation_history, user_message):
        """
        Combines all inputs to create the final system prompt for the model.

        Args:
            conversation_history (list): List of recent conversation messages.
            user_message (str): Current user input.

        Returns:
            str: Full model-ready prompt.
        """
        baseframe_prompt = self.get_baseframe()
        behavior_instructions = "\n".join([doc['content'] for doc in self.session_profile['behavior_modules']])
        history_summary = self.summarize_history(conversation_history)

        full_prompt = f"""{baseframe_prompt}

{behavior_instructions}

[Conversation Context]
{history_summary}

[User Input]
{user_message}
"""
        return full_prompt

    def report_current_personality(self):
        """
        Reports the current behavior settings of GAIA.

        Returns:
            str: Human-readable personality summary.
        """
        if not self.session_profile:
            return "No active session profile."

        selected_style = self.session_profile.get("style", "neutral")
        active_behaviors = [doc['title'] for doc in self.session_profile.get("behavior_modules", [])]

        response = f"Current behavior style: **{selected_style}**\nActive behavior modules: {', '.join(active_behaviors)}"
        return response

    @staticmethod
    def get_baseframe():
        """
        Returns the static baseframe prompt for GAIA.

        Returns:
            str: Baseframe instruction string.
        """
        return (
            "You are GAIA, a modular, adaptive AI Assistant.\n"
            "Your goals are clarity, relevance, adaptability, and user autonomy.\n"
            "You prioritize:\n"
            "- Clear communication, free of unnecessary complexity\n"
            "- Contextual awareness based on user input and available memory\n"
            "- Adjusting your tone and behavior dynamically according to embedded session instructions\n"
            "- Respecting the user's authority to shape or change your behavior\n\n"
            "You are capable of technical, narrative, creative, and analytical assistance.\n"
            "You always strive to act as a thoughtful partner, not a superior or a mere tool."
        )

    @staticmethod
    def summarize_history(conversation_history):
        """
        Summarizes recent conversation history.

        Args:
            conversation_history (list): List of past conversation turns.

        Returns:
            str: Summarized history text.
        """
        if not conversation_history:
            return "(No significant conversation history yet.)"

        # Simple summarization: join last few messages.
        return "\n".join(conversation_history[-5:])

    def sync_behaviors(self):
        """
        Syncs local behavior instruction files with the vector database.
        """
        for filename in os.listdir(self.personalities_path):
            if filename.endswith(".md") or filename.endswith(".txt"):
                filepath = os.path.join(self.personalities_path, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                metadata, instructions = self.parse_behavior_file(content)
                title = metadata.get("Title")
                style = metadata.get("Style")

                # Check if already exists
                existing = self.vectordb.query(
                    filter={"type": "behavior", "style": style},
                    top_k=1
                )

                if not existing:
                    # Embed new behavior
                    embed_doc = {
                        "type": "behavior",
                        "title": title,
                        "style": style,
                        "context": metadata.get("Context", "general"),
                        "priority": metadata.get("Priority", "medium"),
                        "content": instructions
                    }
                    self.vectordb.add(embed_doc)

    @staticmethod
    def parse_behavior_file(content):
        """
        Parses a behavior file into metadata and instructions.

        Args:
            content (str): Raw file content.

        Returns:
            tuple: (metadata dict, instruction text)
        """
        metadata = {}
        parts = content.split("---", 1)
        if len(parts) != 2:
            return metadata, content  # No metadata found

        header, instructions = parts
        for line in header.strip().splitlines():
            key_value = re.split(r":\\s*", line, 1)
            if len(key_value) == 2:
                key, value = key_value
                metadata[key.strip()] = value.strip()

        return metadata, instructions.strip()
