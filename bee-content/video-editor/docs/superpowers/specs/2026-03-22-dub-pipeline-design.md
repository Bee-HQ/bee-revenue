# AI Dubbing Pipeline — Design Spec

**Date:** 2026-03-22
**Status:** Draft
**Context:** Zero channels are dubbing English radio call-in compilations (Second Date Update, War of the Roses, etc.) into other languages. YouTube's AI dubbing ecosystem is exploding (auto-dub launched globally mid-2025, 27 languages, 6M daily viewers). The format is audio-over-slideshow — ideal for AI dubbing since no lip sync is needed.

## Goal

Build a modular dubbing pipeline as a `bee-video dub` CLI that takes an English YouTube compilation, translates and dubs it into target languages using AI voice cloning, and outputs a publish-ready video.

**POC target:** One top-performing English Second Date Update compilation dubbed into Spanish.

**Follow-up languages:** German, Arabic.

## Pipeline Overview

```
Source Video
    |
    v
[Download] --> [Transcribe] --> [Diarize] --> [Separate] --> [Translate]
 (yt-dlp)      (Whisper)      (speakers)     (vocals)       (Claude)
                                                                |
    +-----------------------------------------------------------+
    v
[Voice Clone] --> [TTS Gen] --> [Mix & Burn]
 (ElevenLabs)   (ElevenLabs)     (FFmpeg)
                                    |
                                    v
                              dubbed_es.mp4
```

Each box is an independent service. Services communicate through a shared project directory. Each service is idempotent — re-running skips completed segments. A `status.json` tracks per-segment state (`pending`, `completed`, `failed`, `skipped`) with error messages.

## Project Directory Structure

```
dub-projects/
  my-video/
    dub.json                 # Pipeline config (JSON, matches bee-video conventions)
    status.json              # Per-segment state tracking
    source.mp4               # Downloaded source video
    transcript.json          # Whisper output (timestamped word-level)
    diarization.json         # Speaker segments + labels
    separated/
      vocals.wav             # Isolated vocal track (demucs)
      accompaniment.wav      # Background audio (music, jingles, sfx)
    voices/
      speaker_0.mp3          # Extracted audio sample per speaker
      speaker_1.mp3
      manifest.json          # Maps speaker IDs to ElevenLabs voice IDs
    translations/
      es.json                # Spanish translated segments
      de.json                # German (future)
      ar.json                # Arabic (future)
    tts/
      es/
        seg_001.mp3          # Generated TTS audio per segment
        seg_002.mp3
    output/
      es.mp4                 # Final dubbed video
```

## Services

### 0. Download Service

- **Input:** YouTube URL
- **Output:** `source.mp4`
- **Engine:** yt-dlp (transitive dependency via bee-content-research)
- **Behavior:** Downloads best quality video+audio. Skips if `source.mp4` exists.
- **Configurable:** format, quality

### 1. Transcription Service

- **Input:** `source.mp4`
- **Output:** `transcript.json`
- **Engine:** OpenAI Whisper API (default), local whisper.cpp (configurable)
- **Format:** Timestamped word-level segments with confidence scores
- **Configurable:** engine, model size, language hint

### 2. Diarization Service

- **Input:** `transcript.json` + `source.mp4`
- **Output:** `diarization.json` + `voices/speaker_*.mp3`
- **Engine:** pyannote-audio (default), WhisperX (configurable)
- **Behavior:**
  - Maps each transcript segment to a speaker ID (`speaker_0`, `speaker_1`, etc.)
  - Extracts audio samples per speaker for voice cloning
  - Minimum sample duration: 30s clean audio per speaker
  - Quality filtering: rejects segments with high noise/cross-talk
  - Fallback: speakers with insufficient clean audio are flagged for mapped voice assignment
- **Configurable:** engine, min/max speakers, min_sample_duration
- **Note:** pyannote requires HuggingFace token (manual model access approval) and runs slowly on CPU. For POC, WhisperX (bundles diarization with transcription) is the pragmatic choice.

### 3. Vocal Separation Service

