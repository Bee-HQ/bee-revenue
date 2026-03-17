"""Stock footage library — tracks clip usage across projects to avoid repetition."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".bee-video" / "stock-library.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS clips (
    pexels_id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    path TEXT NOT NULL,
    first_used_project TEXT NOT NULL,
    first_used_at TEXT NOT NULL,
    usage_count INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS usages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pexels_id INTEGER NOT NULL REFERENCES clips(pexels_id),
    project TEXT NOT NULL,
    used_at TEXT NOT NULL
);
"""


class StockLibrary:
    """SQLite-backed stock footage usage tracker."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def register_clip(
        self,
        pexels_id: int,
        query: str,
        path: str,
        project: str,
    ) -> None:
        """Register a downloaded stock clip. Increments usage if already known."""
        now = datetime.now().isoformat()

        existing = self.conn.execute(
            "SELECT pexels_id FROM clips WHERE pexels_id = ?", (pexels_id,)
        ).fetchone()

        if existing:
            self.conn.execute(
                "UPDATE clips SET usage_count = usage_count + 1 WHERE pexels_id = ?",
                (pexels_id,),
            )
        else:
            self.conn.execute(
                "INSERT INTO clips (pexels_id, query, path, first_used_project, first_used_at, usage_count) "
                "VALUES (?, ?, ?, ?, ?, 1)",
                (pexels_id, query, path, project, now),
            )

        self.conn.execute(
            "INSERT INTO usages (pexels_id, project, used_at) VALUES (?, ?, ?)",
            (pexels_id, project, now),
        )
        self.conn.commit()

    def list_clips(self) -> list[dict]:
        """Return all tracked clips, ordered by usage count descending."""
        rows = self.conn.execute(
            "SELECT pexels_id, query, path, first_used_project, first_used_at, usage_count "
            "FROM clips ORDER BY usage_count DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def list_usages(self, pexels_id: int) -> list[dict]:
        """Return all usages for a specific clip."""
        rows = self.conn.execute(
            "SELECT project, used_at FROM usages WHERE pexels_id = ? ORDER BY used_at",
            (pexels_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def check_query(self, query: str) -> list[dict]:
        """Find clips that match (substring) a search query. For reuse warnings."""
        rows = self.conn.execute(
            "SELECT pexels_id, query, path, first_used_project, usage_count "
            "FROM clips WHERE query LIKE ? ORDER BY usage_count DESC",
            (f"%{query}%",),
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.conn.close()
