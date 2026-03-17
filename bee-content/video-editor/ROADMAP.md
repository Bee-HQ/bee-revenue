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
- [ ] **Media library search** — text filter by filename in `MediaLibrary.tsx` (pure frontend)
- [x] **CORS env var** — `CORS_ORIGINS` env var, comma-separated, default `*`
- [ ] **TTS progress** — poll `/api/production/status` during narration, show count in button ("Narration 3/12")

### Graphics (formula alignment)
- [ ] **Mugshot card** — add `mugshot_card(photo_path, charges_list, output)` to `graphics.py`. Split layout: photo right, red charges left. Spec: visual-storyboard-bible.md `[MUGSHOT-CARD]`
- [ ] **Quote card completion** — verify `quote_card()` in `graphics.py` is fully implemented (may be stubbed). Should support teal accent for info quotes, red for threats, warm gold for victim quotes per the 4-color system

---

## v0.4.0 — Core Improvements

Features that meaningfully change the editing workflow.

### Editor
- [ ] **Persistent session state** — auto-reload last project on server start, replace module-level globals with `SessionStore` class, persist to `.bee-video/session.json`
- [ ] **Undo/redo** — Zustand history stack for media assignments, Ctrl+Z / Ctrl+Shift+Z
- [ ] **Segment reordering** — drag-and-drop in segment list, persist order in sidecar JSON
- [ ] **Batch media assignment** — multi-select segments (shift/ctrl click), assign one file to all

### Architecture
- [ ] **Unify data models** — make `Storyboard` the canonical model, add `assembly_guide_to_storyboard()` converter, deprecate direct `Project` usage in production service
- [ ] **Parser resilience** — normalize whitespace before parsing, expand test fixtures with malformed markdown
- [ ] **Parse bible visual codes** — parser should recognize `[CODE: qualifier]` tags and map them to asset requirements. This enables the preflight check (below)

### Pipeline
- [ ] **Asset preflight command** — `bee-video preflight <guide> -p ./proj` scans the assembly guide/storyboard, generates an asset manifest (segment → file path + status), reports what's missing before assembly. This is the #1 time-waster in production — finding missing assets mid-assembly
- [ ] **Asset generation time estimate** — current checklist says 3-4 hours, realistic is 6-8 hours. Update all time estimates to match reality

### Graphics (formula alignment)
- [ ] **Text chat recreation** — `text_chat(messages, platform, output)` for iMessage/SMS/Snapchat bubble UI. Spec: visual-storyboard-bible.md `[TEXT-CHAT]`
- [ ] **Social media post mockup** — `social_post(content, platform, output)` for Facebook/Instagram/Snapchat. Spec: `[SOCIAL-POST]`
- [ ] **News headline montage** — `news_montage(headlines, output)` stacked headlines sliding in. Spec: `[NEWS-MONTAGE]`
- [ ] **Evidence board** — `evidence_board(people, connections, output)` red-string corkboard style. Spec: `[EVIDENCE-BOARD]`

---

## v0.5.0 — Big Features

Architectural work that unlocks new capabilities.

### Production
- [ ] **One-command production** — `bee-video produce` runs full pipeline (init → graphics → narration → trim → assemble) with progress reporting
- [ ] **Preview generation** — low-res FFmpeg composite per segment, cached in `output/previews/`, "Generate Preview" button per segment card
- [ ] **Parallel segment processing** — process independent segments concurrently (currently sequential)

### Real-time
- [ ] **WebSocket progress** — real-time progress for TTS, FFmpeg, and assembly (replace polling)

### Graphics (formula alignment)
- [ ] **Flow diagram** — `flow_diagram(nodes, connections, output)` animated money/process flow. Spec: `[FLOW-DIAGRAM]`. Priority for financial crime cases (Murdaugh Forge scheme, etc.)
- [ ] **Animated timeline sequence** — `timeline_sequence(events, output)` horizontal timeline with cursor/nodes. Spec: `[TIMELINE-SEQUENCE]`. Priority for cases spanning 6+ months
- [ ] **Subtitle generation** — generate ASS/SRT from narration segments. Currently no subtitle support at all — high impact for accessibility and the formula's `[CAPTION-ANIMATED]` requirement

### Maps
- [ ] **Map generation** — integrate MapLibre or static maps API to generate `[MAP-FLAT]`, `[MAP-TACTICAL]`, `[MAP-PULSE]`, `[MAP-ROUTE]` from coordinates. Currently requires manual Google Earth Studio export. High effort but eliminates the most manual step in asset creation

### Security
- [ ] **Auth option** — optional `--auth` flag with token-based auth for non-local deployments

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
