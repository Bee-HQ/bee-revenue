# TTS Narration Guide for True Crime YouTube Videos

Generate AI narrator voiceover from screenplays. Covers five TTS options from free/open-source to paid APIs, with working Python code for each.

**Use case:** Generate ~50 minutes of narration audio from the Alex Murdaugh screenplay (~45K characters of narrator text).

---

## Quick Comparison

| Engine | Cost | Quality (1-10) | Speed (50 min narration) | API Key? | Offline? |
|--------|------|----------------|--------------------------|----------|----------|
| **Kokoro TTS** | Free | 8 | ~5-10 min (GPU), ~30 min (CPU) | No | Yes |
| **Edge TTS** | Free | 7 | ~3-5 min | No (but needs internet) | No |
| **Piper TTS** | Free | 6 | ~2-3 min | No | Yes |
| **OpenAI TTS** | ~$0.50-$0.70 | 9 | ~5-8 min (API throttled) | Yes | No |
| **ElevenLabs** | $5-$22/mo | 9.5 | ~5-10 min (API throttled) | Yes | No |

**Recommendation:** Start with Kokoro TTS. It is free, runs locally, and produces narration quality close to paid APIs. Use Edge TTS as a zero-setup fallback. Move to OpenAI or ElevenLabs only if you need premium quality for published videos.

---

## 1. Kokoro TTS (Apache-2.0) — Recommended

An 82M-parameter open-weight TTS model that punches well above its weight. Produces natural, expressive speech with proper pacing and intonation.

### Install

```bash
pip install kokoro>=0.9.4 soundfile
# Linux only — required for phonemization:
sudo apt-get install espeak-ng
# macOS: brew install espeak-ng
```

The first run downloads the model (~330MB) from Hugging Face automatically.

### Available Voices

Voices follow the pattern `{lang}_{gender}_{name}`:

**American English male (best for true crime narration):**
- `am_adam` — Polished, authoritative, calm (116 Hz). Best for documentary narration.
- `am_michael` — Clear and professional.
- `am_eric` — Warm, slightly deeper.
- `am_fenrir` — Darker, dramatic tone. Good for cold opens.
- `am_onyx` — Rich, deep voice.
- `am_liam` — Conversational, younger.
- `am_puck` — Energetic, faster pace.
- `am_echo` — Smooth, neutral.

**British English male (alternative narration style):**
- `bm_daniel` — Composed, BBC-documentary style.
- `bm_george` — Authoritative British male.
- `bm_fable` — Storytelling tone.
- `bm_lewis` — Warm British male.

**American English female:**
- `af_heart` (default), `af_bella`, `af_sarah`, `af_jessica`, `af_nicole`, `af_nova`, `af_sky`, `af_river`, `af_alloy`, `af_aoede`, `af_kore`

**True crime recommendation:** `am_adam` for main narration, `am_fenrir` for cold opens/dramatic sections.

### Python Code Example

```python
"""Generate narration audio using Kokoro TTS."""

from kokoro import KPipeline
import soundfile as sf
import time

pipeline = KPipeline(lang_code='a')  # 'a' = American English

text = """
This is Alex Murdaugh. A fourth-generation attorney from one of the most
powerful legal dynasties in the American South. Right now, he's standing
over the bodies of his wife and son at the family's 1,770-acre hunting estate.
"""

voice = "am_adam"
start = time.time()
segments = []

for i, (gs, ps, audio) in enumerate(pipeline(text, voice=voice, speed=0.95)):
    # gs = graphemes (text), ps = phonemes, audio = numpy array
    sf.write(f"narration_{i:03d}.wav", audio, 24000)
    segments.append(audio)
    print(f"  Segment {i}: {gs[:60]}...")

elapsed = time.time() - start
print(f"\nGenerated {len(segments)} segments in {elapsed:.1f}s")
```

### Speed and Quality

- **Speed:** On an M1 Mac or NVIDIA GPU, Kokoro generates audio at roughly 10x real-time (50 min of narration in ~5 min). On CPU-only, expect 1.5-2x real-time (~30 min).
- **Quality:** Natural prosody, good pacing, handles long sentences well. Occasional artifacts on unusual proper nouns. Rate 8/10 — noticeably better than Edge TTS, competitive with OpenAI TTS-1.
- **Sample rate:** 24,000 Hz (adequate for YouTube; upsampling to 44.1kHz is trivial with FFmpeg).

