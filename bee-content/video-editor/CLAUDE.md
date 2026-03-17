# CLAUDE.md — bee-video-editor

## What This Is

AI-assisted video production tool. Takes storyboard/assembly guide markdown → generates assets → assembles final video. Built for true crime documentaries but the processors are genre-agnostic.

**Version:** 0.3.1
**Python:** >=3.11, managed with `uv` + `hatchling`
**Entry point:** `bee-video` CLI

## Quick Reference

```bash
cd bee-content/video-editor

# CLI workflow
uv run bee-video parse <guide.md>                           # Inspect
uv run bee-video init <guide.md> --project-dir ./proj       # Create project
uv run bee-video graphics <guide.md> -p ./proj              # Generate overlays
uv run bee-video narration <guide.md> -p ./proj --tts edge  # Generate TTS
uv run bee-video trim-footage <guide.md> -p ./proj          # Trim source clips
uv run bee-video assemble -p ./proj --transition dissolve   # Final assembly

# Web editor
./dev.sh        # Dev mode (backend :8420 + frontend :5173 hot reload)
./start.sh      # Production (single server :8420, built frontend)

# Tests
uv run --extra dev pytest tests/ -v          # All 113 tests
uv run --extra dev pytest tests/FILE -v      # Single file
```

## Architecture

```
Adapters (CLI / Web UI / FastAPI)
    │
Services (production.py — orchestration, no business logic)
    │
┌───┴───┐
Parsers    Processors
├ assembly_guide.py    ├ ffmpeg.py   (17 functions, 657 lines)
└ storyboard.py        ├ graphics.py (Pillow overlays)
                       └ tts.py      (edge / kokoro / openai)
```

**Adapters** are thin protocol translators. CLI (Typer) and Web (FastAPI + React) both delegate to the same service functions.

**Services** resolve targets, call processors, manage state. No FFmpeg commands, no Pillow drawing — just orchestration.

**Parsers** convert markdown → dataclasses. Two formats exist (see "Two Parser Problem" below).

**Processors** are stateless functions wrapping external tools. All I/O, no orchestration.

## Two Parser Problem

There are two input formats and two data models:

| Format | Parser | Model | Used By |
|--------|--------|-------|---------|
| Assembly guide (flat time-coded table) | `parsers/assembly_guide.py` | `models.Project` | CLI pipeline |
| Storyboard (shot-by-shot with layers) | `parsers/storyboard.py` | `models_storyboard.Storyboard` | Web UI |

The storyboard format is richer (6 layers: visual, audio, overlay, music, source, transition) but the production service still expects the assembly guide's `Project` model. The web UI loads storyboards but calls production endpoints that internally work with different data.

**Planned fix (v0.4.0):** Make `Storyboard` canonical, add `assembly_guide_to_storyboard()` converter, deprecate direct `Project` usage.

## Processor Capabilities

### FFmpeg (`processors/ffmpeg.py`)

| Category | Functions |
|----------|-----------|
| Probe | `probe()`, `get_duration()` |
| Basic | `trim()`, `normalize_format()`, `concat_segments()`, `concat_with_transitions()` |
| Image | `image_to_video()` (7 Ken Burns effects), `waveform_video()`, `overlay_png()` |
| Effects | `color_grade()` (12 presets), `drawtext()`, `speed()`, `xfade()` (30+ transitions), `add_fade()`, `picture_in_picture()` |
| Audio | `mix_audio()`, `normalize_loudness()` (target: -14 LUFS) |

**Color presets:** dark_crime, warm_victim, bodycam, noir, sepia, cold_blue, vintage, bleach_bypass, night_vision, golden_hour, surveillance, vhs

**Ken Burns:** zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down, zoom_in_pan_right

**Transitions:** fade, dissolve, wipeleft/right/up/down, slideleft/right/up/down, smoothleft/right, circlecrop, rectcrop, pixelize, radial, diagtl/tr/bl/br, hlslice/hrslice, distance, zoomin, fadeblack, fadewhite, hblur, vuslice, vdslice

### Graphics (`processors/graphics.py`)

