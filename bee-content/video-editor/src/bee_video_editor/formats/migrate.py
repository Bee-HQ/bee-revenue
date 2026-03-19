"""Migration: convert old Storyboard (v1 markdown) to new ParsedStoryboard (format v2).

This module is one-way only. The old Storyboard model is preserved for parsing
legacy markdown files; this converter produces the new ParsedStoryboard that
the rest of the formats package expects.
"""

from __future__ import annotations

import re

from bee_video_editor.models_storyboard import Storyboard
from bee_video_editor.formats.models import (
    AudioEntry,
    OverlayEntry,
    ProjectConfig,
    SegmentConfig,
    TransitionConfig,
    VisualEntry,
)
from bee_video_editor.formats.parser import ParsedSection, ParsedSegment, ParsedStoryboard


# Match a file path at the start of a content string (e.g. "footage/file.mp4 00:01:30-00:02:00")
_FILE_PATH_RE = re.compile(r"^(\S+\.\w+)")


def _extract_src(content: str) -> str | None:
    """Extract a file path from a source layer content string."""
    m = _FILE_PATH_RE.match(content.strip())
    return m.group(1) if m else None


def old_to_new(storyboard: Storyboard) -> ParsedStoryboard:
    """Convert an old Storyboard to a new ParsedStoryboard.

    Layer mapping:
        visual[]   → SegmentConfig.visual  (content_type → type, content → description)
        audio NAR  → ParsedSegment.narration
        audio other → SegmentConfig.audio  (REAL_AUDIO, SFX)
        music[]    → SegmentConfig.audio   (type=MUSIC)
        source[]   → merged into visual[].src  (first source entry → first visual)
        overlay[]  → SegmentConfig.overlay
        transition[] → SegmentConfig.transition_in  (first entry, duration 1.0)

    Sections: derived from segment.section + segment.section_time fields.
    """
    project = ProjectConfig(
        title=storyboard.title,
        version=1,
    )

    # Build sections: ordered unique sections with time ranges
    seen_sections: dict[str, ParsedSection] = {}
    for seg in storyboard.segments:
        section_name = seg.section
        if not section_name or section_name in seen_sections:
            continue
        # Parse section_time "0:00 - 2:30" into start/end
        start_tc = "0:00"
        end_tc = "0:00"
        if seg.section_time:
            parts = [p.strip() for p in seg.section_time.split("-")]
            if len(parts) == 2:
                start_tc = parts[0]
                end_tc = parts[1]
        seen_sections[section_name] = ParsedSection(
            title=section_name,
            start=start_tc,
            end=end_tc,
        )

    sections = list(seen_sections.values())

    # Build segments
    segments: list[ParsedSegment] = []
    for old_seg in storyboard.segments:
        # --- Visual entries ---
        visuals: list[VisualEntry] = []
        for v in old_seg.visual:
            visuals.append(VisualEntry(
                type=v.content_type,
                # content becomes a description; not a model field, but query can hold it
                query=v.content if v.content else None,
            ))

        # --- Source → merge into visual[].src ---
        for i, src_entry in enumerate(old_seg.source):
            file_path = _extract_src(src_entry.content)
            if file_path:
                if i < len(visuals):
                    # Update existing visual entry with src
                    existing = visuals[i]
                    visuals[i] = existing.model_copy(update={"src": file_path})
                else:
                    # No matching visual — create a bare visual with just the src
                    visuals.append(VisualEntry(
                        type=src_entry.content_type or "FOOTAGE",
                        src=file_path,
                    ))

        # --- Audio: separate NAR from real audio ---
        narration_parts: list[str] = []
        audio_entries: list[AudioEntry] = []

        for a in old_seg.audio:
            if a.content_type == "NAR":
                if a.content:
                    narration_parts.append(a.content)
            else:
                audio_entries.append(AudioEntry(
                    type=a.content_type,
                    src=_extract_src(a.content) if a.content else None,
                ))

        # --- Music → audio with type MUSIC ---
        for m in old_seg.music:
            audio_entries.append(AudioEntry(
                type="MUSIC",
                src=_extract_src(m.content) if m.content else None,
            ))

        # --- Overlay ---
        overlay_entries: list[OverlayEntry] = []
        for ov in old_seg.overlay:
            overlay_entries.append(OverlayEntry(
                type=ov.content_type or "TEXT",
                text=ov.content if ov.content else None,
            ))

        # --- Transition (first entry only) ---
        transition_in: TransitionConfig | None = None
        if old_seg.transition:
            first = old_seg.transition[0]
            transition_in = TransitionConfig(
                type=first.content_type.lower() if first.content_type else "cut",
                duration=1.0,
            )

        config = SegmentConfig(
            visual=visuals,
            audio=audio_entries,
            overlay=overlay_entries,
            transition_in=transition_in,
        )

        narration = " ".join(narration_parts)

        segments.append(ParsedSegment(
            title=old_seg.title,
            start=old_seg.start,
            end=old_seg.end,
            section=old_seg.section or "",
            config=config,
            narration=narration,
        ))

    return ParsedStoryboard(
        project=project,
        sections=sections,
        segments=segments,
    )
