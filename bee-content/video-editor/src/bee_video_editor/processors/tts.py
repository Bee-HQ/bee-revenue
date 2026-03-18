"""TTS narration generation — supports multiple engines."""

from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_narration(
    text: str,
    output_path: str | Path,
    engine: str = "edge",
    voice: str | None = None,
    speed: float = 0.95,
) -> Path:
    """Generate narration audio from text.

    Args:
        text: The narrator text to synthesize.
        output_path: Where to save the audio file.
        engine: "edge" (free), "kokoro" (free/local), "openai" (paid).
        voice: Engine-specific voice ID. Defaults per engine.
        speed: Speech speed multiplier (lower = slower/more gravitas).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    engines = {
        "edge": _generate_edge,
        "kokoro": _generate_kokoro,
        "openai": _generate_openai,
    }

    if engine not in engines:
        raise ValueError(f"Unknown TTS engine: {engine}. Available: {list(engines.keys())}")

    logger.debug("Generating narration: engine=%s output=%s", engine, output_path.name)
    try:
        return engines[engine](text, output_path, voice=voice, speed=speed)
    except Exception:
        logger.exception("TTS failed for %s (engine=%s)", output_path.name, engine)
        raise


def _generate_edge(
    text: str,
    output_path: Path,
    voice: str | None = None,
    speed: float = 0.95,
) -> Path:
    """Generate audio using Edge TTS (free, cloud-based)."""
    import asyncio
    import edge_tts

    voice = voice or "en-US-GuyNeural"
    rate_pct = int((speed - 1.0) * 100)
    rate_str = f"{rate_pct:+d}%"

    async def _gen():
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate_str,
            pitch="-5Hz",
        )
        await communicate.save(str(output_path))

    asyncio.run(_gen())
    return output_path


def _generate_kokoro(
    text: str,
    output_path: Path,
    voice: str | None = None,
    speed: float = 0.95,
) -> Path:
    """Generate audio using Kokoro TTS (free, local)."""
    from kokoro import KPipeline
    import numpy as np
    import soundfile as sf

    voice = voice or "am_adam"
    pipeline = KPipeline(lang_code="a")
    all_audio = []

    for _i, (_gs, _ps, audio) in enumerate(pipeline(text, voice=voice, speed=speed)):
        all_audio.append(audio)

    combined = np.concatenate(all_audio)
    sf.write(str(output_path), combined, 24000)
    return output_path


def _generate_openai(
    text: str,
    output_path: Path,
    voice: str | None = None,
    speed: float = 0.95,
) -> Path:
    """Generate audio using OpenAI TTS (paid API)."""
    import openai

    voice = voice or "onyx"
    client = openai.OpenAI()

    # Chunk text if needed (2000 token limit ~1500 words)
    words = text.split()
    chunks = []
    chunk_size = 1200
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))

    all_audio = b""
    for chunk in chunks:
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=chunk,
            instructions=(
                "Narrate in a measured, serious true-crime documentary tone. "
                "Pace is deliberate and weighty. Pause slightly before key "
                "revelations. No excitement — gravitas and controlled intensity."
            ),
            response_format="wav",
        )
        all_audio += response.content

    output_path.write_bytes(all_audio)
    return output_path


def extract_narrator_sections(screenplay_path: str | Path) -> list[dict]:
    """Extract narrator lines from a screenplay markdown file.

    Returns list of {"section": str, "index": int, "text": str}.
    """
    text = Path(screenplay_path).read_text(encoding="utf-8")
    lines = text.split("\n")

    sections = []
    current_section = "INTRO"
    current_paragraphs = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("## ") or stripped.startswith("### "):
            if current_paragraphs:
                combined = " ".join(current_paragraphs).strip()
                if combined:
                    sections.append({
                        "section": current_section,
                        "index": len(sections),
                        "text": combined,
                    })
                current_paragraphs = []
            current_section = stripped.lstrip("#").strip()
            current_section = re.sub(r"\s*\([\d:]+\s*-\s*[\d:]+\)", "", current_section)
            continue

        if re.match(r"^\[.*\]\s*$", stripped):
            continue
        if stripped.startswith(">>"):
            continue
        if stripped.startswith("**") and ":" in stripped.split("**")[1] if len(stripped.split("**")) > 1 else False:
            continue
        if stripped == "---":
            continue

        narrator_match = re.match(r"^(?:\[.*?\]\s*)*\*\*NARRATOR:\*\*\s*(.*)", stripped)
        if narrator_match:
            narrator_text = narrator_match.group(1).strip()
            if narrator_text:
                current_paragraphs.append(narrator_text)
            continue

        if stripped.startswith("["):
            continue

    if current_paragraphs:
        combined = " ".join(current_paragraphs).strip()
        if combined:
            sections.append({
                "section": current_section,
                "index": len(sections),
                "text": combined,
            })

    return sections
