# 📭 GAIA Functional System Narrative

This document presents a top-down, code-verified, single-context overview of the GAIA system. Its purpose is to help both human developers and LLMs (like GAIA herself) understand the architectural and functional interconnections across the project.

---

## 🌐 Entry Points

* **CLI Boot:** `main.py`

  * Instantiates `Config`, then `AIManager`
  * Calls `ai_manager.initialize()`, optionally runs CLI loop

* **Web Boot:** `runserver.py` → `create_app()` in `__init__.py`

  * Registers Flask app, loads `AIManager`, syncs session/personas
  * Mounts `web.routes` under `web_bp`
  * Adds 404 and 500 error handlers

---

## 🤖 Core System

### `AIManager` (`models/ai_manager.py`)

* Central orchestrator for all GAIA operations
* Coordinates modules: persona, session, vector store, code analysis, reflection
* Initialization loads project, persona, core docs, and LLM (Hermes)
* Key methods:

  * `initialize()`, `generate_response()`, `handle_intent()`, `shutdown()`
  * `set_persona()`, `get_persona()`, `summarize_conversation()`, `embed_documents()`, `analyze_codebase()`

### `DocumentProcessor` (`models/document.py`)

* Extracts, converts, saves, and embeds documents via LangChain
* Converts `.txt`, `.md`, `.rtf`, `.docx` → structured markdown (via LLM)
* Loads processed `.md` files into vector DB for embedding and retrieval
* Key methods:

  * `extract_text_from_file()`, `convert_to_markdown()`, `save_markdown()`
  * `process_raw_data()`, `embed_all_documents()`, `generate_artifacts()`

### `VectorStoreManager` (`models/vector_store.py`)

* Manages GAIA’s embedding store using Chroma + HuggingFace
* Adds, persists, deletes, and queries documents via `LangChain` APIs
* Connects to GAIA’s semantic search and code analyzer pipeline
* Key methods:

  * `initialize_store()`, `add_documents()`, `split_and_embed_documents()`
  * `persist()`, `delete_all_documents()`, `as_retriever()`

---

## 🛠️ Utility Modules

### `Verifier` (`utils/verifier.py`)

* Verifies prompts or system-generated actions before execution
* Provides a safeguard layer against prompt injection or hallucination triggers
* Key methods:

  * `verify_prompt_safety(prompt)` — blocks dangerous language unless whitelisted
  * `verify_action_context(context)` — placeholder for contextual intent checks

### `ProjectManager` (`utils/project_manager.py`)

* Handles project discovery, switching, and initialization
* Interfaces with `config.projects_path` and manages subdirectories per project
* Key methods:

  * `set_active_project()`, `get_project_path()`, `list_available_projects()`
  * `get_instruction_file()`, `get_vector_store_path()`

### `StatusTracker` (`utils/status_tracker.py`)

* Manages GAIA’s internal runtime status flags (thread-safe)
* Stores values via key → value, accessible app-wide
* Key methods:

  * `update()`, `get()`, `as_dict()`, `clear()`

### `TopicManager` (`utils/topic_manager.py`)

* Manages unresolved or deferred topics in GAIA’s memory
* Stores structured `topic_cache.json` including priority, origin, and state
* Key methods:

  * `add_topic()`, `resolve_topic()`, `prune_resolved_topics()`
  * `prioritize_topics()`, `load_topics()`, `save_topics()`

### `HardwareOptimizer` (`utils/hardware_optimization.py`)

* Detects platform and adjusts context size, thread count, or mmap settings
* Includes `force_high_performance` override for LLM inference tuning
* Key method:

  * `optimize_config_for_hardware(config, force_high_performance)`

### `Helpers` (`utils/helpers.py`)

* General-purpose utilities shared across modules
* Key methods:

  * `safe_mkdir()`, `get_timestamp()`, `get_file_hash()`
  * `is_binary_file()`, `parse_tier_from_path()`

### `InitiativeHandler` (`utils/initiative_handler.py`)

* Determines if GAIA should proactively speak or act (GIL logic)
* Combines idle monitoring + topic presence + `initiative_level`
* Key methods:

  * `should_gaia_initiate()`, `gil_check_and_generate()`

### `KnowledgeIndex` (`utils/knowledge_index.py`)

* Persistent mapping of embedded files by hash + tier
* Prevents redundant processing across boots
* Key methods:

  * `add()`, `was_already_processed()`, `remove()`, `list_all()`

