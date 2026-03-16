"""Parse storyboard markdown into structured Storyboard data.

Storyboard format (shot-by-shot):

    ## SECTION (time_start - time_end)

    ### subsection (time_start - time_end)   # optional

    #### time_start - time_end | TITLE
    | Layer | Content |
    |-------|---------|
    | Visual | `TYPE:` description |
    | Audio | `TYPE:` description |
    | Overlay | `GRAPHIC:` description |
    | Music | description |
    | Source | path trim info |
    | Transition | description |

Layers can have time-ranged variants:
    | Audio (0:30-0:35) | `REAL AUDIO:` ... |
    | Audio (0:35-0:40) | `NAR:` ... |
"""

from __future__ import annotations

import re
from pathlib import Path

from bee_video_editor.models_storyboard import (
    LayerEntry,
    MapNeeded,
    PhotoNeeded,
    ProductionRules,
    StockFootageNeeded,
    Storyboard,
    StoryboardSegment,
)


def parse_storyboard(path: str | Path) -> Storyboard:
    """Parse a storyboard markdown file into a Storyboard."""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.split("\n")

    storyboard = Storyboard(title=_extract_title(lines))
    storyboard.segments = _parse_segments(lines)
    storyboard.stock_footage = _parse_stock_footage(lines)
    storyboard.photos_needed = _parse_photos(lines)
    storyboard.maps_needed = _parse_maps(lines)
    storyboard.production_rules = _parse_production_rules(lines)

    return storyboard


def _extract_title(lines: list[str]) -> str:
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            title = re.sub(r'^Shot-by-Shot Storyboard:\s*', '', title, flags=re.IGNORECASE)
            title = title.strip('"').strip('\u201c').strip('\u201d')
            return title
    return "Untitled Storyboard"


def _parse_segments(lines: list[str]) -> list[StoryboardSegment]:
    """Parse all segment blocks from the storyboard."""
    segments: list[StoryboardSegment] = []
    current_section = ""
    current_section_time = ""
    current_subsection = ""

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # ## SECTION (time - time) — top-level act/section
        section_match = re.match(
            r'^##\s+(?!#)(.+?)\s*(?:\((\d+:\d+\s*-\s*\d+:\d+)\))?\s*$', line
        )
        if section_match:
            current_section = section_match.group(1).strip()
            current_section_time = section_match.group(2) or ""
            current_subsection = ""
            i += 1
            continue

        # ### subsection OR ### time | TITLE
        h3_match = re.match(r'^###\s+(?!#)(.+)$', line)
        if h3_match:
            content = h3_match.group(1).strip()
            # Check if this is a segment header: "0:00 - 0:05 | THE HOOK"
            seg_match = re.match(r'(\d+:\d+)\s*-\s*(\d+:\d+)\s*\|\s*(.+)', content)
            if seg_match:
                seg = _parse_segment_block(
                    lines, i, seg_match,
                    current_section, current_section_time, current_subsection,
                )
                if seg:
                    segments.append(seg)
                # Skip past the table
                i += 1
                while i < len(lines) and (lines[i].strip().startswith("|") or not lines[i].strip()):
                    i += 1
                continue
            else:
                # It's a subsection name, possibly with time range
                sub_time = re.match(r'(.+?)\s*\((\d+:\d+\s*-\s*\d+:\d+)\)', content)
                if sub_time:
                    current_subsection = sub_time.group(1).strip()
                else:
                    current_subsection = content
                i += 1
                continue

        # #### time | TITLE — segment under a subsection
        h4_match = re.match(r'^####\s+(.+)$', line)
        if h4_match:
            content = h4_match.group(1).strip()
            seg_match = re.match(r'(\d+:\d+)\s*-\s*(\d+:\d+)\s*\|\s*(.+)', content)
            if seg_match:
                seg = _parse_segment_block(
                    lines, i, seg_match,
                    current_section, current_section_time, current_subsection,
                )
                if seg:
                    segments.append(seg)
                i += 1
                while i < len(lines) and (lines[i].strip().startswith("|") or not lines[i].strip()):
                    i += 1
                continue

        i += 1

    return segments


def _parse_segment_block(
    lines: list[str],
    header_idx: int,
    seg_match: re.Match,
    section: str,
    section_time: str,
    subsection: str,
) -> StoryboardSegment | None:
    """Parse a segment header + its layer table."""
    start = seg_match.group(1).strip()
    end = seg_match.group(2).strip()
    title = seg_match.group(3).strip()

    seg_id = f"{start.replace(':', '_')}-{end.replace(':', '_')}"

    segment = StoryboardSegment(
        id=seg_id,
        start=start,
        end=end,
        title=title,
        section=section,
        section_time=section_time,
        subsection=subsection,
    )

    # Parse the table rows after the header
    i = header_idx + 1
    while i < len(lines):
        row = lines[i].strip()
        if not row:
            i += 1
            continue
        if not row.startswith("|"):
            break
        # Skip header/separator rows
        if _is_layer_header(row):
            i += 1
            continue

        _parse_layer_row(row, segment)
        i += 1

    return segment


