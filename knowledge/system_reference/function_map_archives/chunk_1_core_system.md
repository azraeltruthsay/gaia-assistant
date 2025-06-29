## 🔧 Chunk 1: Core System Files

---

### 📄 File: `/main.py`

#### Function: `main()`
**Docstring:** Launch GAIA’s CLI application and interaction loop  
**Tags:** `@tier: 0`, `@entry`, `@startup`, `@cli`  
**@params:** None  
**@calls:**
- `Config()`
- `AIManager(config)`
- `ai_manager.initialize()`
- `ai_manager.query_campaign_world(query)`
- `verify_prompt_safety(query)`
- `EthicalSentinel().check_ethics()`
- `identity_guardian.should_block()`

---

### 📄 File: `/runserver.py`

#### Function: `start_app()`  
**Docstring:** Entry point for launching GAIA’s web server via Flask  
**Tags:** `@tier: 0`, `@web`, `@startup`  
**@params:** None  
**@calls:**
- `Config()`
- `create_app()`
- `app.run(debug=config.DEBUG_MODE, port=config.PORT)`

---

### 📄 File: `/app/__init__.py`

#### Function: `create_app()`
**Docstring:** App factory pattern for Flask app instantiation  
**Tags:** `@tier: 0`, `@init`, `@flask`  
**@params:** None  
**@calls:**
- `AIManager(config=Config())`
- `ai_manager.initialize()`
- `session_manager.sync_personas_with_behavior()`
- `set_ai_manager(ai_manager)`

#### Function: `start_app()`
**@calls:** `create_app()`

---

### 📄 File: `/app/config.py`

#### Class: `Config`
**Docstring:** Central configuration and path registry for GAIA’s runtime behavior  
**Tags:** `@tier: 0`, `@config`, `@core`  
**@params:** `self`  
**@provides:**
- `self.reflections_path`
- `self.topic_cache_dir`
- `self.personas_path`
- `self.projects_path`
- `self.instructions_path`
- `self.vectordb_path`
- `self.raw_data_path`
- `self.structured_path`

**Methods:**
- `__init__(self)`
- `system_reference_path(self, subdir="")`
- `get_path_for_tier(self, tier)`
- `describe_tier(self, tier)`
- `__repr__(self)`
