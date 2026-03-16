"""FFmpeg wrapper for video/audio operations."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


class FFmpegError(Exception):
    pass


def run_ffmpeg(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run an ffmpeg command and return the result."""
    cmd = ["ffmpeg", "-y"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise FFmpegError(f"ffmpeg failed: {result.stderr[:500]}")
    return result


def probe(input_path: str | Path) -> dict:
    """Get media file info via ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(input_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise FFmpegError(f"ffprobe failed: {result.stderr[:500]}")
    return json.loads(result.stdout)


def get_duration(input_path: str | Path) -> float:
    """Get duration of a media file in seconds."""
    info = probe(input_path)
    return float(info.get("format", {}).get("duration", 0))


def trim(
    input_path: str | Path,
    output_path: str | Path,
    start: str,
    duration: str | None = None,
    end: str | None = None,
    reencode: bool = True,
) -> Path:
    """Trim a segment from a media file.

    Args:
        input_path: Source file.
        output_path: Destination file.
        start: Start timestamp (e.g. "0:30", "1:15").
        duration: Duration (e.g. "15" for 15s). Mutually exclusive with end.
        end: End timestamp. Mutually exclusive with duration.
        reencode: If True, re-encode (needed for variable framerate sources).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    args = ["-ss", start]
    if duration:
        args += ["-t", duration]
    elif end:
        args += ["-to", end]

    args += ["-i", str(input_path)]

    if reencode:
        args += ["-c:v", "libx264", "-preset", "fast", "-crf", "23",
                 "-c:a", "aac", "-b:a", "128k"]
    else:
        args += ["-c", "copy"]

    args.append(str(output_path))
    run_ffmpeg(args)
    return output_path


def normalize_format(
    input_path: str | Path,
    output_path: str | Path,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
) -> Path:
    """Normalize a clip to standard format (resolution, fps, codec)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:-1:-1:color=black,"
        f"fps={fps}"
    )
    args = [
        "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def image_to_video(
    image_path: str | Path,
    output_path: str | Path,
    duration: float = 5.0,
    fps: int = 30,
    ken_burns: str | None = "zoom_in",
) -> Path:
    """Convert a static image to a video clip with optional Ken Burns effect.

    Args:
        ken_burns: "zoom_in", "zoom_out", "pan_left", or None for static.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_frames = int(duration * fps)

    if ken_burns == "zoom_in":
        vf = f"zoompan=z='min(zoom+0.0015,1.3)':d={total_frames}:s=1920x1080:fps={fps}"
    elif ken_burns == "zoom_out":
        vf = f"zoompan=z='if(eq(on,1),1.3,max(zoom-0.0015,1.0))':d={total_frames}:s=1920x1080:fps={fps}"
    elif ken_burns == "pan_left":
        vf = f"zoompan=z='1.2':x='if(eq(on,1),0,min(x+1,iw-iw/zoom))':d={total_frames}:s=1920x1080:fps={fps}"
    else:
        vf = f"scale=1920:1080,fps={fps}"

    args = [
        "-loop", "1", "-i", str(image_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-t", str(duration),
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def overlay_png(
    video_path: str | Path,
    overlay_path: str | Path,
    output_path: str | Path,
    fade_in_at: float | None = 2.0,
    fade_duration: float = 0.5,
) -> Path:
    """Overlay a transparent PNG on a video clip."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fade_in_at is not None:
        fc = (
            f"[1:v]fade=in:st={fade_in_at}:d={fade_duration}:alpha=1[ovr];"
            f"[0:v][ovr]overlay=0:0"
        )
    else:
        fc = "[0:v][1:v]overlay=0:0"

    args = [
        "-i", str(video_path),
        "-i", str(overlay_path),
        "-filter_complex", fc,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "copy",
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def color_grade(
    input_path: str | Path,
    output_path: str | Path,
    preset: str = "dark_crime",
) -> Path:
    """Apply color grading to a clip.

    Presets:
        dark_crime: desaturated, cool blue shadows, higher contrast
        warm_victim: warm golden tones, gentle
        bodycam: slightly desaturated, cool tones
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    presets = {
        "dark_crime": "eq=brightness=-0.08:saturation=0.6:contrast=1.2,colorbalance=bs=0.1:bm=0.05",
        "warm_victim": "eq=brightness=0.03:saturation=1.1:contrast=1.0,colorbalance=rs=0.08:rm=0.05",
        "bodycam": "eq=brightness=-0.04:saturation=0.7:contrast=1.1,colorbalance=bs=0.05",
    }

    vf = presets.get(preset, presets["dark_crime"])

    args = [
        "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "copy",
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def add_fade(
    input_path: str | Path,
    output_path: str | Path,
    fade_in_duration: float = 1.0,
    fade_out_duration: float = 1.0,
) -> Path:
    """Add fade in/out to a clip."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dur = get_duration(input_path)
    fade_out_start_frame = int((dur - fade_out_duration) * 30)
    fade_in_frames = int(fade_in_duration * 30)
    fade_out_frames = int(fade_out_duration * 30)

    vf = f"fade=in:0:{fade_in_frames},fade=out:{fade_out_start_frame}:{fade_out_frames}"
    af = f"afade=in:st=0:d={fade_in_duration},afade=out:st={dur - fade_out_duration}:d={fade_out_duration}"

    args = [
        "-i", str(input_path),
        "-vf", vf, "-af", af,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def waveform_video(
    audio_path: str | Path,
    output_path: str | Path,
    duration: float = 15.0,
    color: str = "0x00ff88",
    width: int = 1920,
    height: int = 1080,
) -> Path:
    """Generate a waveform visualization video from audio."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    wave_height = 200
    y_pos = (height - wave_height) // 2

    fc = (
        f"[0:a]showwaves=s={width}x{wave_height}:mode=cline:rate=30:colors={color}[waves];"
        f"color=black:s={width}x{height}:r=30:d={duration}[bg];"
        f"[bg][waves]overlay=0:{y_pos}[out]"
    )

    args = [
        "-ss", "0", "-t", str(duration),
        "-i", str(audio_path),
        "-filter_complex", fc,
        "-map", "[out]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(duration),
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def mix_audio(
    narration_path: str | Path,
    music_path: str | Path,
    output_path: str | Path,
    music_volume: float = 0.15,
) -> Path:
    """Mix narration with background music."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fc = f"[1:a]volume={music_volume}[bg];[0:a][bg]amix=inputs=2:duration=first"

    args = [
        "-i", str(narration_path),
        "-i", str(music_path),
        "-filter_complex", fc,
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def normalize_loudness(
    input_path: str | Path,
    output_path: str | Path,
    target_lufs: float = -14.0,
) -> Path:
    """Normalize audio loudness to target LUFS (YouTube standard: -14)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    af = f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11"

    args = [
        "-i", str(input_path),
        "-af", af,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def concat_segments(
    segment_paths: list[str | Path],
    output_path: str | Path,
    reencode: bool = False,
) -> Path:
    """Concatenate multiple segments into a single video."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write concat list
    concat_file = output_path.parent / f"{output_path.stem}_concat.txt"
    with open(concat_file, "w") as f:
        for p in segment_paths:
            f.write(f"file '{Path(p).resolve()}'\n")

    if reencode:
        # Build filter_complex for concat
        n = len(segment_paths)
        inputs = []
        for i, p in enumerate(segment_paths):
            inputs += ["-i", str(p)]
        streams = "".join(f"[{i}:v][{i}:a]" for i in range(n))
        fc = f"{streams}concat=n={n}:v=1:a=1[v][a]"

        args = inputs + [
            "-filter_complex", fc,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            str(output_path),
        ]
    else:
        args = [
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path),
        ]

    run_ffmpeg(args)
    concat_file.unlink(missing_ok=True)
    return output_path