- **Input:** `source.mp4`
- **Output:** `separated/vocals.wav` + `separated/accompaniment.wav`
- **Engine:** demucs (htdemucs model)
- **Behavior:**
  - Separates speech from background audio (music beds, jingles, sfx)
  - Vocals track used as reference for diarization quality
  - Accompaniment track mixed back in at compositor step if `keep_background_audio` is enabled
- **Configurable:** engine, model

### 4. Translation Service

- **Input:** `diarization.json`
- **Output:** `translations/{lang}.json`
- **Engine:** Claude API (default), swappable to DeepL or Google Translate
- **Behavior:**
  - Translates each segment's text to target language
  - Preserves speaker labels, timestamps, segment boundaries
  - Outputs `target_duration_ms` per segment (matched to original segment duration)
  - Prompted for natural, conversational tone — not literal translation
- **Configurable:** engine, target language, model, style prompt

### 5. Voice Service

- **Input:** `voices/speaker_*.mp3`
- **Output:** `voices/manifest.json` (maps speaker IDs to ElevenLabs voice IDs)
- **Modes:**
  - **clone:** Uploads speaker audio samples to ElevenLabs, creates cloned voices
  - **mapped:** Assigns pre-existing ElevenLabs voice IDs to each speaker (fallback for low-quality samples)
- **Configurable:** mode (clone/mapped), per-speaker voice overrides

### 6. TTS Service

- **Input:** `translations/{lang}.json` + `voices/manifest.json`
- **Output:** `tts/{lang}/seg_*.mp3`
- **Engine:** ElevenLabs multilingual v2 (default)
- **Behavior:**
  - Generates one audio file per segment using the cloned/mapped voice for that speaker
  - Adjusts TTS speed or applies FFmpeg `atempo` to match `target_duration_ms` (drift tolerance: +/- 500ms)
  - Idempotent — skips segments that already have generated audio
  - Failed segments logged to `status.json`, can be retried with `--retry-failed`
- **Configurable:** engine, model, stability, similarity_boost, speed

### 7. Compositor Service

- **Input:** `source.mp4` + `tts/{lang}/seg_*.mp3` + `translations/{lang}.json` + `separated/accompaniment.wav` (optional)
- **Output:** `output/{lang}.mp4`
- **Behavior:**
  - Strips original audio from source video
  - Mixes dubbed segments at correct timestamps
  - Optionally mixes in accompaniment track (radio jingles, music beds) at low volume
  - Generates subtitles in target language (ASS format, reusing existing caption system)
  - Burns subtitles into video
  - Normalizes loudness to target LUFS
- **Configurable:** subtitle style (phrase/karaoke), keep background audio, background volume, target LUFS

## CLI Interface

```bash
# Full pipeline
bee-video dub run <url-or-file> --lang es --voices clone -p ./my-project

# Individual services
bee-video dub download <url> -p ./my-project
bee-video dub transcribe -p ./my-project
bee-video dub diarize -p ./my-project
bee-video dub separate -p ./my-project
bee-video dub translate --lang es --engine claude -p ./my-project
bee-video dub voices --mode clone -p ./my-project
bee-video dub tts --lang es -p ./my-project
bee-video dub compose --lang es -p ./my-project

# Re-run just translation with different engine
bee-video dub translate --lang es --engine deepl -p ./my-project

# Retry failed segments
bee-video dub tts --lang es --retry-failed -p ./my-project

# Add another language (reuses transcript + diarization + separation + voices)
bee-video dub translate --lang de --engine claude -p ./my-project
bee-video dub tts --lang de -p ./my-project
bee-video dub compose --lang de -p ./my-project

# Check pipeline status
bee-video dub status -p ./my-project
```

Key behaviors:
- Each command is idempotent — skips completed segments, resumes on failure
- `run` checks what's already done and only runs remaining steps
- Adding a new language only requires translate + tts + compose
- Project directory (`-p`) follows existing bee-video convention
- First command group in the CLI (uses typer `add_typer()`)

## Configuration

`dub.json` per project (matches existing `.bee-project.json` convention — no YAML), all CLI flags override config:

