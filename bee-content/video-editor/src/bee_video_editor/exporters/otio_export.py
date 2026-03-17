"""Export Storyboard to OpenTimelineIO format."""

from __future__ import annotations

from pathlib import Path

import opentimelineio as otio

from bee_video_editor.models_storyboard import Storyboard


def storyboard_to_otio(storyboard: Storyboard, fps: float = 30.0) -> otio.schema.Timeline:
    """Convert a Storyboard to an OTIO Timeline.

    Each segment becomes a Clip on the video track. Segment metadata
    (visual codes, audio types, overlay info) is preserved in OTIO's
    extensible metadata dict for roundtrip fidelity.

    Args:
        storyboard: The parsed storyboard.
        fps: Frame rate for time calculations.

    Returns:
        An OTIO Timeline object.
    """
    tl = otio.schema.Timeline(name=storyboard.title)

    video_track = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
    audio_track = otio.schema.Track(name="A1", kind=otio.schema.TrackKind.Audio)

    for seg in storyboard.segments:
        duration_secs = seg.duration_seconds
        if duration_secs <= 0:
            continue

        # Create time range
        source_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, fps),
            duration=otio.opentime.RationalTime(duration_secs * fps, fps),
        )

        # Determine media reference from assigned_media or source layer
        media_ref = otio.schema.MissingReference()
        assigned_visual = seg.assigned_media.get("visual:0")
        if assigned_visual:
            media_ref = otio.schema.ExternalReference(
                target_url=assigned_visual,
            )

        # Build metadata with our visual codes
        bee_meta = {
            "segment_id": seg.id,
            "section": seg.section,
            "subsection": seg.subsection,
            "visual_codes": [
                {"type": v.content_type, "content": v.content}
                for v in seg.visual
            ],
            "audio_types": [
                {"type": a.content_type, "content": a.content}
                for a in seg.audio
            ],
            "overlay_codes": [
                {"type": o.content_type, "content": o.content}
                for o in seg.overlay
            ],
        }

        # Video clip
        video_clip = otio.schema.Clip(
            name=f"{seg.id} | {seg.title}",
            media_reference=media_ref,
            source_range=source_range,
            metadata={"bee_video": bee_meta},
        )

        # Add markers for section changes
        seg_idx = storyboard.segments.index(seg)
        is_first_in_section = (
            seg_idx == 0
            or seg.section != storyboard.segments[seg_idx - 1].section
        )
        if is_first_in_section:
            marker = otio.schema.Marker(
                name=seg.section,
                marked_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(0, fps),
                    duration=otio.opentime.RationalTime(0, fps),
                ),
                color=otio.schema.MarkerColor.RED,
            )
            video_clip.markers.append(marker)

        video_track.append(video_clip)

        # Audio clip (matching duration)
        has_narration = any(a.content_type == "NAR" for a in seg.audio)
        has_real_audio = any(a.content_type == "REAL AUDIO" for a in seg.audio)

        if has_narration or has_real_audio:
            audio_clip = otio.schema.Clip(
                name=f"{seg.id} audio",
                media_reference=otio.schema.MissingReference(),
                source_range=source_range,
            )
            audio_track.append(audio_clip)
        else:
            # Gap for segments without audio
            audio_track.append(otio.schema.Gap(
                source_range=source_range,
            ))

    tl.tracks.append(video_track)
    tl.tracks.append(audio_track)

    return tl


def export_otio(storyboard: Storyboard, output_path: Path, fps: float = 30.0) -> Path:
    """Export a Storyboard to an OTIO JSON file.

    Args:
        storyboard: The parsed storyboard.
        output_path: Where to write the .otio file.
        fps: Frame rate.

    Returns:
        Path to the written file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tl = storyboard_to_otio(storyboard, fps=fps)
    otio.adapters.write_to_file(tl, str(output_path))

    return output_path