### Tips

- Set `speed=0.95` for narration — slightly slower than default gives weight to the delivery.
- Kokoro handles paragraph breaks naturally. Feed it one narrator section at a time.
- Voice blending is supported: `voice="am_adam(0.7)+am_fenrir(0.3)"` mixes voices.

---

## 2. OpenAI TTS API (gpt-4o-mini-tts)

The best instruction-following TTS available. You can tell it *how* to speak — tone, pace, emotion — and it actually listens.

### Pricing

- **Text input:** $0.60 per 1M tokens
- **Audio output:** $12 per 1M audio tokens
- **Practical cost:** ~$0.015/minute of generated audio
- **50 min screenplay:** roughly $0.50-$0.75 total (very cheap)
- **Max input:** 2,000 tokens per request (~1,500 words). Must chunk longer texts.

### Voices

11 voices available: `alloy`, `ash`, `ballad`, `coral`, `echo`, `fable`, `nova`, `onyx`, `sage`, `shimmer`, `verse`

**True crime recommendations:**
- `onyx` — Deep, serious male voice. Best for documentary narration.
- `ash` — Measured, authoritative.
- `echo` — Lower register, calm intensity.
- `fable` — British-accented, storytelling quality.

### Instruction-Following (Key Feature)

The `instructions` parameter lets you control delivery style:

```python
instructions = """
Speak in a measured, serious documentary narrator tone. Pace yourself —
this is a true crime story. Pause slightly before revealing key facts.
Maintain gravitas throughout. Do not sound excited or enthusiastic.
Think: Dateline NBC narrator meets podcast host.
"""
```

### Python Code Example

```python
"""Generate narration audio using OpenAI gpt-4o-mini-tts."""

import openai
from pathlib import Path

client = openai.OpenAI()  # uses OPENAI_API_KEY env var

text = """
This is Alex Murdaugh. A fourth-generation attorney from one of the most
powerful legal dynasties in the American South.
"""

response = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="onyx",
    input=text,
    instructions=(
        "Narrate in a measured, serious true-crime documentary tone. "
        "Pace is deliberate and weighty. Pause before key revelations. "
        "No excitement — gravitas and authority throughout."
    ),
    response_format="wav",
)

output_path = Path("narration_openai.wav")
response.stream_to_file(output_path)
print(f"Saved to {output_path}")
```

### Chunking for Long Text

The 2,000-token limit means you must split the screenplay into chunks. Each narrator section is typically well under 2,000 tokens, so splitting by `**NARRATOR:**` blocks works naturally.

### Quality

- Rate 9/10 — excellent prosody, natural pacing, good emphasis.
- The instruction-following is genuinely useful. You can ask for "pause after this sentence" and it works.
- Slightly better than Kokoro on emotional range, but marginal.

---

## 3. ElevenLabs

The gold standard for AI voice quality. Most natural-sounding of all options, with the best control over style and emotion. But it costs money.

### Pricing

| Plan | Characters/month | Minutes | Cost | Enough for 50-min video? |
|------|-------------------|---------|------|--------------------------|
| Free | 10,000 | ~5 min | $0 | No — testing only |
| Starter | 30,000 | ~15 min | $5/mo | No — need ~45K chars |
| Creator | 100,000 | ~50 min | $22/mo | Yes, barely |
| Pro | 500,000 | ~250 min | $99/mo | Yes, with room |

**For one 50-min video:** You need the Creator plan ($22/mo) or buy extra characters on Starter.

### Best Voices for True Crime

ElevenLabs has a voice library with thousands of community voices. For true crime narration:
- **"Adam"** (pre-made) — Deep, authoritative male. Good baseline.
- **"Antoni"** (pre-made) — Warm, narrative male voice.
- **"Josh"** (pre-made) — Measured, documentary style.
- Browse the Voice Library and search "true crime" or "narrator" for community-uploaded voices.

### Python SDK Example

```python
"""Generate narration audio using ElevenLabs."""

from elevenlabs import ElevenLabs
from pathlib import Path

client = ElevenLabs(api_key="YOUR_API_KEY")  # or set ELEVEN_API_KEY env var

text = """
This is Alex Murdaugh. A fourth-generation attorney from one of the most
powerful legal dynasties in the American South.
"""

audio_generator = client.text_to_speech.convert(
    text=text,
    voice_id="pNInz6obpgDQGcFmaJgB",  # "Adam" voice
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)

output_path = Path("narration_elevenlabs.mp3")
with open(output_path, "wb") as f:
    for chunk in audio_generator:
        f.write(chunk)
print(f"Saved to {output_path}")
```

