import os
import json
import hashlib
import logging
from typing import List

logger = logging.getLogger("GAIA.SnapshotManager")

class SnapshotManager:
    """
    Tracks file state hashes to detect changes between boots or scan cycles.
    Prevents unnecessary reprocessing of unchanged code.
    """

    def __init__(self, config):
        self.snapshot_path = os.path.join(config.system_reference_path("code_summaries"), "snapshot.json")
        self.current_snapshot = {}
        self.previous_snapshot = self._load_snapshot()

    def _load_snapshot(self) -> dict:
        if os.path.exists(self.snapshot_path):
            try:
                with open(self.snapshot_path, "r", encoding="utf-8") as f:
                    logger.debug("🗃️ Previous snapshot loaded.")
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load previous snapshot: {e}")
        return {}

    def _hash_file(self, path: str) -> str:
        try:
            with open(path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def update_snapshot(self, file_list: List[str], base_path: str = "/app"):
        """
        Generate new hashes and update current snapshot.
        """
        self.current_snapshot = {
            file: self._hash_file(os.path.join(base_path, file))
            for file in file_list
        }

        try:
            with open(self.snapshot_path, "w", encoding="utf-8") as f:
                json.dump(self.current_snapshot, f, indent=2)
            logger.info("💾 Snapshot updated.")
        except Exception as e:
            logger.error(f"❌ Failed to write snapshot: {e}")

    def get_modified_files(self) -> List[str]:
        """
        Compare current vs previous and return only changed file paths.
        """
        changed = [
            file for file, hash_val in self.current_snapshot.items()
            if self.previous_snapshot.get(file) != hash_val
        ]
        logger.debug(f"🔍 Modified files: {len(changed)}")
        return changed
