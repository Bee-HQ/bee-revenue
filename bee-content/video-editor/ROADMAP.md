# Roadmap

Prioritized improvements for bee-video-editor, organized by effort and impact.

## v0.3.1 — Quick Wins

Small, targeted fixes that improve daily usage.

- [ ] **Configurable API base URL** — replace hardcoded `/api` with `import.meta.env.VITE_API_BASE || '/api'` in `web/src/api/client.ts`
- [ ] **Fix version in server.py** — currently says 0.2.0, should match pyproject.toml
- [ ] **Input validation on API routes** — validate project_dir exists, tts_engine is valid, transition names exist
- [ ] **Surface FFmpeg errors** — stop silently swallowing `FFmpegError` in `services/production.py`, return `{succeeded, failed}` instead
- [ ] **Media library search** — text filter by filename in `MediaLibrary.tsx` (pure frontend)
- [ ] **CORS env var** — `CORS_ORIGINS` env var, default `*` in dev mode
- [ ] **TTS progress** — poll `/api/production/status` during narration, show count in button ("Narration 3/12")

## v0.4.0 — Core Improvements

Features that meaningfully change the editing workflow.

- [ ] **Persistent session state** — auto-reload last project on server start, replace module-level globals with `SessionStore` class, persist to `.bee-video/session.json`
- [ ] **Undo/redo** — Zustand history stack for media assignments, Ctrl+Z / Ctrl+Shift+Z
- [ ] **Segment reordering** — drag-and-drop in segment list, persist order in sidecar JSON
- [ ] **Batch media assignment** — multi-select segments (shift/ctrl click), assign one file to all
- [ ] **Parser resilience** — normalize whitespace before parsing, expand test fixtures with malformed markdown
- [ ] **Unify data models** — make `Storyboard` the canonical model, add `assembly_guide_to_storyboard()` converter, deprecate direct `Project` usage in production service

## v0.5.0 — Big Features

Architectural work that unlocks new capabilities.

- [ ] **Preview generation** — low-res FFmpeg composite per segment, cached in `output/previews/`, "Generate Preview" button per segment card
- [ ] **WebSocket progress** — real-time progress for TTS, FFmpeg, and assembly (replace polling)
- [ ] **One-command production** — `bee-video produce` runs full pipeline (init → graphics → narration → trim → assemble)
- [ ] **Auth option** — optional `--auth` flag with token-based auth for non-local deployments

## Polish (any version)

UX refinements to add when touching nearby code.

- [ ] Keyboard shortcuts panel (`?` to show overlay with all shortcuts)
- [ ] Toast notifications (replace inline status strings in ProductionBar)
- [ ] Loading skeletons for segment list, media library, player during initial load
- [ ] Responsive layout — collapse sidebars to tabs on screens < 1024px
- [ ] Dark/light theme toggle
