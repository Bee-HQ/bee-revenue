# Changelog

All notable changes to bee-video-editor are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.10.0] — 2026-03-22

### Changed
- **JSON project format replaces OTIO** — new `BeeProject`/`BeeSegment` TypeScript types with times in seconds, `src` inline on entries, no `assigned_media` map, transitions as typed objects. Markdown parser (`storyboard-parser.ts`) converts `bee-video:project`/`bee-video:segment` code blocks → `BeeProject` JSON. Timeline adapter, Zustand store, BeeComposition, and all components migrated. Legacy `Storyboard`/`Segment` type aliases removed.
- **Node.js Express backend replaces Python FastAPI** — new Express server in `web/server/` handles all web editor routes (project state, media serving, segment editing, Remotion render). Shared types and parser extracted to `web/shared/`. ProjectStore manages `.bee-project.json` directly (no Python bridge). Python backend remains for CLI only. 25 routes implemented + 5 Remotion stubs + 501 stubs for TTS/stock/matcher (future steps). OTIO export replaced with JSON export.
- **Timeline: DesignCombo → react-timeline-editor** — replaced canvas/Fabric.js-based DesignCombo SDK (4 packages) with DOM-based `@xzdarcy/react-timeline-editor`. Eliminates canvas crashes, invisible tracks, class registry bugs. Bundle size reduced from 930KB to 683KB (-27%).
- **Timeline adapter rewritten** — outputs `TimelineRow[]` in seconds (was `DCState` in ms). Dynamic tracks: only rows with content shown. Action IDs use `{segmentId}-{type}-{layerIndex}` format.
- **Undo/redo unified** — replaced per-assignment `HistoryEntry` stack with full timeline snapshot history (max 50 entries). Single Ctrl+Z/Shift+Z handles all timeline edits.
- **Keyboard shortcuts** — rewired from DesignCombo event dispatch to direct Zustand store calls.

### Added
- **Drag-drop media to timeline** — internal drag from Media Library, external file drop from Finder (auto-uploads), Cmd+V paste file paths
- **Custom action renderer** — colored clips per track type (amber=video, green=narration, teal=audio, purple=music, pink=overlay)
- **Upload route extended** — `POST /api/media/upload` now returns `type` and `duration` fields

### Added
- **Playwright e2e test infrastructure** — 11 end-to-end tests (Chromium) covering project load, editor layout, toolbar, timeline, sidebar tabs, keyboard shortcuts, export menu, zoom, console errors
- **E2E tests in CI** — GitHub Actions job with FFmpeg, Node, Playwright browsers; uploads playwright-report on failure
- **Dark/light theme toggle** — CSS custom properties for all editor colors, Sun/Moon button in header, persisted to localStorage
- **Resizable preview/timeline split** — drag handle between Remotion Player and timeline, height clamped 120px–60vh, persisted to localStorage
- **UI polish** — lucide-react icons for toolbar/sidebar/menus/media library, toolbar visual hierarchy with accent-tinted primary actions and grouped sections, larger color grade swatches with grid layout and labels, custom dark-themed range sliders and select dropdowns
- **WebSocket progress tests** — 5 tests for `/ws/progress` (narration progress, produce pipeline, unknown action, missing project, missing storyboard path)

### Added
- **14 Remotion animated components** — all storyboard visual/overlay types now render as animated React components:
  - QuoteCard (animated quote with accent bar), FinancialCard (counting dollar amount), TextOverlay (typewriter), TimelineMarker (slide-in date stamp)
  - TransitionRenderer with overlap (cross-dissolve) and fade modes, UI toggle persisted to localStorage
  - TextChat — iMessage/Android/Generic chat bubbles with typing/instant/scroll animations
  - EvidenceBoard — conspiracy wall with pinned cards and animated red string connections
  - AnimatedMap — MapLibre GL with satellite/dark/tactical tiles, fly-to/orbit/route/waypoint camera animations
  - SocialPost — Facebook/Instagram/Twitter with slide/reveal/phone frame animations
  - PictureInPicture — corner PiP, side-by-side, top-bottom layouts with any source combo
  - AudioVisualization — animated bars/waveform/pulse for 911 calls with configurable background