## 🛡️ Ethical & Reflective Systems

### `CoreIdentityGuardian` (`ethics/core_identity_guardian.py`)

* Validates prompt + instruction stack against GAIA’s Tier I identity
* Loads immutable traits from `core_identity.json`
* Methods:

  * `load_identity()`, `validate_prompt_stack()`
* Detects forbidden phrases, persona violations, identity overrides

### `EthicalSentinel` (`ethics/ethical_sentinel.py`)

* Monitors system resource usage, infinite loops, and accumulated errors
* Optional Tier I validation if `CoreIdentityGuardian` is available
* Methods:

  * `check_system_resources()`, `check_loop_counter()`, `check_recent_errors()`
  * `register_error()`, `reset_loop()`, `run_full_safety_check()`

### `SelfReflection` (`ethics/self_reflection.py`)

* Periodically runs idle-time or triggered self-reviews
* Calls ethical + identity checks before generating reflective output
* Logs summaries to `thoughtstream_{date}.md`
* Methods:

  * `reflect_on_conversations()`, `reflect_on_codebase()`, `validate_prompt_safety()`
  * `generate_reflective_response()`, `log_thoughtstream()`

## 🧠 Behavior & Persona Modules

### `PersonaTemplate` (`templates/persona_template.py`)

* Defines the canonical structure for a GAIA persona
* Provides `get_blank_persona_template()` for new persona instantiation
* Traits include verbosity, humor, formality, and scope/instruction mapping

### `PersonaAdapter` (`behavior/persona_adapter.py`)

* Wraps persona records into a unified format usable across chat contexts (CLI, web, Discord)
* Converts persona instructions into `SystemMessage` blocks for multi-model delivery
* Handles validation, system message injection, and default formatting behaviors
* Key methods:

  * `__init__(persona_data)`, `to_system_message()`, `apply_defaults()`, `as_dict()`

### `PersonaManager` (`behavior/persona_manager.py`)

* Loads and manages active personas and their instruction sets
* Supports wildcard discovery, embedding-ready structure, and runtime switching
* Wrapped via `PersonaAdapter` for formatting in multi-context outputs
* Key methods:

  * `load_persona()`, `build_persona()`, `set_persona()`
  * `list_personas()`, `list_instructions()`, `create_persona()`
  * `get_current_persona()`, `get_current_persona_name()`

### `SessionManager` (`behavior/session_manager.py`)

* Maintains GAIA's active conversation and memory state per persona
* Handles session start, storage, and summarization
* Uses `/app/web/archives.py` to list and retrieve historical session logs
* Key methods:

  * `initialize_session()`, `load_session_data()`, `save_session()`
  * `clear_session()`, `list_archives()`, `assemble_prompt()`
  * `summarize_history()`, `report_current_persona()`, `sync_personas_with_behavior()`

### `PersonaWriter` (`behavior/persona_writer.py`)

* Writes `persona.json` and instruction overlays to disk
* Optionally embeds persona summaries into the vector DB under `tier: 3_personas`
* Key methods:

  * `create_persona_from_template()`, `_summarize_persona()`, `_embed_to_vectordb()`

### `PersonaCreationManager` (`behavior/creation_manager.py`)

* Drives persona creation interactively or programmatically
* Uses `PersonaWriter` to finalize and save generated personas
* Key methods:

  * `create_persona()`, `generate_persona_from_traits()`
  * `start_persona_creation()`, `process_user_response()` (stub)

### `PersonaTemplateHelper` (`behavior/helper.py`)

* Command-line based interactive filler for blank persona templates
* Key method:

  * `complete_persona_template_interactively()`

### `IntentDetector` (`behavior/intent_detection.py`)

* Lightweight pattern matcher for intent recognition from user text
* Detects commands like `create_behavior`, `trigger_code_analysis`, `normal_chat`
* Key method:

  * `detect_intent(user_input)`

## 🧩 Command & Trigger Modules

### `run_create_persona_command` (`commands/create_persona_command.py`)

* One-shot function to build a new persona from a data dictionary
* Wraps `PersonaCreationManager.create_persona()`
* Key args: `persona_data`, `instructions`, `vectordb_client`

### `create_persona_trigger` (`commands/create_persona_trigger.py`)

