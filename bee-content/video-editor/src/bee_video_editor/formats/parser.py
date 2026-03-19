"""Markdown parser for bee-video storyboard format v2."""

from __future__ import annotations

import json
import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path

from bee_video_editor.formats.models import ProjectConfig, SegmentConfig
from bee_video_editor.formats.slugify import unique_slug


class StoryboardParseError(Exception):
    """Error parsing a v2 storyboard markdown file."""
    pass


@dataclass
class ParsedSection:
    title: str
    start: str   # "0:00"
    end: str      # "2:30"


@dataclass
class ParsedSegment:
    id: str
    title: str
    start: str
    end: str
    section: str
    config: SegmentConfig
    narration: str   # extracted from > NAR: blockquotes


@dataclass
class ParsedStoryboard:
    project: ProjectConfig
    sections: list[ParsedSection]
    segments: list[ParsedSegment]


# Patterns
_SECTION_RE = re.compile(r"^##\s+(.+?)\s*\((\d+:\d{2}(?::\d{2})?)\s*-\s*(\d+:\d{2}(?::\d{2})?)\)\s*$")
_SEGMENT_RE = re.compile(r"^###\s+(\d+:\d{2}(?::\d{2})?)\s*-\s*(\d+:\d{2}(?::\d{2})?)\s*\|\s*(.+?)\s*$")
_FENCE_OPEN_PROJECT = re.compile(r"^```json\s+bee-video:project\s*$")
_FENCE_OPEN_SEGMENT = re.compile(r"^```json\s+bee-video:segment\s*$")
_FENCE_CLOSE = re.compile(r"^```\s*$")
_NAR_LINE = re.compile(r"^>\s*NAR:\s*(.*)$")
_BLOCKQUOTE = re.compile(r"^>")
_BLOCKQUOTE_EMPTY = re.compile(r"^>\s*$")
_TIMECODE = re.compile(r"^\d+:\d{2}(:\d{2})?$")
# Loose pattern to catch malformed segment headers (### ... | ...)
_SEGMENT_LOOSE_RE = re.compile(r"^###\s+(.+?)\s*-\s*(.+?)\s*\|\s*(.+?)\s*$")