def _is_layer_header(line: str) -> bool:
    """Check if a line is a table header or separator."""
    cells = [c.strip() for c in line.split("|")[1:-1]]
    if not cells:
        return True
    if all(re.match(r'^[-:]+$', c) for c in cells if c):
        return True
    first = cells[0].lower().strip()
    return first in ("layer", "")


def _parse_layer_row(line: str, segment: StoryboardSegment) -> None:
    """Parse a single layer row and add to the segment."""
    cells = [c.strip() for c in line.split("|")]
    cells = [c for c in cells if c is not None]
    # Remove empty first/last from pipe splitting
    if cells and not cells[0]:
        cells = cells[1:]
    if cells and not cells[-1]:
        cells = cells[:-1]

    if len(cells) < 2:
        return

    layer_name_raw = cells[0].strip()
    content_raw = cells[1].strip()

    # Parse layer name and optional time range
    # e.g. "Visual (1:16-1:22)" or "Audio (0:30-0:35)" or just "Visual"
    layer_match = re.match(
        r'(Visual|Audio|Overlay|Music|Source|Transition)\s*(?:\((\d+:\d+)\s*-\s*(\d+:\d+)\))?',
        layer_name_raw,
        re.IGNORECASE,
    )
    if not layer_match:
        return

    layer_name = layer_match.group(1).lower()
    time_start = layer_match.group(2)
    time_end = layer_match.group(3)

    # Extract content type from backtick prefix: `FOOTAGE:`, `NAR:`, etc.
    type_match = re.match(r'`([A-Z][A-Z\s]*?):`\s*(.*)', content_raw)
    if type_match:
        content_type = type_match.group(1).strip()
        content = type_match.group(2).strip()
    else:
        content_type = "UNKNOWN"
        content = content_raw

    entry = LayerEntry(
        content=content,
        content_type=content_type,
        time_start=time_start,
        time_end=time_end,
        raw=content_raw,
    )

    layer_list = getattr(segment, layer_name, None)
    if layer_list is not None:
        layer_list.append(entry)


def _parse_stock_footage(lines: list[str]) -> list[StockFootageNeeded]:
    """Parse STOCK FOOTAGE NEEDED table."""
    items: list[StockFootageNeeded] = []
    in_section = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("##") and "STOCK FOOTAGE NEEDED" in stripped.upper():
            in_section = True
            continue

        if in_section and stripped.startswith("---"):
            break

        if in_section and stripped.startswith("##"):
            break

        if not in_section or not stripped.startswith("|"):
            continue

        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        if len(cells) < 4:
            continue

        # Skip header rows
        if cells[0] == "#" or re.match(r'^[-:]+$', cells[0]):
            continue

        try:
            idx = int(cells[0])
        except ValueError:
            continue

        items.append(StockFootageNeeded(
            index=idx,
            search_term=cells[1],
            used_in=cells[2],
            duration_needed=cells[3],
        ))

    return items


def _parse_photos(lines: list[str]) -> list[PhotoNeeded]:
    """Parse PHOTOS NEEDED table."""
    items: list[PhotoNeeded] = []
    in_section = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("##") and "PHOTOS NEEDED" in stripped.upper():
            in_section = True
            continue

        if in_section and stripped.startswith("---"):
            break

        if in_section and stripped.startswith("##"):
            break

        if not in_section or not stripped.startswith("|"):
            continue

        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        if len(cells) < 4:
            continue

        if cells[0] == "#" or re.match(r'^[-:]+$', cells[0]):
            continue

        try:
            idx = int(cells[0])
        except ValueError:
            continue

        items.append(PhotoNeeded(
            index=idx,
            subject=cells[1],
            source=cells[2],
            used_in=cells[3],
        ))

    return items


def _parse_maps(lines: list[str]) -> list[MapNeeded]:
    """Parse MAP IMAGES NEEDED table."""
    items: list[MapNeeded] = []
    in_section = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("##") and ("MAP IMAGES NEEDED" in stripped.upper() or "MAP IMAGE" in stripped.upper()):
            in_section = True
            continue

        if in_section and stripped.startswith("---"):
            break

        if in_section and stripped.startswith("##"):
            break

        if not in_section or not stripped.startswith("|"):
            continue

        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        if len(cells) < 5:
            continue

        if cells[0] == "#" or re.match(r'^[-:]+$', cells[0]):
            continue

        try:
            idx = int(cells[0])
        except ValueError:
            continue

        items.append(MapNeeded(
            index=idx,
            location=cells[1],
            zoom_level=cells[2],
            style=cells[3],
            used_in=cells[4],
        ))

    return items


def _parse_production_rules(lines: list[str]) -> ProductionRules:
    """Parse PRODUCTION RULES section."""
    rules: list[str] = []
    in_section = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("##") and "PRODUCTION RULES" in stripped.upper():
            in_section = True
            continue

        if in_section and stripped.startswith("##"):
            break

        if in_section and re.match(r'^\d+\.\s+', stripped):
            rule = re.sub(r'^\d+\.\s+', '', stripped)
            rules.append(rule)

    return ProductionRules(rules=rules)
