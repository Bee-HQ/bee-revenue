from __future__ import annotations
import json
import os
from pathlib import Path


def setup_voices(
    voices_dir: Path,
    manifest_path: Path,
    speakers: list[str],
    mode: str = "clone",
    overrides: dict[str, str] | None = None,
) -> Path:
    """Set up voice mappings — clone from samples or map to existing voices."""
    if manifest_path.exists():
        return manifest_path
    overrides = overrides or {}
    manifest = {}
    for speaker in speakers:
        if speaker in overrides:
            manifest[speaker] = overrides[speaker]
        elif mode == "clone":
            sample = voices_dir / f"{speaker}.mp3"
            if sample.exists():
                manifest[speaker] = _clone_voice(sample, speaker)
            else:
                manifest[speaker] = _default_voice(speaker)
        elif mode == "mapped":
            manifest[speaker] = _default_voice(speaker)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest_path


def _clone_voice(sample_path: Path, name: str) -> str:
    """Clone a voice using ElevenLabs."""
    from elevenlabs import ElevenLabs

    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set")
    client = ElevenLabs(api_key=api_key)
    voice = client.clone(name=f"dub_{name}", files=[str(sample_path)])
    return voice.voice_id


def _default_voice(speaker: str) -> str:
    """Return a default ElevenLabs voice ID based on speaker index."""
    defaults = ["Daniel", "Charlotte", "Brian", "Lily", "George"]
    idx = int(speaker.split("_")[-1]) if "_" in speaker else 0
    return defaults[idx % len(defaults)]