### Install

```bash
pip install elevenlabs
```

### Quality

- Rate 9.5/10 — the most natural-sounding option. Best emotional range and micro-pausing.
- Voice cloning is available (clone your own voice or a specific narrator style).
- Overkill for testing, but ideal for published videos where audio quality is a differentiator.

---

## 4. Edge TTS (Free, Microsoft)

Uses Microsoft Edge's cloud TTS service. No API key, no account, completely free. Quality is decent — better than old-school TTS, but noticeably more "robotic" than Kokoro or OpenAI.

### Install

```bash
pip install edge-tts
```

### Best Voices for Narration

```bash
# List all available English voices:
edge-tts --list-voices | grep en-US
```

**True crime recommendations:**
- `en-US-GuyNeural` — Deep, authoritative American male. Best option.
- `en-US-DavisNeural` — Warm, slower American male.
- `en-GB-RyanNeural` — British male, least robotic-sounding according to community.
- `en-US-ChristopherNeural` — Clear, professional male.

### Python Code Example

```python
"""Generate narration audio using Edge TTS."""

import edge_tts
import asyncio
from pathlib import Path

text = """
This is Alex Murdaugh. A fourth-generation attorney from one of the most
powerful legal dynasties in the American South.
"""

async def generate():
    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-GuyNeural",
        rate="-10%",   # slightly slower for narration weight
        pitch="-5Hz",  # slightly deeper
    )
    output_path = Path("narration_edge.mp3")
    await communicate.save(str(output_path))
    print(f"Saved to {output_path}")

asyncio.run(generate())
```

### Subtitle Generation (Bonus)

Edge TTS can generate word-level timestamps — useful for syncing text overlays:

```python
async def generate_with_subtitles():
    communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural", rate="-10%")
    submaker = edge_tts.SubMaker()
    with open("narration_edge.mp3", "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
    with open("narration_edge.vtt", "w") as f:
        f.write(submaker.generate_subs())

asyncio.run(generate_with_subtitles())
```

### Quality

- Rate 7/10 — serviceable but recognizably synthetic. The pacing is mechanical.
- Pros: free, fast, subtitle generation, reliable uptime.
- Cons: limited prosody control, no emotional range, "reads text" rather than "narrates."

---

## 5. Piper TTS (Free, Open Source, Fast)

Designed for speed on low-power hardware (Raspberry Pi). Quality is lower than Kokoro but generation speed is excellent.

### Install

```bash
pip install piper-tts
# Or download binary from GitHub releases:
# https://github.com/rhasspy/piper/releases
```

Voice models are downloaded separately from Hugging Face:
```bash
# Download a voice model (example: lessac medium quality):
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

### Best Voices for Narration

Voice models come in quality tiers: `x_low`, `low`, `medium`, `high`.

- `en_US-lessac-high` — Best quality American English. Professional, clear.
- `en_US-joe-medium` — Male, slightly warmer tone.
- `en_GB-alan-medium` — British male, composed.

Browse all voices with samples: https://rhasspy.github.io/piper-samples/

### Python Code Example

```python
"""Generate narration audio using Piper TTS."""

import wave
import struct
from piper import PiperVoice

voice = PiperVoice.load("en_US-lessac-medium.onnx")

text = """
This is Alex Murdaugh. A fourth-generation attorney from one of the most
powerful legal dynasties in the American South.
"""

wav_file = wave.open("narration_piper.wav", "w")
audio = voice.synthesize(text, wav_file)
wav_file.close()
print("Saved to narration_piper.wav")
```

### Command-Line Usage (Simpler)

```bash
echo "This is Alex Murdaugh." | piper \
  --model en_US-lessac-medium.onnx \
  --output_file narration_piper.wav
