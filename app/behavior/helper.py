# behavior_helper.py

def complete_behavior_template_interactively(template_structure, partially_filled=None):
    if partially_filled is None:
        partially_filled = {}
    """
    Completes a behavior template by asking the user for missing fields.
    
    Args:
        template_structure (dict): The master behavior template (with descriptions).
        partially_filled (dict): Fields already provided (optional).
    
    Returns:
        dict: Completed behavior template
    """
    completed = partially_filled.copy()

    for field, field_info in template_structure.items():
        if field not in completed or not completed[field].strip():
            # Ask politely for missing field
            description = field_info.get("description", f"Please provide value for {field}")
            example = field_info.get("example", None)

            print(f"\n🔹 {description}")
            if example:
                print(f"(Example: {example})")

            user_input = input("> ").strip()

            # Handle user refusal
            if user_input.lower() in ["no", "skip", "none", "n/a"]:
                print(f"[Notice] Skipped field '{field}' by user request.")
                continue

            completed[field] = user_input

    return completed
