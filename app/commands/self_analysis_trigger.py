import os
import logging
from pathlib import Path

from app.config import Config
from app.behavior.persona_manager import PersonaManager
from app.templates.persona_template import get_blank_persona_template
from app.utils.code_analyzer import (
    detect_language,
    extract_docstrings,
    extract_structure,
    create_chunks,
    summarize_chunks
)
from app.utils.code_analyzer.file_loader import load_file_safely
from app.models.vector_store import VectorStoreManager

logger = logging.getLogger("GAIA.SelfAnalysis")

# Output paths
SUMMARY_DIR = Path("/app/knowledge/system_reference/code_summaries")
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_FILE = SUMMARY_DIR / "code_summary.md"
FUNCTION_MAP_FILE = SUMMARY_DIR / "function_map.md"

PERSONA_NAME = "code_analyzer"
INSTRUCTION_TEXT = """
You are GAIA, a code analysis assistant. Your job is to review the existing codebase,
extract key structures (classes, functions), summarize each file, and build a function map.
Return your output as markdown, saved to the system reference directory.
"""

def run_self_analysis(ai_manager):
    logger.info("Starting self-analysis routine")

    # 1. Create persona if missing
    persona_manager = PersonaManager(personas_dir=ai_manager.config.personas_dir)
    if not persona_manager.persona_exists(PERSONA_NAME):
        template = get_blank_persona_template(PERSONA_NAME)
        template["default_instruction"] = INSTRUCTION_TEXT
        persona_manager.create_persona(PERSONA_NAME, template)
        logger.info("✅ Created missing code_analyzer persona")

    ai_manager.set_persona(PERSONA_NAME)

    # 2. Analyze codebase directory
    code_dir = Path("/gaia-assistant/app")
    all_summaries = []
    function_map_lines = ["# Function Map\n"]

    for py_file in code_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        code = load_file_safely(py_file)
        if not code:
            continue

        lang = detect_language(py_file, code)
        if lang != "python":
            continue

        docstrings = extract_docstrings(code)
        structure = extract_structure(code)
        chunks = create_chunks(str(py_file), code, structure)
        summary = summarize_chunks(chunks, ai_manager.llm)

        all_summaries.append(f"## {py_file.name}\n{summary}\n")

        for section in structure.get("functions", []) + structure.get("classes", []):
            function_map_lines.append(f"- `{py_file.name}` → `{section['name']}`: {section['type']}")

    # 3. Write markdown outputs
    SUMMARY_FILE.write_text("\n\n".join(all_summaries), encoding="utf-8")
    FUNCTION_MAP_FILE.write_text("\n".join(function_map_lines), encoding="utf-8")

    logger.info(f"✅ Saved summary to {SUMMARY_FILE}")
    logger.info(f"✅ Saved function map to {FUNCTION_MAP_FILE}")

    # 4. Embed summaries into vector DB
    vector_store: VectorStoreManager = ai_manager.vector_store_manager
    vector_store.split_and_embed_documents(
        raw_documents=[SUMMARY_FILE.read_text(), FUNCTION_MAP_FILE.read_text()],
        source="self_analysis"
    )

    # 5. Completion notice
    return (
        "Codebase successfully analyzed. \n"
        "Summaries saved to `/knowledge/system_reference/code_summaries/`. \n"
        "Ready for your next command."
    )
