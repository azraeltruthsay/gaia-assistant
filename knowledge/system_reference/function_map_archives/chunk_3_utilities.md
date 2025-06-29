## 🛠 Chunk 3: Utilities

---

### 📄 File: `/app/utils/helpers.py`
**Docstring:** General-purpose helper functions for directories, timestamps, and tier parsing  
**Tags:** `@utils`, `@tier: 2`

#### Functions:
- `safe_mkdir(path: str)`  
  **@params:** `path: str`  
  **@calls:** `os.makedirs`  

- `get_timestamp(compact: bool = False) -> str`  
  **@params:** `compact: bool = False`  

- `get_tier_from_path(path: str, config=None) -> Optional[str]`  
  **@params:** `path`, `config`

---

### 📄 File: `/app/utils/status_tracker.py`
**Docstring:** Tracks real-time system status across concurrent GAIA tasks  
**Tags:** `@status`, `@tier: 2`, `@concurrency`

#### Class: `GAIAStatus`
- `update(key: str, value)`  
- `get(key: str, default=None)`  
- `as_dict()`  
- `clear()`

---

### 📄 File: `/app/utils/topic_manager.py`
**Docstring:** Maintains and prioritizes GAIA’s internal topic backlog  
**Tags:** `@topic`, `@tier: 3`, `@background`

#### Functions:
- `add_topic(path, topic)`
- `resolve_topic(path, topic_id)`
- `update_topic(path, topic_id, updates)`
- `prune_resolved_topics(path)`
- `list_topics(path, include_resolved=False)`
- `prioritize_topics(path, top_n=5)`

---

### 📄 File: `/app/utils/initiative_handler.py`
**Docstring:** Controls GAIA's self-initiated messaging and idle-time interventions  
**Tags:** `@initiative`, `@trigger`, `@tier: 4`

#### Functions:
- `load_initiative_level(config)`
- `should_gaia_initiate(user_idle_minutes, config)`
- `format_initiative_message(topic)`
- `gil_check_and_generate(user_idle_minutes, config)`

---

### 📄 File: `/app/utils/hardware_optimization.py`
**Docstring:** Tunes performance settings based on system resources  
**Tags:** `@system`, `@optimization`, `@tier: 0`

#### Function:
- `optimize_config_for_hardware(config, force_high_performance=False)`  
  **@params:** `config`, `force_high_performance`

---

### 📄 File: `/app/utils/knowledge_index.py`
**Docstring:** Manages knowledge deduplication and hash tracking  
**Tags:** `@indexing`, `@embedding`, `@tier: 2`

#### Class: `KnowledgeIndex`
- `__init__(self, path)`
- `load()`
- `save()`
- `add(file_path, hash_value, tier)`
- `get(file_path)`
- `get_hash(file_path)`
- `was_already_processed(file_path, hash_value)`
- `remove(file_path)`
- `list_all()`

---

### 📄 File: `/app/utils/project_manager.py`
**Docstring:** Manages dynamic project selection and folder scaffolding  
**Tags:** `@project`, `@routing`, `@tier: 2`

#### Class: `ProjectManager`
- `__init__(self, config)`
- `ensure_default_projects_exist()`
- `set_active_project(project_name)`
- `get_project_path(subdir="")`
- `list_available_projects()`
- `get_vector_store_path()`
- `get_instruction_file()`
- `describe()`
