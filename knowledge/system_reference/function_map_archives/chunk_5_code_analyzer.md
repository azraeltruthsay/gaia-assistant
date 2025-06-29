## 🧠 Chunk 5: Code Analyzer

---

### 📄 File: `/app/utils/code_analyzer/base_analyzer.py`
#### Class: `CodeAnalyzer`  
**Docstring:** Coordinates GAIA's code analysis pipeline from scanning to summarization.  
**Tags:** `@tier: 3`, `@code-analysis`, `@llm`

**@params:** `config`, `llm`, `doc_processor`  
**@calls:**  
- `scan_code_directory()`, `load_file_safely()`  
- `extract_docstrings()`, `extract_structure()`  
- `summarize_chunks()`  

#### Methods:
- `__init__(self, config, llm=None, doc_processor=None)`  
- `refresh_code_tree(root_dir=None)`  
- `review_codebase()`

---

### 📄 File: `/app/utils/code_analyzer/chunk_creator.py`
#### Function: `create_chunks(file_path, code, structure)`  
**Docstring:** Breaks code into prioritized chunks for storage and summarization.  
**Tags:** `@tier: 3`, `@chunking`, `@structure`  
**@params:** `file_path`, `code`, `structure`  
**@returns:** `List[Dict]`

---

### 📄 File: `/app/utils/code_analyzer/docstring_extractor.py`
#### Function: `extract_docstrings(code, language="python")`  
**Docstring:** Extracts Python module, function, and class docstrings.  
**Tags:** `@tier: 3`, `@parsing`, `@python`  
**@params:** `code`, `language`  
**@returns:** `dict`

---

### 📄 File: `/app/utils/code_analyzer/file_loader.py`
#### Function: `load_file_safely(path: str)`  
**Docstring:** Loads UTF-8 compatible text from disk, safely skipping binaries.  
**Tags:** `@tier: 3`, `@file-io`, `@utils`  
**@params:** `path: str`  
**@returns:** `str`

---

### 📄 File: `/app/utils/code_analyzer/__init__.py`
**Docstring:** Central import hub for all analyzer components  
**Tags:** `@tier: 3`, `@entrypoint`  
**@imports:**  
- `CodeAnalyzer`, `load_file_safely`, `extract_docstrings`,  
  `extract_structure`, `create_chunks`, `summarize_chunks`, `detect_language`

---

### 📄 File: `/app/utils/code_analyzer/file_scanner.py`
#### Function: `scan_code_directory(root: str)`  
**Docstring:** Recursively scans directories, returning valid code file paths for analysis.  
**Tags:** `@tier: 3`, `@filesystem`, `@scanner`  
**@params:** `root: str`  
**@returns:** `List[str]`

---

### 📄 File: `/app/utils/code_analyzer/language_detector.py`
#### Function: `detect_language(file_path: str, code: str = None)`  
**Docstring:** Detects programming language based on file extension.  
**Tags:** `@tier: 3`, `@language-id`, `@utils`  
**@params:** `file_path`, `code`  
**@returns:** `str`

---

### 📄 File: `/app/utils/code_analyzer/llm_analysis.py`
#### Function: `summarize_chunks(chunks: List[Dict], llm)`  
**Docstring:** Summarizes code chunks using an LLM for natural language interpretation.  
**Tags:** `@tier: 3`, `@llm`, `@summarization`, `@code-analysis`  
**@params:** `chunks`, `llm`  
**@returns:** `str`

---

### 📄 File: `/app/utils/code_analyzer/snapshot_manager.py`
#### Class: `SnapshotManager`  
**Docstring:** Tracks file hashes to detect modified files and prevent redundant analysis.  
**Tags:** `@tier: 3`, `@history`, `@versioning`

**@params:** `config`  
**@calls:**  
- `_load_snapshot()`, `_hash_file(path)`  
- `get_modified_files()`  
- `update_snapshot(...)`

#### Methods:
- `__init__(self, config)`  
- `_load_snapshot()`  
- `_hash_file(path: str)`  
- `update_snapshot(file_list: List[str], base_path="/app")`  
- `get_modified_files() -> List[str]`

---

### 📄 File: `/app/utils/code_analyzer/structure_extractor.py`
#### Function: `extract_structure(code: str, language: str = "python")`  
**Docstring:** Extracts function/class structure and line ranges from Python source code.  
**Tags:** `@tier: 3`, `@structure`, `@python`  
**@params:** `code`, `language`  
**@returns:** `Dict[str, List[Dict]]`
