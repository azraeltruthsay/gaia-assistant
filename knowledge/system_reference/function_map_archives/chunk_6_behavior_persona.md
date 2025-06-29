## 🧬 Chunk 6: Behavior and Persona System

---

### 📄 File: `/app/behavior/persona_manager.py`
#### Class: `PersonaManager`  
**Docstring:** Loads, switches, and manages personas and their instruction overlays.  
**Tags:** `@persona`, `@behavior`, `@tier: 4`  
**@params:** `personas_path`  
**@calls:** `persona_writer`, `session_manager`

#### Methods:
- `__init__(self, personas_path)`
- `load_persona(persona_name)`
- `build_persona(personality_data, instructions)`
- `get_current_persona()`
- `set_persona(persona_name)`
- `list_personas()`
- `list_instructions(persona_name)`
- `create_persona(name, template, instructions=None) -> bool`
- `get_current_persona_name()`

---

### 📄 File: `/app/behavior/session_manager.py`
#### Class: `SessionManager`  
**Docstring:** Maintains user, project, and session continuity.  
**Tags:** `@persona`, `@context`, `@tier: 4`, `@persistence`  
**@params:** `config`  
**@calls:** `persona_manager`, `helpers.summarize_history`, `os`, `json`

#### Methods:
- `__init__(self, config)`
- `initialize_session(style)`
- `load_persona(style)`
- `load_session_data(style)`
- `save_session(session_data)`
- `clear_session()`
- `list_archives()`
- `assemble_prompt(conversation_history, user_message)`
- `report_current_persona()`
- `sync_personas_with_behavior()`
- `summarize_history(self)`  
  **Summary:** Returns the last 5 items in current session history.  
  **Tags:** `@summary`, `@tier: 4`

---

### 📄 File: `/app/behavior/persona_writer.py`
#### Class: `PersonaWriter`  
**Docstring:** Handles writing persona data and instructions to disk and embedding to vector store.  
**Tags:** `@persona`, `@embedding`, `@tier: 4`  
**@params:** `vectordb_client`, `personas_path`  
**@calls:** `vector_store`, `json`, `os`

#### Methods:
- `__init__(self, vectordb_client, personas_path)`
- `create_persona_from_template(template, instructions=None)`
- `_summarize_persona(template)`
- `_embed_to_vectordb(summary_text, tag)`

---

### 📄 File: `/app/behavior/creation_manager.py`
#### Class: `PersonaCreationManager`  
**Docstring:** Manages persona creation from templates and trait definitions.  
**Tags:** `@persona`, `@behavior`, `@tier: 4`  
**@params:** `vectordb_client`, `personas_path`  
**@calls:** `persona_writer`, `json`, `prompt_toolkit`

#### Methods:
- `__init__(self, vectordb_client, personas_path)`
- `start_persona_creation()`
- `process_user_response(input_str)`
- `create_persona(template, instructions)`
- `generate_persona_from_traits(name, tone, context, traits=None, instructions=None)`

---

### 📄 File: `/app/behavior/helper.py`
#### Function(s)  
**Docstring:** Interactive CLI helper for completing persona templates.  
**Tags:** `@persona`, `@interactive`, `@tier: 4`  
**@params:** `template_structure`, `partially_filled`  
**@returns:** `dict`

- `complete_persona_template_interactively(template_structure, partially_filled=None)`

---

### 📄 File: `/app/behavior/intent_detection.py`
#### Function(s)  
**Docstring:** Basic pattern-matching intent classifier for behavior commands.  
**Tags:** `@intent`, `@routing`, `@tier: 4`  
**@params:** `user_input`  
**@returns:** `str`

- `detect_intent(user_input) -> str`
