"""ASS caption generation — word-by-word karaoke and phrase-by-phrase subtitles."""

from __future__ import annotations

import re
from dataclasses import dataclass
from math import ceil
from pathlib import Path

from bee_video_editor.models_storyboard import Storyboard


@dataclass
class CaptionSegment:
    """A single captioned section."""
    text: str
    start_ms: int
    end_ms: int
    style_name: str  # "Narrator", "NarratorPhrase", "RealAudio"


def _time_to_ms(t: str) -> int:
    """Convert MM:SS or H:MM:SS string to milliseconds."""
    parts = t.strip().split(":")
    if len(parts) == 2:
        return (int(parts[0]) * 60 + int(parts[1])) * 1000
    if len(parts) == 3:
        return (int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])) * 1000
    return 0


def _clean_text(raw: str) -> str:
    """Strip quotes, smart quotes, and trailing notes from caption text."""
    text = re.sub(r'\s*\+\s*.*$', '', raw)
    text = text.strip().strip('"').strip('\u201c').strip('\u201d')
    return text.strip()


CAPTION_CONTENT_TYPES = {"NAR", "REAL AUDIO"}

STYLE_MAP = {
    "NAR": "Narrator",
    "REAL AUDIO": "RealAudio",
}


def extract_caption_segments(storyboard: Storyboard) -> list[CaptionSegment]:
    """Extract captionable text from storyboard segments.

    Walks every segment's audio layer entries. For each NAR or REAL AUDIO entry:
    - Strips quotes and trailing notes
    - Converts times to milliseconds
    - Uses LayerEntry.time_start/time_end if present
    - Maps content_type to style name
    """
    results = []
    for seg in storyboard.segments:
        seg_start_ms = _time_to_ms(seg.start)
        seg_end_ms = _time_to_ms(seg.end)

        for entry in seg.audio:
            if entry.content_type not in CAPTION_CONTENT_TYPES:
                continue

            text = _clean_text(entry.content)
            if not text:
                continue

            # Use entry-level time range if available, else segment range
            if entry.time_start and entry.time_end:
                start_ms = _time_to_ms(entry.time_start)
                end_ms = _time_to_ms(entry.time_end)
            else:
                start_ms = seg_start_ms
                end_ms = seg_end_ms

            style_name = STYLE_MAP.get(entry.content_type, "Narrator")

            results.append(CaptionSegment(
                text=text,
                start_ms=start_ms,
                end_ms=end_ms,
                style_name=style_name,
            ))

    return results
