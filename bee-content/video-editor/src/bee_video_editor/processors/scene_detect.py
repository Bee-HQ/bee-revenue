"""Scene detection processor — detect shot boundaries in video files.

Uses FFmpeg's scene detection filter (no external dependency required).
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Scene:
    index: int
    start_time: float
    end_time: float
    duration: float
    thumbnail_path: Path | None = None

    @property
    def start_timecode(self) -> str:
        m, s = divmod(int(self.start_time), 60)
        return f"{m}:{s:02d}"

    @property
    def end_timecode(self) -> str:
        m, s = divmod(int(self.end_time), 60)
        return f"{m}:{s:02d}"


def detect_scenes(
    video_path: str | Path,
    threshold: float = 0.3,
    min_scene_duration: float = 2.0,
) -> list[Scene]:
    """Detect scene changes in a video using FFmpeg's select filter."""
    if not (0.0 <= threshold <= 1.0):
        raise ValueError(f"threshold must be between 0.0 and 1.0, got {threshold}")
    video_path = Path(video_path)
    if not video_path.exists():
        return []

    duration = _get_duration(video_path)
    if duration <= 0:
        return []

    timestamps = _detect_with_ffmpeg(video_path, threshold)
    return _timestamps_to_scenes(timestamps, duration, min_scene_duration)


def extract_scene_thumbnails(
    video_path: str | Path,
    scenes: list[Scene],
    output_dir: Path,
) -> list[Path]:
    """Extract a representative frame from each scene."""
    video_path = Path(video_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    thumbnails = []

    for scene in scenes:
        capture_time = scene.start_time + min(1.0, scene.duration / 2)
        out_path = output_dir / f"scene-{scene.index:03d}-{scene.start_timecode.replace(':', '_')}.jpg"
        try:
            cmd = [
                "ffmpeg", "-y", "-ss", str(capture_time),
                "-i", str(video_path), "-vframes", "1", "-q:v", "2", str(out_path),
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            scene.thumbnail_path = out_path
            thumbnails.append(out_path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return thumbnails


def _get_duration(video_path: Path) -> float:
    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data.get("format", {}).get("duration", 0))
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError, ValueError):
        return 0.0


def _detect_with_ffmpeg(video_path: Path, threshold: float) -> list[float]:
    try:
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-vf", f"select='gt(scene,{threshold})',showinfo",
            "-vsync", "vfr", "-f", "null", "-",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        timestamps = []
        for line in result.stderr.split("\n"):
            match = re.search(r'pts_time:([\d.]+)', line)
            if match:
                timestamps.append(float(match.group(1)))
        return sorted(set(timestamps))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _timestamps_to_scenes(timestamps: list[float], total_duration: float, min_duration: float) -> list[Scene]:
    boundaries = sorted(set([0.0] + timestamps + [total_duration]))
    scenes = []
    for i in range(len(boundaries) - 1):
        start, end = boundaries[i], boundaries[i + 1]
        duration = end - start
        if duration < min_duration:
            continue
        scenes.append(Scene(index=len(scenes), start_time=start, end_time=end, duration=duration))
    return scenes
