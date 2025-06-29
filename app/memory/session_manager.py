import os
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("GAIA.SessionManager")

class SessionManager:
    def __init__(self, config):
        self.config = config
        self.personas_dir = self.config.personas_dir
        self.history_dir = os.path.join(self.config.projects_path, 'session_history')
        os.makedirs(self.history_dir, exist_ok=True)
        self._current_persona = None
        self.current_persona_name = None

    def initialize_session(self, style: str):
        """Initialize the session by loading the persona and its behavior settings."""
        logger.debug(f"Initializing session with persona: {style}")
        try:
            profile = self.load_persona(style)
            if not profile:
                raise ValueError(f"Persona '{style}' could not be loaded or returned None.")
            self._current_persona = profile
            self.current_persona_name = style
            self.session_data = self.load_session_data(style)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize session: {str(e)}")

    def load_persona(self, style: str) -> Optional[Dict]:
        """Loads the persona configuration file."""
        filepath = os.path.join(self.personas_dir, style, f"{style}_persona.json")
        logger.debug(f"Loading persona from: {filepath}")
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Persona file for '{style}' not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Failed to decode persona JSON for '{style}'.")

    def load_session_data(self, style: str) -> Dict:
        """Load session-related data for a given persona."""
        filepath = os.path.join(self.history_dir, f"{style}_session.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def save_session(self, session_data: Dict):
        """Save the session data for future continuity."""
        if not self.current_persona_name:
            raise ValueError("Current persona name is not set.")
        filepath = os.path.join(self.history_dir, f"{self.current_persona_name}_session.json")
        logger.debug(f"Saving session to: {filepath}")
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(session_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            raise IOError(f"Failed to save session data: {str(e)}")

    def clear_session(self):
        """Clear all session data files."""
        logger.debug("Clearing all session data files...")
        try:
            for file in os.listdir(self.history_dir):
                if file.endswith('_session.json'):
                    os.remove(os.path.join(self.history_dir, file))
        except Exception as e:
            raise IOError(f"Failed to clear session data: {str(e)}")

    def list_archives(self) -> List[str]:
        """Lists all archived session files."""
        try:
            return [f for f in os.listdir(self.history_dir) if f.endswith('_session.json')]
        except FileNotFoundError:
            return []

    def assemble_prompt(self, conversation_history: List[str], user_message: str) -> str:
        """Assemble a complete prompt from the conversation history and new message."""
        return "\n".join(conversation_history) + f"\nUser: {user_message}"

    def report_current_persona(self) -> str:
        """Returns the name of the current persona."""
        if self._current_persona:
            return self._current_persona.get('name', 'Unknown')
        return 'No persona loaded'

    def sync_personas_with_behavior(self):
        """Ensure that the current persona syncs with the latest behavior."""
        if self._current_persona:
            filepath = os.path.join(self.config.personas_dir, f"{self._current_persona['name']}_persona.json")
            logger.debug(f"Syncing persona to: {filepath}")
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(self._current_persona, file, ensure_ascii=False, indent=4)

    def summarize_history(self):
        """Summarizes the current session's message history."""
        history = self.session_data.get("history", [])
        return "\n".join(history[-5:]) if history else "(No recent history.)"
