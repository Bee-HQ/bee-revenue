"""Canonical markdown writer for bee-video storyboard format v2.

Produces deterministic output: same input always yields the exact same string.
This enables reliable round-trip testing (parse → write → parse).
"""

from __future__ import annotations

import json

from bee_video_editor.formats.parser import ParsedStoryboard


def write_v2(parsed: ParsedStoryboard) -> str:
    """Write a ParsedStoryboard to canonical v2 markdown.

    Args:
        parsed: A parsed storyboard (from parse_v2 or constructed directly).

    Returns:
        Canonical markdown string.
    """
    parts: list[str] = []

    # Project block
    project_data = parsed.project.model_dump(by_alias=True, exclude_none=True)
    parts.append("```json bee-video:project")
    parts.append(json.dumps(project_data, indent=2))
    parts.append("```")

    # Build section → segments mapping (preserving order)
    section_segments: dict[str, list] = {}
    for sec in parsed.sections:
        section_segments[sec.title] = []
    for seg in parsed.segments:
        if seg.section in section_segments:
            section_segments[seg.section].append(seg)

    # Emit sections and their segments
    for section in parsed.sections:
        parts.append("")
        parts.append(f"## {section.title} ({section.start} - {section.end})")

        segs = section_segments.get(section.title, [])
        for seg in segs:
            parts.append("")
            parts.append(f"### {seg.start} - {seg.end} | {seg.title}")

            # Segment config JSON block (omit if empty)
            config_data = _dump_segment_config(seg.config)
            if config_data:
                parts.append("")
                parts.append("```json bee-video:segment")
                parts.append(json.dumps(config_data, indent=2))
                parts.append("```")

            # Narration
            if seg.narration:
                parts.append("")
                parts.append(_format_narration(seg.narration))

    # Trailing newline
    return "\n".join(parts) + "\n"


def _dump_segment_config(config) -> dict | None:
    """Dump a SegmentConfig to a dict, omitting None fields and empty lists.

    Returns None if the config is effectively empty (no visual, audio,
    overlay, captions, or transition).
    """
    data = config.model_dump(by_alias=True, exclude_none=True)
    # Remove empty lists
    data = {k: v for k, v in data.items() if v != []}
    # If nothing left, return None (narration-only segment)
    if not data:
        return None
    return data


def _format_narration(narration: str) -> str:
    """Format narration text as blockquote lines.

    Each paragraph (separated by \\n\\n) starts with `> NAR: `.
    Continuation lines within a paragraph use `> ` prefix.
    Paragraphs are separated by a blank blockquote line (`>`).
    """
    paragraphs = narration.split("\n\n")
    parts: list[str] = []

    for i, para in enumerate(paragraphs):
        if i > 0:
            parts.append(">")
        # First line of paragraph gets NAR: prefix
        parts.append(f"> NAR: {para}")

    return "\n".join(parts)
