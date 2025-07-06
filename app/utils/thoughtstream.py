import os, json, time, logging
from datetime import datetime
from app.config import Config
TS_DIR = Config().TS_DIR
os.makedirs(TS_DIR, exist_ok=True)

def write(entry: dict, session_id: str = "default"):
    """
    Append a JSONL line with timestamp + model thought to the current
    session's thought-stream file.
    """
    stamp = datetime.utcnow().isoformat()
    path  = f"{TS_DIR}/{session_id}_{time.strftime('%Y%m%d')}.jsonl"
    entry["ts_utc"] = stamp
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logging.getLogger("GAIA.ThoughtStream").debug("Wrote TS entry: %s", entry.get("type"))