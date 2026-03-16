# bee-content-research Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI + MCP server for YouTube competitor analysis — content gap detection, outlier finding, title pattern analysis, niche benchmarking, engagement scoring, cross-channel comparison, and regional analysis.

**Architecture:** Layered — adapters (CLI/MCP) → services → fetchers/storage/analyzers. Protocol-agnostic core with thin interface adapters. SQLite for local caching. Zero API keys required.

**Tech Stack:** Python 3.11+, typer, rich, yt-dlp, scrapetube, youtube-transcript-api, mcp SDK, uv

**Spec:** `docs/superpowers/specs/2026-03-14-bee-content-research-design.md`

---

## Chunk 1: Project Scaffolding & Storage Layer

### Task 1: Initialize project with uv

**Files:**
- Create: `bee-content-research/pyproject.toml`
- Create: `bee-content-research/src/bee_content_research/__init__.py`
- Create: `bee-content-research/tests/__init__.py`

- [ ] **Step 1: Create project directory and initialize with uv**

```bash
cd /Users/bamboobee/.openclaw/workspace/projects/openclaw-revenue
mkdir -p bee-content-research
cd bee-content-research
uv init --lib --name bee-content-research
```

- [ ] **Step 2: Update pyproject.toml with dependencies**

```toml
[project]
name = "bee-content-research"
version = "0.1.0"
description = "YouTube competitor analysis CLI + MCP server"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "yt-dlp>=2024.0.0",
    "scrapetube>=2.5.0",
    "youtube-transcript-api>=0.6.0",
    "mcp>=1.0.0",
]

[project.scripts]
bee-research = "bee_content_research.adapters.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]

[project.optional-dependencies]
dev = ["pytest>=7.0.0"]
```

- [ ] **Step 3: Create package structure**

```bash
mkdir -p src/bee_content_research/{services,adapters,fetchers,storage,analyzers}
touch src/bee_content_research/__init__.py
touch src/bee_content_research/{services,adapters,fetchers,storage,analyzers}/__init__.py
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 4: Install dependencies**

```bash
uv sync --all-extras
```

- [ ] **Step 5: Verify installation**

```bash
uv run python -c "import bee_content_research; print('OK')"
```

- [ ] **Step 6: Commit**

```bash
git add bee-content-research/
git commit -m "feat: initialize bee-content-research project with uv"
```

---

### Task 2: Storage layer — SQLite schema and database manager

**Files:**
- Create: `bee-content-research/src/bee_content_research/storage/db.py`
- Create: `bee-content-research/src/bee_content_research/storage/models.py`
- Create: `bee-content-research/tests/test_storage.py`

- [ ] **Step 1: Write tests for database initialization and schema**

```python
# tests/test_storage.py
import os
import tempfile
from bee_content_research.storage.db import Database

def test_database_creates_tables():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = {row[0] for row in tables}
        assert "channels" in table_names
        assert "videos" in table_names
        assert "transcripts" in table_names
        assert "niche_groups" in table_names
        assert "niche_group_channels" in table_names
        db.close()

def test_database_default_path():
    db = Database()
    assert db.db_path.endswith("bee_content_research.db")
    db.close()
    os.unlink(db.db_path)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd bee-content-research && uv run pytest tests/test_storage.py -v
```

- [ ] **Step 3: Implement storage/models.py — SQL schema constants**

```python
# src/bee_content_research/storage/models.py
SCHEMA = """
CREATE TABLE IF NOT EXISTS channels (
    id TEXT PRIMARY KEY,
    name TEXT,
    handle TEXT,
    subscriber_count INTEGER,
    video_count INTEGER,
    view_count INTEGER,
    country TEXT,
    language TEXT,
    description TEXT,
    thumbnail_url TEXT,
    fetched_at TEXT,
    discovered_via TEXT
);

CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY,
    channel_id TEXT REFERENCES channels(id),
    title TEXT,
    description TEXT,
    tags TEXT,
    category TEXT,
    duration INTEGER,
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    published_at TEXT,
    thumbnail_url TEXT,
    language TEXT,
    fetched_at TEXT,
    has_transcript INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transcripts (
    video_id TEXT PRIMARY KEY REFERENCES videos(id),
    language TEXT,
    text TEXT,
    fetched_at TEXT
);

CREATE TABLE IF NOT EXISTS niche_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS niche_group_channels (
    group_id INTEGER REFERENCES niche_groups(id) ON DELETE CASCADE,
    channel_id TEXT REFERENCES channels(id),
    added_at TEXT,
    PRIMARY KEY (group_id, channel_id)
);

CREATE INDEX IF NOT EXISTS idx_videos_channel_id ON videos(channel_id);
CREATE INDEX IF NOT EXISTS idx_videos_published_at ON videos(published_at);
CREATE INDEX IF NOT EXISTS idx_niche_group_channels_channel ON niche_group_channels(channel_id);
"""
```

- [ ] **Step 4: Implement storage/db.py — Database connection manager**

```python
# src/bee_content_research/storage/db.py
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
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
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd bee-content-research && uv run pytest tests/test_storage.py -v
```

- [ ] **Step 6: Add more storage tests (groups, videos, resolve_target)**

```python
# Append to tests/test_storage.py

