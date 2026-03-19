# Roadmap

Prioritized improvements for bee-video-editor, organized by effort and impact.

> **This is the single source of truth** for what needs to be built. Formula alignment gaps, code-level issues, and scalability concerns are all tracked here — not scattered across CLAUDE.md, the formula's Appendix C, or other docs.

---

## v0.3.1 — Quick Wins

Small, targeted fixes that improve daily usage.

### Code Quality
- [x] **Surface FFmpeg errors** — ProductionResult returns succeeded/failed/skipped (shipped in production foundation)
- [x] **Fix version in server.py** — bumped to 0.3.1
- [x] **Input validation on API routes** — validate tts_engine, transition names, project_dir existence
- [x] **Update segment status tracking** — track() context manager on ProductionState (shipped in production foundation)

### Web UI
- [x] **Configurable API base URL** — `import.meta.env.VITE_API_BASE || '/api'`
- [x] **Media library search** — text filter by filename in MediaLibrary.tsx
- [x] **CORS env var** — `CORS_ORIGINS` env var, comma-separated, default `*`
- [x] **TTS progress** — async narration with background thread, frontend polls showing "Narration 3/12"

### Graphics (formula alignment)
- [x] **Mugshot card** — `mugshot_card(photo_path, charges, sentence, output)` in graphics.py with photo right, charges left
- [x] **Quote card completion** — `quote_card()` supports `accent` param: red (threats), teal (info), gold (victim)

---

## v0.4.0 — Core Improvements

Features that meaningfully change the editing workflow.

### Editor
- [x] **Persistent session state** — auto-reload last project on restart via `~/.bee-video/last-session.json`
- [x] **Undo/redo** — Zustand history stack for media assignments, Ctrl+Z / Ctrl+Shift+Z, undo/redo buttons in ProductionBar
- [x] **Segment reordering** — HTML5 drag-drop in segment list, persisted to `.bee-video/segment-order.json`
- [x] **Batch media assignment** — shift-click multi-select, drop assigns to all selected segments

### Architecture
- [x] **Unify data models** — `assembly_guide_to_storyboard()` converter, `_ensure_storyboard()` in production service, both input formats work
- [x] **Parser resilience** — whitespace normalization, missing section handling, malformed row skipping in both parsers
- [x] **Parse bible visual codes** — parser recognizes `[CODE]` and `[CODE: qualifier]` bracket syntax (shipped in v0.3.1)

### Pipeline
- [x] **Asset preflight command** — `bee-video preflight` scans storyboard against project files, reports found/missing/needs-check, writes JSON manifest
- [x] **ASS caption generation** — `bee-video captions` generates styled ASS with karaoke (word-by-word) and phrase modes via pysubs2. Burns into final video via FFmpeg `ass` filter.
- [x] **Asset generation time estimate** — formula checklist updated from 3-4 hours to 6-8 hours

### Graphics (formula alignment)
- [x] **Text chat recreation** — `text_chat()` with iMessage/SMS/generic platforms, highlight support
- [x] **Social media post mockup** — `social_post()` for Facebook/Instagram/Twitter/Snapchat
- [x] **News headline montage** — `news_montage()` stacked rotated headline cards
- [x] **Evidence board** — `evidence_board()` red-string corkboard with circle/grid layout
- [x] **Lottie animated overlays (lower-third POC)** — `--animated` CLI flag produces WebM overlays with draw-in/slide/fade animation via Lottie + Cairo + FFmpeg VP9. Proof of concept for `[LOWER-THIRD]`; other overlays remain static PNGs for now

---

## v0.5.0 — Big Features

Architectural work that unlocks new capabilities.

### Production
- [x] **One-command production** — `bee-video produce` runs init → graphics → captions → narration → trim → assemble with auto-skip and progress
- [x] **Preview generation** — 360p thumbnails per segment from assigned media, per-segment + batch, cached in `output/previews/`
- [x] **Parallel narration processing** — `--workers N` flag for concurrent TTS via ThreadPoolExecutor (default: sequential)

### Real-time
- [x] **WebSocket progress** — real-time progress via `/ws/progress` for narration and produce pipeline (replaces polling)

### Graphics (formula alignment)
- [x] **Flow diagram** — `flow_diagram()` with directional arrows, red/teal colors, arrowheads, auto-layout
- [x] **Timeline sequence** — `timeline_sequence()` horizontal timeline with active/current/future nodes, red/grey line segments, date+label per node

