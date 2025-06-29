# dev_matrix.json Schema Reference

This document defines the expected structure of the `dev_matrix.json` file used by GAIA for task management and CI/CD purposes.

## Schema Structure

The `dev_matrix.json` file is a JSON array of task objects.  
Each task object has the following fields:

| Field     | Type     | Description                                       | Example                               |
|-----------|----------|---------------------------------------------------|---------------------------------------|
| `task`    | string   | The name of the task                              | `"Thought seed creation tooling"`     |
| `status`  | string   | The current status (`open` or `resolved`)         | `"resolved"`                          |
| `urgency` | string   | The urgency level (`low`, `medium`, `high`)       | `"high"`                              |
| `impact`  | string   | The impact level (`low`, `medium`, `high`)        | `"medium"`                            |
| `source`  | string   | The origin of the task (e.g., `"bootstrap"`)      | `"bootstrap"`                         |
| `created` | timestamp| The task creation time (ISO-8601 format)          | `"2025-06-04T12:34:56Z"`              |
| `resolved`| timestamp| The resolution time (if applicable)               | `"2025-06-04T15:22:10Z"` (optional)   |

## Usage Notes

- GAIA must reason about this schema when editing `dev_matrix.json`.
- To mark a task as complete, GAIA:
  1. Locates the task object by matching the `task` field.
  2. Updates `status` to `"resolved"`.
  3. Optionally adds a `resolved` timestamp.
  4. Uses `ai.write()` to save the modified file.