def test_upsert_and_get_channel():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC123", "name": "Test", "handle": "@test",
                           "subscriber_count": 1000, "video_count": 50,
                           "view_count": 100000, "country": "US", "language": "en",
                           "description": "A test channel", "thumbnail_url": "",
                           "fetched_at": "2026-03-14T00:00:00", "discovered_via": "manual"})
        ch = db.get_channel("UC123")
        assert ch is not None
        assert ch["name"] == "Test"
        assert ch["subscriber_count"] == 1000
        db.close()

def test_create_group_and_resolve():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC2", "name": "Ch2", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.create_group("test_niche", ["UC1", "UC2"])
        channel_ids = db.resolve_target("test_niche")
        assert set(channel_ids) == {"UC1", "UC2"}
        # Single channel resolve
        assert db.resolve_target("UC1") == ["UC1"]
        # Unknown target
        assert db.resolve_target("nonexistent") == []
        db.close()

def test_add_remove_from_group():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        db.upsert_channel({"id": "UC1", "name": "Ch1", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC2", "name": "Ch2", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.upsert_channel({"id": "UC3", "name": "Ch3", "fetched_at": "2026-03-14T00:00:00",
                           "discovered_via": "manual"})
        db.create_group("grp", ["UC1"])
        db.add_to_group("grp", ["UC2", "UC3"])
        assert len(db.resolve_target("grp")) == 3
        db.remove_from_group("grp", ["UC2"])
        assert set(db.resolve_target("grp")) == {"UC1", "UC3"}
        db.close()

def test_is_stale():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))
        assert db.is_stale(None) is True
        assert db.is_stale("2020-01-01T00:00:00") is True
        assert db.is_stale(datetime.now().isoformat()) is False
        db.close()
```

- [ ] **Step 7: Run all storage tests**

```bash
cd bee-content-research && uv run pytest tests/test_storage.py -v
```

- [ ] **Step 8: Commit**

```bash
cd bee-content-research && git add -A && git commit -m "feat: add storage layer with SQLite schema and database manager"
```

---

## Chunk 2: Fetchers Layer

### Task 3: Video metadata fetcher (yt-dlp)

**Files:**
- Create: `bee-content-research/src/bee_content_research/fetchers/video.py`
- Create: `bee-content-research/tests/test_fetchers_video.py`

- [ ] **Step 1: Write tests for video metadata extraction**

Test with a well-known, stable YouTube video ID. Use a mock/fixture for CI, but allow real fetching for integration tests.

```python
# tests/test_fetchers_video.py
import json
from bee_content_research.fetchers.video import parse_video_metadata

def test_parse_video_metadata():
    """Test parsing of yt-dlp JSON output into our schema."""
    raw = {
        "id": "dQw4w9WgXcQ",
        "title": "Rick Astley - Never Gonna Give You Up",
        "description": "The official video...",
        "tags": ["rick astley", "never gonna give you up"],
        "categories": ["Music"],
        "duration": 212,
        "view_count": 1500000000,
        "like_count": 15000000,
        "comment_count": 2500000,
        "upload_date": "20091025",
        "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
        "channel": "Rick Astley",
        "language": "en",
    }
    video = parse_video_metadata(raw)
    assert video["id"] == "dQw4w9WgXcQ"
    assert video["channel_id"] == "UCuAXFkgsw1L7xaCfnd5JJOw"
    assert video["duration"] == 212
    assert video["view_count"] == 1500000000
    assert json.loads(video["tags"]) == ["rick astley", "never gonna give you up"]
    assert video["published_at"] == "2009-10-25"
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Implement video fetcher**

