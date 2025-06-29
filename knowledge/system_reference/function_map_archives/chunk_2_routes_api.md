## 🌐 Chunk 2: Routes and API Endpoints

---

### 📄 File: `/app/web/routes.py`

#### Blueprint: `web_bp`
**Docstring:** Core routes for web UI and user API endpoints  
**Tags:** `@api`, `@routes`, `@tier: 1`  
**@params:**  
- `user_input` via `POST /api/chat`  
- `name` via `/api/project/<name>` and `/api/persona/<name>`  
- `archive_id` via `/api/archive/<archive_id>`

**@calls:**  
- `ai_manager.generate_response()`, `.project_manager.set_project()`, `.persona_manager.load_persona()`  
- `detect_intent()`, `verify_prompt_safety()`  
- `session_manager.load_archive()`, `delete_archive()`  
- `background_processor.get_status()`  

---

### 📄 File: `/app/web/project_routes.py`

#### Blueprint: `projects_bp`  
**Docstring:** REST API for managing GAIA’s multi-project contexts  
**Tags:** `@api`, `@projects`, `@tier: 1`  
**@params:**  
- `project_id` via route path in `switch`, `update`, `delete`  
- `data` from JSON payload in `create` and `update`

**@calls:**  
- `ai_manager.project_manager.switch_project()`, `.get_current_project()`, `.create_project()`  
- Rebinds `core_instructions`, `vector_store.config`, and `vector_store = ...`

---

### 📄 File: `/app/web/routes_archive.py`

#### Blueprint: `future_bp`  
**Docstring:** Additional endpoints for structured conversation archives  
**Tags:** `@api`, `@archive`, `@future`, `@tier: 1`  
**@params:**  
- `archive_id` as route param  
- Uses `ai_manager.conversation_manager.structured_archives_dir`

**@calls:**  
- File system I/O  
- `current_app.config.get("AI_MANAGER")`

---

### 📄 File: `/app/web/archives.py`

#### Blueprint: `archives_bp`  
**Docstring:** Lists and fetches raw `.md` or `.log` conversation files  
**Tags:** `@api`, `@archives`, `@conversation`, `@tier: 1`  
**@params:**  
- `archive_id` as route param  
- Uses `.conversation_manager.archiver.load_archived_conversation()`

---

### 📄 File: `/app/web/error_handlers.py`

#### Blueprint: `errors_bp`  
**Docstring:** HTTP error handlers for user-friendly responses  
**Tags:** `@error`, `@tier: 1`, `@handler`  
**@params:**  
- `error` passed to each handler (`400`, `404`, `405`, `413`, `500`, fallback)  

**@calls:**  
- `logger.warning()` or `.error()` with appropriate HTTP codes

---
