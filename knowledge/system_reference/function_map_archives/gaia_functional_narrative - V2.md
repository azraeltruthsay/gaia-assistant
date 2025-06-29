## ✨ GAIA Functional System Narrative (Updated)

This document presents a top-down, code-verified, single-context overview of the GAIA system. It helps developers and LLMs understand the architectural and functional interconnections across the project. This version includes the most recent integration of the GAIA Initiative Loop (GIL), topic cache, and self-analysis routing.

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
* Coordinates modules: persona, session, vector store, code analysis, reflection, and GIL
* Initialization loads project, persona, core docs, and LLM (Hermes)
* Key methods:

  * `initialize()`, `generate_response()`, `handle_intent()`, `shutdown()`
  * `set_persona()`, `get_persona()`, `summarize_conversation()`, `embed_documents()`, `analyze_codebase()`
  * `run_self_analysis()` (calls self-analysis routines)
  * `start_initiative_loop()` (starts GIL)

### `GAIAInitiativeLoop` (`initiative_loop.py`)

* Executes during idle time, runs internal initiative logic
* Two-tiered logic:

  1. Calls `should_gaia_initiate()` and enqueues autonomous reflection tasks
  2. Loads prioritized `topic_cache.json` and routes to handlers (e.g. self-analysis)
* Triggered from `AIManager.start_initiative_loop()` during boot

---

## 📁 Knowledge, Indexing, and Vector Embedding

### `DocumentProcessor`, `VectorStoreManager`, and `KnowledgeIndex`

* `DocumentProcessor`: Handles extraction + conversion of raw files → markdown
* `VectorStoreManager`: Uses LangChain + Chroma for retrieval
* `KnowledgeIndex`: Prevents redundant processing across boots

---

## 🛠️ Utility Modules (Key Additions)

### `TopicManager` (`utils/topic_manager.py`)

* Manages topic queue used by GIL
* Stores JSON at `config.topic_cache_path`
* Key methods:

  * `add_topic()`, `resolve_topic()`, `prioritize_topics()`
  * New topics added in `AIManager.generate_response()`

### `InitiativeHandler` (`utils/initiative_handler.py`)

* Returns boolean `should_gaia_initiate()` based on config thresholds and idle time
* Generates default initiative responses if no tasks or topics present

---

## 🧠 Behavior & Reflection Modules

### `SelfReflection` + `run_self_analysis`

* `ethics/self_reflection.py` — evaluates recent chat and codebase state
* `commands/self_analysis_trigger.py` — entrypoint used by GIL topic: `self_analysis`
* Topics are added via GIL or user input; topic `self_analysis` routes to `ai_manager.run_self_analysis()`

---

## 🧪 Background Processing (Retained, with GIL now dominant)

* `task_queue.py`: still used by initiative tasks
* `background_tasks.py`: still handles execution
* However, `idle_monitor.py` + `processor.py` are currently optional due to GIL

---

## 🌐 API and Routes (Relevant to GIL & Topics)

### `/api/chat`

* `routes.py` → `ai_manager.generate_response()`
* Adds topic via `topic_manager.add_topic()`

### `/api/background/status`

* Still used by frontend polling (JS modules)
* May be refactored now that GIL is source of all background behavior

---

## 🖥️ Frontend Integration (GIL-Aware)

* `chat.js`: Calls POST `/api/chat`, parses LLM response
* `background_processing_ui.js`: Continues polling `/api/background/status`, but could transition to GIL-driven triggers

---

## ✅ Status

* GIL wired into boot via `ai_manager.start_initiative_loop()`
* First topic (`self_analysis`) works via topic routing
* All changes tracked and verified in this narrative — **no truncation**