```python
# src/bee_content_research/fetchers/video.py
import json
import subprocess
import time
from datetime import datetime

DEFAULT_DELAY = 1.5
DEFAULT_MAX_VIDEOS = 200


def parse_video_metadata(raw: dict) -> dict:
    tags = raw.get("tags") or []
    upload_date = raw.get("upload_date", "")
    published_at = ""
    if upload_date and len(upload_date) == 8:
        published_at = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"

    return {
        "id": raw.get("id", ""),
        "channel_id": raw.get("channel_id", ""),
        "title": raw.get("title", ""),
        "description": raw.get("description", ""),
        "tags": json.dumps(tags),
        "category": (raw.get("categories") or [""])[0],
        "duration": raw.get("duration", 0),
        "view_count": raw.get("view_count", 0),
        "like_count": raw.get("like_count", 0),
        "comment_count": raw.get("comment_count", 0),
        "published_at": published_at,
        "thumbnail_url": raw.get("thumbnail", ""),
        "language": raw.get("language", ""),
        "fetched_at": datetime.now().isoformat(),
        "has_transcript": 0,
    }


def fetch_video_metadata(video_id: str) -> dict | None:
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        raw = json.loads(result.stdout)
        return parse_video_metadata(raw)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def fetch_channel_videos(channel_id: str, max_videos: int = DEFAULT_MAX_VIDEOS,
                         delay: float = DEFAULT_DELAY, progress_callback=None) -> list[dict]:
    """Fetch metadata for all videos in a channel using yt-dlp."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", "--flat-playlist",
             f"https://www.youtube.com/channel/{channel_id}/videos"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            return []

        video_ids = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)
                vid = data.get("id", "")
                if vid:
                    video_ids.append(vid)
            except json.JSONDecodeError:
                continue

        video_ids = video_ids[:max_videos]
        videos = []
        for i, vid in enumerate(video_ids):
            meta = fetch_video_metadata(vid)
            if meta:
                videos.append(meta)
            if progress_callback:
                progress_callback(i + 1, len(video_ids))
            if i < len(video_ids) - 1:
                time.sleep(delay)
        return videos
    except subprocess.TimeoutExpired:
        return []
```

- [ ] **Step 4: Run tests**

```bash
cd bee-content-research && uv run pytest tests/test_fetchers_video.py -v
```

- [ ] **Step 5: Commit**

```bash
cd bee-content-research && git add -A && git commit -m "feat: add video metadata fetcher using yt-dlp"
```

---

### Task 4: Channel fetcher (scrapetube + yt-dlp)

**Files:**
- Create: `bee-content-research/src/bee_content_research/fetchers/channel.py`
- Create: `bee-content-research/tests/test_fetchers_channel.py`

- [ ] **Step 1: Write test for channel metadata parsing**

```python
# tests/test_fetchers_channel.py
from bee_content_research.fetchers.channel import parse_channel_metadata

def test_parse_channel_metadata():
    raw = {
        "id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
        "channel": "MrBeast",
        "channel_url": "https://www.youtube.com/channel/UCX6OQ3DkcsbYNE6H8uQQuVA",
        "uploader": "MrBeast",
        "uploader_id": "@MrBeast",
        "channel_follower_count": 350000000,
    }
    ch = parse_channel_metadata(raw, discovered_via="manual")
    assert ch["id"] == "UCX6OQ3DkcsbYNE6H8uQQuVA"
    assert ch["handle"] == "@MrBeast"
    assert ch["subscriber_count"] == 350000000
    assert ch["discovered_via"] == "manual"
```

- [ ] **Step 2: Implement channel fetcher**

```python
# src/bee_content_research/fetchers/channel.py
import json
import subprocess
from datetime import datetime


def parse_channel_metadata(raw: dict, discovered_via: str = "manual") -> dict:
    return {
        "id": raw.get("id") or raw.get("channel_id", ""),
        "name": raw.get("channel") or raw.get("uploader", ""),
        "handle": raw.get("uploader_id", ""),
        "subscriber_count": raw.get("channel_follower_count", 0),
        "video_count": None,
        "view_count": None,
        "country": raw.get("country", ""),
        "language": raw.get("language", ""),
        "description": raw.get("description", ""),
        "thumbnail_url": raw.get("thumbnail", ""),
        "fetched_at": datetime.now().isoformat(),
        "discovered_via": discovered_via,
    }


def fetch_channel_metadata(channel_url: str, discovered_via: str = "manual") -> dict | None:
    """Fetch channel metadata using yt-dlp. Accepts URL or @handle."""
    if channel_url.startswith("@"):
        channel_url = f"https://www.youtube.com/{channel_url}"
    elif not channel_url.startswith("http"):
        channel_url = f"https://www.youtube.com/channel/{channel_url}"

    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", "--playlist-items", "1",
             f"{channel_url}/videos"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        raw = json.loads(result.stdout.split("\n")[0])
        return parse_channel_metadata(raw, discovered_via=discovered_via)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, IndexError):
        return None


def list_channel_video_ids(channel_url: str, max_videos: int = 200) -> list[str]:
    """List all video IDs for a channel using scrapetube."""
    import scrapetube

    if channel_url.startswith("@"):
        channel_url = channel_url.lstrip("@")
        videos = scrapetube.get_channel(channel_username=channel_url, limit=max_videos)
    elif channel_url.startswith("UC"):
        videos = scrapetube.get_channel(channel_id=channel_url, limit=max_videos)
    else:
        # Try to extract channel ID from URL
        if "/channel/" in channel_url:
            ch_id = channel_url.split("/channel/")[1].split("/")[0]
            videos = scrapetube.get_channel(channel_id=ch_id, limit=max_videos)
        elif "/@" in channel_url:
            username = channel_url.split("/@")[1].split("/")[0]
            videos = scrapetube.get_channel(channel_username=username, limit=max_videos)
        else:
            return []

    return [v["videoId"] for v in videos]
```