```

### Quality

- Rate 6/10 — noticeably more robotic than Kokoro or Edge TTS. Flat prosody.
- Extremely fast: generates audio at 50-100x real-time on CPU.
- Best for prototyping, testing timing, or applications where speed matters more than polish.
- No emotional range. Reads text flatly.

---

## Practical Script: Screenplay to Narration Audio

This script reads the Alex Murdaugh screenplay, extracts narrator lines (stripping stage directions and clip tags), and generates audio for each section using Kokoro TTS.

### Usage

```bash
python generate_narration.py \
  --screenplay bee-content-discovery/true-crime/cases/alex-murdaugh/screenplay-v2.md \
  --output-dir output/narration \
  --engine kokoro \
  --voice am_adam
```

### Full Script: `generate_narration.py`

```python
#!/usr/bin/env python3
"""
generate_narration.py — Extract narrator lines from a screenplay and generate
TTS audio for each section.

Supports: kokoro, openai, edge, elevenlabs, piper

Usage:
    python generate_narration.py --screenplay screenplay.md --output-dir output/ --engine kokoro
"""

import argparse
import re
import sys
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Parse the screenplay — extract narrator text only
# ---------------------------------------------------------------------------

def extract_narrator_sections(screenplay_path: str) -> list[dict]:
    """
    Read a screenplay markdown file and extract narrator lines.

    Returns a list of dicts:
        [{"section": "COLD OPEN", "index": 0, "text": "This is Alex Murdaugh..."}]

    Strips out:
    - Stage directions: [BROLL-DARK], [TEXT-TIMELINE: "..."], [MAP-REGION], etc.
    - Audio clip lines: >> **SPEAKER:** "dialogue"
    - Markdown headers (used for section tracking only)
    - Empty lines and formatting artifacts
    """
    text = Path(screenplay_path).read_text(encoding="utf-8")
    lines = text.split("\n")

    sections = []
    current_section = "INTRO"
    current_paragraphs = []

    for line in lines:
        stripped = line.strip()

        # Track section headers (## or ###)
        if stripped.startswith("## ") or stripped.startswith("### "):
            # Flush accumulated narrator text
            if current_paragraphs:
                combined = " ".join(current_paragraphs).strip()
                if combined:
                    sections.append({
                        "section": current_section,
                        "index": len(sections),
                        "text": combined,
                    })
                current_paragraphs = []
            # Update section name
            current_section = stripped.lstrip("#").strip()
            # Remove timestamp patterns like "(0:00 - 2:30)"
            current_section = re.sub(r"\s*\([\d:]+\s*-\s*[\d:]+\)", "", current_section)
            continue

        # Skip stage directions: lines that are only [TAGS]
        if re.match(r"^\[.*\]\s*$", stripped):
            continue

        # Skip audio clip lines: >> **SPEAKER:** "text"
        if stripped.startswith(">>"):
            continue

        # Skip metadata lines at the top
        if stripped.startswith("**Style:") or stripped.startswith("**Target Duration:"):
            continue
        if stripped.startswith("**Tense:") or stripped.startswith("**POV:"):
            continue
        if stripped.startswith("**Audio Ratio:") or stripped.startswith("**Real Audio"):
            continue

        # Skip horizontal rules
        if stripped == "---":
            continue

        # Extract narrator lines: **NARRATOR:** text
        narrator_match = re.match(r"^(?:\[.*?\]\s*)*\*\*NARRATOR:\*\*\s*(.*)", stripped)
        if narrator_match:
            narrator_text = narrator_match.group(1).strip()
            if narrator_text:
                current_paragraphs.append(narrator_text)
            continue

        # Skip lines that start with [TAG] followed by non-narrator content
        if stripped.startswith("["):
            continue

        # Skip empty lines (but don't break sections)
        if not stripped:
            continue

    # Flush final section
    if current_paragraphs:
        combined = " ".join(current_paragraphs).strip()
        if combined:
            sections.append({
                "section": current_section,
                "index": len(sections),
                "text": combined,
            })

    return sections


# ---------------------------------------------------------------------------
# 2. TTS Engine wrappers
# ---------------------------------------------------------------------------

def generate_kokoro(text: str, output_path: Path, voice: str = "am_adam", speed: float = 0.95):
    """Generate audio using Kokoro TTS (free, local)."""
    from kokoro import KPipeline
    import soundfile as sf
    import numpy as np

    pipeline = KPipeline(lang_code='a')
    all_audio = []

    for _i, (_gs, _ps, audio) in enumerate(pipeline(text, voice=voice, speed=speed)):
        all_audio.append(audio)

    combined = np.concatenate(all_audio)
    sf.write(str(output_path), combined, 24000)


