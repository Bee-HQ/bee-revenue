# Changelog

All notable changes to bee-video-editor are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-03-17

### Added

- **`bee-video produce`** — one-command full pipeline (init → graphics → captions → narration → trim → assemble) with auto-skip and step progress
- **Preview generation** — 360p thumbnails per segment from assigned media, per-segment + batch, cached in `output/previews/`
- **Parallel narration** — `--workers N` flag for concurrent TTS via ThreadPoolExecutor
- **WebSocket progress** — real-time progress for narration and produce pipeline via `/ws/progress`
- **Flow diagram** — `flow_diagram()` with directional arrows, red/teal colors, arrowheads, auto-layout
- **Timeline sequence** — `timeline_sequence()` horizontal timeline with active/current/future nodes
- **OTIO timeline export** — `bee-video export` compiles storyboard to OpenTimelineIO with visual code metadata, section markers, media references
- **Map generation** — `bee-video map` generates `[MAP-FLAT]`, `[MAP-TACTICAL]`, `[MAP-PULSE]`, `[MAP-ROUTE]` from lat/lng via py-staticmaps + dark grade + vignette

## [0.4.0] - 2026-03-17

### Added

- **ASS caption generation** — `bee-video captions` with karaoke (word-by-word `\kf`) and phrase modes via pysubs2, burns into final video via FFmpeg `ass` filter
- **Asset preflight** — `bee-video preflight` scans storyboard against project files, reports found/missing/needs-check with JSON manifest
- **Model unification** — `assembly_guide_to_storyboard()` converter, `_ensure_storyboard()` in production service, both input formats work transparently
- **Parser resilience** — whitespace normalization, missing section handling, malformed row skipping in both parsers
- **Text chat recreation** — `text_chat()` with iMessage/SMS/generic platforms
- **Social media post** — `social_post()` for Facebook/Instagram/Twitter/Snapchat
- **News headline montage** — `news_montage()` stacked rotated headline cards
- **Evidence board** — `evidence_board()` red-string corkboard with circle/grid layout
- **Lottie animated overlays** — `--animated` CLI flag for animated lower-thirds via Lottie + Cairo + FFmpeg VP9
- **Persistent session** — auto-reload last project on restart via `~/.bee-video/last-session.json`
- **Undo/redo** — Zustand history stack for media assignments, Ctrl+Z / Ctrl+Shift+Z
- **Segment reordering** — HTML5 drag-drop, persisted to `.bee-video/segment-order.json`
- **Batch media assignment** — shift-click multi-select, drop assigns to all selected
- **ElevenLabs TTS** — 4th TTS engine with `ELEVENLABS_API_KEY` env var, default voice: Daniel
- 100+ new tests (113 → 269)

### Changed

- Production functions use Storyboard internally via `_ensure_storyboard()` converter
- Storyboard parser recognizes `[CODE: qualifier]` bible visual codes

## [0.3.1] - 2026-03-17

### Added

- **ProductionResult** structured return type — all production functions return succeeded/failed/skipped lists instead of silently swallowing errors
- **FailedItem** dataclass — captures path + error message for each failure
- **track() context manager** on ProductionState — automatic segment status transitions (pending→processing→done/error) with disk persistence
- **SessionStore** class — replaces 3 module-level globals with FastAPI Depends injection. Centralizes storyboard loading, media assignment, and session state
- **Input validation** — tts_engine validated against allowed engines, transition names validated against XFADE_TRANSITIONS, project_dir existence checked on load
- **Configurable API base URL** — `VITE_API_BASE` env var in frontend (default `/api`)
- **CORS env var** — `CORS_ORIGINS` env var, comma-separated (default `*`)
- **Media library search** — text filter by filename in MediaLibrary.tsx
- **Async narration with progress** — TTS generation runs in background thread, frontend polls showing "Narration 3/12"
- **Mugshot card** — `mugshot_card(photo_path, charges, sentence, output)` in graphics.py with photo right, charges left layout
- **Quote card color variants** — `accent` parameter on `quote_card()`: red (threats), teal (info), gold (victim)
- **Storyboard parser bible code support** — recognizes `[CODE]` and `[CODE: qualifier]` bracket syntax in addition to backtick notation
- `state_path` property on ProductionConfig
- `GET /api/production/narration/status` endpoint for progress polling
- ROADMAP.md with prioritized improvement plan (v0.4.0 → v0.6.0+)
- Screenshot infrastructure: `docs/screenshots/`, capture checklist, README integration
- Design spec and implementation plan for production foundation
- 19 new tests (128 total)

