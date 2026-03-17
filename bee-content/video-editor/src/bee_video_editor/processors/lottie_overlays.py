"""Lottie animated overlays — create, render, and composite animated graphics."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from lottie import NVector, objects


def _has_cairo() -> bool:
    """Check if Cairo renderer is available."""
    try:
        from lottie.exporters import cairo  # noqa: F401

        return True
    except ImportError:
        return False


def create_lower_third_animation(
    name: str,
    role: str,
    duration: float = 5.0,
    fps: int = 30,
) -> objects.Animation:
    """Create an animated lower-third as a Lottie Animation object.

    Animation timeline:
    - 0-0.5s: Red accent line draws in from left
    - 0.17-0.67s: Name slides in from left with fade
    - 0.5-0.83s: Role fades in
    - 0.83-4.33s: Hold
    - 4.33-5.0s: Everything fades out
    """
    total_frames = int(duration * fps)

    anim = objects.Animation()
    anim.width = 1920
    anim.height = 1080
    anim.frame_rate = fps
    anim.in_point = 0
    anim.out_point = total_frames

    # Timing keyframes
    line_start = 0
    line_end = int(0.5 * fps)
    name_start = int(0.17 * fps)
    name_end = int(0.67 * fps)
    role_start = int(0.5 * fps)
    role_end = int(0.83 * fps)
    fade_start = int((duration - 0.67) * fps)
    fade_end = total_frames

    # Position constants
    bar_x = 40
    bar_y = 950
    bar_w = 600
    bar_h = 80
    line_y = bar_y - 3

    # Layer 1: Semi-transparent background bar
    bar_layer = objects.ShapeLayer()
    bar_rect = objects.Rect()
    bar_rect.position.value = NVector(bar_x + bar_w / 2, bar_y + bar_h / 2)
    bar_rect.size.value = NVector(bar_w, bar_h)
    bar_layer.add_shape(bar_rect)

    bar_fill = objects.Fill()
    bar_fill.color.value = NVector(0, 0, 0)
    bar_fill.opacity.value = 70
    bar_layer.add_shape(bar_fill)

    # Bar opacity: fade in then fade out
    bar_layer.transform.opacity.add_keyframe(0, 0)
    bar_layer.transform.opacity.add_keyframe(line_end, 100)
    bar_layer.transform.opacity.add_keyframe(fade_start, 100)
    bar_layer.transform.opacity.add_keyframe(fade_end, 0)

    anim.add_layer(bar_layer)

    # Layer 2: Red accent line (draws in from left)
    line_layer = objects.ShapeLayer()
    line_rect = objects.Rect()
    line_rect.position.value = NVector(bar_x + bar_w / 2, line_y)
    line_rect.size.value = NVector(bar_w, 3)
    line_layer.add_shape(line_rect)

    line_fill = objects.Fill()
    line_fill.color.value = NVector(200 / 255, 30 / 255, 30 / 255)  # #C81E1E
    line_layer.add_shape(line_fill)

    # Line scale X: 0 -> 100% (draw-in effect)
    line_layer.transform.scale.add_keyframe(line_start, NVector(0, 100))
    line_layer.transform.scale.add_keyframe(line_end, NVector(100, 100))
    # Fade out
    line_layer.transform.opacity.add_keyframe(fade_start, 100)
    line_layer.transform.opacity.add_keyframe(fade_end, 0)

    anim.add_layer(line_layer)

    # Layer 3: Name text (slide in + fade)
    name_layer = objects.ShapeLayer()
    # Use a rectangle as text placeholder (Lottie text support is limited in python-lottie)
    # The actual text will be rendered by the consumer — this creates the animation envelope
    name_placeholder = objects.Rect()
    name_placeholder.position.value = NVector(bar_x + 20 + len(name) * 12, bar_y + 30)
    name_placeholder.size.value = NVector(len(name) * 24, 42)
    name_layer.add_shape(name_placeholder)

    name_fill = objects.Fill()
    name_fill.color.value = NVector(1, 1, 1)  # white
    name_layer.add_shape(name_fill)

    # Slide in from left
    name_layer.transform.position.add_keyframe(name_start, NVector(-200, 0))
    name_layer.transform.position.add_keyframe(name_end, NVector(0, 0))
    # Fade in
    name_layer.transform.opacity.add_keyframe(name_start, 0)
    name_layer.transform.opacity.add_keyframe(name_end, 100)
    # Fade out
    name_layer.transform.opacity.add_keyframe(fade_start, 100)
    name_layer.transform.opacity.add_keyframe(fade_end, 0)

    anim.add_layer(name_layer)

    # Layer 4: Role text (fade in)
    if role:
        role_layer = objects.ShapeLayer()
        role_placeholder = objects.Rect()
        role_placeholder.position.value = NVector(bar_x + 20 + len(role) * 9, bar_y + 60)
        role_placeholder.size.value = NVector(len(role) * 18, 28)
        role_layer.add_shape(role_placeholder)

        role_fill = objects.Fill()
        role_fill.color.value = NVector(180 / 255, 180 / 255, 180 / 255)  # grey
        role_layer.add_shape(role_fill)

        # Fade in
        role_layer.transform.opacity.add_keyframe(role_start, 0)
        role_layer.transform.opacity.add_keyframe(role_end, 100)
        # Fade out
        role_layer.transform.opacity.add_keyframe(fade_start, 100)
        role_layer.transform.opacity.add_keyframe(fade_end, 0)

        anim.add_layer(role_layer)

    return anim


def _render_frames(animation: objects.Animation, frames_dir: Path) -> Path:
    """Render Lottie animation frames to PNG via Cairo."""
    frames_dir.mkdir(parents=True, exist_ok=True)

    from lottie.exporters.cairo import export_png

    total_frames = int(animation.out_point - animation.in_point)
    for i in range(total_frames):
        frame_path = frames_dir / f"frame_{i:04d}.png"
        export_png(animation, str(frame_path), i)

    return frames_dir


def render_lottie_overlay(
    animation: objects.Animation,
    output_path: Path,
    width: int = 1920,
    height: int = 1080,
) -> Path:
    """Render Lottie animation to WebM with alpha channel."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        frames_dir = Path(tmp) / "frames"
        _render_frames(animation, frames_dir)

        cmd = [
            "ffmpeg",
            "-y",
            "-framerate",
            str(int(animation.frame_rate)),
            "-i",
            str(frames_dir / "frame_%04d.png"),
            "-c:v",
            "libvpx-vp9",
            "-pix_fmt",
            "yuva420p",
            "-auto-alt-ref",
            "0",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg WebM render failed: {result.stderr[:500]}")

    return output_path


def overlay_lottie(
    video_path: Path,
    overlay_path: Path,
    output_path: Path,
    start_time: float = 0.0,
) -> Path:
    """Composite a WebM overlay (with alpha) onto video at specified time."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get overlay duration from the file
    probe_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(overlay_path),
    ]
    try:
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        overlay_duration = float(probe_result.stdout.strip())
    except (ValueError, subprocess.SubprocessError):
        overlay_duration = 5.0  # fallback

    end_time = start_time + overlay_duration

    filter_complex = (
        f"[1:v]setpts=PTS+{start_time}/TB[ovr];"
        f"[0:v][ovr]overlay=enable='between(t,{start_time},{end_time})'"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(overlay_path),
        "-filter_complex",
        filter_complex,
        "-c:a",
        "copy",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg overlay failed: {result.stderr[:500]}")

    return output_path


def generate_animated_lower_third(
    name: str,
    role: str,
    output_path: Path,
    duration: float = 5.0,
) -> Path:
    """High-level: create + render an animated lower-third to WebM."""
    anim = create_lower_third_animation(name, role, duration=duration)
    return render_lottie_overlay(anim, output_path)
