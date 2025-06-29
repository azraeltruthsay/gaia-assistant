# Development Matrix (`dev_matrix.json`) Reference

## Purpose

The `dev_matrix.json` file serves as the primary task list and roadmap for GAIA's self-development. It contains a list of features, bugs, or architectural goals that need to be addressed.

## Schema

Each entry in the JSON array is an object with the following keys:
- `task`: A descriptive name for the task (e.g., "Thought seed creation tooling").
- `status`: The current state, typically "open" or "resolved".
- `urgency`: How quickly the task should be addressed (low, medium, high).
- `impact`: The importance of the task to the overall system (low, medium, high).
- `source`: Where the task originated (e.g., "bootstrap", "reflection", "user_request").
- `created`: An ISO-8601 timestamp of when the task was created.
- `resolved`: An ISO-8601 timestamp added when the status is changed to "resolved".

## Interaction Protocol

When GAIA determines a task is complete, she should use her `ai.read()` and `ai.write()` primitives to load the `dev_matrix.json` file, find the correct task object, update its `status` and `resolved` fields, and write the modified data back to the file.