def parse_v2(path: str | Path, *, lenient: bool = False) -> ParsedStoryboard:
    """Parse a v2 storyboard markdown file.

    Args:
        path: Path to the markdown file.
        lenient: If True, downgrade errors to warnings and skip bad segments.

    Returns:
        ParsedStoryboard with project config, sections, and segments.
    """
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines()

    project_configs: list[tuple[int, dict]] = []
    sections: list[ParsedSection] = []
    segments: list[ParsedSegment] = []
    seen_ids: set[str] = set()

    # State
    current_section: ParsedSection | None = None
    current_segment_header: dict | None = None  # {title, start, end, line}
    current_segment_config: SegmentConfig | None = None
    current_narration_lines: list[str] = []
    in_nar_paragraph: bool = False
    has_segment_json: bool = False

    # Track whether we're inside a fenced block
    in_fence: bool = False
    fence_type: str | None = None  # "project" or "segment"
    fence_lines: list[str] = []
    fence_start_line: int = 0

    def _error(msg: str, line_num: int | None = None) -> None:
        full = f"{msg} (line {line_num})" if line_num else msg
        if lenient:
            warnings.warn(full)
        else:
            raise StoryboardParseError(full)

    def _flush_segment() -> None:
        nonlocal current_segment_header, current_segment_config
        nonlocal current_narration_lines, has_segment_json, in_nar_paragraph

        if current_segment_header is None:
            return

        config = current_segment_config if current_segment_config is not None else SegmentConfig()
        narration = _join_narration(current_narration_lines)
        seg_title = current_segment_header["title"]
        seg_id = unique_slug(seg_title, seen_ids)

        segments.append(ParsedSegment(
            id=seg_id,
            title=seg_title,
            start=current_segment_header["start"],
            end=current_segment_header["end"],
            section=current_section.title if current_section else "",
            config=config,
            narration=narration,
        ))

        current_segment_header = None
        current_segment_config = None
        current_narration_lines = []
        has_segment_json = False
        in_nar_paragraph = False

    def _join_narration(lines: list[str]) -> str:
        """Join narration lines, preserving paragraph breaks."""
        if not lines:
            return ""
        # Lines are stored with None as paragraph separators
        result: list[str] = []
        current_para: list[str] = []
        for line in lines:
            if line is None:
                if current_para:
                    result.append(" ".join(current_para))
                    current_para = []
            else:
                current_para.append(line)
        if current_para:
            result.append(" ".join(current_para))
        return "\n\n".join(result)

    i = 0
    while i < len(lines):
        line = lines[i]
        line_num = i + 1

        # Inside a fenced code block — collect lines until closing fence
        if in_fence:
            if _FENCE_CLOSE.match(line):
                raw = "\n".join(fence_lines)
                if fence_type == "project":
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError as e:
                        _error(f"Invalid JSON in project block at line {fence_start_line}: {e}", fence_start_line)
                        in_fence = False
                        fence_type = None
                        fence_lines = []
                        i += 1
                        continue
                    project_configs.append((fence_start_line, data))
                elif fence_type == "segment":
                    if current_segment_header is None:
                        _error(f"orphaned segment block without preceding ### header", fence_start_line)
                        in_fence = False
                        fence_type = None
                        fence_lines = []
                        i += 1
                        continue
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError as e:
                        _error(f"Invalid JSON in segment block at line {fence_start_line}: {e}", fence_start_line)
                        in_fence = False
                        fence_type = None
                        fence_lines = []
                        i += 1
                        continue
                    try:
                        current_segment_config = SegmentConfig(**data)
                    except Exception as e:
                        _error(f"Invalid segment config at line {fence_start_line}: {e}", fence_start_line)
                        in_fence = False
                        fence_type = None
                        fence_lines = []
                        i += 1
                        continue
                    has_segment_json = True
                in_fence = False
                fence_type = None
                fence_lines = []
            else:
                fence_lines.append(line)
            i += 1
            continue

        # Check for fence openings
        if _FENCE_OPEN_PROJECT.match(line):
            in_fence = True
            fence_type = "project"
            fence_lines = []
            fence_start_line = line_num
            i += 1
            continue

        if _FENCE_OPEN_SEGMENT.match(line):
            in_fence = True
            fence_type = "segment"
            fence_lines = []
            fence_start_line = line_num
            i += 1
            continue

        # Section header: ## Title (start - end)
        m_section = _SECTION_RE.match(line)
        if m_section:
            _flush_segment()
            title = m_section.group(1).strip()
            start = m_section.group(2).strip()
            end = m_section.group(3).strip()
            current_section = ParsedSection(title=title, start=start, end=end)
            sections.append(current_section)
            i += 1
            continue

        # Segment header: ### start - end | Title
        m_segment = _SEGMENT_RE.match(line)
        if m_segment:
            _flush_segment()
            start = m_segment.group(1).strip()
            end = m_segment.group(2).strip()
            title = m_segment.group(3).strip()

            # Validate timecodes
            if not _TIMECODE.match(start) or not _TIMECODE.match(end):
                _error(f"Invalid timecode in segment header: {start} - {end}", line_num)
                i += 1
                continue

            current_segment_header = {
                "title": title,
                "start": start,
                "end": end,
                "line": line_num,
            }
            i += 1
            continue

        # Catch malformed segment headers (### X - Y | Title where X/Y aren't valid timecodes)
        m_loose = _SEGMENT_LOOSE_RE.match(line)
        if m_loose:
            start_raw = m_loose.group(1).strip()
            end_raw = m_loose.group(2).strip()
            if not _TIMECODE.match(start_raw) or not _TIMECODE.match(end_raw):
                _error(f"Invalid timecode in segment header: {start_raw} - {end_raw}", line_num)
                i += 1
                continue

        # NAR blockquote: > NAR: text
        m_nar = _NAR_LINE.match(line)
        if m_nar:
            if current_segment_header is None and len(segments) == 0:
                _error(f"NAR line before any segment header", line_num)
                i += 1
                continue
            text = m_nar.group(1).strip()
            if text:
                current_narration_lines.append(text)
            in_nar_paragraph = True
            i += 1
            continue

        # Continuation line within a blockquote (> text without NAR:)
        if _BLOCKQUOTE.match(line):
            # Empty blockquote line (just ">") — paragraph break in narration
            if _BLOCKQUOTE_EMPTY.match(line):
                if in_nar_paragraph:
                    current_narration_lines.append(None)  # paragraph separator
                i += 1
                continue
            # Check if it's a continuation of NAR (starts with > but no NAR: prefix)
            stripped = re.sub(r"^>\s*", "", line).strip()
            if in_nar_paragraph and stripped and not stripped.startswith("NAR:"):
                # Continuation of previous NAR line
                current_narration_lines.append(stripped)
                i += 1
                continue
            # Non-NAR blockquote — ignore
            in_nar_paragraph = False
            i += 1
            continue

        # Empty line — might be paragraph break in narration
        if not line.strip():
            if in_nar_paragraph:
                # Check if next non-empty line is also > NAR:
                # Insert paragraph break marker
                current_narration_lines.append(None)
                in_nar_paragraph = False
            i += 1
            continue

        # Any other line resets narration paragraph state
        in_nar_paragraph = False
        i += 1

    # Flush last segment
    _flush_segment()

    # Validate project blocks
    if len(project_configs) > 1:
        _error("Found multiple project blocks — only one is allowed")
        # In lenient mode, use the first
        project_configs = project_configs[:1]

    if len(project_configs) == 0:
        warnings.warn("No project block found — using defaults")
        project = ProjectConfig(title="Untitled", version=1)
    else:
        _, data = project_configs[0]
        try:
            project = ProjectConfig(**data)
        except Exception as e:
            _error(f"Invalid project config: {e}")
            project = ProjectConfig(title="Untitled", version=1)

    return ParsedStoryboard(
        project=project,
        sections=sections,
        segments=segments,
    )


def segment_duration(seg: ParsedSegment) -> float:
    """Return the duration of a segment in seconds."""
    from bee_video_editor.formats.timecodes import parse_header_tc
    return parse_header_tc(seg.end) - parse_header_tc(seg.start)
