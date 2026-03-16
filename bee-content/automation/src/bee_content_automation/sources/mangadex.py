"""MangaDex REST API integration.

MangaDex is the primary source for chapter data and page images.
Free, no auth needed. Has rate limits (~5 req/s).

API docs: https://api.mangadex.org/docs/
"""

import asyncio

import httpx

from ..models import Chapter

MANGADEX_URL = "https://api.mangadex.org"
RATE_LIMIT_DELAY = 0.3  # seconds between requests


class MangaDexError(Exception):
    """MangaDex API error."""


class RateLimitError(MangaDexError):
    """Rate limit exceeded."""


async def _get(path: str, params: dict | None = None) -> dict:
    """Make a GET request to MangaDex API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{MANGADEX_URL}{path}",
            params=params or {},
            headers={"User-Agent": "bee-content-automation/0.1.0"},
        )
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "60"))
            raise RateLimitError(f"Rate limited. Retry after {retry_after}s")
        resp.raise_for_status()
        return resp.json()


async def search_manga(title: str, limit: int = 10) -> list[dict]:
    """Search MangaDex for a manga by title.

    Args:
        title: Manga title to search for.
        limit: Max results (max 100).

    Returns:
        List of dicts with keys: id, title, alt_titles, description,
        status, year, tags, content_rating.
    """
    data = await _get("/manga", {
        "title": title,
        "limit": min(limit, 100),
        "includes[]": ["cover_art"],
        "order[relevance]": "desc",
    })
    results = []
    for item in data.get("data", []):
        attrs = item.get("attributes", {})
        titles = attrs.get("title", {})
        desc = attrs.get("description", {})
        tags = [
            t.get("attributes", {}).get("name", {}).get("en", "")
            for t in attrs.get("tags", [])
        ]
        results.append({
            "id": item["id"],
            "title": titles.get("en") or titles.get("ja") or next(iter(titles.values()), ""),
            "alt_titles": attrs.get("altTitles", []),
            "description": desc.get("en", ""),
            "status": attrs.get("status", ""),
            "year": attrs.get("year"),
            "tags": [t for t in tags if t],
            "content_rating": attrs.get("contentRating", ""),
        })
    return results


async def get_chapters(
    manga_id: str, language: str = "en", limit: int = 50
) -> list[Chapter]:
    """Get chapters for a manga, sorted by chapter number.

    Args:
        manga_id: MangaDex manga UUID.
        language: Language code (default: "en").
        limit: Max chapters to return (max 100 per request).

    Returns:
        List of Chapter objects sorted by chapter number.
    """
    data = await _get(f"/manga/{manga_id}/feed", {
        "translatedLanguage[]": [language],
        "limit": min(limit, 100),
        "order[chapter]": "asc",
        "includes[]": ["scanlation_group"],
    })
    chapters = []
    for item in data.get("data", []):
        attrs = item.get("attributes", {})
        chapter_num = attrs.get("chapter")
        if chapter_num is None:
            continue
        try:
            num = float(chapter_num)
        except (ValueError, TypeError):
            continue

        # Extract scanlation group name from relationships
        group_name = None
        for rel in item.get("relationships", []):
            if rel.get("type") == "scanlation_group":
                group_attrs = rel.get("attributes", {})
                if group_attrs:
                    group_name = group_attrs.get("name")

        chapters.append(Chapter(
            id=item["id"],
            number=num,
            title=attrs.get("title"),
            language=language,
            pages=attrs.get("pages", 0),
            scanlation_group=group_name,
            published_at=attrs.get("publishAt", ""),
        ))
    return sorted(chapters, key=lambda c: c.number)


async def get_chapter_pages(chapter_id: str) -> list[str]:
    """Get page image URLs for a chapter.

    Uses the MangaDex@Home delivery network.

    Args:
        chapter_id: MangaDex chapter UUID.

    Returns:
        List of full image URLs for each page.
    """
    data = await _get(f"/at-home/server/{chapter_id}")
    base_url = data.get("baseUrl", "")
    chapter_data = data.get("chapter", {})
    chapter_hash = chapter_data.get("hash", "")
    pages = chapter_data.get("data", [])

    urls = [
        f"{base_url}/data/{chapter_hash}/{page}"
        for page in pages
    ]
    return urls


async def get_cover(manga_id: str) -> str | None:
    """Get cover art URL for a manga.

    Args:
        manga_id: MangaDex manga UUID.

    Returns:
        Cover image URL or None.
    """
    data = await _get(f"/cover", {
        "manga[]": [manga_id],
        "limit": 1,
        "order[volume]": "desc",
    })
    covers = data.get("data", [])
    if not covers:
        return None
    filename = covers[0].get("attributes", {}).get("fileName", "")
    if not filename:
        return None
    return f"https://uploads.mangadex.org/covers/{manga_id}/{filename}"
