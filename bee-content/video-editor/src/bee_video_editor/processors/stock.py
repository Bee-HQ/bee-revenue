"""Stock footage search and download via Pexels API."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

import httpx

PEXELS_API_URL = "https://api.pexels.com/videos/search"


@dataclass
class PexelsResult:
    """A single video result from Pexels."""
    id: int
    url: str
    duration: int
    width: int
    height: int
    hd_url: str
    sd_url: str | None = None


def search_pexels(
    query: str,
    api_key: str | None = None,
    per_page: int = 10,
    min_duration: int = 0,
    orientation: str | None = None,
) -> list[PexelsResult]:
    """Search Pexels for stock video clips.

    Args:
        query: Search terms (e.g. "aerial farm dusk").
        api_key: Pexels API key. Falls back to PEXELS_API_KEY env var.
        per_page: Results per page (max 80).
        min_duration: Minimum clip duration in seconds (0 = no filter).
        orientation: "landscape", "portrait", or "square" (None = any).

    Returns:
        List of PexelsResult with download URLs.
    """
    api_key = api_key or os.environ.get("PEXELS_API_KEY")
    if not api_key:
        raise ValueError(
            "No API key provided. Set PEXELS_API_KEY env var or pass api_key parameter."
        )

    params = {"query": query, "per_page": per_page}
    if orientation:
        params["orientation"] = orientation

    response = httpx.get(
        PEXELS_API_URL,
        headers={"Authorization": api_key},
        params=params,
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(f"Pexels API error {response.status_code}: {response.text[:200]}")

    data = response.json()
    results = []

    for video in data.get("videos", []):
        if min_duration and video.get("duration", 0) < min_duration:
            continue

        hd_url = None
        sd_url = None
        for vf in video.get("video_files", []):
            if vf.get("quality") == "hd" and vf.get("file_type") == "video/mp4":
                hd_url = vf["link"]
            elif vf.get("quality") == "sd" and vf.get("file_type") == "video/mp4":
                sd_url = vf["link"]

        if not hd_url and not sd_url:
            continue

        results.append(PexelsResult(
            id=video["id"],
            url=video.get("url", ""),
            duration=video.get("duration", 0),
            width=video.get("width", 0),
            height=video.get("height", 0),
            hd_url=hd_url or sd_url,
            sd_url=sd_url,
        ))

    return results


def download_stock_clip(
    url: str,
    output_path: Path,
    timeout: int = 120,
) -> Path:
    """Download a stock video clip to the given path.

    Skips download if the file already exists (idempotent).
    Uses streaming to avoid loading entire video into memory.
    """
    output_path = Path(output_path)
    if output_path.exists():
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with httpx.stream("GET", url, timeout=timeout, follow_redirects=True) as response:
        if response.status_code != 200:
            raise RuntimeError(f"Download failed ({response.status_code})")
        with open(output_path, "wb") as f:
            for chunk in response.iter_bytes(chunk_size=65536):
                f.write(chunk)

    return output_path


def slugify_query(query: str) -> str:
    """Convert search query to a filename-safe slug."""
    slug = re.sub(r'[^\w\s-]', '', query.lower())
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug.strip('-')[:40]
