"""
GAIA Primitives (pillar-compliant, robust)
- Exposes: read, write, vector_query, shell (all core safe primitives)
"""

import logging
import os
import subprocess
from pathlib import Path
from app.utils.vector_indexer import vector_query as _vector_query

logger = logging.getLogger("GAIA.Primitives")

def read(filepath):
    try:
        path = Path(filepath)
        if not path.exists():
            logger.warning(f"File not found: {filepath}")
            return f"⚠️ File not found: {filepath}"
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return f"❌ Error reading file: {e}"

def write(filepath, content):
    try:
        path = Path(filepath)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return "✅ Write successful."
    except Exception as e:
        logger.error(f"Error writing file {filepath}: {e}")
        return f"❌ Error writing file: {e}"

def vector_query(query):
    try:
        return _vector_query(query)
    except Exception as e:
        logger.error(f"Error in vector_query: {e}")
        return f"❌ Error in vector_query: {e}"

def shell(command):
    from app.config import Config
    config = Config()
    SAFE_EXECUTE_FUNCTIONS = config.SAFE_EXECUTE_FUNCTIONS
    try:
        cmd_name = command.split()[0] if command.strip() else ""
        if cmd_name not in SAFE_EXECUTE_FUNCTIONS:
            logger.warning(f"Rejected unsafe shell command: {command}")
            return f"❌ Unsafe shell command: {cmd_name} is not permitted."
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logger.error(f"Shell command error: {result.stderr.strip()}")
            return f"❌ Shell error: {result.stderr.strip()}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"Shell command timed out: {command}")
        return f"❌ Shell command timed out."
    except Exception as e:
        logger.error(f"Shell execution error: {e}")
        return f"❌ Shell execution error: {e}"
