# GAIA Primitives Reference

This document defines GAIA’s core primitive functions, their usage, and intended reasoning pathways.

## Primitives

| Function | Description | Example Usage |
|----------|-------------|---------------|
| `ai.read(filepath)` | Read the full content of a file. | `ai.read("app/dev_matrix.json")` |
| `ai.write(filepath, content)` | Write content to a file, overwriting it. | `ai.write("app/dev_matrix.json", <new content>)` |
| `ai.vector_query(query)` | Query GAIA’s embedded knowledge base. | `ai.vector_query("What is the schema of dev_matrix.json?")` |
| `ai.helper.queue_thought_seed(prompt)` | Queue a reflection prompt for later review. | `ai.helper.queue_thought_seed("Should I refactor the file structure?")` |
| `ai.helper.process_thought_seeds()` | Process and reflect on all queued thought seeds. | `ai.helper.process_thought_seeds()` |
| `embed_gaia_reference()` | Re-embed GAIA’s core knowledge into the vector store. | `embed_gaia_reference()` |
| `ai.helper.sketch(title, content)` | Append a new sketch entry with a title and content. | `ai.helper.sketch("Idea for vector refactor", "Should we hash files per line?")` |
| `ai.helper.show_sketchpad()` | View all current sketches with timestamps. | `ai.helper.show_sketchpad()` |
| `ai.helper.clear_sketchpad()` | Clear all sketches (backed up with timestamp). | `ai.helper.clear_sketchpad()` |

## Core Primitives
These can be directly invoked by GAIA or the user via `ai.<primitive>()`:
- `ai.read(filepath)`
- `ai.write(filepath, content)`
- `ai.vector_query(query)`
- `ai.helper.queue_thought_seed(prompt)`
- `ai.helper.process_thought_seeds()`
- `ai.helper.generate_json_schema(filepath)`
- `ai.helper.update_json(filepath, key_path, new_value)`

## Extended Utility Functions (via `ai.helper`)
These are powerful helper tools exposed via GAIA's internal limb:
- `ai.helper.update_json(filepath, key_path, new_value)` — Safely update nested keys in a JSON file with a backup.
- `ai.helper.generate_json_schema(filepath)` — Auto-generates a `.schema.json` file alongside any valid JSON input.
- `ai.helper.sketch(title, content)` — Appends a freeform entry to the sketchpad.
- `ai.helper.show_sketchpad()` — Returns the current sketchpad content.
- `ai.helper.clear_sketchpad()` — Clears and backs up the sketchpad.

## Usage Philosophy

GAIA proposes **actions** using these primitives, not pre-coded helpers.  
She reasons about schemas, file contents, and system state to decide **when** and **how** to call these primitives.  

For example, to update `dev_matrix.json`, GAIA would:  
1. `ai.read()` to load the file.  
2. Find the correct task by label.  
3. Edit the task’s status.  
4. `ai.write()` the new file.

No task-specific helpers (e.g., `mark_task_complete()`) are used. GAIA reasons using **core knowledge + primitives only**.

