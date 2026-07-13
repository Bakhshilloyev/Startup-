"""SQLite-backed persistent key-value + fuzzy search memory store.

Pure standard library; compact and safe for weak devices. Stores small values
and keeps an FTS-free substring index on keys for recall.
"""

import os
import sqlite3
import time
from typing import List, Optional


class SQLiteStore:
    def __init__(self, path: str = "data/memory/agent.db"):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS kv ("
            "key TEXT PRIMARY KEY, value TEXT, ts REAL)"
        )
        self.conn.commit()

    def put(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO kv (key, value, ts) VALUES (?, ?, ?)",
            (key, value, time.time()),
        )
        self.conn.commit()

    def get(self, key: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT value FROM kv WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None

    def search(self, query: str, limit: int = 20) -> List[dict]:
        if query:
            rows = self.conn.execute(
                "SELECT key, value, ts FROM kv WHERE key LIKE ? OR value LIKE ? "
                "ORDER BY ts DESC LIMIT ?",
                (f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT key, value, ts FROM kv ORDER BY ts DESC LIMIT ?", (limit,)
            ).fetchall()
        return [{"key": r[0], "value": r[1], "ts": r[2]} for r in rows]

    def delete(self, key: str) -> None:
        self.conn.execute("DELETE FROM kv WHERE key = ?", (key,))
        self.conn.commit()

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
