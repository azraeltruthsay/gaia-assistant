import os
import time
import psutil
import logging
from pathlib import Path
from app.config import Config
from app.memory.status_tracker import GAIAStatus

logger = logging.getLogger("GAIA.TelemetricSenses")

config = Config()

# File telemetry config
WATCHED_EXTENSIONS = [".py", ".md", ".json"]
WATCHED_DIRS = ["app", "knowledge/system_reference"]
MODIFIED_TIMES = {}

# Initialize loop counter and last activity timestamp
if GAIAStatus.get("loop_tick_count") is None:
    GAIAStatus.update("loop_tick_count", 0)
if GAIAStatus.get("last_loop_time") is None:
    GAIAStatus.update("last_loop_time", time.time())


def tick():
    GAIAStatus.update("loop_tick_count", GAIAStatus.get("loop_tick_count", 0) + 1)
    GAIAStatus.update("last_loop_time", time.time())
    logger.debug("🔁 Loop ticked.")


def update_token_usage(count: int):
    GAIAStatus.update("last_token_count", count)
    GAIAStatus.update("last_token_time", time.time())
    logger.debug(f"🔢 Tokens used: {count}")


def scan_files():
    changes = []
    for root_dir in WATCHED_DIRS:
        for dirpath, _, filenames in os.walk(root_dir):
            for fname in filenames:
                if any(fname.endswith(ext) for ext in WATCHED_EXTENSIONS):
                    fpath = Path(dirpath) / fname
                    mtime = int(fpath.stat().st_mtime)
                    if fpath not in MODIFIED_TIMES:
                        MODIFIED_TIMES[fpath] = mtime
                    elif MODIFIED_TIMES[fpath] != mtime:
                        changes.append(str(fpath))
                        MODIFIED_TIMES[fpath] = mtime
    if changes:
        GAIAStatus.update("file_changes", changes)
        GAIAStatus.update("last_file_scan", time.time())
        logger.info(f"📂 Detected file changes: {changes}")


def system_health():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage(".").percent
    GAIAStatus.update("cpu_usage", cpu)
    GAIAStatus.update("mem_usage", mem)
    GAIAStatus.update("disk_usage", disk)
    logger.debug(f"🩺 System Health - CPU: {cpu}%, Mem: {mem}%, Disk: {disk}%")


def get_telemetry_summary() -> str:
    tick_count = GAIAStatus.get("loop_tick_count", 0)
    token_use = GAIAStatus.get("last_token_count", 0)
    file_changes = GAIAStatus.get("file_changes", [])
    cpu = GAIAStatus.get("cpu_usage", 0)
    mem = GAIAStatus.get("mem_usage", 0)
    disk = GAIAStatus.get("disk_usage", 0)

    summary = [
        f"[Telemetry Summary]",
        f"Ticks since boot: {tick_count}",
        f"Last token usage: {token_use} tokens",
        f"System Load — CPU: {cpu}%, Mem: {mem}%, Disk: {disk}%",
    ]

    if file_changes:
        summary.append(f"Changed files: {len(file_changes)} (e.g. {file_changes[0]})")

    return "\n".join(summary)


# Optional: Periodic combined update (can be called by loop or reflection cycle)
def full_sense_sweep():
    tick()
    scan_files()
    system_health()
    logger.info("👁️ Telemetric senses sweep complete.")
    logger.debug(get_telemetry_summary())
