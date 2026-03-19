"""ASS caption generation — word-by-word karaoke and phrase-by-phrase subtitles."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from math import ceil
from pathlib import Path

import pysubs2

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


CAPTION_CONTENT_TYPES = {"NAR", "REAL_AUDIO"}

STYLE_MAP = {
    "NAR": "Narrator",
    "REAL_AUDIO": "RealAudio",
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


def _create_ass_styles(subs: pysubs2.SSAFile) -> None:
    """Add caption styles to an ASS file."""
    base = dict(
        fontname="Arial",
        fontsize=48,
        primarycolor=pysubs2.Color(255, 255, 255, 0),
        outlinecolor=pysubs2.Color(0, 0, 0, 0),
        backcolor=pysubs2.Color(0, 0, 0, 128),
        bold=True,
        outline=3,
        shadow=2,
        alignment=2,  # bottom-center
        marginl=40,
        marginr=40,
        marginv=50,
    )
    subs.styles["Narrator"] = pysubs2.SSAStyle(**base)
    subs.styles["NarratorPhrase"] = pysubs2.SSAStyle(**base)
    subs.styles["RealAudio"] = pysubs2.SSAStyle(
        **{**base, "fontsize": 44, "italic": True, "outline": 2},
    )


def _karaoke_text(text: str, duration_ms: int) -> str:
    """Generate karaoke-tagged text with \\kf tags.

    Distributes duration proportionally to word length with
    integer division. Any remainder is added to the last word
    so the total always sums exactly to total_cs.
    """
    words = text.split()
    if not words:
        return text

    total_cs = duration_ms // 10
    if total_cs <= 0:
        return text

    total_chars = sum(len(w) for w in words)
    if total_chars == 0:
        # All empty strings somehow
        per_word = total_cs // len(words)
        return " ".join(f"{{\\kf{per_word}}}{w}" for w in words)

    base_per_char = total_cs // total_chars
    remainder = total_cs - (base_per_char * total_chars)

    parts = []
    for i, word in enumerate(words):
        dur = base_per_char * len(word)
        if i == len(words) - 1:
            dur += remainder  # dump remainder onto last word
        parts.append(f"{{\\kf{dur}}}{word}")

    return " ".join(parts)


def _phrase_chunks(words: list[str], target_size: int = 4) -> list[list[str]]:
    """Split words into balanced chunks of 3-5 words."""
    if len(words) <= 5:
        return [words]

    chunk_size = min(5, max(3, len(words) // ceil(len(words) / target_size)))
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        chunks.append(chunk)
    return chunks


def generate_captions_estimated(
    segments: list[CaptionSegment],
    output_path: Path,
    style: str = "karaoke",
) -> Path:
    """Generate ASS captions from text + duration estimates.

    Args:
        segments: List of CaptionSegment with text, timing, and style.
        output_path: Where to write the .ass file.
        style: "karaoke" for word-by-word fill, "phrase" for 3-5 word blocks.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    subs = pysubs2.SSAFile()
    subs.info["PlayResX"] = "1920"
    subs.info["PlayResY"] = "1080"
    _create_ass_styles(subs)

    for seg in segments:
        if style == "phrase":
            words = seg.text.split()
            chunks = _phrase_chunks(words)
            total_dur = seg.end_ms - seg.start_ms
            dur_per_chunk = total_dur // len(chunks) if chunks else total_dur

            for j, chunk in enumerate(chunks):
                chunk_start = seg.start_ms + j * dur_per_chunk
                chunk_end = chunk_start + dur_per_chunk
                if j == len(chunks) - 1:
                    chunk_end = seg.end_ms  # last chunk gets remainder

                event = pysubs2.SSAEvent(
                    start=chunk_start,
                    end=chunk_end,
                    text=" ".join(chunk),
                    style=seg.style_name if seg.style_name != "Narrator" else "NarratorPhrase",
                )
                subs.events.append(event)
        else:
            # Karaoke mode
            duration_ms = seg.end_ms - seg.start_ms
            tagged_text = _karaoke_text(seg.text, duration_ms)
            event = pysubs2.SSAEvent(
                start=seg.start_ms,
                end=seg.end_ms,
                text=tagged_text,
                style=seg.style_name,
            )
            subs.events.append(event)

    subs.save(str(output_path))
    return output_path


def burn_captions(
    video_path: Path,
    ass_path: Path,
    output_path: Path,
) -> Path:
    """Burn ASS subtitles into video via FFmpeg ass filter.

    This is a post-processing step — runs a second encode pass.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # FFmpeg ass filter needs absolute path with escaped colons
    abs_ass = str(ass_path.resolve()).replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"ass={abs_ass}",
        "-c:a", "copy",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg caption burn failed: {result.stderr[:500]}")

    return output_path
