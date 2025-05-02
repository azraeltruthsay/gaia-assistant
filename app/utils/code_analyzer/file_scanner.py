# /app/utils/code_analyzer/file_scanner.py

import os
import logging
from typing import Optional, List, Dict

logger = logging.getLogger("GAIA")


def load_code_tree(root_path: str = "/app", extensions: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Load source code files from the given directory tree.

    Args:
        root_path: Directory to walk from (default: /app)
        extensions: List of extensions to include (default: common code/doc types)

    Returns:
        Dictionary mapping relative paths to file contents.
    """
    if extensions is None:
        extensions = [".py", ".md", ".json", ".yml"]

    code_map = {}

    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            if any(fname.endswith(ext) for ext in extensions):
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, root_path)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        code_map[rel_path] = f.read()
                except Exception as e:
                    logger.warning(f"Failed to read {full_path}: {e}")

    logger.info(f"Loaded {len(code_map)} code files from {root_path}")
    return code_map