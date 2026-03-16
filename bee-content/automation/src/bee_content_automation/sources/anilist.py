"""AniList GraphQL API integration.

AniList is the primary source for manga/manhwa metadata: trending series,
search, genres, tags, character info, and popularity metrics.

API docs: https://anilist.gitbook.io/anilist-apiv2-docs/
No authentication required for read operations.
"""

import asyncio

import httpx

from ..models import Series

ANILIST_URL = "https://graphql.anilist.co"
RATE_LIMIT_DELAY = 0.7  # seconds between requests

# --- GraphQL Queries ---

SEARCH_QUERY = """
query ($search: String, $page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(search: $search, type: MANGA, sort: POPULARITY_DESC) {
      id
      title { english romaji native }
      description(asHtml: false)
      genres
      tags { name rank }
      status
      chapters
      popularity
      meanScore
      coverImage { large }
      bannerImage
    }
  }
}
"""

TRENDING_QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: MANGA, sort: TRENDING_DESC) {
      id
      title { english romaji native }
      description(asHtml: false)
      genres
      tags { name rank }
      status
      chapters
      popularity
      meanScore
      coverImage { large }
      bannerImage
    }
  }
}
"""

DETAILS_QUERY = """
query ($id: Int) {
  Media(id: $id, type: MANGA) {
    id
    title { english romaji native }
    description(asHtml: false)
    genres
    tags { name rank }
    status
    chapters
    popularity
    meanScore
    coverImage { large }
    bannerImage
  }
}
"""

CHARACTERS_QUERY = """
query ($id: Int, $page: Int) {
  Media(id: $id, type: MANGA) {
    characters(page: $page, perPage: 25, sort: ROLE) {
      edges {
        role
        node {
          id
          name { full native }
          description(asHtml: false)
          image { large }
        }
      }
    }
  }
}
"""


def _parse_series(data: dict) -> Series:
    """Parse an AniList media object into a Series."""
    title = data.get("title", {})
    tags = data.get("tags", [])
    cover = data.get("coverImage", {})
    score = data.get("meanScore")

    return Series(
        id=str(data["id"]),
        title_english=title.get("english") or "",
        title_romaji=title.get("romaji") or "",
        title_native=title.get("native"),
        synopsis=data.get("description") or "",
        genres=data.get("genres", []),
        tags=[t["name"] for t in tags if t.get("rank", 0) >= 50],
        status=data.get("status", "UNKNOWN"),
        chapters=data.get("chapters"),
        popularity=data.get("popularity", 0),
        score=score / 10.0 if score else None,  # normalize to 0-10
        cover_url=cover.get("large") if cover else None,
        banner_url=data.get("bannerImage"),
    )


async def _graphql(query: str, variables: dict | None = None) -> dict:
    """Execute a GraphQL query against AniList."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            ANILIST_URL,
            json={"query": query, "variables": variables or {}},
        )
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "60"))
            raise RateLimitError(f"Rate limited. Retry after {retry_after}s")
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise AniListError(data["errors"][0].get("message", "Unknown error"))
        return data.get("data", {})


class AniListError(Exception):
    """AniList API error."""


class RateLimitError(AniListError):
    """Rate limit exceeded."""


async def search_manga(query: str, limit: int = 10) -> list[Series]:
    """Search for manga/manhwa/manhua by title.

    Args:
        query: Search string (title or keyword).
        limit: Maximum results to return (max 50).

    Returns:
        List of matching Series.
    """
    data = await _graphql(SEARCH_QUERY, {
        "search": query,
        "page": 1,
        "perPage": min(limit, 50),
    })
    media_list = data.get("Page", {}).get("media", [])
    return [_parse_series(m) for m in media_list]


async def get_trending_manga(limit: int = 20) -> list[Series]:
    """Get currently trending manga/manhwa.

    Args:
        limit: Maximum results (max 50).

    Returns:
        List of trending Series sorted by trend score.
    """
    data = await _graphql(TRENDING_QUERY, {
        "page": 1,
        "perPage": min(limit, 50),
    })
    media_list = data.get("Page", {}).get("media", [])
    return [_parse_series(m) for m in media_list]


async def get_series_details(anilist_id: int) -> Series:
    """Get full details for a specific series.

    Args:
        anilist_id: AniList media ID.

    Returns:
        Series with complete metadata.

    Raises:
        AniListError: If series not found or API error.
    """
    data = await _graphql(DETAILS_QUERY, {"id": anilist_id})
    media = data.get("Media")
    if not media:
        raise AniListError(f"Series {anilist_id} not found")
    return _parse_series(media)


async def get_characters(anilist_id: int) -> list[dict]:
    """Get character list with descriptions.

    Args:
        anilist_id: AniList media ID.

    Returns:
        List of character dicts with keys: id, name, native_name, role,
        description, image_url.
    """
    data = await _graphql(CHARACTERS_QUERY, {"id": anilist_id, "page": 1})
    edges = (
        data.get("Media", {})
        .get("characters", {})
        .get("edges", [])
    )
    characters = []
    for edge in edges:
        node = edge.get("node", {})
        name = node.get("name", {})
        image = node.get("image", {})
        characters.append({
            "id": node.get("id"),
            "name": name.get("full", ""),
            "native_name": name.get("native"),
            "role": edge.get("role", ""),
            "description": node.get("description") or "",
            "image_url": image.get("large") if image else None,
        })
    return characters