- **BeeComposition refactored** — overlay registry dispatch, transition-aware segment positioning, extracted PlaceholderFrame + SafeMedia
- **Timeline cursor sync** — clicking ruler seeks Remotion, playback moves timeline cursor
- **MM:SS timecode ruler** — `getScaleRender` shows minutes:seconds instead of raw numbers
- **Scroll-to-zoom** — Ctrl+scroll zooms timeline in/out
- **Audio waveforms on timeline** — Web Audio API decoding with placeholder patterns for missing files
- **Timeline multi-select** — Shift+click clips, blue outline highlight
- **Copy/paste/duplicate clips** — Ctrl+C/V/D keyboard shortcuts
- **Delete clips** — Delete/Backspace key
- **Right-click context menu** — Split, Duplicate, Copy, Paste, Delete on timeline clips
- **Track lock/mute/hide** — per-track controls with visual indicators

### Fixed
- **Remotion PlayerEmitter.addEventListener crash** — graceful fallback to polling when addEventListener is unavailable or throws internally
- **9 bugs from deep code audit** — various fixes across timeline sync, state management, and edge cases
- **7 timeline integration bugs** — track sync, click handler race conditions, drag-drop state issues after react-timeline-editor migration

### Removed
- **Python web server** — `bee-video serve` command, FastAPI backend (`src/bee_video_editor/api/`), `web` optional deps (fastapi, uvicorn, python-multipart). Web editor is now 100% Node.js.
- `@designcombo/state`, `@designcombo/timeline`, `@designcombo/types`, `@designcombo/events`
- `TimelineRuler.tsx` (library has built-in ruler)
- `SPIKE-NOTES.md` (stale DesignCombo API docs)

## [0.9.0] — 2026-03-20

### Added
- **NLE multi-track timeline** — DesignCombo SDK canvas with V1/A1/A2/A3/OV1 tracks, clips as colored blocks proportional to duration
- **Remotion Player** — composited video preview with real-time overlay rendering
- **Remotion overlay components** — animated LowerThird (slide-in), CaptionOverlay (karaoke/phrase word highlighting), color grades as CSS filters, timeline markers
- **Remotion-based export** — `POST /render-remotion` endpoint, Node.js render script for pixel-perfect MP4 with all overlays
- **Clip property panel** — tabbed right sidebar (Media/Props/AI) with color grade picker, volume slider, trim inputs, transition picker
- **Timeline interactions** — drag/resize clips with backend sync, split at playhead (S key), zoom slider, snap toggle
- **Playback controls** — JKL shuttle, playback speed (0.5-2x), frame step, Space/Arrow keyboard shortcuts
- **AI panel** — B-Roll stock search from narration, caption generation, auto color grade suggestions
- **Timeline adapter** — bidirectional Storyboard ↔ DesignCombo state conversion (24 vitest tests)
- **Time utilities** — timecode ↔ frames ↔ milliseconds conversions
- **Production dropdown** — consolidated pipeline actions into single dropdown menu

### Changed
- Layout restructured: sidebars kept, center replaced with Remotion Player + DesignCombo timeline
- Right sidebar now tabbed: Media / Properties / AI
- Undo/redo dispatches to timeline history instead of per-assignment Zustand stack

### Removed
- StoryboardTimeline, VideoPlayer, ProductionBar, SegmentCard (replaced by NLE timeline)
- TransitionPicker, ColorGradePicker, VolumeSlider, TrimControls (replaced by ClipProperties panel)

### Dependencies
- Added: @xzdarcy/react-timeline-editor, @xzdarcy/timeline-engine, remotion, @remotion/player, @remotion/cli, @remotion/bundler, @remotion/renderer, vitest

## [0.8.0] — 2026-03-19

### Added

- **Multi-layer compositor** — per-segment composition: visual → trim → normalize → color grade → overlay → audio mix → muxed output
- **Auto-assign media matcher** — keyword + src matching to auto-assign media files to segments
- **Batch media acquisition** — orchestrated stock search + download for all storyboard queries
- **Scene detection** — FFmpeg-based shot boundary detection with `bee-video scenes` CLI command
- **Multi-provider stock search** — unified Pexels + Pixabay search with query extraction
- **AI video providers** — Kling + Veo stubs alongside existing FFmpeg stub
- **Satellite maps** — `map_satellite()` + `map_hybrid()` using Esri World Imagery tiles
- **Toast notifications** — success/error/info/warning with auto-dismiss
- **Stock search panel** — Pexels search in MediaLibrary sidebar
- **Keyboard shortcuts panel** — press `?` to show all shortcuts
- **Loading skeletons** — skeleton cards during initial load
- **Per-entry download buttons** — `download_url`/`pexels_url` fields + inline download
- **Production bar buttons** — Captions, Rough Cut, Preflight, Composite, Auto-Assign, Acquire

