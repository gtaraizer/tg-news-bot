
import os
import sqlite3
from contextlib import closing

DB_PATH = os.getenv("DB_PATH", "state.db")

def _ensure_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS posted ("
            " url TEXT PRIMARY KEY,"
            " posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
        conn.commit()

def is_posted(url: str) -> bool:
    _ensure_db()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("SELECT 1 FROM posted WHERE url = ?", (url,))
        return cur.fetchone() is not None

def mark_posted(url: str) -> None:
    _ensure_db()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("INSERT OR IGNORE INTO posted(url) VALUES (?)", (url,))
        conn.commit()
