from __future__ import annotations
import json
import os
from pathlib import Path


def transcribe_audio(
    audio_path: Path,
    output_path: Path,
    engine: str = "whisper",
    model: str = "large-v3",
) -> Path:
    """Transcribe audio to timestamped segments."""
    if output_path.exists():
        return output_path
    if engine == "whisper":
        segments = _whisper_api(audio_path, model)
    else:
        raise ValueError(f"Unknown transcription engine: {engine}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"segments": segments}, indent=2))
    return output_path


def _whisper_api(audio_path: Path, model: str) -> list[dict]:
    """Transcribe using OpenAI Whisper API."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )
    return [
        {
            "id": i,
            "start_ms": int(seg.start * 1000),
            "end_ms": int(seg.end * 1000),
            "text": seg.text.strip(),
        }
        for i, seg in enumerate(response.segments)
    ]
