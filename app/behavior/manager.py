# behavior_manager.py

import os
import re

class BehaviorWriter:
    def __init__(self, vectordb_client, personalities_path="/personalities/"):
        """
        Initializes the Behavior Writer.

        Args:
            vectordb_client: Vector database client instance.
            personalities_path: Path to local personalities directory.
        """
        self.vectordb = vectordb_client
        self.personalities_path = personalities_path

    def create_behavior(self, title, style, context, priority, instructions):
        """
        Creates a new behavior module.

        Args:
            title (str): Title of the behavior.
            style (str): Unique style key (e.g., "formal", "playful").
            context (str): General context (e.g., "technical", "creative").
            priority (str): Importance level ("high", "medium", "low").
            instructions (str): Core instruction text.

        Returns:
            bool: True if created and embedded successfully, False if skipped.
        """
        filename = f"{style}.md"
        filepath = os.path.join(self.personalities_path, filename)

        
        # NEW: Ensure the folder exists before writing
        os.makedirs(self.personalities_path, exist_ok=True)

        # Check if file already exists
        if os.path.exists(filepath):
            print(f"[Behavior Writer] Behavior file {filename} already exists. Skipping creation.")
            return False

        # Build the markdown content
        content = f"""Title: {title}
Style: {style}
Context: {context}
Priority: {priority}

---
{instructions}
"""

        # Save locally
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[Behavior Writer] Saved new behavior to {filepath}")

        # Embed immediately
        embed_doc = {
            "type": "behavior",
            "title": title,
            "style": style,
            "context": context,
            "priority": priority,
            "content": instructions
        }
        self.vectordb.add(embed_doc)

        print(f"[Behavior Writer] Embedded new behavior '{title}' into VectorDB.")

        return True

    def interactive_behavior_creation(self):
        """
        CLI-style guided creation of a new behavior module.
        """
        print("\n🎨 Behavior Creation Wizard 🎨")
        title = input("Enter behavior TITLE: ").strip()
        style = input("Enter behavior STYLE (unique key, e.g., 'cheerful_mentor'): ").strip()
        context = input("Enter behavior CONTEXT (general, technical, creative, gaming, etc.): ").strip()
        priority = input("Enter behavior PRIORITY (high, medium, low): ").strip()
        print("Now enter the core INSTRUCTIONS (finish by typing 'END' on a new line):")

        # Multi-line input for instructions
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)

        instructions = "\n".join(lines)

        # Create the behavior
        self.create_behavior(title, style, context, priority, instructions)

    def create_behavior_from_template(self, template_filled):
        """
        Creates a new behavior from a filled-out template.

        Args:
            template_filled (dict): Dictionary containing fields (title, style, context, priority, instructions)
        """
        required_fields = ["title", "style", "context", "priority", "instructions"]

        if not all(field in template_filled for field in required_fields):
            print("[Behavior Writer] ERROR: Missing fields in template.")
            return False

        return self.create_behavior(
            title=template_filled["title"],
            style=template_filled["style"],
            context=template_filled["context"],
            priority=template_filled["priority"],
            instructions=template_filled["instructions"]
        )
