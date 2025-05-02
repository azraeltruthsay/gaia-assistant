# behavior_creation_manager.py

from app.behavior.manager import BehaviorWriter
from app.templates.behavior_template import BEHAVIOR_TEMPLATE

class BehaviorCreationManager:
    def __init__(self, vectordb_client, personalities_path="/personalities/"):
        self.template_structure = BEHAVIOR_TEMPLATE
        self.filled_fields = {}
        self.current_field = None
        self.writer = BehaviorWriter(vectordb_client, personalities_path)
        self.awaiting_user_response = False

    def start_behavior_creation(self):
        """Initialize new behavior creation."""
        self.filled_fields = {}
        self.current_field = self._find_next_missing_field()
        self.awaiting_user_response = True

        if self.current_field:
            return self._generate_question_for_field(self.current_field)
        else:
            return "All fields are already filled. Nothing to do!"

    def process_user_response(self, user_input):
        """Process user input during behavior creation."""
        # === NEW: Allow graceful cancellation
        if user_input.lower() in ["cancel", "stop", "nevermind", "abort"]:
            self.awaiting_user_response = False
            self.filled_fields = {}
            self.current_field = None
            return "🛑 Behavior creation has been canceled as you requested."

        if not self.awaiting_user_response:
            return "No behavior creation is currently active."

        if user_input.lower() in ["no", "skip", "none", "n/a"]:
            self.filled_fields[self.current_field] = ""
        else:
            self.filled_fields[self.current_field] = user_input

        self.current_field = self._find_next_missing_field()

        if self.current_field:
            return self._generate_question_for_field(self.current_field)
        else:
            self.awaiting_user_response = False
            return self._finalize_behavior()

    def _find_next_missing_field(self):
        for field in self.template_structure.keys():
            if field not in self.filled_fields or not self.filled_fields[field].strip():
                return field
        return None

    def _generate_question_for_field(self, field_name):
        field_info = self.template_structure[field_name]
        question = f"🔹 {field_info['description']}"
        if field_info.get("example"):
            question += f"\n(Example: {field_info['example']})"
        return question

    def _finalize_behavior(self):
        success = self.writer.create_behavior_from_template(self.filled_fields)
        if success:
            return "🎉 The new behavior has been created and embedded successfully!"
        else:
            return "⚠️ Failed to create the behavior. Some fields may have been missing."