- [ ] **Step 3: Run tests**

```bash
cd bee-content-research && uv run pytest tests/test_fetchers_channel.py -v
```

- [ ] **Step 4: Commit**

```bash
cd bee-content-research && git add -A && git commit -m "feat: add channel fetcher using scrapetube and yt-dlp"
```

---

### Task 5: Transcript fetcher and search/suggestions fetcher

**Files:**
- Create: `bee-content-research/src/bee_content_research/fetchers/transcript.py`
- Create: `bee-content-research/src/bee_content_research/fetchers/search.py`
- Create: `bee-content-research/tests/test_fetchers_transcript.py`
- Create: `bee-content-research/tests/test_fetchers_search.py`

- [ ] **Step 1: Implement transcript fetcher**

```python
# src/bee_content_research/fetchers/transcript.py
from youtube_transcript_api import YouTubeTranscriptApi


def fetch_transcript(video_id: str, languages: list[str] | None = None) -> dict | None:
    """Fetch transcript for a video. Returns {language, text} or None."""
    if languages is None:
        languages = ["en"]
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_transcript(languages)
        except Exception:
            transcript = transcript_list.find_generated_transcript(languages)

        segments = transcript.fetch()
        full_text = " ".join(seg.text for seg in segments)
        return {"language": transcript.language_code, "text": full_text}
    except Exception:
        return None
```

- [ ] **Step 2: Implement search/suggestions fetcher**

```python
# src/bee_content_research/fetchers/search.py
import json
import subprocess
import urllib.request
import urllib.parse
import time
import scrapetube


def search_channels(keyword: str, max_results: int = 20) -> list[dict]:
    """Search YouTube for channels matching keyword. Returns basic channel info."""
    try:
        videos = scrapetube.get_search(query=keyword, limit=max_results * 3)
        seen_channels = {}
        for v in videos:
            ch_id = v.get("channelId") or (v.get("ownerText", {}).get("runs", [{}])[0].get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", ""))
            ch_name = v.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
            if ch_id and ch_id not in seen_channels:
                seen_channels[ch_id] = {"id": ch_id, "name": ch_name}
            if len(seen_channels) >= max_results:
                break
        return list(seen_channels.values())
    except Exception:
        return []


def fetch_youtube_suggestions(keyword: str) -> list[str]:
    """Fetch YouTube search autocomplete suggestions."""
    try:
        encoded = urllib.parse.quote(keyword)
        url = f"http://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            # Response is JSONP: window.google.ac.h(...)
            json_str = raw[raw.index("(") + 1 : raw.rindex(")")]
            data = json.loads(json_str)
            return [item[0] for item in data[1]] if len(data) > 1 else []
    except Exception:
        return []
```

- [ ] **Step 3: Write tests**

```python
# tests/test_fetchers_search.py
from bee_content_research.fetchers.search import fetch_youtube_suggestions

def test_fetch_youtube_suggestions_returns_list():
    # This is a basic structural test - suggestions endpoint is public
    result = fetch_youtube_suggestions("python tutorial")
    assert isinstance(result, list)
    # Should return some suggestions for a common query
    # (may fail if network is down, but acceptable for integration test)
```

```python
# tests/test_fetchers_transcript.py
# Transcript tests are integration-only since they hit YouTube
# Included as a manual test reference
def test_transcript_import():
    from bee_content_research.fetchers.transcript import fetch_transcript
    assert callable(fetch_transcript)
```

- [ ] **Step 4: Run tests**

```bash
cd bee-content-research && uv run pytest tests/test_fetchers_search.py tests/test_fetchers_transcript.py -v
```

- [ ] **Step 5: Commit**

```bash
cd bee-content-research && git add -A && git commit -m "feat: add transcript and search/suggestions fetchers"
```

---

### Task 6: Snowball discovery fetcher

**Files:**
- Create: `bee-content-research/src/bee_content_research/fetchers/snowball.py`

- [ ] **Step 1: Implement snowball discovery**

```python
# src/bee_content_research/fetchers/snowball.py
import re
from .channel import fetch_channel_metadata, list_channel_video_ids
from .video import fetch_video_metadata
from .search import search_channels


def discover_related_channels(channel_url: str, max_results: int = 10,
                              delay: float = 1.5) -> list[dict]:
    """Discover related channels via featured channels, collaborations, and search expansion."""
    discovered = {}

    # Strategy 1: Scan video descriptions for @mentions
    video_ids = list_channel_video_ids(channel_url, max_videos=20)
    for vid in video_ids[:10]:
        meta = fetch_video_metadata(vid)
        if meta and meta.get("description"):
            handles = re.findall(r'@([\w.-]+)', meta["description"])
            for handle in handles:
                if handle not in discovered and len(discovered) < max_results:
                    ch = fetch_channel_metadata(f"@{handle}", discovered_via=f"snowball:{channel_url}")
                    if ch and ch.get("id"):
                        discovered[ch["id"]] = ch

    # Strategy 2: Search expansion using channel's top tags/keywords
    if len(discovered) < max_results:
        sample_video = fetch_video_metadata(video_ids[0]) if video_ids else None
        if sample_video:
            import json
            tags = json.loads(sample_video.get("tags", "[]"))
            if tags:
                keyword = tags[0] if tags else ""
                if keyword:
                    results = search_channels(keyword, max_results=max_results)
                    for r in results:
                        if r["id"] not in discovered and len(discovered) < max_results:
                            ch = fetch_channel_metadata(r["id"], discovered_via=f"snowball:{channel_url}")
                            if ch:
                                discovered[ch["id"]] = ch

    if not discovered:
        return []

    return list(discovered.values())
```

