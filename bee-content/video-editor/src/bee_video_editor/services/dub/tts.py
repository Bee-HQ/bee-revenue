from __future__ import annotations
import json
import os
from pathlib import Path
from bee_video_editor.services.dub.models import SegmentState
from bee_video_editor.services.dub.status import StatusTracker


def generate_dubbed_audio(
    translations_path: Path,
    manifest_path: Path,
    tts_dir: Path,
    status: StatusTracker,
    model: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
) -> Path:
    """Generate TTS audio for each translated segment."""
    from elevenlabs import ElevenLabs
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set")
    client = ElevenLabs(api_key=api_key)
    translations = json.loads(translations_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    tts_dir.mkdir(parents=True, exist_ok=True)
    for seg in translations["segments"]:
        seg_id = f"seg_{seg['id']:03d}"
        output_path = tts_dir / f"{seg_id}.mp3"
        if status.get(seg_id, "tts") == SegmentState.COMPLETED and output_path.exists():
            continue
        try:
            _generate_segment(
                text=seg["translated_text"],
                voice_id=manifest.get(seg["speaker"], "Daniel"),
                output_path=output_path,
                target_duration_ms=seg["target_duration_ms"],
                model=model,
                stability=stability,
                similarity_boost=similarity_boost,
                client=client,
            )
            status.set(seg_id, "tts", SegmentState.COMPLETED)
        except Exception as e:
            status.set(seg_id, "tts", SegmentState.FAILED, error=str(e))
    return tts_dir


def _generate_segment(
    text: str,
    voice_id: str,
    output_path: Path,
    target_duration_ms: int,
    model: str,
    stability: float,
    similarity_boost: float,
    client=None,
) -> None:
    """Generate TTS for a single segment using ElevenLabs."""
    from elevenlabs import ElevenLabs, VoiceSettings
    if client is None:
        api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not set")
        client = ElevenLabs(api_key=api_key)
    audio_generator = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model,
        output_format="mp3_44100_128",
        voice_settings=VoiceSettings(stability=stability, similarity_boost=similarity_boost),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)
    _adjust_duration(output_path, target_duration_ms)


def _adjust_duration(audio_path: Path, target_ms: int, tolerance_ms: int = 500) -> None:
    """Speed up/slow down audio to match target duration."""
    import subprocess
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", str(audio_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return
    actual_ms = int(float(result.stdout.strip()) * 1000)
    drift = abs(actual_ms - target_ms)
    if drift <= tolerance_ms:
        return
    ratio = actual_ms / target_ms
    ratio = max(0.5, min(2.0, ratio))
    adjusted = audio_path.with_suffix(".adj.mp3")
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(audio_path),
            "-filter:a", f"atempo={ratio}", str(adjusted),
        ],
        capture_output=True,
    )
    if adjusted.exists():
        adjusted.replace(audio_path)
