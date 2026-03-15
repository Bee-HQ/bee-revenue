"""MCP server adapter for bee-content-research.

Thin translation layer that exposes service functions as MCP tools.
Uses FastMCP from the mcp SDK (v1.0+).
"""

import json

from mcp.server import FastMCP

from ..storage.db import Database
from ..services import discovery, analysis, groups, reporting

mcp = FastMCP("bee-content-research")


def _db():
    """Create a new database connection."""
    return Database()


# --- Discovery & Data tools ---

@mcp.tool()
def discover_channels(keyword: str, max_results: int = 20) -> str:
    """Find YouTube channels by keyword search."""
    db = _db()
    try:
        channels = discovery.discover(db, keyword, max_results)
        return json.dumps(channels, default=str)
    finally:
        db.close()


@mcp.tool()
def add_channel(url: str) -> str:
    """Manually add a YouTube channel by URL or @handle."""
    db = _db()
    try:
        ch = discovery.add_channel(db, url)
        return json.dumps(ch, default=str)
    finally:
        db.close()


@mcp.tool()
def snowball_discover(channel_url: str, depth: int = 1) -> str:
    """Discover related channels via featured channels and collaborations."""
    db = _db()
    try:
        channels = discovery.snowball(db, channel_url, max_results=10 * depth)
        return json.dumps(channels, default=str)
    finally:
        db.close()


@mcp.tool()
def fetch_channel(channel_id: str, include_transcripts: bool = False) -> str:
    """Fetch video data for a single channel."""
    db = _db()
    try:
        result = discovery.fetch_data(db, channel_id, include_transcripts=include_transcripts)
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def fetch_niche(niche_name: str, include_transcripts: bool = False) -> str:
    """Fetch video data for all channels in a niche group."""
    db = _db()
    try:
        result = discovery.fetch_data(db, niche_name, include_transcripts=include_transcripts)
        return json.dumps(result, default=str)
    finally:
        db.close()


# --- Group tools ---

@mcp.tool()
def create_niche_group(name: str, channel_ids: list[str]) -> str:
    """Create a niche group with the given channels."""
    db = _db()
    try:
        group_id = groups.create(db, name, channel_ids)
        return json.dumps({"id": group_id, "name": name, "channels": channel_ids})
    finally:
        db.close()


@mcp.tool()
def list_niche_groups() -> str:
    """List all niche groups."""
    db = _db()
    try:
        grps = groups.list_all(db)
        return json.dumps(grps, default=str)
    finally:
        db.close()


@mcp.tool()
def add_to_group(niche_name: str, channel_ids: list[str]) -> str:
    """Add channels to an existing niche group."""
    db = _db()
    try:
        groups.add_channels(db, niche_name, channel_ids)
        return json.dumps({"status": "ok", "added": channel_ids})
    finally:
        db.close()


@mcp.tool()
def remove_from_group(niche_name: str, channel_ids: list[str]) -> str:
    """Remove channels from a niche group."""
    db = _db()
    try:
        groups.remove_channels(db, niche_name, channel_ids)
        return json.dumps({"status": "ok", "removed": channel_ids})
    finally:
        db.close()


# --- Analysis tools ---

@mcp.tool()
def find_outliers(target: str, threshold: float = 2.0) -> str:
    """Find viral outlier videos that dramatically outperform a channel's average."""
    db = _db()
    try:
        result = analysis.outliers(db, target, threshold)
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def find_content_gaps(niche: str) -> str:
    """Identify content topics with high search demand but low competitor coverage."""
    db = _db()
    try:
        result = analysis.content_gaps(db, niche)
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def analyze_titles(target: str) -> str:
    """Analyze title patterns and their correlation with view performance."""
    db = _db()
    try:
        result = analysis.titles(db, target)
        result.pop("title_details", None)
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def analyze_engagement(target: str) -> str:
    """Analyze engagement ratios and find hidden gems."""
    db = _db()
    try:
        result = analysis.engagement(db, target)
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def benchmark_niche(niche: str) -> str:
    """Calculate niche averages and per-channel benchmark deviations."""
    db = _db()
    try:
        result = analysis.benchmarks(db, niche)
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def analyze_seo(target: str) -> str:
    """Analyze tag usage, shared tags, and tag-to-performance correlation."""
    db = _db()
    try:
        result = analysis.seo(db, target)
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def analyze_timing(target: str) -> str:
    """Analyze upload timing patterns and their performance impact."""
    db = _db()
    try:
        result = analysis.timing(db, target)
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def compare_channels(channel_ids: list[str]) -> str:
    """Side-by-side comparison of multiple channels."""
    db = _db()
    try:
        result = analysis.compare(db, channel_ids)
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def analyze_regional(niche: str) -> str:
    """Analyze regional and language distribution with CPM-adjusted estimates."""
    db = _db()
    try:
        result = analysis.regional(db, niche)
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def full_report(niche: str) -> str:
    """Run all analyzers and produce a comprehensive report."""
    db = _db()
    try:
        result = reporting.full_report(db, niche)
        return json.dumps(result, default=str)
    finally:
        db.close()


# --- Utility tools ---

@mcp.tool()
def get_status() -> str:
    """Get cached data statistics and freshness info."""
    db = _db()
    try:
        result = db.get_status()
        return json.dumps(result, default=str)
    finally:
        db.close()


@mcp.tool()
def get_channel_info(channel_id: str) -> str:
    """Get detailed info about a cached channel."""
    db = _db()
    try:
        ch = db.get_channel(channel_id)
        return json.dumps(ch, default=str)
    finally:
        db.close()


@mcp.tool()
def get_video_info(video_id: str) -> str:
    """Get detailed info about a cached video."""
    db = _db()
    try:
        row = db.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
        result = dict(row) if row else None
        return json.dumps(result, default=str)
    finally:
        db.close()


def main():
    """Run the MCP server via stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
