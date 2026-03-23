"""Compositor service — assembles final dubbed video from TTS segments + source video."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from bee_video_editor.processors.captions import CaptionSegment, generate_captions_estimated, burn_captions
from bee_video_editor.processors.ffmpeg import normalize_loudness


def compose_dubbed_video(
    source_video: Path,
    translations_path: Path,
    tts_dir: Path,
    output_path: Path,
    accompaniment_path: Path | None = None,
    background_volume: float = 0.05,
    subtitles: bool = True,
    subtitle_style: str = "phrase",
    target_lufs: float = -14.0,
) -> Path:
    """Compose the final dubbed video from TTS segments + source video."""
    if output_path.exists() and output_path.stat().st_size > 0:
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    translations = json.loads(translations_path.read_text())
    segments = translations["segments"]

    # Step 1: Build mixed audio track from TTS segments
    mixed_audio = output_path.parent / "mixed_audio.mp3"
    _mix_tts_segments(segments, tts_dir, mixed_audio)

    # Step 2: Optionally mix in background audio
    if accompaniment_path and accompaniment_path.exists():
        bg_mixed = output_path.parent / "bg_mixed.mp3"
        _mix_with_background(mixed_audio, accompaniment_path, bg_mixed, background_volume)
        mixed_audio = bg_mixed

    # Step 3: Normalize loudness
    normalized = output_path.parent / "normalized.mp3"
    normalize_loudness(mixed_audio, normalized, target_lufs)

    # Step 4: Replace audio in source video
    no_subs = output_path.parent / "no_subs.mp4"
    _replace_audio(source_video, normalized, no_subs)

    # Step 5: Generate and burn subtitles
    if subtitles:
        caption_segs = [
            CaptionSegment(
                text=seg["translated_text"],
                start_ms=seg["start_ms"],
                end_ms=seg["end_ms"],
                style_name="Narrator",
            )
            for seg in segments
        ]
        ass_path = output_path.parent / "captions.ass"
        generate_captions_estimated(caption_segs, ass_path, style=subtitle_style)
        burn_captions(no_subs, ass_path, output_path)
    else:
        no_subs.rename(output_path)

    # Cleanup temp files
    for f in [mixed_audio, normalized, no_subs]:
        if f.exists() and f != output_path:
            f.unlink(missing_ok=True)

    return output_path


def _mix_tts_segments(segments: list[dict], tts_dir: Path, output: Path) -> None:
    """Concatenate TTS segments with silence padding at correct timestamps."""
    inputs = []
    filter_parts = []
    for i, seg in enumerate(segments):
        seg_file = tts_dir / f"seg_{seg['id']:03d}.mp3"
        if not seg_file.exists():
            continue
        inputs.extend(["-i", str(seg_file)])
        delay_ms = seg["start_ms"]
        filter_parts.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[a{i}]")

    if not filter_parts:
        return

    mix_inputs = "".join(f"[a{i}]" for i in range(len(filter_parts)))
    filter_parts.append(f"{mix_inputs}amix=inputs={len(filter_parts)}:duration=longest")
    filter_str = ";".join(filter_parts)
    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_str, str(output)]
    subprocess.run(cmd, capture_output=True, text=True)


def _mix_with_background(foreground: Path, background: Path, output: Path, bg_volume: float) -> None:
    """Mix foreground audio with background at given volume."""
    cmd = [
        "ffmpeg", "-y", "-i", str(foreground), "-i", str(background),
        "-filter_complex",
        f"[1:a]volume={bg_volume}[bg];[0:a][bg]amix=inputs=2:duration=first",
        "-ac", "2", str(output),
    ]
    subprocess.run(cmd, capture_output=True, text=True)


def _replace_audio(video: Path, audio: Path, output: Path) -> None:
    """Replace a video's audio track with a new audio file."""
    cmd = [
        "ffmpeg", "-y", "-i", str(video), "-i", str(audio),
        "-c:v", "copy", "-map", "0:v", "-map", "1:a",
        "-shortest", str(output),
    ]
    subprocess.run(cmd, capture_output=True, text=True)