- [ ] **Step 2: Commit**

```bash
cd bee-content-research && git add -A && git commit -m "feat: add snowball discovery fetcher"
```

---

## Chunk 3: Analyzers

### Task 7: Outlier detection analyzer

**Files:**
- Create: `bee-content-research/src/bee_content_research/analyzers/outliers.py`
- Create: `bee-content-research/tests/test_analyzers.py`

- [ ] **Step 1: Write test**

```python
# tests/test_analyzers.py
from bee_content_research.analyzers.outliers import find_outliers

def test_find_outliers():
    videos = [
        {"id": f"v{i}", "channel_id": "UC1", "title": f"Video {i}",
         "view_count": 1000, "like_count": 100, "comment_count": 10,
         "published_at": "2026-01-01", "tags": "[]"}
        for i in range(20)
    ]
    # Add one outlier
    videos.append({"id": "viral", "channel_id": "UC1", "title": "Viral Video",
                    "view_count": 50000, "like_count": 5000, "comment_count": 500,
                    "published_at": "2026-02-01", "tags": "[]"})
    result = find_outliers(videos, threshold=2.0)
    assert len(result["outliers"]) >= 1
    assert any(o["id"] == "viral" for o in result["outliers"])
```

- [ ] **Step 2: Implement outlier detection**

```python
# src/bee_content_research/analyzers/outliers.py
from statistics import median


def find_outliers(videos: list[dict], threshold: float = 2.0) -> dict:
    if not videos:
        return {"outliers": [], "channel_medians": {}}

    # Group by channel
    by_channel = {}
    for v in videos:
        ch = v.get("channel_id", "unknown")
        by_channel.setdefault(ch, []).append(v)

    channel_medians = {}
    outliers = []

    for ch_id, ch_videos in by_channel.items():
        views = [v.get("view_count", 0) or 0 for v in ch_videos]
        if not views:
            continue
        med = median(views)
        channel_medians[ch_id] = med

        if med == 0:
            continue

        for v in ch_videos:
            vc = v.get("view_count", 0) or 0
            multiplier = vc / med if med > 0 else 0
            if multiplier >= threshold:
                outliers.append({
                    "id": v["id"],
                    "channel_id": ch_id,
                    "title": v.get("title", ""),
                    "view_count": vc,
                    "like_count": v.get("like_count", 0),
                    "comment_count": v.get("comment_count", 0),
                    "multiplier": round(multiplier, 1),
                    "published_at": v.get("published_at", ""),
                    "tags": v.get("tags", "[]"),
                })

    outliers.sort(key=lambda x: x["multiplier"], reverse=True)
    return {"outliers": outliers, "channel_medians": channel_medians}
```

- [ ] **Step 3: Run test, commit**

```bash
cd bee-content-research && uv run pytest tests/test_analyzers.py::test_find_outliers -v
git add -A && git commit -m "feat: add outlier detection analyzer"
```

---

### Task 8: Remaining analyzers (content gaps, titles, engagement, benchmarks, SEO, timing, regional, comparison)

**Files:**
- Create: `bee-content-research/src/bee_content_research/analyzers/content_gaps.py`
- Create: `bee-content-research/src/bee_content_research/analyzers/titles.py`
- Create: `bee-content-research/src/bee_content_research/analyzers/engagement.py`
- Create: `bee-content-research/src/bee_content_research/analyzers/benchmarks.py`
- Create: `bee-content-research/src/bee_content_research/analyzers/seo.py`
- Create: `bee-content-research/src/bee_content_research/analyzers/timing.py`
- Create: `bee-content-research/src/bee_content_research/analyzers/regional.py`

Each analyzer follows the same pattern: pure function, takes list of video dicts (and optionally transcripts/channels), returns a result dict. No I/O.

- [ ] **Step 1: Implement all analyzers** (see spec Section 7 for algorithm details)

Implement each file following the pattern established in outliers.py. Key algorithms:
- `content_gaps.py`: n-gram counting on titles/tags, cross-ref with YouTube suggestions
- `titles.py`: regex patterns for numbers, questions, emoji, length bucketing, correlate with views
- `engagement.py`: like/view %, comment/view %, composite score, hidden gems detection
- `benchmarks.py`: median aggregation across channels, per-channel deviation
- `seo.py`: tag frequency counting, shared vs unique tags, tag-to-performance correlation
- `timing.py`: day-of-week and hour-of-day view performance distribution
- `regional.py`: country/language grouping, CPM lookup table, opportunity scoring

