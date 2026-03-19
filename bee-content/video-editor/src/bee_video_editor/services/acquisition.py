"""Media acquisition service — batch search and download for a storyboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from bee_video_editor.formats.parser import ParsedStoryboard
from bee_video_editor.processors.media_search import (
    SearchQuery, SearchResult, download_media, extract_search_queries, search_stock,
)


@dataclass
class AcquisitionItem:
    query: str
    media_type: str
    provider: str
    file_path: Path
    segment_ids: list[str] = field(default_factory=list)


@dataclass
class AcquisitionReport:
    queries_total: int = 0
    queries_matched: int = 0
    downloads_succeeded: int = 0
    downloads_failed: int = 0
    downloads_skipped: int = 0
    items: list[AcquisitionItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def acquire_media(
    parsed: ParsedStoryboard,
    project_dir: Path,
    *,
    providers: list[str] | None = None,
    per_query: int = 3,
    on_progress: callable | None = None,
) -> AcquisitionReport:
    """Search and download all stock media needed by the storyboard.

    Extracts queries from visual entries (STOCK, PHOTO), searches
    configured providers, downloads best matches.
    """
    report = AcquisitionReport()

    queries = extract_search_queries(parsed)
    report.queries_total = len(queries)

    if not queries:
        return report

    for i, sq in enumerate(queries):
        if on_progress:
            on_progress(f"Searching: {sq.query}", f"{i+1}/{len(queries)}")

        results = search_stock(
            sq.query,
            media_type=sq.media_type,
            providers=providers,
            per_page=per_query,
            min_duration=sq.min_duration,
        )

        if not results:
            report.errors.append(f"No results for: {sq.query}")
            continue

        report.queries_matched += 1

        # Download the best result (first one)
        best = results[0]
        out_dir = project_dir / ("stock" if sq.media_type == "video" else "photos")

        downloaded = download_media(best, out_dir)
        if downloaded:
            report.downloads_succeeded += 1
            report.items.append(AcquisitionItem(
                query=sq.query,
                media_type=sq.media_type,
                provider=best.provider,
                file_path=downloaded,
                segment_ids=sq.segment_ids,
            ))
        else:
            report.downloads_failed += 1
            report.errors.append(f"Download failed: {sq.query} from {best.provider}")

    return report
