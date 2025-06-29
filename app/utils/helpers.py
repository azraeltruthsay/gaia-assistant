"""
Helper functions for GAIA D&D Campaign Assistant.
"""

import os
import datetime
import logging
from typing import Optional

logger = logging.getLogger("GAIA.Helpers")

def safe_mkdir(path: str):
    """Create a directory if it doesn't already exist."""
    try:
        os.makedirs(path, exist_ok=True)
        logger.debug(f"📁 Ensured directory exists: {path}")
    except Exception as e:
        logger.error(f"❌ Failed to create directory {path}: {e}", exc_info=True)

def get_timestamp(compact: bool = False) -> str:
    """Return ISO 8601 timestamp. Compact format uses YYYYMMDD_HHMMSS."""
    now = datetime.datetime.utcnow()
    return now.strftime("%Y%m%d_%H%M%S") if compact else now.isoformat()

def get_tier_from_path(path: str, config=None) -> Optional[str]:
    """
    Infer the memory tier from a path string using config.tier_names.
    If no config is provided, fallback to default keywords.
    """
    if config:
        tier_keywords = {
            keyword.lower().replace(" ", "_"): str(tier)
            for tier, keyword in config.tier_names.items()
        }
    else:
        # Fallback static keywords if config not passed
        tier_keywords = {
            "identity": "1",
            "system_reference": "0",
            "structured": "2",
            "raw_data": "3",
            "conversations": "1",
            "code_summaries": "0"
        }

    for key, val in tier_keywords.items():
        if key in path.lower():
            return val
    return None
