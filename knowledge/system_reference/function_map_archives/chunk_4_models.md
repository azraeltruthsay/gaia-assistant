## 🧠 Chunk 4: Models

---

### 📄 File: `/app/models/ai_manager.py`
#### Class: `AIManager`  
**Docstring:** Central brain of GAIA. Coordinates major modules, routing, persona, and project logic.  
**Tags:** `@tier: 0`, `@core`, `@boot`, `@routing`

**@params:** `config`  
**@calls:**  
- `/behavior/session_manager.py` → `SessionManager(...)`  
- `/behavior/persona_manager.py` → `PersonaManager(...)`  
- `/utils/vector_store.py` → `VectorStoreManager(...)`  
- `/utils/background_tasks.py` → `background_processor.init(...)`  

#### Methods:
- `__init__(self, config)`
- `initialize(self)`
- `set_persona(self, persona_name)`
- `get_persona(self)`
- `summarize_conversation(self)`
- `embed_documents(self, doc_paths)`
- `analyze_codebase(self)`
- `handle_intent(self, intent, message=None)`
- `generate_response(self, user_input)`  
  → Generates output using GAIA's LLM pipeline. Enforces a layered reflection model where user input is interpreted through Session Instructions, which are themselves governed by a Session Persona that cannot override the Core Persona. Ensures output remains aligned to the AI’s identity framework and ethical boundaries.  
  **Tags:** `@identity_loop`, `@response`, `@core_logic`
- `shutdown(self)`

---

### 📄 File: `/app/models/document.py`
#### Class: `DocumentProcessor`  
**Docstring:** Handles ingestion, markdown conversion, and vector-prep for text documents.  
**Tags:** `@tier: 2`, `@embedding`, `@doc-ingestion`

**@params:** `config`, `llm (optional)`  
**@calls:**  
- `convert_to_markdown()`, `save_markdown()`  
- `process_documents(...) → vector_store.split_and_embed_documents()`

#### Methods:
- `__init__(self, config, llm=None)`
- `extract_text_from_file(self, filepath)`
- `convert_to_markdown(self, text)`
- `save_markdown(self, filepath, content)`
- `load_and_preprocess_data(self, data_path)`
- `process_raw_data(self)`
- `get_document_info(self, filepath)`
- `process_documents(self, directory, tier=None, project=None)`

---

### 📄 File: `/app/models/tts.py`
#### Class: `SpeechManager`  
**Docstring:** Manages text-to-speech voice initialization and playback for GAIA.  
**Tags:** `@tier: 5`, `@placeholder`, `@speech`, `@dnd`

**@params:** `config`  
**@calls:** None (placeholder module)

#### Methods:
- `__init__(self, config)`
- `initialize(self) -> bool`
- `_select_voice(self, voices)`
- `speak(self, text)`
- `stop(self)`
- `set_properties(self, rate=None, volume=None)`

---

### 📄 File: `/app/models/vector_store.py`
#### Class: `VectorStoreManager`  
**Docstring:** Manages document embedding, retrieval, and vector DB persistence.  
**Tags:** `@tier: 2`, `@embedding`, `@search`, `@vectordb`

**@params:** `config`  
**@calls:**  
- `Chroma(...)` for embedding store  
- Connected to `DocumentProcessor.process_documents()`  
- Exported to `ai_manager.vector_store`, `project_manager.get_vector_store_path()`

#### Methods:
- `__init__(self, config)`
- `initialize_store(self)`
- `persist(self)`
- `delete_all_documents(self)`
- `as_retriever(self)`
- `add_documents(self, documents)`
- `split_and_embed_documents(self, raw_documents, source=None)`