| Function | Output |
|----------|--------|
| `lower_third(name, role)` | PNG — semi-transparent bar + name/role text |
| `timeline_marker(date, desc)` | PNG — full-frame date stamp |
| `financial_card(amount, desc)` | PNG — red dollar amount display |
| `quote_card(quote, author)` | PNG — quote display |
| `text_overlay(text)` | PNG — simple text |
| `black_frame()` | PNG — solid black |

All output 1920x1080 PNG. Colors follow Dr. Insanity palette (dark bg, red/teal accents).

### TTS (`processors/tts.py`)

| Engine | Cost | Quality | Notes |
|--------|------|---------|-------|
| Edge | Free (cloud) | Good | Default voice: en-US-GuyNeural |
| Kokoro | Free (local) | Good | 24kHz WAV, needs `kokoro>=0.9.4` |
| OpenAI | Paid | Best | gpt-4o-mini-tts, 1200-word chunking |
| ElevenLabs | Free tier / Paid | Best | Default voice: Daniel. Needs `ELEVENLABS_API_KEY` env var. Formula-recommended engine. |

`extract_narrator_sections(screenplay_path)` pulls `**NARRATOR:**` lines from screenplay markdown.

## Web UI

React 18 + TypeScript + Vite + Tailwind + Zustand.

**Layout:** 4-column NLE-style grid — segment list (left), timeline + segment detail (center-top), video player (center-bottom), media library + production bar (right).

**Key flows:**
- Load storyboard → segments populate the list
- Browse media library → drag file onto segment layer → assignment saved to `.bee-video/assignments.json`
- Click "Graphics" / "Narration" / "Assemble" → API calls to production endpoints

**API routes:**
- `POST /api/projects/load` — load storyboard + restore assignments
- `GET /api/media/list` — list project media by category
- `POST /api/production/{graphics|narration|assemble}` — generate assets
- `GET /api/production/status` — phase + file counts

## Known Gaps & Issues

> **All gaps, issues, and planned work are tracked in `ROADMAP.md`** — that's the single source of truth. Summary below for quick reference.

**Formula alignment gaps** (graphics the formula needs that bee-video can't generate): text chat recreations, social media mockups, evidence boards, flow diagrams, animated timelines, news montages, subtitle generation, maps, asset preflight. See ROADMAP v0.4.0 through v0.5.0 for when each is planned.

**v0.3.1 code issues — all resolved:** FFmpeg errors now surface via ProductionResult. Module globals replaced by SessionStore. API base URL configurable. Segment statuses tracked via track(). Mugshot cards and quote card colors implemented.

**Scale issues** (v0.6.0+): stock footage repetition across videos, no LLM screenplay generation, no batch graphics from config, no FOIA pipeline tracking.

## Project Directory Structure (after init)

```
my-project/
├── output/
│   ├── segments/       # Trimmed source clips
│   ├── normalized/     # 1080p/30fps standardized
│   ├── composited/     # With overlays applied
│   ├── graphics/       # Generated PNGs
│   ├── narration/      # TTS audio files
│   └── final/          # final_assembled.mp4
├── .bee-video/
│   └── assignments.json  # Media assignments (sidecar)
└── production_state.json # Pipeline state
```

## Test Patterns

- **Parsers:** Inline markdown fixtures → assert on parsed structure
- **Graphics:** Mock Pillow → verify function calls + output paths
- **FFmpeg:** Mock subprocess.run → verify filter strings (no real video)
- **Production:** Temp directories → integration-style pipeline calls

113 tests across 7 files. Run with `uv run --extra dev pytest tests/ -v`.

## Dependencies

**Core:** typer, rich, pillow, edge-tts
**Web:** fastapi, uvicorn, python-multipart (`uv sync --extra web`)
**TTS extras:** kokoro + soundfile (`--extra tts-kokoro`), openai (`--extra tts-openai`)
**Dev:** pytest (`--extra dev`)
**System:** FFmpeg must be installed and on PATH

## Related Documents

| Doc | Purpose |
|-----|---------|
| `CHANGELOG.md` | Version history (v0.1.0 → v0.3.1) |
| `ROADMAP.md` | Planned features (v0.3.1 → v0.5.0) |
| `PLAN.md` | Original v0.2.0 web editor design doc |
| `README.md` | User-facing usage docs |
| `../research/screenplay-storyboard-formula.md` | The production formula this tool serves |
| `../research/visual-storyboard-bible.md` | Visual element specs the graphics processor should implement |
