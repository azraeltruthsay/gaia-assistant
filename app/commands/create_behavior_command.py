# create_behavior_command.py

from app.behavior_helper import complete_behavior_template_interactively
from app.behavior_manager import BehaviorWriter
from app.templates import BEHAVIOR_TEMPLATE  # This should be your behavior generation template

def handle_create_behavior_command(vectordb_client):
    """
    Handles the 'create new behavior' command interaction.

    Args:
        vectordb_client: The active vector database client
    """
    print("\n🛠️ Starting Behavior Creation Process...\n")

    # Initialize BehaviorWriter
    writer = BehaviorWriter(vectordb_client)

    # Start with empty behavior details
    partial_behavior = {}

    # Dynamically complete the behavior template
    completed_behavior = complete_behavior_template_interactively(BEHAVIOR_TEMPLATE, partial_behavior)

    # Confirm completion
    print("\n✅ Template filled. Saving and embedding behavior...\n")

    # Create the behavior
    success = writer.create_behavior_from_template(completed_behavior)

    if success:
        print("\n🎉 New behavior created and embedded successfully!")
        print(f"Behavior Title: {completed_behavior.get('title', 'Unknown')}")
    else:
        print("\n⚠️ Behavior creation failed or was skipped.")