### Interop
- [x] **OTIO timeline export** — `bee-video export` compiles storyboard to OTIO with visual code metadata, section markers, media references. NLE interchange for Resolve/Premiere.

### Maps
- [x] **Map generation** — `bee-video map` generates `[MAP-FLAT]`, `[MAP-TACTICAL]`, `[MAP-PULSE]`, `[MAP-ROUTE]` from lat/lng via py-staticmaps + dark grade + vignette post-processing

### Security
- [ ] **Auth option** — optional `--auth` flag with token-based auth for non-local deployments (deferred — low priority, tool is designed for local use)

---

## v0.6.0+ — Scale

Features needed when producing 2+ videos/month consistently.

### Pipeline Automation
- [x] **Stock footage API** — `bee-video fetch-stock --query "aerial farm dusk" -n 3` searches Pexels, downloads HD clips to stock/ dir. Needs `PEXELS_API_KEY` env var
- [x] **AI video generation infra** — `bee-video generate-clip --prompt "..." --provider stub` with pluggable provider interface. Ships with stub provider; real providers auto-register on import
- [x] **Multi-provider stock search** — unified Pexels + Pixabay search with query extraction
- [x] **Batch media acquisition** — `Acquire` button searches + downloads all storyboard stock queries in one shot

### Video Generation Providers

Wire up real AI providers for `generate-clip`. The infra is built — stubs exist for kling and veo.

- [ ] **Kling** — wire up real Kling API (stub exists, needs `KLING_API_KEY`)
- [ ] **Veo** — wire up real Veo API (stub exists, needs Google Cloud credentials)
- [ ] **Runway Gen-4** — text-to-video + image-to-video. Add as `video-gen-runway = ["runwayml"]` extra in pyproject.toml
- [x] **Stub → FFmpeg placeholder** — stub provider generates a real playable MP4 (black frame + drawtext) via FFmpeg

### Pipeline Automation (continued)
- [ ] **LLM screenplay → storyboard** — accept a case-research doc + formula, generate a v2 storyboard draft. Human review required but saves 2-3 hours per video
- [x] **Batch graphics from config** — `bee-video graphics-batch config.json` generates all graphics from a single JSON config file

### Quality
- [x] **Stock footage library** — SQLite tracker at `~/.bee-video/stock-library.db`. `bee-video stock-list` / `stock-check`. Auto-registers clips on `fetch-stock`
- [x] **TTS voice lock** — `bee-video voice-lock elevenlabs --voice Daniel` persists TTS settings per project; narration uses locked voice unless explicitly overridden
- [x] **Rough cut review** — `bee-video rough-cut` exports a fast 720p concatenation for structure review before full assembly

### Infrastructure
- [ ] **FOIA pipeline tracker** — structured template for tracking FOIA requests per case (filed date, jurisdiction, expected response, received date, status)
- [x] **Naming convention enforcement** — `bee-video validate` checks project structure and filename conventions

---

## v0.7.0 — OTIO Project Format (complete)

- [x] **OTIO project format** — v2 storyboard with JSON blocks, bidirectional OTIO conversion
- [x] **Pydantic models** — `ProjectConfig`, `SegmentConfig`, `VisualEntry`, `AudioEntry`, `OverlayEntry`
- [x] **Markdown parser/writer** — round-trip fidelity
- [x] **OTIO converters** — `to_otio()`, `from_otio()`, `clean_otio()`
- [x] **Migration converter** — `old_to_new()` for old table-based storyboards
- [x] **CLI** — `bee-video import-md`, `bee-video export`
- [x] **Export menu** — markdown + clean OTIO from web UI
- [x] **Inline segment editing** — transition picker, color grade, volume, trim handles
- [x] **SessionStore rewritten** — OTIO persistence, all services use `ParsedStoryboard`
- [x] **Sidecar files removed** — assignments.json, voice.json, segment-order.json → OTIO

## v0.8.0 — Compositor + Search (complete)

