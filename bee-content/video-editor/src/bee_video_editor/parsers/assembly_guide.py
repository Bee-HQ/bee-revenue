"""Parse assembly guide markdown into structured Project data."""

from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

from bee_video_editor.models import (
    PostChecklistItem,
    PreProductionAsset,
    Project,
    Segment,
    SegmentType,
    Timecode,
    TrimInstruction,
    TrimNote,
)


def parse_assembly_guide(path: str | Path) -> Project:
    """Parse an assembly guide markdown file into a Project."""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.split("\n")

    project = Project(
        title=_extract_title(lines),
        total_duration=_extract_metadata(lines, "Total Duration"),
        resolution=_extract_metadata(lines, "Resolution"),
        format=_extract_metadata(lines, "Format"),
    )

    project.segments = _parse_segments(lines)
    project.pre_production = _parse_pre_production(lines)
    project.trim_notes = _parse_trim_notes(lines)
    project.post_checklist = _parse_post_checklist(lines)

    logger.info("Parsed %s: %d sections, %d segments", Path(path).name, len(project.sections), len(project.segments))
    return project


def _extract_title(lines: list[str]) -> str:
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            # Strip "Assembly Guide: " prefix if present
            title = re.sub(r'^Assembly Guide:\s*', '', title)
            # Strip surrounding quotes
            title = title.strip('"').strip('"').strip('"')
            return title
    return "Untitled Project"


def _extract_metadata(lines: list[str], key: str) -> str:
    for line in lines:
        match = re.match(rf'\*\*{re.escape(key)}:\*\*\s*(.*)', line.strip())
        if match:
            return match.group(1).strip()
    return ""


def _parse_segments(lines: list[str]) -> list[Segment]:
    """Parse all table rows in the Minute-by-Minute Assembly section."""
    segments = []
    current_section = ""
    current_subsection = ""
    in_assembly = False

    for line in lines:
        stripped = line.strip()

        # Detect when we enter the assembly section
        if "Minute-by-Minute Assembly" in stripped or "minute-by-minute assembly" in stripped.lower():
            in_assembly = True
            continue

        # Detect when we leave (Clip Trim Notes, Post-Assembly, etc.)
        if in_assembly and stripped.startswith("## ") and "Assembly" not in stripped:
            if "Clip Trim" in stripped or "Post-Assembly" in stripped:
                in_assembly = False
                continue

        if not in_assembly:
            continue

        # Track sections (### ACT 1: ...) and subsections (#### Murdaugh Country)
        if stripped.startswith("### "):
            current_section = stripped.lstrip("#").strip()
            # Remove timecodes from section names
            current_section = re.sub(r'\s*\([\d:]+\s*-\s*[\d:]+\)', '', current_section)
            current_subsection = ""
            continue

        if stripped.startswith("#### "):
            current_subsection = stripped.lstrip("#").strip()
            current_subsection = re.sub(r'\s*\([\d:]+\s*-\s*[\d:]+\)', '', current_subsection)
            continue

        # Parse table rows: | Time | Dur | Type | Visual | Audio | Source |
        if stripped.startswith("|") and not _is_table_header(stripped):
            segment = _parse_table_row(stripped, current_section, current_subsection)
            if segment:
                segments.append(segment)

    return segments


def _is_table_header(line: str) -> bool:
    """Check if a line is a table header or separator."""
    cells = [c.strip() for c in line.split("|")[1:-1]]
    if not cells:
        return True
    # Header separator: |------|-----|
    if all(re.match(r'^[-:]+$', c) for c in cells if c):
        return True
    # Actual header: | Time | Dur | Type |
    header_words = {"time", "dur", "type", "visual", "audio", "source", "notes", "source file", "source file / notes"}
    first_cell = cells[0].lower().strip() if cells else ""
    return first_cell in header_words