```json
{
  "source": "source.mp4",
  "languages": ["es"],
  "transcription": {
    "engine": "whisper",
    "model": "large-v3"
  },
  "diarization": {
    "engine": "whisperx",
    "min_speakers": 2,
    "max_speakers": 10,
    "min_sample_duration": 30
  },
  "separation": {
    "engine": "demucs",
    "model": "htdemucs"
  },
  "translation": {
    "engine": "claude",
    "model": "claude-sonnet-4-6",
    "style": "Translate as a native speaker telling a funny dating story. Keep slang natural. Don't be literal — capture the vibe."
  },
  "voices": {
    "mode": "clone",
    "engine": "elevenlabs",
    "overrides": {}
  },
  "tts": {
    "engine": "elevenlabs",
    "model": "eleven_multilingual_v2",
    "stability": 0.5,
    "similarity_boost": 0.75
  },
  "compositor": {
    "keep_background_audio": true,
    "background_volume": 0.05,
    "subtitles": true,
    "subtitle_style": "phrase",
    "target_lufs": -14.0
  }
}
```

## Dependencies

**New:**
- `openai-whisper` or Whisper API — transcription
- `pyannote-audio` — speaker diarization (requires HuggingFace token, GPU recommended)
- `demucs` — vocal/accompaniment separation
- `anthropic` — translation via Claude (not currently in pyproject.toml, add as optional extra)
- `yt-dlp` — source video download

**Existing (no changes):**
- `elevenlabs` — voice cloning + multilingual TTS
- FFmpeg — audio extraction, mixing, subtitle burn
- Caption system — ASS subtitle generation

## Cost Estimate

Per 2-3h compilation (~25K words, ~130K chars), single language:

| Step | Service | Est. Cost |
|------|---------|-----------|
| Download | yt-dlp (local) | $0 |
| Transcribe | Whisper API | ~$0.36 (3h x $0.006/min) |
| Diarize | whisperx (local) | $0 |
| Separate | demucs (local) | $0 |
| Translate | Claude Sonnet | ~$0.50 (~50K tokens) |
| Voice clone | ElevenLabs | $0 (included in plan) |
| TTS generation | ElevenLabs | ~$4-10 (~130K chars) |
| Compose | FFmpeg (local) | $0 |
| **Total** | | **~$5-11 per video** |

ElevenLabs plan minimum: Creator ($22/mo, 100K chars) covers ~1 video. Scale ($99/mo, 500K chars) for production volume.

At 3-5 videos/week across 3 languages = ~$45-165/week in API costs.

## Integration Points

Hooks into existing bee-video infrastructure:
- **FFmpeg processor** — new: `extract_audio()`. Reuse: `mix_audio()`, `normalize_loudness()`
- **TTS processor** — reuse ElevenLabs engine, add language parameter
- **Caption processor** — reuse ASS subtitle generation with translated text
- **CLI** — new `dub` command group via `add_typer()` (first command group in the codebase)

## Risks & Mitigations

### DMCA / Copyright

This is the highest-impact risk. The pipeline dubs copyrighted radio show content for monetization on YouTube. Mitigations:
- The transformation (translation + voice cloning + new language market) adds substantial value not available to original rights holders
- Start with content from channels that are themselves unauthorized repurposers — if they haven't been taken down, the rights holders may not be actively enforcing
- Monitor for strikes and be prepared to pivot to original content or licensed material
- Long-term: explore licensing deals with iHeart or creating original call-in content

### Technical Risks

- **Voice cloning quality:** Cloning from compressed podcast/phone audio may produce lower quality. Mitigation: quality filtering on samples, fallback to mapped voices
- **Diarization accuracy:** Radio call-in shows have interruptions, overlapping speech, phone-quality audio. Mitigation: WhisperX for POC, manual correction for high-value segments
- **Translation timing:** Spanish is ~25% longer than English, German varies, Arabic can go either way. Mitigation: `target_duration_ms` + TTS speed adjustment + 500ms drift tolerance
- **Cost scaling:** API costs are manageable at POC scale but add up at production volume. Mitigation: batch processing, caching, consider local TTS alternatives for scale
