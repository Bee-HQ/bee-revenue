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
- [ ] **Stock footage API** — `bee-video fetch-stock --query "aerial farm dusk" --duration 10` hits Pexels API, downloads, renames per naming convention. Eliminates manual stock footage sourcing
- [ ] **LLM screenplay → assembly guide** — accept a case-research doc + formula, generate an assembly guide draft. Human review required but saves 2-3 hours per video
- [ ] **Batch graphics from config** — accept a JSON/YAML with all graphic specs (lower thirds, quote cards, financial cards, etc.) and generate all in one command. Currently requires one CLI call per graphic

### Quality
- [ ] **Stock footage library** — track which stock clips have been used across videos to avoid repetition. Tag by visual code, case, and usage count
- [ ] **TTS voice lock** — persist voice config per channel so narration stays consistent across videos
- [ ] **Rough cut review** — export low-quality 720p rough cut quickly (no color grading) for structure review before investing in final assembly

### Infrastructure
- [ ] **FOIA pipeline tracker** — not a bee-video feature per se, but the production pipeline stalls on footage acquisition. At minimum: a structured template for tracking FOIA requests per case (filed date, jurisdiction, expected response, received date, status)
- [ ] **Naming convention enforcement** — `bee-video validate` checks that project directories follow the naming convention defined in the formula's Phase 6.5

---

## Polish (any version)

UX refinements to add when touching nearby code.

- [ ] Keyboard shortcuts panel (`?` to show overlay with all shortcuts)
- [ ] Toast notifications (replace inline status strings in ProductionBar)
- [ ] Loading skeletons for segment list, media library, player during initial load
- [ ] Responsive layout — collapse sidebars to tabs on screens < 1024px
- [ ] Dark/light theme toggle
- [ ] Retry logic in production.py for transient FFmpeg failures
- [ ] Configurable codec/CRF in FFmpeg processor (currently hardcoded libx264 CRF 23)