def generate_openai(text: str, output_path: Path, voice: str = "onyx"):
    """Generate audio using OpenAI gpt-4o-mini-tts (paid API)."""
    import openai

    client = openai.OpenAI()

    # Chunk text if it exceeds ~1500 words (token limit is 2000 tokens)
    words = text.split()
    chunks = []
    chunk_size = 1200  # words per chunk, conservative
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


def generate_edge(text: str, output_path: Path, voice: str = "en-US-GuyNeural"):
    """Generate audio using Edge TTS (free, cloud)."""
    import edge_tts
    import asyncio

    async def _generate():
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate="-10%",
            pitch="-5Hz",
        )
        await communicate.save(str(output_path))

    asyncio.run(_generate())


def generate_elevenlabs(text: str, output_path: Path, voice_id: str = "pNInz6obpgDQGcFmaJgB"):
    """Generate audio using ElevenLabs (paid API). Default voice: Adam."""
    from elevenlabs import ElevenLabs

    client = ElevenLabs()  # uses ELEVEN_API_KEY env var
    audio_generator = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    with open(output_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)


def generate_piper(text: str, output_path: Path, model: str = "en_US-lessac-medium.onnx"):
    """Generate audio using Piper TTS (free, local, fast)."""
    import wave
    from piper import PiperVoice

    voice = PiperVoice.load(model)
    wav_file = wave.open(str(output_path), "w")
    voice.synthesize(text, wav_file)
    wav_file.close()


ENGINES = {
    "kokoro": generate_kokoro,
    "openai": generate_openai,
    "edge": generate_edge,
    "elevenlabs": generate_elevenlabs,
    "piper": generate_piper,
}


# ---------------------------------------------------------------------------
# 3. Main — parse screenplay, generate audio per section
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate TTS narration from a screenplay."
    )
    parser.add_argument(
        "--screenplay", required=True,
        help="Path to the screenplay markdown file.",
    )
    parser.add_argument(
        "--output-dir", default="output/narration",
        help="Directory to save generated audio files.",
    )
    parser.add_argument(
        "--engine", choices=list(ENGINES.keys()), default="kokoro",
        help="TTS engine to use (default: kokoro).",
    )
    parser.add_argument(
        "--voice", default=None,
        help="Voice ID (engine-specific). Defaults vary by engine.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse screenplay and print sections without generating audio.",
    )
    args = parser.parse_args()

    # Parse screenplay
    print(f"Parsing screenplay: {args.screenplay}")
    sections = extract_narrator_sections(args.screenplay)
    total_chars = sum(len(s["text"]) for s in sections)
    print(f"Found {len(sections)} narrator sections ({total_chars:,} characters total)")
    print()

    if args.dry_run:
        for s in sections:
            preview = s["text"][:80] + "..." if len(s["text"]) > 80 else s["text"]
            print(f"  [{s['index']:02d}] {s['section']}")
            print(f"       {len(s['text']):,} chars | {preview}")
            print()
        print("Dry run complete. No audio generated.")
        return

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Select engine
    engine_fn = ENGINES[args.engine]
    ext = "mp3" if args.engine in ("edge", "elevenlabs") else "wav"

    print(f"Engine: {args.engine}")
    print(f"Output: {output_dir}/")
    print()

    total_start = time.time()

    for section in sections:
        idx = section["index"]
        name = re.sub(r"[^\w\s-]", "", section["section"]).strip().replace(" ", "_").lower()
        filename = f"{idx:02d}_{name}.{ext}"
        output_path = output_dir / filename

        print(f"[{idx:02d}/{len(sections)-1}] {section['section']} ({len(section['text']):,} chars)")

        start = time.time()

        kwargs = {}
        if args.voice:
            # Map the --voice arg to the correct parameter name per engine
            if args.engine == "elevenlabs":
                kwargs["voice_id"] = args.voice
            elif args.engine == "piper":
                kwargs["model"] = args.voice
            else:
                kwargs["voice"] = args.voice

        try:
            engine_fn(section["text"], output_path, **kwargs)
            elapsed = time.time() - start
            print(f"         -> {filename} ({elapsed:.1f}s)")
        except Exception as e:
            print(f"         !! ERROR: {e}", file=sys.stderr)

    total_elapsed = time.time() - total_start
    print(f"\nDone. {len(sections)} files in {total_elapsed:.1f}s")
    print(f"Output directory: {output_dir.resolve()}")

    # Write a manifest file
    manifest_path = output_dir / "manifest.txt"
    with open(manifest_path, "w") as f:
        for section in sections:
            idx = section["index"]
            name = re.sub(r"[^\w\s-]", "", section["section"]).strip().replace(" ", "_").lower()
            filename = f"{idx:02d}_{name}.{ext}"
            f.write(f"file '{filename}'\n")
    print(f"FFmpeg concat manifest: {manifest_path}")
    print(f"  Concatenate all: ffmpeg -f concat -safe 0 -i {manifest_path} -c copy full_narration.{ext}")


