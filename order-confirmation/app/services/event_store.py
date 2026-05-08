import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_DB_PATH = Path("events.db")
_TTL_HOURS = 24


def init_db() -> None:
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_events (
                event_id TEXT PRIMARY KEY,
                processed_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    logger.info("Dedup store initialised at %s", _DB_PATH)


def is_processed(event_id: str) -> bool:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=_TTL_HOURS)).isoformat()
    with sqlite3.connect(_DB_PATH) as conn:
        row = conn.execute(
            "SELECT 1 FROM processed_events WHERE event_id = ? AND processed_at > ?",
            (event_id, cutoff),
        ).fetchone()
    return row is not None


def mark_processed(event_id: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO processed_events (event_id, processed_at) VALUES (?, ?)",
            (event_id, now),
        )
        conn.commit()
