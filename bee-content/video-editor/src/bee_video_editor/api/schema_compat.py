"""Convert ParsedStoryboard → StoryboardSchema for API backward compatibility."""

from __future__ import annotations

from bee_video_editor.api.schemas import (
    LayerEntrySchema,
    SegmentSchema,
    StoryboardSchema,
)
from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, segment_duration
from bee_video_editor.formats.timecodes import parse_header_tc


def parsed_to_schema(parsed: ParsedStoryboard) -> StoryboardSchema:
    segments = [_segment_to_schema(seg) for seg in parsed.segments]

    stock_count = sum(1 for s in parsed.segments for v in s.config.visual if v.type == "STOCK")
    photo_count = sum(1 for s in parsed.segments for v in s.config.visual if v.type == "PHOTO")
    map_count = sum(1 for s in parsed.segments for v in s.config.visual if v.type == "MAP")
    max_end = max((parse_header_tc(s.end) for s in parsed.segments), default=0)

    return StoryboardSchema(
        title=parsed.project.title,
        total_segments=len(segments),
        total_duration_seconds=int(max_end),
        sections=[sec.title for sec in parsed.sections],
        segments=segments,
        stock_footage_needed=stock_count,
        photos_needed=photo_count,
        maps_needed=map_count,
        production_rules=[],
    )


def _segment_to_schema(seg: ParsedSegment) -> SegmentSchema:
    visual = [
        LayerEntrySchema(
            content=v.src or v.query or v.prompt or v.type,
            content_type=v.type,
            metadata={
                "color": v.color,
                "ken_burns": v.ken_burns,
                "tc_in": v.tc_in,
                "out": v.out,
            },
        )
        for v in seg.config.visual
    ]

    audio = [
        LayerEntrySchema(
            content=a.src or "",
            content_type=a.type,
            metadata={
                "volume": a.volume,
                "fade_in": a.fade_in,
                "fade_out": a.fade_out,
            },
        )
        for a in seg.config.audio if a.type != "MUSIC"
    ]
    if seg.narration:
        audio.append(LayerEntrySchema(content=seg.narration, content_type="NAR"))

    music = [
        LayerEntrySchema(
            content=a.src or "",
            content_type=a.type,
            metadata={
                "volume": a.volume,
                "fade_in": a.fade_in,
                "fade_out": a.fade_out,
            },
        )
        for a in seg.config.audio if a.type == "MUSIC"
    ]

    overlay = [
        LayerEntrySchema(
            content=o.text or o.quote or o.date or o.amount or "",
            content_type=o.type,
        )
        for o in seg.config.overlay
    ]

    source = [
        LayerEntrySchema(content=v.src or "", content_type=v.type)
        for v in seg.config.visual if v.src
    ]

    transition = []
    if seg.config.transition_in:
        transition.append(LayerEntrySchema(
            content=f"{seg.config.transition_in.duration}s",
            content_type=seg.config.transition_in.type.upper(),
        ))

    assigned_media: dict[str, str] = {}
    for i, v in enumerate(seg.config.visual):
        if v.src:
            assigned_media[f"visual:{i}"] = v.src

    return SegmentSchema(
        id=seg.id,
        start=seg.start,
        end=seg.end,
        title=seg.title,
        section=seg.section,
        section_time="",
        subsection="",
        duration_seconds=segment_duration(seg),
        visual=visual,
        audio=audio,
        overlay=overlay,
        music=music,
        source=source,
        transition=transition,
        assigned_media=assigned_media,
    )
