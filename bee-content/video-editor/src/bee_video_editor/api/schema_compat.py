"""Convert ParsedStoryboard → BeeProjectSchema for API responses."""

from __future__ import annotations

from bee_video_editor.api.schemas import (
    AudioEntrySchema,
    BeeProjectSchema,
    BeeSegmentSchema,
    MusicEntrySchema,
    OverlayEntrySchema,
    ProductionStateSchema,
    TransitionEntrySchema,
    VisualEntrySchema,
)
from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, segment_duration
from bee_video_editor.formats.timecodes import parse_header_tc


def parsed_to_schema(parsed: ParsedStoryboard) -> BeeProjectSchema:
    segments = [_segment_to_schema(seg) for seg in parsed.segments]

    production = ProductionStateSchema()
    if parsed.project.voice_lock:
        production.narrationEngine = parsed.project.voice_lock.engine
        production.narrationVoice = parsed.project.voice_lock.voice

    fps = 30
    resolution = [1920, 1080]
    if parsed.project.output:
        fps = parsed.project.output.fps
        parts = parsed.project.output.resolution.split("x")
        if len(parts) == 2:
            resolution = [int(parts[0]), int(parts[1])]

    return BeeProjectSchema(
        title=parsed.project.title,
        fps=fps,
        resolution=resolution,
        segments=segments,
        production=production,
    )


def _segment_to_schema(seg: ParsedSegment) -> BeeSegmentSchema:
    start_sec = parse_header_tc(seg.start)
    dur_sec = segment_duration(seg)

    visual: list[VisualEntrySchema] = []
    for v in seg.config.visual:
        trim: list[float] | None = None
        if v.tc_in is not None or v.out is not None:
            try:
                tc_in = parse_header_tc(v.tc_in) if v.tc_in else 0.0
            except (ValueError, AttributeError):
                try:
                    tc_in = float(v.tc_in)
                except (TypeError, ValueError):
                    tc_in = 0.0
            try:
                tc_out = parse_header_tc(v.out) if v.out else None
            except (ValueError, AttributeError):
                try:
                    tc_out = float(v.out) if v.out else None
                except (TypeError, ValueError):
                    tc_out = None
            trim = [tc_in, tc_out] if tc_out is not None else [tc_in]

        visual.append(VisualEntrySchema(
            type=v.type,
            src=v.src or None,
            trim=trim,
            color=v.color,
            kenBurns=v.ken_burns,
            query=v.query,
        ))

    audio: list[AudioEntrySchema] = []
    for a in seg.config.audio:
        if a.type == "MUSIC":
            continue
        audio.append(AudioEntrySchema(
            type=a.type,
            src=a.src or None,
            volume=a.volume,
        ))
    if seg.narration:
        audio.append(AudioEntrySchema(
            type="NAR",
            text=seg.narration,
        ))

    music: list[MusicEntrySchema] = []
    for a in seg.config.audio:
        if a.type != "MUSIC":
            continue
        music.append(MusicEntrySchema(
            type=a.type,
            src=a.src or None,
            volume=a.volume,
        ))

    overlay: list[OverlayEntrySchema] = []
    for o in seg.config.overlay:
        content = o.text or o.quote or o.date or o.amount or ""
        overlay.append(OverlayEntrySchema(
            type=o.type,
            content=content,
            duration=o.duration,
        ))

    transition: TransitionEntrySchema | None = None
    if seg.config.transition_in:
        transition = TransitionEntrySchema(
            type=seg.config.transition_in.type.upper(),
            duration=seg.config.transition_in.duration,
        )

    return BeeSegmentSchema(
        id=seg.id,
        title=seg.title,
        section=seg.section,
        start=start_sec,
        duration=dur_sec,
        visual=visual,
        audio=audio,
        overlay=overlay,
        music=music,
        transition=transition,
    )
