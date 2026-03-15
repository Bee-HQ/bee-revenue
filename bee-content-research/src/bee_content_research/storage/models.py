"""SQLite schema definitions for bee-content-research."""

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
