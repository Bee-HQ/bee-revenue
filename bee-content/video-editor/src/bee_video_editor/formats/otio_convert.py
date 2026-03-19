"""OTIO ↔ Markdown conversion layer.

to_otio:   ParsedStoryboard → otio.schema.Timeline
from_otio: otio.schema.Timeline → ParsedStoryboard
clean_otio: Strip bee_video metadata for clean NLE export
"""

from __future__ import annotations

import opentimelineio as otio
from opentimelineio.opentime import RationalTime, TimeRange

from bee_video_editor.formats.models import (
    AudioEntry,
    CaptionsConfig,
    OverlayEntry,
    ProjectConfig,
    SegmentConfig,
    TransitionConfig,
    VisualEntry,
)
from bee_video_editor.formats.parser import (
    ParsedSection,
    ParsedSegment,
    ParsedStoryboard,
)
from bee_video_editor.formats.slugify import unique_slug
from bee_video_editor.formats.timecodes import (
    format_header_tc,
    parse_header_tc,
    parse_precise_tc,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seconds_to_rt(seconds: float, fps: float) -> RationalTime:
    """Convert seconds to RationalTime at the given fps."""
    return RationalTime(round(seconds * fps), fps)


def _make_source_range(
    duration_seconds: float,
    fps: float,
    tc_in: str | None = None,
    tc_out: str | None = None,
) -> TimeRange:
    """Build a source TimeRange from timecodes or a plain duration."""
    if tc_in is not None and tc_out is not None:
        start_sec = parse_precise_tc(tc_in)
        end_sec = parse_precise_tc(tc_out)
        return TimeRange(
            _seconds_to_rt(start_sec, fps),
            _seconds_to_rt(end_sec - start_sec, fps),
        )
    return TimeRange(
        _seconds_to_rt(0, fps),
        _seconds_to_rt(duration_seconds, fps),
    )


# ---------------------------------------------------------------------------
# to_otio
# ---------------------------------------------------------------------------

def to_otio(parsed: ParsedStoryboard, fps: float = 30.0) -> otio.schema.Timeline:
    """Convert a ParsedStoryboard to an OTIO Timeline.

    Tracks created:
        V1  — main video (TrackKind.Video)
        A1  — narration  (TrackKind.Audio)
        A2  — real audio / SFX (TrackKind.Audio)
        A3  — music      (TrackKind.Audio)
        OV1 — overlays   (TrackKind.Video)
    """
    tl = otio.schema.Timeline(name=parsed.project.title)
    tl.metadata["bee_video"] = {
        "project": parsed.project.model_dump(by_alias=True, exclude_none=True),
    }

    # Create tracks
    v1 = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
    a1 = otio.schema.Track(name="A1", kind=otio.schema.TrackKind.Audio)
    a2 = otio.schema.Track(name="A2", kind=otio.schema.TrackKind.Audio)
    a3 = otio.schema.Track(name="A3", kind=otio.schema.TrackKind.Audio)
    ov1 = otio.schema.Track(name="OV1", kind=otio.schema.TrackKind.Video)

    seen_ids: set[str] = set()
    last_section: str | None = None

    for seg in parsed.segments:
        segment_id = unique_slug(seg.title, seen_ids)
        seg_duration = parse_header_tc(seg.end) - parse_header_tc(seg.start)

        # Common segment metadata stored on every V1 item for this segment
        seg_meta_base = {
            "segment_id": segment_id,
            "segment_start": seg.start,
            "segment_end": seg.end,
        }

        # --- Transition on V1 ---
        if seg.config.transition_in is not None:
            t_dur = seg.config.transition_in.duration
            half = t_dur / 2.0
            transition = otio.schema.Transition(
                name=seg.config.transition_in.type,
                in_offset=_seconds_to_rt(half, fps),
                out_offset=_seconds_to_rt(half, fps),
            )
            transition.metadata["bee_video"] = {
                "transition_in": seg.config.transition_in.model_dump(exclude_none=True),
            }
            v1.append(transition)

        # --- V1 clips (one per visual entry) ---
        if seg.config.visual:
            for vi, visual in enumerate(seg.config.visual):
                if visual.src is not None:
                    media_ref = otio.schema.ExternalReference(target_url=visual.src)
                else:
                    media_ref = otio.schema.MissingReference()

                # Source range: use in/out if present, else segment duration
                source_range = _make_source_range(
                    seg_duration, fps, visual.tc_in, visual.out,
                )

                clip = otio.schema.Clip(
                    name=seg.title,
                    media_reference=media_ref,
                    source_range=source_range,
                )
                clip.metadata["bee_video"] = {
                    **seg_meta_base,
                    "visual": visual.model_dump(by_alias=True, exclude_none=True),
                }
                if seg.config.captions is not None:
                    clip.metadata["bee_video"]["captions"] = (
                        seg.config.captions.model_dump(exclude_none=True)
                    )

                # Section marker on first clip of a new section
                if vi == 0 and seg.section and seg.section != last_section:
                    marker = otio.schema.Marker(
                        name=seg.section,
                        marked_range=TimeRange(
                            _seconds_to_rt(0, fps),
                            _seconds_to_rt(0, fps),
                        ),
                    )
                    clip.markers.append(marker)
                    last_section = seg.section

                v1.append(clip)
        else:
            # No-visual segment (narration only, etc.) — use a Gap with metadata
            gap = otio.schema.Gap(
                source_range=TimeRange(
                    _seconds_to_rt(0, fps),
                    _seconds_to_rt(seg_duration, fps),
                ),
            )
            gap.metadata["bee_video"] = {
                **seg_meta_base,
                "no_visual": True,
                "title": seg.title,
            }
            # Section marker on gap if needed
            if seg.section and seg.section != last_section:
                marker = otio.schema.Marker(
                    name=seg.section,
                    marked_range=TimeRange(
                        _seconds_to_rt(0, fps),
                        _seconds_to_rt(0, fps),
                    ),
                )
                gap.markers.append(marker)
                last_section = seg.section
            v1.append(gap)

        # --- A1: Narration ---
        if seg.narration:
            word_count = len(seg.narration.split())
            nar_duration = word_count / 150.0 * 60.0
            nar_clip = otio.schema.Clip(
                name=f"{seg.title} — narration",
                media_reference=otio.schema.MissingReference(),
                source_range=TimeRange(
                    _seconds_to_rt(0, fps),
                    _seconds_to_rt(nar_duration, fps),
                ),
            )
            nar_clip.metadata["bee_video"] = {
                "narration": {"text": seg.narration},
                "segment_id": segment_id,
            }
            a1.append(nar_clip)
        else:
            a1.append(otio.schema.Gap(
                source_range=TimeRange(
                    _seconds_to_rt(0, fps),
                    _seconds_to_rt(seg_duration, fps),
                ),
            ))

        # --- A2 / A3: Audio entries ---
        has_a2 = False
        has_a3 = False
        for audio in seg.config.audio:
            if audio.src is not None:
                a_ref = otio.schema.ExternalReference(target_url=audio.src)
            else:
                a_ref = otio.schema.MissingReference()

            a_clip = otio.schema.Clip(
                name=f"{seg.title} — {audio.type.lower()}",
                media_reference=a_ref,
                source_range=TimeRange(
                    _seconds_to_rt(0, fps),
                    _seconds_to_rt(seg_duration, fps),
                ),
            )
            a_clip.metadata["bee_video"] = {
                "audio": audio.model_dump(by_alias=True, exclude_none=True),
                "segment_id": segment_id,
            }

            if audio.type == "MUSIC":
                a3.append(a_clip)
                has_a3 = True
            else:
                a2.append(a_clip)
                has_a2 = True

        if not has_a2:
            a2.append(otio.schema.Gap(
                source_range=TimeRange(
                    _seconds_to_rt(0, fps),
                    _seconds_to_rt(seg_duration, fps),
                ),
            ))
        if not has_a3:
            a3.append(otio.schema.Gap(
                source_range=TimeRange(
                    _seconds_to_rt(0, fps),
                    _seconds_to_rt(seg_duration, fps),
                ),
            ))

        # --- OV1: Overlays ---
        if seg.config.overlay:
            for ov in seg.config.overlay:
                ov_duration = ov.duration if ov.duration is not None else 4.0
                ov_clip = otio.schema.Clip(
                    name=f"{seg.title} — {ov.type.lower()}",
                    media_reference=otio.schema.MissingReference(),
                    source_range=TimeRange(
                        _seconds_to_rt(0, fps),
                        _seconds_to_rt(ov_duration, fps),
                    ),
                )
                ov_clip.metadata["bee_video"] = {
                    "overlay": ov.model_dump(exclude_none=True),
                    "segment_id": segment_id,
                }
                ov1.append(ov_clip)
        else:
            ov1.append(otio.schema.Gap(
                source_range=TimeRange(
                    _seconds_to_rt(0, fps),
                    _seconds_to_rt(seg_duration, fps),
                ),
            ))

    tl.tracks.append(v1)
    tl.tracks.append(a1)
    tl.tracks.append(a2)
    tl.tracks.append(a3)
    tl.tracks.append(ov1)

    return tl


# ---------------------------------------------------------------------------
# from_otio
# ---------------------------------------------------------------------------

def from_otio(timeline: otio.schema.Timeline) -> ParsedStoryboard:
    """Convert an OTIO Timeline back to a ParsedStoryboard.

    Expects the timeline to contain bee_video metadata (as produced by to_otio).
    """
    # --- Project config ---
    project_data = timeline.metadata.get("bee_video", {}).get("project", {})
    project = ProjectConfig(**project_data)

    # --- Find tracks by name ---
    tracks_by_name: dict[str, otio.schema.Track] = {}
    for track in timeline.tracks:
        tracks_by_name[track.name] = track

    v1 = tracks_by_name.get("V1")
    a1 = tracks_by_name.get("A1")
    a2 = tracks_by_name.get("A2")
    a3 = tracks_by_name.get("A3")
    ov1 = tracks_by_name.get("OV1")

    if v1 is None:
        return ParsedStoryboard(project=project, sections=[], segments=[])

    # --- Index non-V1 clips by segment_id ---
    def _index_by_segment_id(track: otio.schema.Track | None) -> dict[str, list]:
        result: dict[str, list] = {}
        if track is None:
            return result
        for item in track:
            if not isinstance(item, otio.schema.Clip):
                continue
            bv = item.metadata.get("bee_video", {})
            sid = bv.get("segment_id")
            if sid:
                result.setdefault(sid, []).append(item)
        return result

    a1_by_sid = _index_by_segment_id(a1)
    a2_by_sid = _index_by_segment_id(a2)
    a3_by_sid = _index_by_segment_id(a3)
    ov1_by_sid = _index_by_segment_id(ov1)

    # --- Walk V1: collect segments (clips and annotated gaps) ---
    # Each entry: (segment_id, title, start_tc, end_tc, clips_or_none, transition)
    SegmentInfo = tuple[
        str,  # segment_id
        str,  # title
        str,  # start_tc
        str,  # end_tc
        list[otio.schema.Clip],  # V1 clips (empty for no-visual)
        otio.schema.Transition | None,  # transition before
    ]
    segment_groups: list[SegmentInfo] = []
    pending_transition: otio.schema.Transition | None = None

    for item in v1:
        if isinstance(item, otio.schema.Transition):
            pending_transition = item
            continue

        bv = item.metadata.get("bee_video", {})
        sid = bv.get("segment_id", "")

        if isinstance(item, otio.schema.Gap):
            if bv.get("no_visual"):
                # This is a narration-only / config-less segment
                segment_groups.append((
                    sid,
                    bv.get("title", ""),
                    bv.get("segment_start", "0:00"),
                    bv.get("segment_end", "0:00"),
                    [],
                    pending_transition,
                ))
                pending_transition = None
            else:
                # Plain gap (no segment metadata) — skip
                pending_transition = None
            continue

        if isinstance(item, otio.schema.Clip):
            start_tc = bv.get("segment_start", "0:00")
            end_tc = bv.get("segment_end", "0:00")
            # Check if this clip belongs to the same segment as the previous
            if segment_groups and segment_groups[-1][0] == sid:
                segment_groups[-1][4].append(item)
            else:
                segment_groups.append((
                    sid,
                    item.name,
                    start_tc,
                    end_tc,
                    [item],
                    pending_transition,
                ))
                pending_transition = None
            continue

    # --- Reconstruct sections from markers ---
    sections: list[ParsedSection] = []
    segment_section_map: dict[str, str] = {}  # sid → section name
    current_section_name: str = ""
    section_start_map: dict[str, str] = {}  # section name → start tc

    # Re-scan V1 to extract markers and map to segment_ids
    for item in v1:
        if isinstance(item, (otio.schema.Clip, otio.schema.Gap)):
            bv = item.metadata.get("bee_video", {})
            sid = bv.get("segment_id", "")
            for marker in item.markers:
                if marker.name and marker.name != current_section_name:
                    current_section_name = marker.name
                    # Use the segment_start from this item's metadata
                    section_start_map[current_section_name] = bv.get(
                        "segment_start", "0:00"
                    )
            if current_section_name and sid:
                segment_section_map[sid] = current_section_name

    # Build sections: each section runs from its start to the end of its last seg
    section_names = list(section_start_map.keys())
    # Collect end timecodes per section
    section_end_map: dict[str, str] = {}
    for sid, title, start_tc, end_tc, clips, trans in segment_groups:
        sec = segment_section_map.get(sid, "")
        if sec:
            section_end_map[sec] = end_tc  # last one wins (ordered)

    for sec_name in section_names:
        sections.append(ParsedSection(
            title=sec_name,
            start=section_start_map[sec_name],
            end=section_end_map.get(sec_name, "0:00"),
        ))

    # --- Build segments ---
    segments: list[ParsedSegment] = []

    for sid, title, start_tc, end_tc, clips, trans in segment_groups:
        section = segment_section_map.get(sid, "")

        # Visuals
        visuals: list[VisualEntry] = []
        captions_cfg: CaptionsConfig | None = None
        for clip in clips:
            clip_bv = clip.metadata.get("bee_video", {})
            visual_data = dict(clip_bv.get("visual", {}))
            # Reconstruct src from media reference
            if isinstance(clip.media_reference, otio.schema.ExternalReference):
                visual_data["src"] = clip.media_reference.target_url
            elif isinstance(clip.media_reference, otio.schema.MissingReference):
                visual_data["src"] = None
            visuals.append(VisualEntry(**visual_data))
            # Captions from first clip that has them
            if captions_cfg is None and "captions" in clip_bv:
                captions_cfg = CaptionsConfig(**clip_bv["captions"])

        # Transition
        transition_in: TransitionConfig | None = None
        if trans is not None:
            trans_bv = trans.metadata.get("bee_video", {})
            trans_data = trans_bv.get("transition_in")
            if trans_data:
                transition_in = TransitionConfig(**trans_data)
            else:
                # Fallback: reconstruct from transition properties
                t_dur = (
                    trans.in_offset.to_seconds() + trans.out_offset.to_seconds()
                )
                transition_in = TransitionConfig(type=trans.name, duration=t_dur)

        # Audio: A2 first (REAL_AUDIO, SFX), then A3 (MUSIC)
        audio_entries: list[AudioEntry] = []
        for a_clip in a2_by_sid.get(sid, []):
            a_bv = a_clip.metadata.get("bee_video", {})
            audio_data = dict(a_bv.get("audio", {}))
            audio_entries.append(AudioEntry(**audio_data))
        for a_clip in a3_by_sid.get(sid, []):
            a_bv = a_clip.metadata.get("bee_video", {})
            audio_data = dict(a_bv.get("audio", {}))
            audio_entries.append(AudioEntry(**audio_data))

        # Overlays
        overlay_entries: list[OverlayEntry] = []
        for ov_clip in ov1_by_sid.get(sid, []):
            ov_bv = ov_clip.metadata.get("bee_video", {})
            overlay_data = dict(ov_bv.get("overlay", {}))
            overlay_entries.append(OverlayEntry(**overlay_data))

        # Narration
        narration = ""
        for n_clip in a1_by_sid.get(sid, []):
            n_bv = n_clip.metadata.get("bee_video", {})
            nar_data = n_bv.get("narration", {})
            narration = nar_data.get("text", "")

        config = SegmentConfig(
            visual=visuals,
            audio=audio_entries,
            overlay=overlay_entries,
            captions=captions_cfg,
            transition_in=transition_in,
        )

        segments.append(ParsedSegment(
            id=sid,
            title=title,
            start=start_tc,
            end=end_tc,
            section=section,
            config=config,
            narration=narration,
        ))

    return ParsedStoryboard(
        project=project,
        sections=sections,
        segments=segments,
    )


# ---------------------------------------------------------------------------
# clean_otio
# ---------------------------------------------------------------------------

def clean_otio(timeline: otio.schema.Timeline) -> otio.schema.Timeline:
    """Return a deep copy of the timeline with all bee_video metadata removed.

    Useful for exporting a clean OTIO file to external NLEs.
    """
    copy = timeline.deepcopy()

    if "bee_video" in copy.metadata:
        del copy.metadata["bee_video"]

    for track in copy.tracks:
        if hasattr(track, "metadata") and "bee_video" in track.metadata:
            del track.metadata["bee_video"]
        for item in track:
            if hasattr(item, "metadata") and "bee_video" in item.metadata:
                del item.metadata["bee_video"]
            # Clean markers on clips
            if hasattr(item, "markers"):
                for marker in item.markers:
                    if hasattr(marker, "metadata") and "bee_video" in marker.metadata:
                        del marker.metadata["bee_video"]

    return copy