* Manually initiates persona creation in Flask or CLI contexts
* Stores `PersonaCreationManager` in app config for reuse
* Includes a preset `create_code_analyzer_persona()` with hardcoded traits

### `run_self_analysis` (`commands/self_analysis_trigger.py`)

* Triggers a full self-review of GAIA’s codebase
* Generates `code_summary.md` and `function_map.md` and embeds both
* Auto-generates `code_analyzer` persona if missing
* Uses: `load_file_safely()`, `extract_structure()`, `summarize_chunks()`

## 🔄 Background Processing Modules

### `BackgroundTask` (`utils/background/background_tasks.py`)

* Core executor for summarization, document embedding, and artifact generation
* Used by task queue, triggered by processor or idle events
* Key methods:

  * `process_conversation_task(task)`, `get_status()`

### `IdleMonitor` (`utils/background/idle_monitor.py`)

* Tracks system idle time, runs idle-triggered events like self-analysis
* Verifies presence of summary files and defers duplicate runs
* Key methods:

  * `mark_active()`, `is_system_idle()`, `idle_check(ai_manager)`

### `BackgroundProcessor` (`utils/background/processor.py`)

* Monitors idle loop, dispatches tasks via queue + reflection check
* Triggers initiative messages using GIL if no task present
* Calls `InitiativeHandler.should_gaia_initiate()` during idle time if queue is empty
* Key methods:

  * `start()`, `stop()`, `run()`

### `TaskQueue` (`utils/background/task_queue.py`)

* Thread-safe FIFO for background jobs
* Tracks pending task count and next job
* Key methods:

  * `add_task()`, `pop_next_task()`, `is_empty()`, `size()`

## 🧪 Code Analyzer Modules

### `__init__` (`utils/code_analyzer/__init__.py`)

* Provides imports for external access:

  * `CodeAnalyzer`, `load_file_safely`, `extract_docstrings`, `extract_structure`, `create_chunks`, `summarize_chunks`, `detect_language`

### `CodeAnalyzer` (`utils/code_analyzer/base_analyzer.py`)

* Central pipeline for code summarization and structure extraction
* Calls all other modules to generate summaries and artifacts
* Key methods:

  * `refresh_code_tree()`, `review_codebase()`

### `file_scanner` (`utils/code_analyzer/file_scanner.py`)

* Recursively scans a root folder and returns all valid code file paths
* Excludes binary formats and known junk dirs
* Method: `scan_code_directory()`

### `file_loader` (`utils/code_analyzer/file_loader.py`)

* Safely reads UTF-8 source files from disk, skips binaries
* Method: `load_file_safely()`

### `language_detector` (`utils/code_analyzer/language_detector.py`)

* Detects language based on file extension
* Method: `detect_language()`

### `docstring_extractor` (`utils/code_analyzer/docstring_extractor.py`)

* Pulls function/class/module docstrings via Python AST
* Method: `extract_docstrings()`

### `structure_extractor` (`utils/code_analyzer/structure_extractor.py`)

* Extracts class/function blocks using AST
* Method: `extract_structure()`

### `chunk_creator` (`utils/code_analyzer/chunk_creator.py`)

* Creates hash-stamped chunks of code for vector embedding
* Method: `create_chunks()`

### `llm_analysis` (`utils/code_analyzer/llm_analysis.py`)

* Summarizes chunk content using an LLM
* Method: `summarize_chunks()`

### `snapshot_manager` (`utils/code_analyzer/snapshot_manager.py`)

* Tracks last-seen hashes for all scanned files
* Detects modifications to reduce duplicate work
* Methods:

  * `update_snapshot()`, `get_modified_files()`

## 💬 Conversation Modules

### `ConversationSummarizer` (`utils/conversation/summarizer.py`)

* Uses the LLM to generate a summary of the conversation history
* Falls back to a placeholder summary if no LLM is configured
* Key method:

  * `generate_summary(messages)`

### `ConversationKeywordExtractor` (`utils/conversation/keywords.py`)

* Extracts a list of the most relevant keywords from message content
* Excludes common stopwords and ranks terms by frequency
* Key method:

  * `extract_keywords(messages, max_keywords)`

### `ConversationManager` (`utils/conversation/manager.py`)

* Orchestrates conversation history, summarization, keyword extraction, and archiving
* Integrates `summarizer`, `keywords`, and `archiver` modules for full session processing
* Clears history after summarization and saves to `structured_data_path/conversations/{persona}/`
* Key methods:

  * `add_message()`, `summarize_and_archive()`, `get_recent_messages()`, `reset()`