def _parse_table_row(line: str, section: str, subsection: str) -> Segment | None:
    """Parse a single assembly guide table row into a Segment."""
    cells = [c.strip() for c in line.split("|")]
    # Remove empty first/last from pipe splitting
    cells = [c for c in cells if c or cells.index(c) not in (0, len(cells) - 1)]
    # Filter out truly empty leading/trailing
    while cells and not cells[0]:
        cells.pop(0)
    while cells and not cells[-1]:
        cells.pop()

    if len(cells) < 5:
        return None

    # Parse time range: "0:00-0:15" or "0:00 - 0:15"
    time_str = cells[0].strip()
    time_match = re.match(r'(\d+:\d+)\s*-\s*(\d+:\d+)', time_str)
    if not time_match:
        return None

    start = Timecode.parse(time_match.group(1))
    end = Timecode.parse(time_match.group(2))

    # Parse duration: "15s" or "15"
    dur_str = cells[1].strip()
    dur_match = re.match(r'(\d+)', dur_str)
    if not dur_match:
        return None
    duration = int(dur_match.group(1))

    # Parse type
    type_str = cells[2].strip().upper()
    try:
        seg_type = SegmentType(type_str)
    except ValueError:
        seg_type = SegmentType.MIX  # default fallback

    visual = cells[3].strip() if len(cells) > 3 else ""
    audio = cells[4].strip() if len(cells) > 4 else ""
    source_notes = cells[5].strip() if len(cells) > 5 else ""

    return Segment(
        start=start,
        end=end,
        duration_seconds=duration,
        segment_type=seg_type,
        visual=visual,
        audio=audio,
        source_notes=source_notes,
        section=section,
        subsection=subsection,
    )


def _parse_pre_production(lines: list[str]) -> list[PreProductionAsset]:
    """Parse the Pre-Production Assets Needed section."""
    assets = []
    in_section = False
    current_category = ""

    for line in lines:
        stripped = line.strip()

        if "Pre-Production Assets" in stripped:
            in_section = True
            continue

        if in_section and stripped.startswith("## "):
            break

        if in_section and stripped.startswith("### "):
            current_category = stripped.lstrip("#").strip()
            continue

        if in_section and stripped.startswith("- ["):
            done = stripped.startswith("- [x]") or stripped.startswith("- [X]")
            desc = re.sub(r'^- \[.\]\s*', '', stripped)
            assets.append(PreProductionAsset(
                category=current_category,
                description=desc,
                done=done,
            ))

    return assets


def _parse_trim_notes(lines: list[str]) -> list[TrimNote]:
    """Parse the Clip Trim Notes section."""
    notes = []
    in_section = False
    current_note: TrimNote | None = None

    for line in lines:
        stripped = line.strip()

        if "Clip Trim Notes" in stripped:
            in_section = True
            continue

        if in_section and stripped.startswith("## ") and "Clip Trim" not in stripped:
            break

        if not in_section:
            continue

        # New file: ### `footage/911-calls/...` (7.7MB)
        file_match = re.match(r'^###\s+`([^`]+)`\s*(?:\(([^)]+)\))?', stripped)
        if file_match:
            current_note = TrimNote(
                source_file=file_match.group(1),
                file_size=file_match.group(2) or "",
            )
            notes.append(current_note)
            continue

        # Trim instruction: - **Trim 1:** 0:00-0:15 — description
        trim_match = re.match(r'^-\s+\*\*Trim\s+\d+:\*\*\s+([\d:]+)[-–—]([\d:]+)\s*[-–—]\s*(.*)', stripped)
        if trim_match and current_note:
            start = trim_match.group(1)
            end = trim_match.group(2)
            desc = trim_match.group(3).strip()

            # Parse usage from description (text in parentheses at end)
            usage_match = re.search(r'\(([^)]+)\)\s*$', desc)
            usage = usage_match.group(1) if usage_match else ""
            label = re.sub(r'\s*\([^)]+\)\s*$', '', desc)

            current_note.trims.append(TrimInstruction(
                label=label,
                start=start,
                duration=end,
                usage=usage,
            ))

    return notes


def _parse_post_checklist(lines: list[str]) -> list[PostChecklistItem]:
    """Parse the Post-Assembly Checklist section."""
    items = []
    in_section = False

    for line in lines:
        stripped = line.strip()

        if "Post-Assembly Checklist" in stripped:
            in_section = True
            continue

        if in_section and stripped.startswith("## "):
            break

        if in_section and stripped.startswith("- ["):
            done = stripped.startswith("- [x]") or stripped.startswith("- [X]")
            desc = re.sub(r'^- \[.\]\s*', '', stripped)
            items.append(PostChecklistItem(description=desc, done=done))

    return items