- [ ] **Step 2: Write tests for each analyzer**

Add tests to `tests/test_analyzers.py` following the outlier test pattern — provide synthetic video data, verify output structure.

- [ ] **Step 3: Run all tests, commit**

```bash
cd bee-content-research && uv run pytest tests/test_analyzers.py -v
git add -A && git commit -m "feat: add all analyzer modules"
```

---

## Chunk 4: Services & Adapters

### Task 9: Service layer

**Files:**
- Create: `bee-content-research/src/bee_content_research/services/discovery.py`
- Create: `bee-content-research/src/bee_content_research/services/analysis.py`
- Create: `bee-content-research/src/bee_content_research/services/groups.py`
- Create: `bee-content-research/src/bee_content_research/services/reporting.py`

- [ ] **Step 1: Implement service layer**

Each service function orchestrates fetchers + storage + analyzers. Example:

```python
# src/bee_content_research/services/discovery.py
from ..storage.db import Database
from ..fetchers.channel import fetch_channel_metadata, list_channel_video_ids
from ..fetchers.video import fetch_channel_videos
from ..fetchers.search import search_channels
from ..fetchers.snowball import discover_related_channels


def discover(db: Database, keyword: str, max_results: int = 20) -> list[dict]:
    results = search_channels(keyword, max_results)
    channels = []
    for r in results:
        ch = fetch_channel_metadata(r["id"], discovered_via=f"keyword:{keyword}")
        if ch:
            db.upsert_channel(ch)
            channels.append(ch)
    return channels


def add_channel(db: Database, url: str) -> dict | None:
    ch = fetch_channel_metadata(url, discovered_via="manual")
    if ch:
        db.upsert_channel(ch)
    return ch


def snowball(db: Database, channel_url: str, max_results: int = 10) -> list[dict]:
    channels = discover_related_channels(channel_url, max_results)
    for ch in channels:
        db.upsert_channel(ch)
    return channels


def fetch_data(db: Database, target: str, include_transcripts: bool = False,
               max_videos: int = 200, delay: float = 1.5, force: bool = False,
               progress_callback=None) -> dict:
    channel_ids = db.resolve_target(target)
    if not channel_ids:
        return {"error": f"Target '{target}' not found"}

    results = {"fetched": 0, "skipped": 0, "errors": [], "warnings": []}
    for ch_id in channel_ids:
        ch = db.get_channel(ch_id)
        if ch and not force and not db.is_stale(ch.get("fetched_at")):
            results["skipped"] += 1
            continue

        videos = fetch_channel_videos(ch_id, max_videos=max_videos,
                                       delay=delay, progress_callback=progress_callback)
        if videos:
            db.upsert_videos(videos)
            results["fetched"] += len(videos)
        else:
            results["warnings"].append(f"No videos fetched for {ch_id}")

        if include_transcripts:
            from ..fetchers.transcript import fetch_transcript
            for v in videos:
                if not v.get("has_transcript"):
                    t = fetch_transcript(v["id"])
                    if t:
                        db.upsert_transcript(v["id"], t["language"], t["text"])
                    else:
                        results["warnings"].append(f"No transcript for {v['id']}")

    return results
```

- [ ] **Step 2: Implement analysis service, groups service, reporting service**

Same pattern — thin orchestrators that call storage + analyzers.

- [ ] **Step 3: Commit**

```bash
cd bee-content-research && git add -A && git commit -m "feat: add service layer"
```

---

### Task 10: CLI adapter (typer)

**Files:**
- Create: `bee-content-research/src/bee_content_research/adapters/cli.py`
- Create: `bee-content-research/src/bee_content_research/formatters.py`

- [ ] **Step 1: Implement formatters**

```python
# src/bee_content_research/formatters.py
import json
import csv
import io
from rich.table import Table
from rich.console import Console
from rich.panel import Panel

console = Console()

def format_channels_table(channels: list[dict]) -> Table:
    table = Table(title="Channels")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Handle")
    table.add_column("Subscribers", justify="right")
    table.add_column("Country")
    table.add_column("Discovered Via")
    for ch in channels:
        table.add_row(
            ch.get("id", "")[:12],
            ch.get("name", ""),
            ch.get("handle", ""),
            f"{ch.get('subscriber_count', 0):,}" if ch.get("subscriber_count") else "—",
            ch.get("country", ""),
            ch.get("discovered_via", ""),
        )
    return table

# ... similar functions for outliers, engagement, benchmarks, etc.

def to_json(data: dict | list) -> str:
    return json.dumps(data, indent=2, default=str)

def to_csv(data: list[dict]) -> str:
    if not data:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()
```

