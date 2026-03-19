"""Compositor -- multi-layer per-segment video composition.

Takes a ParsedSegment and produces one composited video:
visual -> trim -> normalize -> color grade -> overlay -> audio mix.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from bee_video_editor.formats.models import OverlayEntry
from bee_video_editor.formats.parser import ParsedStoryboard, ParsedSegment, segment_duration
from bee_video_editor.processors.ffmpeg import (
    COLOR_GRADE_PRESETS,
    FFmpegError,
    color_grade,
    image_to_video,
    mix_audio,
    normalize_format,
    overlay_png,
    trim,
)


@dataclass
class CompositeResult:
    segment_id: str
    output_path: Path | None = None
    error: str | None = None
    layers_applied: list[str] = field(default_factory=list)


@dataclass
class CompositeReport:
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    results: list[CompositeResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def composite_segment(
    seg: ParsedSegment,
    project_dir: Path,
    output_dir: Path,
    *,
    default_color: str | None = None,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
) -> CompositeResult:
    """Composite a single segment from all its layers.

    Processing order:
    1. Resolve visual source (from seg.config.visual[].src)
    2. Trim to in/out points if specified
    3. Normalize to target resolution
    4. Apply color grade (from visual.color or default_color)
    5. Burn overlay graphics (lower thirds, etc.)
    6. Mix audio (narration + real audio + music at their volumes)
    7. Mux mixed audio into the video
    """
    result = CompositeResult(segment_id=seg.id)
    output_dir.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r'[^\w-]', '_', seg.id)[:40]
    base = f"comp-{slug}"

    # Step 1: Resolve base visual
    visual = seg.config.visual[0] if seg.config.visual else None
    if not visual or not visual.src:
        result.error = "No visual source assigned"
        return result

    src_path = Path(visual.src)
    if not src_path.is_absolute():
        src_path = project_dir / visual.src
    if not src_path.exists():
        result.error = f"Source file not found: {visual.src}"
        return result

    # Handle images → convert to video
    if src_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
        img_video = output_dir / f"{base}-img.mp4"
        try:
            dur = segment_duration(seg) or 5.0
            image_to_video(src_path, img_video, duration=int(dur))
            current = img_video
            result.layers_applied.append("visual:image_to_video")
        except FFmpegError as e:
            result.error = f"Image conversion failed: {e}"
            return result
    else:
        # Copy source into output dir so we never modify the original
        working_copy = output_dir / f"{base}-src.mp4"
        shutil.copy2(str(src_path), str(working_copy))
        current = working_copy
        result.layers_applied.append("visual")

    # Step 2: Trim to in/out if specified
    if visual.tc_in or visual.out:
        trimmed = output_dir / f"{base}-trim.mp4"
        try:
            start = visual.tc_in or "0"
            trim(current, trimmed, start=start, end=visual.out)
            current = trimmed
            result.layers_applied.append(f"trim:{visual.tc_in}-{visual.out}")
        except FFmpegError:
            result.layers_applied.append("trim:FAILED")

    # Step 3: Normalize
    norm = output_dir / f"{base}-norm.mp4"
    try:
        normalize_format(current, norm, width, height, fps)
        current = norm
        result.layers_applied.append("normalize")
    except FFmpegError:
        result.layers_applied.append("normalize:FAILED")

    # Step 4: Color grade
    grade = visual.color or default_color
    if grade and grade in COLOR_GRADE_PRESETS:
        graded = output_dir / f"{base}-graded.mp4"
        try:
            color_grade(current, graded, preset=grade)
            current = graded
            result.layers_applied.append(f"color:{grade}")
        except FFmpegError:
            pass

    # Step 5: Overlay graphics
    graphics_dir = output_dir.parent / "graphics"
    if graphics_dir.exists():
        for overlay in seg.config.overlay:
            png = _find_overlay_graphic(overlay, graphics_dir, seg.id)
            if png:
                overlaid = output_dir / f"{base}-ov-{png.stem}.mp4"
                try:
                    overlay_png(current, png, overlaid)
                    current = overlaid
                    result.layers_applied.append(f"overlay:{overlay.type}")
                except FFmpegError:
                    pass

    # Step 6: Audio mix
    audio_paths: list[Path] = []
    audio_volumes: list[float] = []

    # Narration audio
    narration_dir = output_dir.parent / "narration"
    nar_file = _find_narration_file(seg, narration_dir)
    if nar_file:
        audio_paths.append(nar_file)
        audio_volumes.append(1.0)

    # Real audio / SFX
    for a in seg.config.audio:
        if a.type in ("REAL_AUDIO", "SFX") and a.src:
            a_path = Path(a.src) if Path(a.src).is_absolute() else project_dir / a.src
            if a_path.exists():
                audio_paths.append(a_path)
                audio_volumes.append(a.volume or 1.0)

    # Music
    for a in seg.config.audio:
        if a.type == "MUSIC" and a.src:
            m_path = Path(a.src) if Path(a.src).is_absolute() else project_dir / a.src
            if m_path.exists():
                audio_paths.append(m_path)
                audio_volumes.append(a.volume or 0.15)

    mixed_audio: Path | None = None
    if len(audio_paths) >= 2:
        mixed_audio = output_dir / f"{base}-mixed.mp3"
        try:
            mix_audio(audio_paths[0], audio_paths[1], mixed_audio, music_volume=audio_volumes[1])
            if len(audio_paths) > 2:
                result.layers_applied.append(f"audio:mix(2/{len(audio_paths)} tracks, {len(audio_paths)-2} dropped)")
            else:
                result.layers_applied.append(f"audio:mix({len(audio_paths)} tracks)")
        except FFmpegError:
            mixed_audio = None
    elif len(audio_paths) == 1:
        mixed_audio = audio_paths[0]
        result.layers_applied.append("audio:single")

    # Step 7: Mux audio into video
    if mixed_audio and mixed_audio.exists():
        muxed = output_dir / f"{base}-muxed.mp4"
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(current),
                "-i", str(mixed_audio),
                "-c:v", "copy", "-c:a", "aac",
                "-map", "0:v:0", "-map", "1:a:0",
                "-shortest",
                str(muxed),
            ]
            subprocess.run(cmd, capture_output=True, check=True, timeout=120)
            current = muxed
            result.layers_applied.append("audio:muxed")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            result.layers_applied.append("audio:mux_FAILED")

    # Write final output
    final = output_dir / f"{base}.mp4"
    if current != final:
        if final.exists():
            final.unlink()
        shutil.move(str(current), str(final))
    result.output_path = final

    # Clean intermediates
    for suffix in ["-src.mp4", "-img.mp4", "-trim.mp4", "-norm.mp4", "-graded.mp4", "-mixed.mp3", "-muxed.mp4"]:
        tmp = output_dir / f"{base}{suffix}"
        if tmp.exists() and tmp != final:
            try:
                tmp.unlink()
            except OSError:
                pass
    # Clean overlay intermediates
    for tmp in output_dir.glob(f"{base}-ov-*.mp4"):
        if tmp != final:
            try:
                tmp.unlink()
            except OSError:
                pass

    return result


def composite_all(
    parsed: ParsedStoryboard,
    project_dir: Path,
    output_dir: Path,
    *,
    default_color: str | None = None,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    on_progress: Callable[[str, str], None] | None = None,
) -> CompositeReport:
    """Composite all segments in a storyboard."""
    report = CompositeReport()
    comp_dir = output_dir / "composited"

    # Use project-level color preset if available
    if not default_color and parsed.project.color_preset:
        default_color = parsed.project.color_preset

    for i, seg in enumerate(parsed.segments):
        if on_progress:
            on_progress("composite", f"[{i+1}/{len(parsed.segments)}] {seg.title}")

        result = composite_segment(
            seg, project_dir, comp_dir,
            default_color=default_color,
            width=width, height=height, fps=fps,
        )
        report.results.append(result)

        if result.output_path:
            report.succeeded += 1
        elif result.error:
            report.failed += 1
            report.errors.append(f"{seg.id}: {result.error}")
        else:
            report.skipped += 1

    return report


# --- Helpers ---

def _find_overlay_graphic(overlay: OverlayEntry, graphics_dir: Path, segment_id: str) -> Path | None:
    """Find a pre-generated graphic PNG for an overlay entry."""
    slug = re.sub(r'[^\w-]', '', (overlay.text or "").lower())[:30]

    for png in graphics_dir.glob("*.png"):
        name = png.stem.lower()
        if overlay.type == "LOWER_THIRD" and "lower-third" in name and slug and slug in name:
            return png
        if overlay.type == "TIMELINE_MARKER" and "timeline" in name:
            return png
        if overlay.type == "QUOTE_CARD" and "quote" in name:
            return png
        if overlay.type == "FINANCIAL_CARD" and "financial" in name:
            return png

    return None


def _find_narration_file(seg: ParsedSegment, narration_dir: Path) -> Path | None:
    """Find the narration audio file for a segment."""
    if not seg.narration or not narration_dir.exists():
        return None

    slug = re.sub(r'[^\w-]', '', seg.id)
    for f in sorted(narration_dir.glob("nar-*")):
        if slug in f.stem.lower() or seg.section.lower().replace(" ", "-") in f.stem.lower():
            return f

    return None