- [x] **Multi-layer compositor** — per-segment visual → trim → normalize → color → overlay → audio → mux
- [x] **Auto-assign matcher** — keyword + src matching
- [x] **Batch acquisition** — search + download all stock from storyboard queries
- [x] **Scene detection** — FFmpeg shot boundary detection, `bee-video scenes`
- [x] **Multi-provider stock search** — Pexels + Pixabay unified
- [x] **AI video providers** — Kling + Veo stubs
- [x] **Satellite maps** — Esri World Imagery tiles
- [x] **Toast notifications** — auto-dismiss success/error/info/warning
- [x] **Stock search panel** — Pexels search in MediaLibrary sidebar
- [x] **Keyboard shortcuts panel** — `?` to show all shortcuts
- [x] **Loading skeletons** — during initial load
- [x] **Per-entry download buttons** — `download_url`/`pexels_url` metadata
- [x] **Production bar** — Captions, Rough Cut, Preflight, Composite, Auto-Assign, Acquire buttons
- [x] **Security hardening** — SSRF validation, YouTube URL check, path sanitization, drawtext escaping

---

## Polish (any version)

UX refinements to add when touching nearby code.

- [ ] Responsive layout — collapse sidebars to tabs on screens < 1024px
- [ ] Dark/light theme toggle
- [ ] Retry logic in production.py for transient FFmpeg failures
- [ ] Configurable codec/CRF in FFmpeg processor (currently hardcoded libx264 CRF 23)

### Code cleanup (from v0.5.0 review)

- [x] **Unbounded `_download_tasks` dict** — prune completed tasks to last 20 on new task creation, tracked via `finished_at` timestamp
- [x] **`_narration_task` global state** — scoped to project_dir so stale state from a different project is ignored; REST path now delegates to service layer (same as WS)
- [x] **Remove dead `PreviewPanel` component** — deleted `PreviewPanel.tsx`
- [x] **Deduplicate narration codepaths** — REST `POST /narration` now uses `generate_narration_for_project` from the service layer, same as the WebSocket handler
- [x] **Remove `selectedSegmentId` shim** — migrated `VideoPlayer` and `StoryboardTimeline` to `selectedSegmentIds[0]`, removed shim from store
- [x] **`POST /produce` ignores TTS engine** — added `tts_engine` and `tts_voice` params, forwarded to `ProductionConfig`
- [x] **`duration_seconds` precision loss** — changed `SegmentSchema.duration_seconds` from `int` to `float`
- [x] **Undo/redo silently swallows API errors** — API call now happens before stack mutation; on failure, stacks stay untouched and error is logged
- [x] **API smoke tests** — `test_api.py` with 42 FastAPI TestClient tests covering project load, assign/unassign, reorder, media list, upload path traversal, script execution, category validation, symlink traversal, preview session reads, task pruning

### Future API test coverage (from v0.5.0 review)

Untested endpoints and edge cases to add when touching nearby code.

**WebSocket progress (zero coverage)**
- [ ] `ws/progress` narration action — connect, send `{action: "narration"}`, verify step messages stream back and end with `{step: "complete"}`
- [ ] `ws/progress` produce action — same pattern, verify step-by-step pipeline messages
- [ ] `ws/progress` unknown action — verify error response, clean disconnect
- [ ] `ws/progress` malformed JSON — verify error handling, no server crash

**Production endpoints (partial coverage)**
- [ ] `POST /graphics` with storyboard containing lower-thirds — verify PNGs generated, count matches
- [ ] `POST /graphics` with no overlays — verify ok with count=0
- [ ] `POST /captions` — verify ASS file generated, segment count returned
- [ ] `POST /captions` with no NAR segments — verify count=0 response
- [ ] `GET /preflight` — verify report structure, found/missing counts against known project layout
- [ ] `POST /export/otio` — verify OTIO file created, segment count returned
- [ ] `POST /narration` then `GET /narration/status` — verify running=true immediately, then poll to completion (needs mock TTS)
- [ ] Concurrent `POST /narration` while one is running — verify 409

**State integrity**
- [ ] Load project A, assign media, load project B — verify A's assignments don't leak into B
- [ ] Assign → reload same project — verify assignments restore from disk
- [ ] Multiple assign/unassign cycles on same key — verify assignments.json stays consistent (no duplicate keys, no orphan entries)
- [ ] Upload file with same name twice — verify overwrite behavior (currently silently overwrites)

**Media edge cases**
- [ ] Media list with files in nested subdirs — scanner uses `rglob`, verify deep files appear
- [ ] Serve file with special characters in path (spaces, unicode) — verify URL encoding roundtrips
- [ ] `POST /download/yt-dlp` with invalid category — verify 400 (matches upload validation)
- [ ] Download scripts listing — verify only .sh files in project tree returned, not arbitrary files