- [ ] **Step 2: Implement CLI adapter with all commands**

```python
# src/bee_content_research/adapters/cli.py
import typer
from rich.console import Console
from ..storage.db import Database
from ..services import discovery, analysis, groups, reporting
from ..formatters import format_channels_table, to_json, to_csv

app = typer.Typer(name="bee-research", help="YouTube competitor analysis tool")
console = Console()

# Subcommands
group_app = typer.Typer(help="Manage niche groups")
analyze_app = typer.Typer(help="Run analysis")
app.add_typer(group_app, name="group")
app.add_typer(analyze_app, name="analyze")


@app.command()
def discover(keyword: str, snowball: bool = False, max_results: int = 20):
    """Discover channels by keyword or snowball from a channel."""
    db = Database()
    if snowball:
        channels = discovery.snowball(db, keyword, max_results)
    else:
        channels = discovery.discover(db, keyword, max_results)
    console.print(format_channels_table(channels))
    console.print(f"\n[green]{len(channels)} channels discovered[/green]")
    db.close()


@app.command()
def add(urls: list[str]):
    """Manually add channels by URL or @handle."""
    db = Database()
    for url in urls:
        ch = discovery.add_channel(db, url)
        if ch:
            console.print(f"[green]Added:[/green] {ch['name']} ({ch['id']})")
        else:
            console.print(f"[red]Failed:[/red] {url}")
    db.close()


@app.command()
def fetch(target: str, transcripts: bool = False, max_videos: int = 200,
          delay: float = 1.5, force: bool = False):
    """Fetch video data for a channel or niche group."""
    from rich.progress import Progress
    db = Database()
    with Progress() as progress:
        task = progress.add_task("Fetching...", total=None)
        def cb(current, total):
            progress.update(task, completed=current, total=total)
        result = discovery.fetch_data(db, target, include_transcripts=transcripts,
                                       max_videos=max_videos, delay=delay, force=force,
                                       progress_callback=cb)
    console.print(f"[green]Fetched {result.get('fetched', 0)} videos[/green]")
    if result.get("warnings"):
        for w in result["warnings"]:
            console.print(f"[yellow]Warning:[/yellow] {w}")
    db.close()


@app.command()
def status():
    """Show cached data statistics."""
    db = Database()
    s = db.get_status()
    console.print(f"Database: {s['db_path']}")
    console.print(f"Channels: {s['channels']}")
    console.print(f"Videos: {s['videos']}")
    console.print(f"Transcripts: {s['transcripts']}")
    console.print(f"Groups: {s['groups']}")
    console.print(f"Data range: {s['oldest_fetch'] or 'N/A'} → {s['newest_fetch'] or 'N/A'}")
    db.close()


# Group commands
@group_app.command("create")
def group_create(name: str, channel_ids: list[str]):
    db = Database()
    groups.create(db, name, channel_ids)
    console.print(f"[green]Created group '{name}' with {len(channel_ids)} channels[/green]")
    db.close()

@group_app.command("list")
def group_list():
    db = Database()
    grps = groups.list_all(db)
    for g in grps:
        console.print(f"  {g['name']} ({g['channel_count']} channels)")
    db.close()

@group_app.command("show")
def group_show(name: str):
    db = Database()
    channels = groups.show(db, name)
    console.print(format_channels_table(channels))
    db.close()

@group_app.command("add")
def group_add(name: str, channel_ids: list[str]):
    db = Database()
    groups.add_channels(db, name, channel_ids)
    console.print(f"[green]Added {len(channel_ids)} channels to '{name}'[/green]")
    db.close()

@group_app.command("remove")
def group_remove(name: str, channel_ids: list[str]):
    db = Database()
    groups.remove_channels(db, name, channel_ids)
    console.print(f"[green]Removed {len(channel_ids)} channels from '{name}'[/green]")
    db.close()


# Analyze commands
@analyze_app.command("outliers")
def analyze_outliers(target: str, threshold: float = 2.0,
                     format: str = typer.Option("table", help="Output format: table, json, csv")):
    db = Database()
    result = analysis.outliers(db, target, threshold)
    if format == "json":
        console.print(to_json(result))
    else:
        # Rich table output
        from ..formatters import format_outliers_table
        console.print(format_outliers_table(result))
    db.close()

# ... similar pattern for gaps, titles, engagement, benchmark, seo, timing, compare, regional


@app.command()
def report(niche: str, format: str = typer.Option("table", help="Output format: table, json, csv")):
    """Run all analyzers and produce a full report."""
    db = Database()
    result = reporting.full_report(db, niche)
    if format == "json":
        console.print(to_json(result))
    elif format == "csv":
        console.print(to_csv(result))
    else:
        # Rich formatted report
        from ..formatters import format_full_report
        console.print(format_full_report(result))
    db.close()
```

- [ ] **Step 3: Test CLI basics**

```bash
cd bee-content-research && uv run bee-research --help
uv run bee-research status
```

