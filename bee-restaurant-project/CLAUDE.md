# CLAUDE.md — AR Smart Menu

## Project Overview

WebAR restaurant menu — customers scan a QR code, browse 3D food models, and view them in AR on their table. Progressive enhancement: 3D viewer (always works) → native AR → MindAR image tracking.

**Status:** v0.1.0 (demo)
**Branch:** `bee/restaurant-ar-demo`
**Stack:** Three.js (v0.160.0), MindAR.js (v1.2.5), Vite, vanilla JS

## Commands

```bash
npm run dev        # Dev server (exposes to local network for mobile testing)
npm run build      # Production build -> dist/
npm run preview    # Preview production build
npm test           # Run all tests (34 tests, 5 files)
npm run test:watch # Watch mode
```

## Architecture

Three-layer progressive AR — each layer works independently:

| Layer | Module | Tech | Camera? |
|-------|--------|------|---------|
| 1. 3D Viewer | `src/viewer/` | Three.js + OrbitControls | No |
| 2. Native AR | `src/native-ar/` | Quick Look (iOS) / Scene Viewer (Android) | OS-managed |
| 3. Image Tracking | `src/ar/` | MindAR.js (code-split, dynamic import) | Yes |

**State machine** (`src/utils/state.js`): `LOADING → VIEWING → SCANNING → TRACKING → STICKY` (+ `NATIVE_AR`)

**Config-driven**: Adding a dish = JSON entry in `menu.json` + GLB model in `public/models/`. No code changes.

## Key Files

- `src/main.js` — Entry point, orchestrates all layers
- `menu.json` — Restaurant config + menu items (name, price, model paths, transforms)
- `src/utils/device.js` — In-app browser detection, feature detection (canMindAR, canNativeAR)
- `src/viewer/scene.js` — Three.js scene with RoomEnvironment PBR lighting
- `src/viewer/model-loader.js` — GLB loading with Draco, caching, preloading
- `src/ar/mind-ar.js` — MindAR session (dynamically imported to keep bundle small)
- `src/ar/sticky-mode.js` — Holds model position when AR target lost, auto-pauses after 10s

## Target Market

Indian restaurants. ~60% Android (budget: Samsung A, Redmi Note), ~40% iPhone.

**Optimization constraints:**
- Models < 2MB (Draco + WebP textures + 512px cap)
- Pixel ratio capped at 2x
- MindAR code-split (TensorFlow.js ~2MB only loads on demand)
- Lazy model loading (current item only, preload next/prev)

## Known Risks

- **MindAR iOS 17+ crash** (issue #478) — Layer 3 is feature-gated on iOS
- **In-app browsers** block camera — detected, shows "Open in Safari/Chrome"
- **WebXR** has zero iOS Safari support — that's why we use native AR (Quick Look) as Layer 2

## Test Patterns

- Pure logic is unit tested (state machine, device detection, config validation, sticky mode, native AR URLs)
- Three.js rendering and MindAR tracking are verified visually on real devices
- Tests use `vitest` with `node` environment; native-ar tests use `jsdom` for `window.location`

## Current Limitations (v0.1.0)

- Placeholder 3D models (DamagedHelmet) — need real food GLBs from Sketchfab
- Placeholder USDZ files — need conversion via Reality Converter for iOS native AR
- Placeholder .mind target — need to compile a real menu design
- Not yet deployed to Vercel
- No CMS, analytics, or multi-restaurant support (architecture supports it)

## Docs

- **Design spec:** `docs/superpowers/specs/2026-03-17-ar-smart-menu-design.md`
- **Implementation plan:** `docs/superpowers/plans/2026-03-17-ar-smart-menu.md`
- **WebAR research:** `research/webar-menu-deep-dive.md`
