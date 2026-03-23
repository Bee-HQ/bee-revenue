from __future__ import annotations
import json
import subprocess
from pathlib import Path


def diarize_segments(
    audio_path: Path,
    transcript_path: Path,
    output_path: Path,
    voices_dir: Path,
    engine: str = "pyannote",
    min_speakers: int = 2,
    max_speakers: int = 10,
    min_sample_duration: int = 30,
) -> Path:
    """Assign speakers to transcript segments and extract voice samples."""
    if output_path.exists():
        return output_path
    transcript = json.loads(transcript_path.read_text())
    segments = transcript["segments"]
    if engine == "pyannote":
        speaker_turns = _diarize_pyannote(audio_path, min_speakers, max_speakers)
    else:
        raise ValueError(f"Unknown diarization engine: {engine}")
    for seg in segments:
        seg["speaker"] = _best_speaker(seg, speaker_turns)
    speakers = sorted(set(seg["speaker"] for seg in segments))
    voices_dir.mkdir(parents=True, exist_ok=True)
    _extract_voice_samples(audio_path, segments, speakers, voices_dir, min_sample_duration)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"segments": segments, "speakers": speakers}, indent=2))
    return output_path


def _best_speaker(segment: dict, turns: list[dict]) -> str:
    """Find the speaker with most overlap for a given segment."""
    best = "speaker_unknown"
    best_overlap = 0
    for turn in turns:
        overlap_start = max(segment["start_ms"], turn["start_ms"])
        overlap_end = min(segment["end_ms"], turn["end_ms"])
        overlap = max(0, overlap_end - overlap_start)
        if overlap > best_overlap:
            best_overlap = overlap
            best = turn["speaker"]
    return best


def _diarize_pyannote(audio_path: Path, min_speakers: int, max_speakers: int) -> list[dict]:
    """Run pyannote speaker diarization."""
    from pyannote.audio import Pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    diarization = pipeline(str(audio_path), min_speakers=min_speakers, max_speakers=max_speakers)
    turns = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        turns.append({
            "start_ms": int(turn.start * 1000),
            "end_ms": int(turn.end * 1000),
            "speaker": speaker,
        })
    return turns


def _extract_voice_samples(
    audio_path: Path, segments: list[dict], speakers: list[str],
    voices_dir: Path, min_duration: int,
) -> None:
    """Extract clean audio samples per speaker for voice cloning."""
    for speaker in speakers:
        speaker_segs = [s for s in segments if s["speaker"] == speaker]
        speaker_segs.sort(key=lambda s: s["end_ms"] - s["start_ms"], reverse=True)
        collected, total_ms = [], 0
        for seg in speaker_segs:
            collected.append(seg)
            total_ms += seg["end_ms"] - seg["start_ms"]
            if total_ms >= min_duration * 1000:
                break
        if not collected:
            continue
        sample_path = voices_dir / f"{speaker}.mp3"
        parts = []
        for i, seg in enumerate(collected):
            part = voices_dir / f"_tmp_{speaker}_{i}.mp3"
            start_s = seg["start_ms"] / 1000
            duration_s = (seg["end_ms"] - seg["start_ms"]) / 1000
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", str(audio_path),
                 "-ss", str(start_s), "-t", str(duration_s),
                 "-vn", "-acodec", "mp3", "-b:a", "192k", str(part)],
                capture_output=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")
            if part.exists():
                parts.append(part)
        if len(parts) == 1:
            parts[0].rename(sample_path)
        elif parts:
            list_file = voices_dir / f"_concat_{speaker}.txt"
            list_file.write_text("\n".join(f"file '{p.name}'" for p in parts))
            result = subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                 "-i", str(list_file), "-c", "copy", str(sample_path)],
                capture_output=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")
            list_file.unlink(missing_ok=True)
        for p in parts:
            p.unlink(missing_ok=True)