- [ ] **Step 4: Commit**

```bash
cd bee-content-research && git add -A && git commit -m "feat: add CLI adapter with all commands"
```

---

### Task 11: MCP adapter

**Files:**
- Create: `bee-content-research/src/bee_content_research/adapters/mcp.py`

- [ ] **Step 1: Implement MCP server**

```python
# src/bee_content_research/adapters/mcp.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import json
from ..storage.db import Database
from ..services import discovery, analysis, groups, reporting

server = Server("bee-content-research")


def _db():
    return Database()


@server.tool()
async def discover_channels(keyword: str, max_results: int = 20) -> list[TextContent]:
    """Find YouTube channels by keyword search."""
    db = _db()
    channels = discovery.discover(db, keyword, max_results)
    db.close()
    return [TextContent(type="text", text=json.dumps(channels, default=str))]


@server.tool()
async def add_channel(url: str) -> list[TextContent]:
    """Manually add a YouTube channel by URL or @handle."""
    db = _db()
    ch = discovery.add_channel(db, url)
    db.close()
    return [TextContent(type="text", text=json.dumps(ch, default=str))]


# ... similar pattern for all other tools from spec Section 6


@server.tool()
async def find_outliers(target: str, threshold: float = 2.0) -> list[TextContent]:
    """Find viral outlier videos that dramatically outperform a channel's average."""
    db = _db()
    result = analysis.outliers(db, target, threshold)
    db.close()
    return [TextContent(type="text", text=json.dumps(result, default=str))]


@server.tool()
async def find_content_gaps(niche: str) -> list[TextContent]:
    """Identify content topics with high search demand but low competitor coverage."""
    db = _db()
    result = analysis.content_gaps(db, niche)
    db.close()
    return [TextContent(type="text", text=json.dumps(result, default=str))]


# ... remaining tools ...


def main():
    import asyncio
    from mcp.server.stdio import stdio_server

    async def run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Add MCP entry point to pyproject.toml**

```toml
[project.scripts]
bee-research = "bee_content_research.adapters.cli:app"
bee-research-mcp = "bee_content_research.adapters.mcp:main"
```

- [ ] **Step 3: Commit**

```bash
cd bee-content-research && git add -A && git commit -m "feat: add MCP server adapter"
```

---

## Chunk 5: Integration & Polish

### Task 12: End-to-end integration test

- [ ] **Step 1: Write integration test that exercises the full workflow**

```python
# tests/test_integration.py
import os
import tempfile
from bee_content_research.storage.db import Database
from bee_content_research.services import discovery, analysis, groups

def test_full_workflow_with_mock_data():
    """Test the full workflow using pre-seeded data (no network calls)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "test.db"))

        # Seed channels
        for i in range(3):
            db.upsert_channel({"id": f"UC{i}", "name": f"Channel {i}",
                               "handle": f"@ch{i}", "subscriber_count": (i+1)*10000,
                               "country": ["US", "DE", "JP"][i],
                               "language": ["en", "de", "ja"][i],
                               "fetched_at": "2026-03-14T00:00:00",
                               "discovered_via": "manual"})

        # Create group
        db.create_group("test_niche", ["UC0", "UC1", "UC2"])

        # Seed videos with varied performance
        import json
        for ch_idx in range(3):
            for v_idx in range(20):
                views = 1000 * (v_idx + 1)
                if v_idx == 19:  # Make last video an outlier
                    views = 100000
                db.upsert_video({
                    "id": f"v{ch_idx}_{v_idx}", "channel_id": f"UC{ch_idx}",
                    "title": f"How to do thing {v_idx}" if v_idx % 2 == 0 else f"Top {v_idx} tips",
                    "tags": json.dumps(["tag1", "tag2"]),
                    "duration": 600, "view_count": views,
                    "like_count": views // 10, "comment_count": views // 100,
                    "published_at": f"2026-01-{(v_idx+1):02d}",
                    "fetched_at": "2026-03-14T00:00:00",
                })
        db.commit()

        # Run analyses
        result = analysis.outliers(db, "test_niche")
        assert len(result["outliers"]) > 0

        result = analysis.engagement(db, "test_niche")
        assert "videos" in result

        result = analysis.benchmarks(db, "test_niche")
        assert "niche_medians" in result

        db.close()
```

- [ ] **Step 2: Run integration test**

```bash
cd bee-content-research && uv run pytest tests/test_integration.py -v
```

- [ ] **Step 3: Final commit**

```bash
cd bee-content-research && git add -A && git commit -m "feat: add integration tests and polish"
```

---

### Task 13: README and final cleanup

- [ ] **Step 1: Verify CLI works end-to-end**

```bash
cd bee-content-research
uv run bee-research --help
uv run bee-research status
```

- [ ] **Step 2: Final commit**

```bash
cd bee-content-research && git add -A && git commit -m "docs: finalize bee-content-research v0.1.0"
```
