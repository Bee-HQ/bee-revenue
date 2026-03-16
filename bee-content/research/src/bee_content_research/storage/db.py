"""SQLite database connection manager for bee-content-research."""

import os
import sqlite3
from datetime import datetime, timedelta
from .models import SCHEMA

DEFAULT_DB_DIR = os.path.expanduser("~/.bee-content-research")
DEFAULT_DB_NAME = "bee_content_research.db"
DEFAULT_TTL_DAYS = 7


class Database:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            os.makedirs(DEFAULT_DB_DIR, exist_ok=True)
            db_path = os.path.join(DEFAULT_DB_DIR, DEFAULT_DB_NAME)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, params)

    def executemany(self, sql: str, params: list) -> sqlite3.Cursor:
        return self.conn.executemany(sql, params)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def is_stale(self, fetched_at: str | None, ttl_days: int = DEFAULT_TTL_DAYS) -> bool:
        if fetched_at is None:
            return True
        fetched = datetime.fromisoformat(fetched_at)
        return datetime.now() - fetched > timedelta(days=ttl_days)

    # --- Channel operations ---

    def upsert_channel(self, channel: dict):
        self.execute(
            """INSERT INTO channels (id, name, handle, subscriber_count, video_count,
               view_count, country, language, description, thumbnail_url, fetched_at, discovered_via)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
               name=excluded.name, handle=excluded.handle,
               subscriber_count=excluded.subscriber_count, video_count=excluded.video_count,
               view_count=excluded.view_count, country=excluded.country,
               language=excluded.language, description=excluded.description,
               thumbnail_url=excluded.thumbnail_url, fetched_at=excluded.fetched_at""",
            (channel.get("id"), channel.get("name"), channel.get("handle"),
             channel.get("subscriber_count"), channel.get("video_count"),
             channel.get("view_count"), channel.get("country"),
             channel.get("language"), channel.get("description"),
             channel.get("thumbnail_url"), channel.get("fetched_at"),
             channel.get("discovered_via")),
        )
        self.commit()

    def get_channel(self, channel_id: str) -> dict | None:
        row = self.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
        return dict(row) if row else None

    def list_channels(self) -> list[dict]:
        rows = self.execute("SELECT * FROM channels ORDER BY name").fetchall()
        return [dict(r) for r in rows]

    def delete_channel(self, channel_id: str) -> bool:
        """Delete a channel and all its videos, transcripts, and group memberships."""
        ch = self.get_channel(channel_id)
        if not ch:
            return False
        self.execute("DELETE FROM transcripts WHERE video_id IN (SELECT id FROM videos WHERE channel_id = ?)", (channel_id,))
        self.execute("DELETE FROM videos WHERE channel_id = ?", (channel_id,))
        self.execute("DELETE FROM niche_group_channels WHERE channel_id = ?", (channel_id,))
        self.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
        self.commit()
        return True

    # --- Video operations ---

    def upsert_video(self, video: dict):
        self.execute(
            """INSERT INTO videos (id, channel_id, title, description, tags, category,
               duration, view_count, like_count, comment_count, published_at,
               thumbnail_url, language, fetched_at, has_transcript)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
               title=excluded.title, description=excluded.description,
               tags=excluded.tags, view_count=excluded.view_count,
               like_count=excluded.like_count, comment_count=excluded.comment_count,
               fetched_at=excluded.fetched_at""",
            (video.get("id"), video.get("channel_id"), video.get("title"),
             video.get("description"), video.get("tags"), video.get("category"),
             video.get("duration"), video.get("view_count"), video.get("like_count"),
             video.get("comment_count"), video.get("published_at"),
             video.get("thumbnail_url"), video.get("language"),
             video.get("fetched_at"), video.get("has_transcript", 0)),
        )

    def upsert_videos(self, videos: list[dict]):
        for v in videos:
            self.upsert_video(v)
        self.commit()

    def get_videos_for_channel(self, channel_id: str, limit: int = 200) -> list[dict]:
        rows = self.execute(
            "SELECT * FROM videos WHERE channel_id = ? ORDER BY published_at DESC LIMIT ?",
            (channel_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_videos_for_group(self, group_name: str) -> list[dict]:
        rows = self.execute(
            """SELECT v.* FROM videos v
               JOIN niche_group_channels gc ON v.channel_id = gc.channel_id
               JOIN niche_groups g ON gc.group_id = g.id
               WHERE g.name = ?
               ORDER BY v.published_at DESC""",
            (group_name,),
        ).fetchall()
        return [dict(r) for r in rows]

    # --- Transcript operations ---

    def upsert_transcript(self, video_id: str, language: str, text: str):
        now = datetime.now().isoformat()
        self.execute(
            """INSERT INTO transcripts (video_id, language, text, fetched_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(video_id) DO UPDATE SET
               language=excluded.language, text=excluded.text, fetched_at=excluded.fetched_at""",
            (video_id, language, text, now),
        )
        self.execute("UPDATE videos SET has_transcript = 1 WHERE id = ?", (video_id,))
        self.commit()

    def get_transcript(self, video_id: str) -> dict | None:
        row = self.execute("SELECT * FROM transcripts WHERE video_id = ?", (video_id,)).fetchone()
        return dict(row) if row else None

    def get_transcripts_for_group(self, group_name: str) -> list[dict]:
        rows = self.execute(
            """SELECT t.* FROM transcripts t
               JOIN videos v ON t.video_id = v.id
               JOIN niche_group_channels gc ON v.channel_id = gc.channel_id
               JOIN niche_groups g ON gc.group_id = g.id
               WHERE g.name = ?""",
            (group_name,),
        ).fetchall()
        return [dict(r) for r in rows]

    # --- Niche group operations ---

    def create_group(self, name: str, channel_ids: list[str]) -> int:
        now = datetime.now().isoformat()
        cursor = self.execute(
            "INSERT INTO niche_groups (name, created_at) VALUES (?, ?)", (name, now)
        )
        group_id = cursor.lastrowid
        for ch_id in channel_ids:
            self.execute(
                "INSERT OR IGNORE INTO niche_group_channels (group_id, channel_id, added_at) VALUES (?, ?, ?)",
                (group_id, ch_id, now),
            )
        self.commit()
        return group_id

    def add_to_group(self, name: str, channel_ids: list[str]):
        group = self.execute("SELECT id FROM niche_groups WHERE name = ?", (name,)).fetchone()
        if not group:
            raise ValueError(f"Group '{name}' not found")
        now = datetime.now().isoformat()
        for ch_id in channel_ids:
            self.execute(
                "INSERT OR IGNORE INTO niche_group_channels (group_id, channel_id, added_at) VALUES (?, ?, ?)",
                (group["id"], ch_id, now),
            )
        self.commit()

    def remove_from_group(self, name: str, channel_ids: list[str]):
        group = self.execute("SELECT id FROM niche_groups WHERE name = ?", (name,)).fetchone()
        if not group:
            raise ValueError(f"Group '{name}' not found")
        for ch_id in channel_ids:
            self.execute(
                "DELETE FROM niche_group_channels WHERE group_id = ? AND channel_id = ?",
                (group["id"], ch_id),
            )
        self.commit()

    def list_groups(self) -> list[dict]:
        rows = self.execute(
            """SELECT g.*, COUNT(gc.channel_id) as channel_count
               FROM niche_groups g
               LEFT JOIN niche_group_channels gc ON g.id = gc.group_id
               GROUP BY g.id ORDER BY g.name"""
        ).fetchall()
        return [dict(r) for r in rows]

    def get_group_channels(self, name: str) -> list[dict]:
        rows = self.execute(
            """SELECT c.* FROM channels c
               JOIN niche_group_channels gc ON c.id = gc.channel_id
               JOIN niche_groups g ON gc.group_id = g.id
               WHERE g.name = ?""",
            (name,),
        ).fetchall()
        return [dict(r) for r in rows]

    def resolve_target(self, target: str) -> list[str]:
        """Resolve a target (channel_id or group name) to a list of channel IDs."""
        group = self.execute("SELECT id FROM niche_groups WHERE name = ?", (target,)).fetchone()
        if group:
            rows = self.execute(
                "SELECT channel_id FROM niche_group_channels WHERE group_id = ?",
                (group["id"],),
            ).fetchall()
            return [r["channel_id"] for r in rows]
        channel = self.get_channel(target)
        if channel:
            return [target]
        return []

    # --- Status ---

    def get_status(self) -> dict:
        channels = self.execute("SELECT COUNT(*) as c FROM channels").fetchone()["c"]
        videos = self.execute("SELECT COUNT(*) as c FROM videos").fetchone()["c"]
        transcripts = self.execute("SELECT COUNT(*) as c FROM transcripts").fetchone()["c"]
        groups = self.execute("SELECT COUNT(*) as c FROM niche_groups").fetchone()["c"]
        oldest = self.execute("SELECT MIN(fetched_at) as m FROM channels").fetchone()["m"]
        newest = self.execute("SELECT MAX(fetched_at) as m FROM channels").fetchone()["m"]
        return {
            "channels": channels,
            "videos": videos,
            "transcripts": transcripts,
            "groups": groups,
            "oldest_fetch": oldest,
            "newest_fetch": newest,
            "db_path": self.db_path,
        }