if __name__ == "__main__":
    main()
```

### Dry Run (Test Parsing)

```bash
python generate_narration.py \
  --screenplay bee-content-discovery/true-crime/cases/alex-murdaugh/screenplay-v2.md \
  --dry-run
```

Output:
```
Parsing screenplay: ...screenplay-v2.md
Found 42 narrator sections (38,412 characters total)

  [00] Visceral Hook
       412 chars | This is Alex Murdaugh. A fourth-generation attorney from one of the most power...

  [01] Flash-Forward Montage
       287 chars | Unknowingly, this deputy is speaking to the man who pulled the trigger just ni...
  ...
```

### Generate Full Narration with Kokoro

```bash
# Generate all sections:
python generate_narration.py \
  --screenplay bee-content-discovery/true-crime/cases/alex-murdaugh/screenplay-v2.md \
  --output-dir output/narration-kokoro \
  --engine kokoro \
  --voice am_adam

# Concatenate into single file:
cd output/narration-kokoro
ffmpeg -f concat -safe 0 -i manifest.txt -c copy full_narration.wav

# Convert to mp3 for smaller file size:
ffmpeg -i full_narration.wav -codec:a libmp3lame -b:a 192k full_narration.mp3
```

### Generate with Edge TTS (Zero Setup)

```bash
python generate_narration.py \
  --screenplay bee-content-discovery/true-crime/cases/alex-murdaugh/screenplay-v2.md \
  --output-dir output/narration-edge \
  --engine edge \
  --voice en-US-GuyNeural
```

---

## Post-Processing Recipes

### Normalize Audio Levels

```bash
# Normalize all WAV files to -16 LUFS (YouTube recommended):
for f in output/narration-kokoro/*.wav; do
  ffmpeg -i "$f" -af loudnorm=I=-16:TP=-1.5:LRA=11 -y "${f%.wav}_norm.wav"
done
```

### Add Room Tone / Ambient Bed

```bash
# Mix narration with subtle ambient background:
ffmpeg -i full_narration.wav -i ambient_dark_room.wav \
  -filter_complex "[1:a]volume=0.08[bg];[0:a][bg]amix=inputs=2:duration=first" \
  -c:a pcm_s16le narration_with_ambience.wav
```

### Speed Adjustment (Without Pitch Change)

```bash
# Slow down 5% for more gravitas:
ffmpeg -i full_narration.wav -af "atempo=0.95" narration_slower.wav

# Speed up 10% to tighten pacing:
ffmpeg -i full_narration.wav -af "atempo=1.10" narration_faster.wav
```

---

## Cost Summary for Full 50-Minute Video

| Engine | Total Cost | Notes |
|--------|-----------|-------|
| Kokoro TTS | $0 | Local GPU/CPU. Free forever. |
| Edge TTS | $0 | Microsoft's cloud service. Free. |
| Piper TTS | $0 | Local CPU. Free forever. |
| OpenAI TTS | ~$0.50-$0.75 | Based on ~45K chars / token pricing |
| ElevenLabs | $22/mo (Creator plan) | Need ~45K chars. Starter plan is not enough. |

---

## Workflow Recommendation

1. **Prototyping / testing timing:** Use Edge TTS (instant, free, no setup).
2. **Draft narration:** Use Kokoro TTS locally (free, good quality, iterate fast).
3. **Final published video:** Either Kokoro (if quality is acceptable) or OpenAI TTS ($0.50-$0.75 per video is negligible).
4. **Premium quality:** ElevenLabs (if the channel revenue justifies $22/mo).

The quality gap between Kokoro and the paid APIs has narrowed significantly. For a faceless true crime channel, Kokoro is likely good enough — especially after normalization and ambient mixing in post-production.
