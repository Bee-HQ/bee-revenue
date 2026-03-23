from __future__ import annotations
import json
import os
from pathlib import Path

LANG_NAMES = {
    "es": "Spanish", "de": "German", "ar": "Arabic",
    "pt": "Portuguese", "hi": "Hindi", "fr": "French",
}


def translate_segments(
    diarization_path: Path, output_path: Path, lang: str = "es",
    engine: str = "claude", model: str = "claude-sonnet-4-6", style: str | None = None,
) -> Path:
    """Translate diarized segments to target language."""
    if output_path.exists():
        return output_path
    diarization = json.loads(diarization_path.read_text())
    segments = diarization["segments"]
    if engine == "claude":
        translations = _translate_claude(segments, lang, model, style)
    else:
        raise ValueError(f"Unknown translation engine: {engine}")
    trans_map = {t["id"]: t for t in translations}
    for seg in segments:
        t = trans_map.get(seg["id"], {})
        seg["translated_text"] = t.get("text", seg["text"])
        seg["target_duration_ms"] = t.get("target_duration_ms", seg["end_ms"] - seg["start_ms"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"segments": segments, "lang": lang}, indent=2))
    return output_path


def _translate_claude(segments: list[dict], lang: str, model: str, style: str | None) -> list[dict]:
    """Translate segments using Claude API."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    lang_name = LANG_NAMES.get(lang, lang)
    style_instruction = style or (
        f"Translate to {lang_name} as a native speaker telling a funny dating story. "
        "Keep slang natural. Don't be literal — capture the vibe."
    )
    batch_size = 20
    results = []
    for i in range(0, len(segments), batch_size):
        batch = segments[i:i + batch_size]
        segments_text = "\n".join(
            f'[{s["id"]}] ({s["end_ms"] - s["start_ms"]}ms) {s["text"]}' for s in batch
        )
        response = client.messages.create(
            model=model, max_tokens=4096,
            messages=[{"role": "user", "content": (
                f"{style_instruction}\n\n"
                f"Translate each segment below to {lang_name}. "
                "Return JSON array with objects: "
                '{"id": <number>, "text": "<translated>", "target_duration_ms": <original_duration>}\n'
                "Keep the same segment IDs. Match the original duration in target_duration_ms.\n\n"
                f"Segments:\n{segments_text}"
            )}],
        )
        text = response.content[0].text
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            results.extend(json.loads(text[start:end]))
    return results
