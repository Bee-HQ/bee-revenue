"""Multi-provider stock media search — Pexels + Pixabay.

Provides a unified interface for searching and downloading stock footage
and photos from multiple providers.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import httpx


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class SearchResult:
    """A single result from any provider."""
    provider: str          # "pexels" | "pixabay"
    media_type: str        # "video" | "photo"
    id: str
    url: str               # page URL
    download_url: str      # direct download URL
    width: int = 0
    height: int = 0
    duration: int = 0      # seconds (0 for photos)
    thumbnail_url: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class SearchQuery:
    """A search request extracted from a storyboard."""
    query: str
    media_type: str = "video"   # "video" | "photo"
    min_duration: int = 5
    segment_ids: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pexels
# ---------------------------------------------------------------------------

PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"
PEXELS_PHOTO_URL = "https://api.pexels.com/v1/search"


def search_pexels_videos(
    query: str,
    api_key: str | None = None,
    per_page: int = 10,
    min_duration: int = 0,
    orientation: str | None = None,
) -> list[SearchResult]:
    """Search Pexels for stock video clips."""
    api_key = api_key or os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        return []

    params: dict = {"query": query, "per_page": per_page}
    if orientation:
        params["orientation"] = orientation

    try:
        response = httpx.get(
            PEXELS_VIDEO_URL,
            headers={"Authorization": api_key},
            params=params,
            timeout=30,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    results = []
    for video in response.json().get("videos", []):
        if min_duration and video.get("duration", 0) < min_duration:
            continue

        download_url = ""
        for vf in video.get("video_files", []):
            if vf.get("quality") == "hd" and vf.get("file_type") == "video/mp4":
                download_url = vf["link"]
                break
        if not download_url:
            for vf in video.get("video_files", []):
                if vf.get("file_type") == "video/mp4":
                    download_url = vf["link"]
                    break

        if not download_url:
            continue

        results.append(SearchResult(
            provider="pexels",
            media_type="video",
            id=str(video["id"]),
            url=video.get("url", ""),
            download_url=download_url,
            width=video.get("width", 0),
            height=video.get("height", 0),
            duration=video.get("duration", 0),
        ))

    return results


def search_pexels_photos(
    query: str,
    api_key: str | None = None,
    per_page: int = 10,
    orientation: str | None = None,
) -> list[SearchResult]:
    """Search Pexels for stock photos."""
    api_key = api_key or os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        return []

    params: dict = {"query": query, "per_page": per_page}
    if orientation:
        params["orientation"] = orientation

    try:
        response = httpx.get(
            PEXELS_PHOTO_URL,
            headers={"Authorization": api_key},
            params=params,
            timeout=30,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    results = []
    for photo in response.json().get("photos", []):
        src = photo.get("src", {})
        download_url = src.get("original") or src.get("large2x") or src.get("large", "")
        if not download_url:
            continue

        results.append(SearchResult(
            provider="pexels",
            media_type="photo",
            id=str(photo["id"]),
            url=photo.get("url", ""),
            download_url=download_url,
            width=photo.get("width", 0),
            height=photo.get("height", 0),
        ))

    return results


# ---------------------------------------------------------------------------
# Pixabay
# ---------------------------------------------------------------------------

PIXABAY_VIDEO_URL = "https://pixabay.com/api/videos/"
PIXABAY_PHOTO_URL = "https://pixabay.com/api/"


def search_pixabay_videos(
    query: str,
    api_key: str | None = None,
    per_page: int = 10,
    min_duration: int = 0,
) -> list[SearchResult]:
    """Search Pixabay for stock video clips."""
    api_key = api_key or os.environ.get("PIXABAY_API_KEY", "")
    if not api_key:
        return []

    params: dict = {"key": api_key, "q": query, "per_page": min(per_page, 200)}
    if min_duration:
        params["min_duration"] = min_duration

    try:
        response = httpx.get(PIXABAY_VIDEO_URL, params=params, timeout=30)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    results = []
    for hit in response.json().get("hits", []):
        videos = hit.get("videos", {})
        # Prefer large > medium > small > tiny
        download_url = ""
        for quality in ("large", "medium", "small", "tiny"):
            vid = videos.get(quality, {})
            if vid.get("url"):
                download_url = vid["url"]
                break

        if not download_url:
            continue

        results.append(SearchResult(
            provider="pixabay",
            media_type="video",
            id=str(hit["id"]),
            url=hit.get("pageURL", ""),
            download_url=download_url,
            width=hit.get("videos", {}).get("large", {}).get("width", 0),
            height=hit.get("videos", {}).get("large", {}).get("height", 0),
            duration=hit.get("duration", 0),
            tags=hit.get("tags", "").split(", "),
        ))

    return results


def search_pixabay_photos(
    query: str,
    api_key: str | None = None,
    per_page: int = 10,
) -> list[SearchResult]:
    """Search Pixabay for stock photos."""
    api_key = api_key or os.environ.get("PIXABAY_API_KEY", "")
    if not api_key:
        return []

    params: dict = {"key": api_key, "q": query, "per_page": min(per_page, 200), "image_type": "photo"}

    try:
        response = httpx.get(PIXABAY_PHOTO_URL, params=params, timeout=30)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    results = []
    for hit in response.json().get("hits", []):
        download_url = hit.get("largeImageURL") or hit.get("webformatURL", "")
        if not download_url:
            continue

        results.append(SearchResult(
            provider="pixabay",
            media_type="photo",
            id=str(hit["id"]),
            url=hit.get("pageURL", ""),
            download_url=download_url,
            width=hit.get("imageWidth", 0),
            height=hit.get("imageHeight", 0),
            tags=hit.get("tags", "").split(", "),
        ))

    return results


# ---------------------------------------------------------------------------
# Unified search
# ---------------------------------------------------------------------------

def search_stock(
    query: str,
    media_type: str = "video",
    providers: list[str] | None = None,
    per_page: int = 5,
    min_duration: int = 0,
) -> list[SearchResult]:
    """Search across enabled providers and merge results.

    Args:
        query: Search terms.
        media_type: "video" or "photo".
        providers: List of providers to use. Defaults to all with API keys set.
        per_page: Results per provider.
        min_duration: Minimum video duration (ignored for photos).

    Returns:
        Combined list of SearchResult from all providers.
    """
    if providers is None:
        providers = []
        if os.environ.get("PEXELS_API_KEY"):
            providers.append("pexels")
        if os.environ.get("PIXABAY_API_KEY"):
            providers.append("pixabay")

    if not providers:
        return []

    results: list[SearchResult] = []

    for provider in providers:
        if provider == "pexels":
            if media_type == "video":
                results.extend(search_pexels_videos(query, per_page=per_page, min_duration=min_duration))
            else:
                results.extend(search_pexels_photos(query, per_page=per_page))
        elif provider == "pixabay":
            if media_type == "video":
                results.extend(search_pixabay_videos(query, per_page=per_page, min_duration=min_duration))
            else:
                results.extend(search_pixabay_photos(query, per_page=per_page))

    return results


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def download_media(
    result: SearchResult,
    output_path: Path,
    timeout: int = 120,
) -> Path | None:
    """Download a stock media file. Skips if already exists (idempotent).

    Returns the output path on success, None on failure.
    """
    from bee_video_editor.api.session import _validate_download_url, _stream_download

    output_path = Path(output_path)
    if output_path.exists():
        return output_path

    if not result.download_url:
        return None

    try:
        _validate_download_url(result.download_url)
    except Exception:
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        _stream_download(result.download_url, output_path)
        return output_path
    except Exception:
        if output_path.exists():
            output_path.unlink()
        return None


# ---------------------------------------------------------------------------
# Query extraction
# ---------------------------------------------------------------------------

_SHOT_TYPE_PREFIXES = re.compile(
    r"^(establishing shot of|close[\s-]up of|aerial shot of|aerial view of|"
    r"wide shot of|medium shot of|tracking shot of|overhead shot of|"
    r"slow[\s-]motion|time[\s-]lapse)\s+",
    re.IGNORECASE,
)
_KEN_BURNS_SUFFIX = re.compile(
    r"\s+with ken burns\s+\w+$",
    re.IGNORECASE,
)
_PARENTHETICAL = re.compile(r"\s*\([^)]*\)\s*$")


def _clean_search_term(term: str) -> str:
    """Strip cinematographic descriptors that confuse stock search APIs."""
    term = _SHOT_TYPE_PREFIXES.sub("", term.strip())
    term = _KEN_BURNS_SUFFIX.sub("", term)
    term = _PARENTHETICAL.sub("", term)
    return term.strip()


def extract_search_queries(parsed) -> list[SearchQuery]:
    """Extract search queries from a ParsedStoryboard's visual entries."""
    from bee_video_editor.formats.parser import ParsedStoryboard, segment_duration

    queries: dict[str, SearchQuery] = {}

    for seg in parsed.segments:
        for entry in seg.config.visual:
            if entry.type in ("STOCK", "FOOTAGE"):
                query = _clean_search_term(entry.query or entry.src or "")
                if query:
                    key = f"video:{query}"
                    if key not in queries:
                        queries[key] = SearchQuery(
                            query=query, media_type="video",
                            min_duration=max(int(segment_duration(seg)), 5),
                        )
                    queries[key].segment_ids.append(seg.id)
            elif entry.type == "PHOTO":
                query = _clean_search_term(entry.query or entry.text or "")
                if query:
                    key = f"photo:{query}"
                    if key not in queries:
                        queries[key] = SearchQuery(query=query, media_type="photo")
                    queries[key].segment_ids.append(seg.id)

    return list(queries.values())