### `ConversationArchiver` (`utils/conversation/archiver.py`)

* Saves session archives to JSON files tagged with session ID and persona
* Stored at `structured_data_path/conversations/{persona}/{session_id}.json`
* Method:

  * `archive_conversation(session_id, persona, messages, summary, keywords)`

## 🖥️ Frontend Interface

### `chat.js` (`static/js/chat.js`)

* Manages message input, formatting, and dynamic response display
* Sends user input to `/api/chat`, injects AI reply into DOM

### `project_switcher.js` (`static/js/project_switcher.js`)

* Allows users to switch projects via dropdown or button controls
* Sends updates to `/api/projects/switch/<id>`

### `background.js` (`static/js/background.js`)

* Polls `/api/background/status` every few seconds for queue info
* Updates task status UI elements in real-time

### `background_processing_ui.js` (`static/js/background_processing_ui.js`)

* Coordinates queue progress bar and status display during idle events
* Triggers animations and disables buttons based on active task state

### `code-analyzer.js` (`static/js/code-analyzer.js`)

* Triggers codebase review via `/api/code/analyze` (if enabled)
* Displays returned summary or links to generated artifacts

### `conversation_archives.js` (`static/js/conversation_archives.js`)

* Loads past conversation archives from `/api/archives`
* Provides selector for archive view and restoration

### `troubleshoot.js` (`static/js/troubleshoot.js`)

* Displays diagnostic data such as app status, vector counts, and recent logs
* Pulls from `/api/status`, `/api/healthcheck` (local-only or pending route), `/api/healthcheck`, and internal memory logs

### `archives.js` (`static/js/archives.js`)

* Secondary archive viewer; loads saved summaries or topics
* Used during reflection or debug sessions

### `api.js` (`static/js/api.js`)

* Abstracts `fetch()` and error handling for all backend calls
* Exposes: `postJSON`, `getJSON`, `putJSON`, `deleteRequest`

### `startup.js` (`static/js/startup.js`)

* Initialization logic for preloading UI modules
* Attaches event listeners and executes on DOM ready

### `ui.js` (`static/js/ui.js`)

* Controls tab logic, scrollback, and utility toggles
* Handles debug panel behavior, dynamic section loading

### `app.js` (`static/js/app.js`)

* Master module for triggering coordinated startup logic
* Depends on `startup.js`, `chat.js`, `ui.js`, `api.js`

### `index.html` (`templates/index.html`)

* Main interface file returned by `GET /`
* Connects GAIA frontend to JavaScript modules and API routes
* Hosts dynamic debug tabs and embeds chat tools
* Loads: `chat.js`, `project_switcher.js`, `background.js`, `code-analyzer.js`, `project_switcher.js`, `startup.js`, `ui.js`, `api.js`, `app.js`, `conversation_archives.js`, `troubleshoot.js`, `archives.js`

## 🌐 API and Routes

### `/app/web/routes.py`

* `GET /` → returns UI index page
* `GET /api/status` → returns GAIA’s internal status (via `status_tracker.py`)
* `POST /api/chat` → routes input through `ai_manager.generate_response()`
* `POST /api/persona/<name>` → loads and applies a new persona
* `GET /api/personas` → returns available persona list
* `POST /api/project/<name>` → switches active project
* `GET /api/archives` → returns list of archived conversations
* `GET /api/archive/<id>` → loads specific archive
* `DELETE /api/archive/<id>` → removes an archive
* `GET /api/background/status` → reflects queue status (if background tasks exist)

### `/app/web/project_routes.py`

* `GET /api/projects` → returns all defined project directories
* `GET /api/projects/current` → returns currently active project
* `POST /api/projects/switch/<id>` → activates another project
* `POST /api/projects/create` → makes a new project folder/record
* `PUT /api/projects/update/<id>` → updates an existing project
* `DELETE /api/projects/delete/<id>` → deletes the specified project

### `/app/web/routes_archive.py`

* (Duplicate aliases for `/api/archives` and `/api/archive/<id>` routes)

### `/app/web/archives.py`

* Internal loader used by `SessionManager` to list and retrieve saved conversation logs

### `/app/web/error_handlers.py`

* Flask error handler for 404 and 500 errors
* Returns friendly HTML pages or JSON fallback depending on route

---