### Changed

- Compositor integrated into `run_full_pipeline` as Step 6
- `assemble_final()` prefers composited segments over raw normalized

### Security

- SSRF validation with DNS resolution on all download paths
- YouTube URL validation via `urlparse` hostname check
- Path sanitization for segment IDs in download paths
- FFmpeg drawtext escaping hardened
- Centralized download validation across all paths

## [0.7.0] — 2026-03-19

### Added

- **OTIO project format** — new storyboard format with JSON code blocks, bidirectional OTIO conversion
- **Pydantic models** — `ProjectConfig`, `SegmentConfig`, `VisualEntry`, `AudioEntry`, `OverlayEntry`
- **Markdown parser/writer** — reads/writes v2 format with round-trip fidelity
- **OTIO converters** — `to_otio()`, `from_otio()`, `clean_otio()` for NLE interchange
- **Migration converter** — `old_to_new()` converts old table-based storyboards
- **CLI commands** — `bee-video import-md`, `bee-video export`
- **Export menu** — markdown + clean OTIO export from web UI
- **Inline segment editing** — transition picker, color grade selector, volume sliders, draggable trim handles
- **`PUT /projects/update-segment`** — endpoint for all property changes

### Changed

- **SessionStore rewritten** — OTIO persistence, `ParsedStoryboard` as runtime model
- **All services migrated** — graphics, narration, trim, captions, preflight, previews, rough cut accept `ParsedStoryboard`
- **All API routes migrated** — `parsed_to_schema()` maintains backward-compatible response shape
- **LoadProject accepts `.otio`** files
- `pydantic` and `opentimelineio` moved to core dependencies
- `REAL_AUDIO` enum value normalized (space → underscore)
- `GENERATED` visual type added

### Removed

- Assembly guide parser (`parsers/assembly_guide.py`)
- Old `Project`/`Segment` model (`models.py`)
- Old OTIO exporter (`exporters/otio_export.py`)
- Streamlit dashboard adapter
- Sidecar files deprecated (assignments.json, voice.json, segment-order.json)

## [0.6.0] - 2026-03-17

### Added

- **Batch graphics from config** — `bee-video graphics-batch config.json` generates all graphics (lower thirds, quote cards, financial cards, timeline markers, text overlays, mugshot cards, news montages, black frames) from a single JSON config file with idempotent numbered outputs
- **TTS voice lock** — `bee-video voice-lock elevenlabs --voice Daniel` persists TTS settings per project in `.bee-video/voice.json`; narration commands use locked voice unless explicitly overridden via `--tts`/`--voice` flags
- **Rough cut export** — `bee-video rough-cut` exports a fast 720p concatenation (no color grading, no transitions) for structure review before investing in full assembly

### Fixed

- **Security: category path traversal** — upload and yt-dlp endpoints now reject unknown media categories (previously `category=../../evil` could write files outside the project directory)
- **Security: upload filename sanitization** — filenames with path traversal (`../../etc/passwd`), dots (`.`, `..`), or hidden prefixes are rejected or sanitized
- **Security: script execution path validation** — `run-script` endpoint validates script is within the project directory tree
- **Preview reads from session memory** — preview endpoint now uses in-memory `seg.assigned_media` instead of reading stale `assignments.json` from disk
- **Undo/redo backend sync** — undo of fresh assignments now calls backend with empty string to remove from `assignments.json`; undo/redo failures no longer corrupt history stacks
- **Narration codepath dedup** — REST narration endpoint now delegates to `generate_narration_for_project` service (same as WebSocket), eliminating duplicated logic
- **`POST /produce` forwards TTS engine** — HTTP produce endpoint now passes `tts_engine`/`tts_voice` to `ProductionConfig` (previously hardcoded defaults)
- **`duration_seconds` precision** — `SegmentSchema.duration_seconds` changed from `int` to `float`
- **Download tasks bounded** — completed download tasks pruned to last 20 entries
- **Removed dead code** — deleted unused `PreviewPanel.tsx`, removed deprecated `selectedSegmentId` store shim

### Added (Tests)

- 72 API smoke tests via FastAPI TestClient covering all route groups, security boundaries, batch graphics, voice lock, rough cut, and edge cases
- 9 batch graphics tests (config parsing + generation orchestration)
- 9 voice lock tests (save/load/corrupt/integration with ProductionConfig)
- 4 rough cut tests (media collection, missing files, 720p normalization)

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
