## 🛡️ Chunk 7: Ethics and Command Triggers

---

### 📄 File: `/app/ethics/self_reflection.py`
#### Function: `trigger_self_reflection()`  
**Docstring:** Initiates a full diagnostic and introspection routine.  
**Tags:** `@tier: 5`, `@self-diagnostic`, `@background`  
**@params:** _None_  
**@returns:** `None`

---

### 📄 File: `/app/ethics/core_identity_guardian.py`
#### Function: `enforce_identity_safety(response: str) -> str`  
**Docstring:** Applies constraints to prevent unwanted personality drift.  
**Tags:** `@tier: 5`, `@ethics`, `@guardian`  
**@params:** `response: str`  
**@returns:** `str`

---

### 📄 File: `/app/ethics/ethical_sentinel.py`
#### Class: `EthicalSentinel`  
**Docstring:** Monitors output for violations of core ethical constraints.  
**Tags:** `@tier: 5`, `@moderation`, `@ethics`  
**@calls:** `flag_violation()`

**@params:** _None_

#### Methods:
- `__init__(self)`
- `check_output(self, text: str) -> bool`
- `flag_violation(self) -> None`

---

### 📄 File: `/app/commands/create_persona_command.py`
#### Function: `create_persona_command(args: List[str]) -> None`  
**Docstring:** CLI utility for creating a new persona interactively.  
**Tags:** `@tier: 4`, `@cli`, `@persona`  
**@params:** `args: List[str]`  
**@returns:** `None`

---

### 📄 File: `/app/commands/create_persona_trigger.py`
#### Function: `trigger_persona_creation(data: Dict[str, Any]) -> bool`  
**Docstring:** Invoked when a new persona is requested dynamically.  
**Tags:** `@tier: 4`, `@persona`, `@dynamic`  
**@params:** `data: Dict[str, Any]`  
**@returns:** `bool`

---

### 📄 File: `/app/commands/self_analysis_trigger.py`
#### Function: `trigger_self_analysis(config: Config, ai_manager: AIManager) -> None`  
**Docstring:** External call to launch GAIA’s function mapping and self-review.  
**Tags:** `@tier: 5`, `@self-analysis`, `@background`  
**@params:** `config`, `ai_manager`  
**@returns:** `None`
