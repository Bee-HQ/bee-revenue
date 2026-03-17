"""Convert between assembly guide (Project) and storyboard (Storyboard) models."""

from __future__ import annotations

import re

from bee_video_editor.models import Project, Segment, SegmentType
from bee_video_editor.models_storyboard import (
    LayerEntry,
    ProductionRules,
    Storyboard,
    StoryboardSegment,
)


def assembly_guide_to_storyboard(project: Project) -> Storyboard:
    """Convert an assembly guide Project to a Storyboard.

    Best-effort parsing of flat string fields into typed LayerEntry objects.
    Quotes in text are preserved — stripping is the consumer's job.
    """
    segments = []
    for seg in project.segments:
        start_str = str(seg.start)
        end_str = str(seg.end)
        seg_id = f"{start_str.replace(':', '_')}-{end_str.replace(':', '_')}"

        visual, overlay = _parse_visual(seg.visual, seg.segment_type)
        audio, music = _parse_audio(seg.audio, seg.segment_type)
        source = _parse_source(seg.source_notes)

        title = seg.subsection or seg.section or f"{start_str}-{end_str}"

        segments.append(StoryboardSegment(
            id=seg_id,
            start=start_str,
            end=end_str,
            title=title,
            section=seg.section,
            section_time="",
            subsection=seg.subsection,
            visual=visual,
            audio=audio,
            overlay=overlay,
            music=music,
            source=source,
            transition=[],
        ))

    return Storyboard(
        title=project.title,
        segments=segments,
        production_rules=ProductionRules(),
    )


def _parse_visual(visual_str: str, seg_type: SegmentType) -> tuple[list[LayerEntry], list[LayerEntry]]:
    """Parse visual string into visual + overlay layer entries."""
    visual_entries = []
    overlay_entries = []

    if not visual_str.strip():
        return visual_entries, overlay_entries

    # Check for bible code: [CODE: qualifier] rest  or  [CODE] rest
    bible_match = re.match(r'\[([A-Z][A-Z0-9_-]+)(?::\s*([^\]]*))?\]\s*(.*)', visual_str)
    if bible_match:
        code = bible_match.group(1)
        qualifier = bible_match.group(2)
        rest = bible_match.group(3).strip()
        content = f"{qualifier.strip()} {rest}".strip() if qualifier else rest

        entry = LayerEntry(content=content, content_type=code, raw=visual_str)

        # Lower thirds go to overlay layer
        if code == "LOWER-THIRD" or "lower third" in visual_str.lower():
            entry.content_type = "LOWER-THIRD"
            overlay_entries.append(entry)
        else:
            visual_entries.append(entry)
        return visual_entries, overlay_entries

    # Check for backtick prefix: `TYPE:` content
    bt_match = re.match(r'`([A-Z][A-Z\s]*?):`\s*(.*)', visual_str)
    if bt_match:
        content_type = bt_match.group(1).strip()
        content = bt_match.group(2).strip()
        visual_entries.append(LayerEntry(content=content, content_type=content_type, raw=visual_str))
        return visual_entries, overlay_entries

    # Check for lower third in raw text
    if "lower third" in visual_str.lower():
        overlay_entries.append(LayerEntry(content=visual_str, content_type="LOWER-THIRD", raw=visual_str))
        return visual_entries, overlay_entries

    # Default based on segment type
    default_type = "UNKNOWN"
    if seg_type == SegmentType.REAL:
        default_type = "BODYCAM"

    visual_entries.append(LayerEntry(content=visual_str, content_type=default_type, raw=visual_str))
    return visual_entries, overlay_entries


def _parse_audio(audio_str: str, seg_type: SegmentType) -> tuple[list[LayerEntry], list[LayerEntry]]:
    """Parse audio string into audio + music layer entries."""
    audio_entries = []
    music_entries = []

    if not audio_str.strip():
        return audio_entries, music_entries

    # Extract music notes from trailing "+ music..."
    music_match = re.search(r'\s*\+\s*(.+)$', audio_str)
    main_audio = audio_str
    if music_match:
        music_text = music_match.group(1).strip()
        music_entries.append(LayerEntry(content=music_text, content_type="MUSIC", raw=music_text))
        main_audio = audio_str[:music_match.start()]

    main_audio = main_audio.strip()
    if not main_audio:
        return audio_entries, music_entries

    # Check for NAR: prefix
    nar_match = re.match(r'NAR:\s*(.*)', main_audio, re.IGNORECASE)
    if nar_match:
        content = nar_match.group(1).strip()
        audio_entries.append(LayerEntry(content=content, content_type="NAR", raw=main_audio))
        return audio_entries, music_entries

    # Check for REAL AUDIO: or REAL: prefix
    real_match = re.match(r'REAL(?:\s+AUDIO)?:\s*(.*)', main_audio, re.IGNORECASE)
    if real_match:
        content = real_match.group(1).strip()
        audio_entries.append(LayerEntry(content=content, content_type="REAL AUDIO", raw=main_audio))
        return audio_entries, music_entries

    # Default based on segment type
    if seg_type in (SegmentType.NAR, SegmentType.MIX):
        audio_entries.append(LayerEntry(content=main_audio, content_type="NAR", raw=main_audio))
    else:
        audio_entries.append(LayerEntry(content=main_audio, content_type="UNKNOWN", raw=main_audio))

    return audio_entries, music_entries


def _parse_source(source_str: str) -> list[LayerEntry]:
    """Parse source notes into source layer entries."""
    if not source_str.strip():
        return []
    return [
        LayerEntry(content=line.strip(), content_type="SOURCE", raw=line.strip())
        for line in source_str.split("\n")
        if line.strip()
    ]
