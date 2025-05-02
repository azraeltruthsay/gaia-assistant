import os
import json
import hashlib
from typing import Dict, Tuple
from datetime import datetime
import logging

logger = logging.getLogger("GAIA")

class SnapshotManager:
    def __init__(self, snapshot_path="/app/shared/gaia_code_snapshot.json"):
        self.snapshot_path = snapshot_path
        self.current_snapshot = {}
        self.previous_snapshot = self._load_existing_snapshot()

    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _load_existing_snapshot(self) -> Dict:
        if os.path.exists(self.snapshot_path):
            try:
                with open(self.snapshot_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load previous snapshot: {e}")
        return {}

    def generate_snapshot(self, code_tree: Dict[str, str], summaries: Dict[str, str]) -> Dict:
        """Create a new snapshot with hashes and summaries."""
        snapshot = {}
        for path, content in code_tree.items():
            hash_val = self._hash_content(content)
            snapshot[path] = {
                "hash": hash_val,
                "summary": summaries.get(path, ""),
                "updated": datetime.utcnow().isoformat()
            }
        return snapshot

    def get_files_to_update(self, code_tree: Dict[str, str]) -> Dict[str, str]:
        """
        Identify files whose content has changed vs previous snapshot.
        Returns a dictionary: path → content (for changed files only).
        """
        changed = {}
        for path, content in code_tree.items():
            new_hash = self._hash_content(content)
            prev_hash = self.previous_snapshot.get(path, {}).get("hash")
            if new_hash != prev_hash:
                changed[path] = content
        logger.info(f"🔍 {len(changed)} files changed since last snapshot")
        return changed

    def update_snapshot_file(self, new_snapshot: Dict):
        try:
            with open(self.snapshot_path, "w", encoding="utf-8") as f:
                json.dump(new_snapshot, f, indent=2)
            logger.info(f"✅ Snapshot updated: {self.snapshot_path}")
        except Exception as e:
            logger.error(f"❌ Failed to write snapshot file: {e}")
