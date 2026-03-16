# Changelog

All notable changes to bee-video-editor are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
