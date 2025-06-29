# GAIA Function Reference Map  
*Updated: June 2025 – Post-Refactor*

This reference maps key classes and functions in GAIA’s Python codebase as of the June 2025 refactor, including arguments and docstrings when available.

---

## File: `main.py`

### Function: `main()`
**Args:** *(none)*  
**Docstring:** Main CLI entrypoint for GAIA.  
**Tags:** `@tier: 0`, `@entry`, `@calls: AIManager.initialize, ai.read, ai.write, CouncilManager.propose`

---

## File: `runserver.py`

### Function: `start_app()`
**Args:** *(none)*  
**Docstring:** Starts the Flask API server for GAIA.  
**Tags:** `@tier: 0`, `@calls: create_app, app.run`

---

## File: `__init__.py`

### Function: `create_app()`
**Args:** *(none)*  
**Docstring:** Creates and configures the Flask app instance.  
**Tags:** `@tier: 0`, `@used-in: start_app`, `@calls: AIManager.initialize, PersonaManager.sync, register_routes`

---

## File: `config.py`

### Class: `Config`
**Docstring:** Centralized configuration for paths, tiers, and environment.

#### `__init__(self)`
Initializes configuration, loads environment variables, sets paths.

#### `_initialize_directories(self)`
Ensures required directories exist.
**Tags:** `@background: true`

#### `system_reference_path(self, subdir="")`
Returns a system reference path.

#### `get_path_for_tier(self, tier)`
Maps knowledge tier to directory.

#### `describe_tier(self, tier)`
Returns description for a knowledge tier.

#### `__repr__(self)`
Returns string representation.

---

## File: `ai_manager.py`

### Class: `AIManager`
Manages main AI loop, state, session, and user interaction.

#### `initialize(self)`
Initializes state and pipeline.

#### `process_input(self, user_input)`
Processes user input, handles session routing.

#### `conversation_history`
Session-level conversation state.

---

## File: `session_manager.py`

### Class: `SessionManager`
Manages per-user, per-project, per-session context.

#### `get_session(self, user_id, project_id)`
Retrieves or creates session.

#### `prune_history(self, session_id)`
Manual or automatic trimming of session logs.

#### `inject_history(self, session_id, conversation)`
Injects history for stateful continuity.

---

## File: `persona_manager.py`

### Class: `PersonaManager`
Handles persona/instruction selection and injection.

#### `select_persona(self, name)`
Selects persona.

#### `create_persona(self, name, config)`
Creates new persona dynamically.

#### `sync(self)`
Ensures persona state matches config/files.

---

## File: `inner_monologue.py`

### Function: `think(input_data)`
Generates system’s immediate thought/response.  
**Tags:** `@pipeline`, `@calls: self_reflection.reflect, CouncilManager.propose`

---

## File: `self_reflection.py`

### Function: `reflect(recent_activity)`
Performs self-review, proposes corrections or seeds.  
**Tags:** `@pipeline`, `@calls: thought_seeds.create`

---

## File: `thought_seeds.py`

### Function: `create(seed_content)`
Creates new atomic “thought seed.”  
**Tags:** `@knowledge`, `@pipeline`

---

## File: `thought_stream.py`

### Function: `log(seed)`
Logs thought seed or stream for session/project.  
**Tags:** `@knowledge`

### Function: `replay(session_id)`
Replays stream for session/project.  
**Tags:** `@knowledge`

---

## File: `council_manager.py`

### Class: `CouncilManager`
Orchestrates council-driven reflection, voting, and consensus.

#### `propose(self, message)`
Submits proposal to council.

#### `deliberate(self, proposal)`
Runs model voting/deliberation cycle.

#### `decide(self)`
Finalizes action/decision or escalates to user.

---

## File: `observer_manager.py`

### Class: `ObserverManager`
Assigns model as observer/validator for output.

#### `assign_observer(self, responder)`
Chooses idle model as observer.

#### `interrupt(self, token_stream)`
Allows observer to interrupt/refute mid-stream or after.

---

## File: `mcp_server.py` / `gcp_server.py`

### Function: `receive(message)`
Receives JSON message over HTTP/WireGuard.

### Function: `broadcast(message)`
Sends message to council models.

---

## File: `external_voice.py`

### Function: `listen()`
Accepts audio input.

### Function: `speak(output)`
Outputs synthesized speech.

---

## File: `resource_monitor.py`

### Class: `ResourceMonitor`
Tracks resources, switches model load if low.

#### `check(self)`
Checks CPU/mem/etc.

#### `adjust_model_load(self)`
Activates/deactivates models by resource state.

---

## File: `safe_execute.py`

### Function: `whitelist(command)`
Checks/approves command for execution.

### Function: `audit_log(command)`
Logs all executions.

---

## File: `knowledge_manager.py`

### Class: `KnowledgeManager`
Handles tiered knowledge, embedding, validation.

#### `validate_tiers(self)`
Ensures all knowledge tiers are mapped and current.

#### `embed_gaia_reference(self)`
Embeds changed files via hash.

#### `hash_compare(self, file_path)`
Compares hash to detect change.

---

## File: `functions_reference.py`

### Function: `generate()`
Builds/updates this reference.

---

## File: `system_narrative.py`

### Function: `update(content)`
Updates system narrative.

---

## File: `routes.py`, `project_routes.py` (Web API/CLI)

#### Standard Flask or CLI route handlers for:
- Status: `/status`, `/api/status`
- Chat: `/api/chat`
- Projects: `/api/projects`, `/api/projects/current`, `/api/projects/switch/<id>`, `/api/projects/create`
- Personas: `/api/personas`, `/api/persona/<name>`
- Archives: `/api/archives`, `/api/archive/<id>`, `/api/archive/<id>/delete`
- Background: `/api/background/status`

---

*This reference covers current major modules and functions; further details (args, docstrings, and line numbers) can be expanded on request.*

