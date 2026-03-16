"""MangaUpdates API integration.

MangaUpdates tracks release groups and chapter releases.
Primary use: detecting new chapter drops for content scheduling.

API docs: https://api.mangaupdates.com/
No authentication required for read operations.
"""

import httpx

MANGAUPDATES_URL = "https://api.mangaupdates.com/v1"
RATE_LIMIT_DELAY = 0.5


class MangaUpdatesError(Exception):
    """MangaUpdates API error."""


async def _request(method: str, path: str, **kwargs) -> dict:
    """Make a request to MangaUpdates API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(
            method,
            f"{MANGAUPDATES_URL}{path}",
            headers={"User-Agent": "bee-content-automation/0.1.0"},
            **kwargs,
        )
        if resp.status_code == 429:
            raise MangaUpdatesError("Rate limited")
        resp.raise_for_status()
        if resp.status_code == 204:
            return {}
        return resp.json()


async def search_series(query: str) -> list[dict]:
    """Search for a series on MangaUpdates.

    Args:
        query: Series title to search.

    Returns:
        List of dicts with keys: id, title, url, description, year,
        type, genres.
    """
    # MangaUpdates search uses POST with JSON body
    data = await _request("POST", "/series/search", json={
        "search": query,
        "perpage": 10,
    })
    results = []
    for item in data.get("results", []):
        record = item.get("record", {})
        results.append({
            "id": record.get("series_id"),
            "title": record.get("title", ""),
            "url": record.get("url", ""),
            "description": record.get("description", ""),
            "year": record.get("year"),
            "type": record.get("type", ""),
            "genres": [
                g.get("genre", "") for g in record.get("genres", [])
            ],
        })
    return results


async def get_latest_releases(series_id: int) -> list[dict]:
    """Get latest chapter releases for a series.

    Args:
        series_id: MangaUpdates series ID.

    Returns:
        List of dicts with keys: id, title, chapter, volume,
        group_name, release_date.
    """
    data = await _request("GET", f"/releases/search", params={
        "search": str(series_id),
        "search_type": "series",
        "perpage": 20,
    })
    releases = []
    for item in data.get("results", []):
        record = item.get("record", {})
        metadata = record.get("metadata", {})
        series = metadata.get("series", {})
        groups = record.get("groups", [])
        releases.append({
            "id": record.get("id"),
            "title": series.get("title", ""),
            "chapter": record.get("chapter", ""),
            "volume": record.get("volume", ""),
            "group_name": groups[0].get("name", "") if groups else "",
            "release_date": record.get("release_date", ""),
        })
    return releases


async def get_series_info(series_id: int) -> dict:
    """Get series metadata from MangaUpdates.

    Args:
        series_id: MangaUpdates series ID.

    Returns:
        Dict with keys: id, title, url, description, type, year,
        genres, categories, status, latest_chapter, authors, publishers.
    """
    data = await _request("GET", f"/series/{series_id}")
    return {
        "id": data.get("series_id"),
        "title": data.get("title", ""),
        "url": data.get("url", ""),
        "description": data.get("description", ""),
        "type": data.get("type", ""),
        "year": data.get("year"),
        "genres": [g.get("genre", "") for g in data.get("genres", [])],
        "categories": [
            c.get("category", "") for c in data.get("categories", [])
        ],
        "status": data.get("status", ""),
        "latest_chapter": data.get("latest_chapter"),
        "authors": [
            a.get("name", "") for a in data.get("authors", [])
        ],
        "publishers": [
            p.get("publisher_name", "") for p in data.get("publishers", [])
        ],
    }