### Changed

- Production functions accept optional `state` parameter for progress tracking
- API production endpoints return `{status, succeeded, failed, skipped, count}` instead of `{status, generated, count}`
- API routes use `Depends(get_session)` instead of cross-module global imports

### Removed

- Module-level globals in `api/routes/projects.py` (`_current_storyboard`, `_current_project_dir`, `_assignments_path`)
- Silent `except FFmpegError: pass` in production functions

## [0.3.0] - 2026-03-16

### Added

- **30+ xfade transitions** — fade, dissolve, wipeleft, slideright, radial, circlecrop, pixelize, etc.
- **9 new color grade presets** — noir, sepia, cold_blue, vintage, bleach_bypass, night_vision, golden_hour, surveillance, vhs (12 total)
- **Text overlay** via FFmpeg `drawtext` filter — position, timed display, background box
- **Speed ramping** — 0.25x to 4x+ with chained `atempo` for extreme values
- **Picture-in-picture** compositing with configurable size and position
- **4 new Ken Burns effects** — pan_right, pan_up, pan_down, zoom_in_pan_right (7 total)
- **Transition-aware assembly** — `concat_with_transitions` chains xfade between all segments
- CLI: `bee-video effects` command — apply color/speed/text/fade in one pass
- CLI: `bee-video transition` command — xfade between two clips
- CLI: `bee-video list-effects` command — show all available presets, transitions, effects
- CLI: `bee-video assemble --transition` flag for transitions during final assembly
- API: `GET /api/production/effects` endpoint — list all available effects
- API: `POST /api/production/assemble` now accepts `transition` and `transition_duration` params
- 26 new tests for effects, transitions, and filter construction (113 total)
- Comprehensive README with usage docs, Python API examples, and preset reference tables

## [0.2.0] - 2026-03-16

### Added

- **Storyboard-first web editor** — React + TypeScript + Tailwind + Zustand frontend
- FastAPI backend with project loading, media management, and production endpoints
- Storyboard parser for shot-by-shot markdown format with visual/audio/overlay/music layers
- NLE-style timeline UI with segment cards grouped by section
- Media library with drag-and-drop assignment to storyboard layers
- Video preview panel with HTML5 player
- Media download support (yt-dlp integration via API)
- Production bar for one-click narration/graphics generation and assembly
- `bee-video serve` command to launch web editor
- setup.sh for Python + Node.js dependency installation
- dev.sh and start.sh helper scripts

## [0.1.0] - 2026-03-16

### Added

- Initial release — CLI-based video production from assembly guide markdown
- Assembly guide parser (sections, segments, timecodes, pre-production, trim notes, post checklist)
- **FFmpeg processors**: trim, normalize_format, image_to_video (Ken Burns: zoom_in, zoom_out, pan_left), overlay_png, color_grade (dark_crime, warm_victim, bodycam), add_fade, waveform_video, mix_audio, normalize_loudness, concat_segments
- **Pillow graphics**: lower_third, timeline_marker, quote_card, financial_card, text_overlay, black_frame
- **TTS engines**: edge (free cloud), kokoro (free local), openai (paid API)
- Production pipeline: parse → init → graphics → narration → trim → assemble
- Production state tracking (JSON persistence)
- Streamlit dashboard adapter
- 87 tests across parser, models, graphics, and production modules
