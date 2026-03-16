"""FFmpeg wrapper for video/audio operations."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


class FFmpegError(Exception):
    pass


# --- Transition presets (xfade) ---

XFADE_TRANSITIONS = [
    "fade", "wipeleft", "wiperight", "wipeup", "wipedown",
    "slideleft", "slideright", "slideup", "slidedown",
    "smoothleft", "smoothright", "smoothup", "smoothdown",
    "circlecrop", "rectcrop", "distance", "fadeblack", "fadewhite",
    "radial", "smoothdown", "diagtl", "diagtr", "diagbl", "diagbr",
    "hlslice", "hrslice", "vuslice", "vdslice",
    "dissolve", "pixelize", "hblur", "zoomin",
]


# --- Color grade presets ---

COLOR_GRADE_PRESETS = {
    # Original presets
    "dark_crime": "eq=brightness=-0.08:saturation=0.6:contrast=1.2,colorbalance=bs=0.1:bm=0.05",
    "warm_victim": "eq=brightness=0.03:saturation=1.1:contrast=1.0,colorbalance=rs=0.08:rm=0.05",
    "bodycam": "eq=brightness=-0.04:saturation=0.7:contrast=1.1,colorbalance=bs=0.05",
    # New presets
    "noir": "eq=brightness=-0.05:saturation=0.0:contrast=1.4,curves=m='0/0 0.25/0.15 0.5/0.5 0.75/0.85 1/1'",
    "sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
    "cold_blue": "eq=brightness=-0.03:saturation=0.8:contrast=1.15,colorbalance=bs=0.15:bm=0.1:bh=0.05",
    "vintage": "eq=brightness=0.05:saturation=0.85:contrast=0.95,colorbalance=rs=0.1:gs=-0.05:bs=-0.1",
    "bleach_bypass": "eq=brightness=-0.02:saturation=0.5:contrast=1.5,colorbalance=bs=0.05",
    "night_vision": "eq=brightness=0.1:saturation=0.0:contrast=1.3,colorbalance=gs=0.3:gm=0.2",
    "golden_hour": "eq=brightness=0.06:saturation=1.2:contrast=1.05,colorbalance=rs=0.12:rm=0.08:gs=0.03",
    "surveillance": "eq=brightness=-0.06:saturation=0.5:contrast=1.1,colorbalance=bs=0.08,noise=alls=15:allf=t",
    "vhs": "eq=brightness=0.04:saturation=1.3:contrast=0.9,colorbalance=rs=0.05:bs=-0.05",
}


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
        ken_burns: "zoom_in", "zoom_out", "pan_left", "pan_right",
                   "pan_up", "pan_down", "zoom_in_pan_right",
                   or None for static.
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
    elif ken_burns == "pan_right":
        vf = f"zoompan=z='1.2':x='if(eq(on,1),iw-iw/zoom,max(x-1,0))':d={total_frames}:s=1920x1080:fps={fps}"
    elif ken_burns == "pan_up":
        vf = f"zoompan=z='1.2':y='if(eq(on,1),ih-ih/zoom,max(y-1,0))':d={total_frames}:s=1920x1080:fps={fps}"
    elif ken_burns == "pan_down":
        vf = f"zoompan=z='1.2':y='if(eq(on,1),0,min(y+1,ih-ih/zoom))':d={total_frames}:s=1920x1080:fps={fps}"
    elif ken_burns == "zoom_in_pan_right":
        vf = (
            f"zoompan=z='min(zoom+0.0015,1.3)'"
            f":x='if(eq(on,1),iw/2-iw/zoom/2,max(x-0.5,0))'"
            f":d={total_frames}:s=1920x1080:fps={fps}"
        )
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

    Presets: dark_crime, warm_victim, bodycam, noir, sepia, cold_blue,
    vintage, bleach_bypass, night_vision, golden_hour, surveillance, vhs.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    vf = COLOR_GRADE_PRESETS.get(preset, COLOR_GRADE_PRESETS["dark_crime"])

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


def xfade(
    clip_a: str | Path,
    clip_b: str | Path,
    output_path: str | Path,
    transition: str = "fade",
    duration: float = 1.0,
) -> Path:
    """Apply an xfade transition between two clips.

    Args:
        clip_a: First clip.
        clip_b: Second clip.
        transition: xfade transition name (fade, wipeleft, dissolve, etc.).
        duration: Transition duration in seconds.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if transition not in XFADE_TRANSITIONS:
        transition = "fade"

    dur_a = get_duration(clip_a)
    offset = max(0, dur_a - duration)

    fc = (
        f"[0:v][1:v]xfade=transition={transition}:duration={duration}:offset={offset}[v];"
        f"[0:a][1:a]acrossfade=d={duration}[a]"
    )

    args = [
        "-i", str(clip_a),
        "-i", str(clip_b),
        "-filter_complex", fc,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def drawtext(
    input_path: str | Path,
    output_path: str | Path,
    text: str,
    x: str = "(w-text_w)/2",
    y: str = "h-th-50",
    fontsize: int = 48,
    fontcolor: str = "white",
    start: float | None = None,
    end: float | None = None,
    box: bool = False,
    boxcolor: str = "black@0.6",
    boxborderw: int = 10,
) -> Path:
    """Burn text onto a video clip using the drawtext filter.

    Args:
        text: Text to render. Supports newlines with '\\n'.
        x/y: Position expressions (FFmpeg drawtext syntax).
        fontsize: Font size in pixels.
        fontcolor: Font color (name or hex).
        start/end: Optional time window to show text (seconds).
        box: Draw a background box behind text.
        boxcolor: Box color with optional alpha (e.g. "black@0.6").
        boxborderw: Box padding in pixels.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Escape special chars for drawtext
    escaped = text.replace("'", "'\\\\\\''").replace(":", "\\:")

    parts = [
        f"drawtext=text='{escaped}'",
        f"x={x}:y={y}",
        f"fontsize={fontsize}:fontcolor={fontcolor}",
    ]

    if box:
        parts.append(f"box=1:boxcolor={boxcolor}:boxborderw={boxborderw}")

    if start is not None:
        enable = f"between(t\\,{start}\\,{end or 9999})"
        parts.append(f"enable='{enable}'")

    vf = ":".join(parts)

    args = [
        "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "copy",
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def speed(
    input_path: str | Path,
    output_path: str | Path,
    factor: float = 2.0,
) -> Path:
    """Change playback speed of a clip.

    Args:
        factor: Speed multiplier. >1 = faster, <1 = slower (e.g. 0.5 = half speed).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pts = 1.0 / factor
    vf = f"setpts={pts}*PTS"
    af = f"atempo={factor}" if 0.5 <= factor <= 2.0 else f"atempo={factor}"

    # atempo only supports 0.5-2.0 range, chain for extreme values
    if factor > 2.0:
        af_parts = []
        remaining = factor
        while remaining > 2.0:
            af_parts.append("atempo=2.0")
            remaining /= 2.0
        af_parts.append(f"atempo={remaining}")
        af = ",".join(af_parts)
    elif factor < 0.5:
        af_parts = []
        remaining = factor
        while remaining < 0.5:
            af_parts.append("atempo=0.5")
            remaining /= 0.5
        af_parts.append(f"atempo={remaining}")
        af = ",".join(af_parts)

    args = [
        "-i", str(input_path),
        "-vf", vf, "-af", af,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def picture_in_picture(
    main_video: str | Path,
    pip_video: str | Path,
    output_path: str | Path,
    pip_width: int = 480,
    pip_x: str = "W-w-20",
    pip_y: str = "20",
) -> Path:
    """Overlay a picture-in-picture video on the main video.

    Args:
        pip_width: Width of PiP window (height scales proportionally).
        pip_x/pip_y: Position expressions for PiP placement.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fc = (
        f"[1:v]scale={pip_width}:-1[pip];"
        f"[0:v][pip]overlay={pip_x}:{pip_y}"
    )

    args = [
        "-i", str(main_video),
        "-i", str(pip_video),
        "-filter_complex", fc,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "copy",
        "-shortest",
        str(output_path),
    ]
    run_ffmpeg(args)
    return output_path


def concat_with_transitions(
    segment_paths: list[str | Path],
    output_path: str | Path,
    transition: str = "fade",
    transition_duration: float = 1.0,
) -> Path:
    """Concatenate segments with xfade transitions between each pair.

    Chains xfade filters so each adjacent pair gets a smooth transition.
    Falls back to simple concat for single segments.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if len(segment_paths) < 2:
        return concat_segments(segment_paths, output_path, reencode=True)

    if transition not in XFADE_TRANSITIONS:
        transition = "fade"

    n = len(segment_paths)
    inputs = []
    for p in segment_paths:
        inputs += ["-i", str(p)]

    # Get durations for offset calculation
    durations = [get_duration(p) for p in segment_paths]

    # Build xfade chain: [0:v][1:v]xfade...[v01]; [v01][2:v]xfade...[v02]; ...
    vf_parts = []
    af_parts = []
    offset = durations[0] - transition_duration

    # First transition
    vf_parts.append(
        f"[0:v][1:v]xfade=transition={transition}:duration={transition_duration}:offset={offset}[v01]"
    )
    af_parts.append(
        f"[0:a][1:a]acrossfade=d={transition_duration}[a01]"
    )

    for i in range(2, n):
        prev_v = f"v{i-2:02d}{i-1:02d}" if i == 2 else f"v{i-2:02d}{i-1:02d}"
        # The running clip is shorter by transition_duration for each prior xfade
        offset += durations[i-1] - transition_duration
        if i < 10:
            prev_v = f"v{(i-2):02d}{(i-1):02d}"
        cur_v = f"v{(i-1):02d}{i:02d}"
        prev_a = f"a{(i-2):02d}{(i-1):02d}"
        cur_a = f"a{(i-1):02d}{i:02d}"

        vf_parts.append(
            f"[{prev_v}][{i}:v]xfade=transition={transition}:duration={transition_duration}:offset={offset}[{cur_v}]"
        )
        af_parts.append(
            f"[{prev_a}][{i}:a]acrossfade=d={transition_duration}[{cur_a}]"
        )

    # Final output labels
    final_v = f"v{(n-2):02d}{(n-1):02d}" if n > 2 else "v0001"
    final_a = f"a{(n-2):02d}{(n-1):02d}" if n > 2 else "a0001"

    fc = ";".join(vf_parts + af_parts)

    args = inputs + [
        "-filter_complex", fc,
        "-map", f"[{final_v}]", "-map", f"[{final_a}]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
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
