# AR Smart Menu — Design Spec

**Date:** 2026-03-17
**Status:** Approved
**Branch:** `bee/restaurant-ar-demo`

---

## Goal

Build a WebAR restaurant menu that lets dine-in customers view 3D food models by scanning a QR code on a physical menu. Demo-quality first, architected for production.

**Target market:** Indian restaurants. Device mix is ~60% Android (budget to mid-range), ~40% iPhone.

---

## Approach: Progressive AR

Three layers in one app. Each layer works independently. Higher layers enhance but never gate the experience.

| Layer | What | Tech | Camera? | Works On |
|-------|------|------|---------|----------|
| **1. 3D Viewer** | Interactive model — rotate, zoom, pinch. Menu carousel with item info. | Three.js + GLTFLoader | No | Everything |
| **2. Native AR** | "View in AR" button → OS places food on table | Quick Look (iOS) / Scene Viewer (Android) | Yes (OS-managed) | Most modern phones |
| **3. Image Tracking** | "Scan Menu" → camera recognizes menu, food appears anchored | MindAR.js + Three.js | Yes | Android (reliable), iOS (gated) |

### Why progressive, not AR-first

- MindAR has an open crash bug on iOS 17+ with Three.js (issue #478)
- WebXR surface tracking has zero iOS Safari support
- In-app browsers (Instagram, Facebook, Twitter) block camera on iOS
- Budget Android phones may struggle with camera + ML tracking + 3D rendering simultaneously
- When MindAR and the WebAR ecosystem mature, Layer 3 can become the default landing

---

## User Flow

```
Physical Menu (QR code)
    → Mobile browser opens (HTTPS)
    → Loading screen (restaurant branding + progress bar)
    → Layer 1: 3D Viewer (default landing)
        - Swipe left/right to browse menu items
        - Item name, price, description shown below model
        - Rotate/zoom/pinch the 3D model
        → Tap "View in AR" → Layer 2: Native AR (OS handles placement)
        → Tap "Scan Menu" → Layer 3: MindAR image tracking
            - Camera activates
            - Point at menu → food appears anchored
            - Bottom HUD: item name + price, swipe dots to browse
            - Sticky mode: model holds position when target lost
            - Feature-detected: button hidden if unsupported
```

### Edge Cases

- **In-app browser detected:** Show "Open in Safari/Chrome" with copy-link button
- **Camera denied:** Stay on Layer 1 (3D viewer). Show message explaining how to enable.
- **MindAR crash/fail:** Catch error, fall back to Layer 1. Hide "Scan Menu" button.
- **Slow connection:** Lazy load models. Show skeleton/placeholder until ready.
- **Target lost (Layer 3):** Model stays at last known position (sticky mode). Subtle visual indicator. Re-detecting menu snaps model back.

---

## System Architecture

### Client (Mobile Browser)

**AR Engine Layer**
- MindAR.js v1.2.5 — image tracking with compiled `.mind` target files
- TensorFlow.js (MindAR dependency) — GPU-accelerated feature detection
- Only loaded when Layer 3 is activated (code-split)

**3D Rendering Layer**
- Three.js (latest stable, v0.160.0+)
- GLTFLoader + DRACOLoader for compressed GLB models
- RoomEnvironment for PBR lighting (no external HDR download)
- Warm directional key light + ambient fill for restaurant ambiance
- Renderer config: alpha=true, ACES filmic tone mapping, pixel ratio capped at 2x

**UI Layer (HUD Overlay)**
- Vanilla JS — no framework
- Swipe navigation (touch events) to cycle menu items
- Bottom bar: item name, price, description
- Dot indicators for menu position
- Loading state with progress bar
- "View in AR" / "Scan Menu" action buttons

**State Machine**
```
LOADING     → models + .mind file buffering
VIEWING     → Layer 1: 3D viewer active
NATIVE_AR   → Layer 2: handed off to Quick Look / Scene Viewer
SCANNING    → Layer 3: camera active, searching for target
TRACKING    → Layer 3: target found, model anchored
STICKY      → Layer 3: target lost, model holds last position
```

### Server / Infrastructure

**Vercel (Static Host)**
- HTML/JS/CSS bundle (Vite build)
- Menu config JSON per restaurant
- `.mind` target files
- HTTPS auto-configured

**Cloudflare R2 (CDN)**
- `.glb` models (target: <2MB each, Draco compressed, 512px textures)
- `.usdz` models (iOS native AR)
- Environment maps (if needed beyond RoomEnvironment)
- Thumbnail images for loading placeholders

**Menu Configuration (JSON)**
```json
{
  "restaurant": {
    "name": "Demo Pizza Co",
    "slug": "demo-pizza",
    "branding": {
      "logo": "cdn/logo.png",
      "primaryColor": "#ff6b35"
    }
  },
  "targetImage": "targets/menu.mind",
  "items": [
    {
      "id": "margherita",
      "name": "Margherita Pizza",
      "price": "₹499",
      "description": "Fresh mozzarella, San Marzano tomatoes, basil",
      "category": "pizza",
      "models": {
        "glb": "cdn/models/margherita.glb",
        "usdz": "cdn/models/margherita.usdz"
      },
      "transform": {
        "scale": [0.3, 0.3, 0.3],
        "position": [0, 0.05, 0],
        "rotation": [0, 0, 0]
      },
      "thumbnail": "cdn/thumbs/margherita.webp"
    }
  ]
}
```

Adding a new dish = adding a JSON entry + uploading models to CDN. No code changes.

---

## Project Structure

```
bee-restaurant-project/
├── public/
│   ├── index.html
│   ├── models/              # stock .glb/.usdz for demo
│   └── targets/             # .mind files
├── src/
│   ├── ar/                  # MindAR integration (Layer 3)
│   │   ├── mind-ar.js       # MindAR setup, start/stop, anchor management
│   │   ├── sticky-mode.js   # Hold model position when target lost
│   │   └── hud.js           # AR overlay UI (swipe bar, item info)
│   ├── viewer/              # 3D viewer (Layer 1)
│   │   ├── scene.js         # Three.js scene, renderer, lighting
│   │   ├── model-loader.js  # GLB loading, caching, swapping
│   │   └── controls.js      # Orbit controls, touch gestures
│   ├── native-ar/           # Native AR (Layer 2)
│   │   └── launcher.js      # Quick Look / Scene Viewer detection + launch
│   ├── ui/                  # Shared UI
│   │   ├── menu-carousel.js # Swipe navigation, dot indicators
│   │   ├── loading.js       # Progress bar, skeleton states
│   │   └── item-info.js     # Name, price, description display
│   ├── config/
│   │   └── menu-loader.js   # Fetch + parse menu.json
│   ├── utils/
│   │   ├── device.js        # Feature detection, in-app browser check
│   │   └── state.js         # State machine
│   └── main.js              # Entry point, orchestration
├── menu.json                # Demo restaurant config
├── package.json
├── vite.config.js
└── research/                # Deep research docs (already created)
    └── webar-menu-deep-dive.md
```

**Build:** Vite for dev server + production build. Code-split MindAR/TensorFlow.js so Layer 3 only loads on demand.

**No framework.** Vanilla JS keeps the bundle small and the initial load fast. A framework (Vue/React) can be introduced later for a CMS/admin dashboard.

---

## 3D Model Requirements

### Demo Phase (Stock Models)
- Source: Sketchfab (CC-licensed food models)
- 5-8 items across categories (pizzas, appetizers, desserts)
- Optimize with glTF-Transform before serving

### Production Phase (Future)
- AI-generated from video (Luma AI / Meshy) or photo (Tripo / Rodin)
- Blender cleanup for scale calibration
- USDZ conversion via Reality Converter or usdzconvert

### Optimization Targets

| Metric | Target |
|--------|--------|
| File size (GLB) | < 2 MB |
| Polygon count | < 50K triangles |
| Texture size | 512x512 max |
| Draw calls | < 5 per model |
| Texture format | WebP (in GLB) |

### Lighting Setup
- `RoomEnvironment` via PMREMGenerator (no file download)
- Warm directional key light: color `#fff4e6`, intensity 1.0, position (0.5, 1.5, 1.0)
- Ambient fill: intensity 0.5
- Renderer: ACES filmic tone mapping, sRGB color space

---

## Indian Market Optimizations

- **Models < 2MB:** Draco compression + WebP textures + 512px cap + polygon simplification
- **Lazy loading:** Only load the current item's model. Preload next/prev in carousel.
- **Budget phone target:** Test on Samsung A series / Redmi Note. Cap pixel ratio at 2x. Use `MeshStandardMaterial` not `MeshPhysicalMaterial`.
- **Battery aware:** Auto-pause MindAR tracking after 10s of target lost.
- **Slow 4G:** Show loading progress with restaurant branding. Skeleton placeholders for models.
- **In-app browser detection:** Detect FBAN/Instagram/Twitter/TikTok user agents. Show "Open in Safari/Chrome" instructions.

---

## MindAR Image Tracking Details

### Target Image Guidelines
- High contrast, dense feature points, asymmetric patterns
- Menu designed WITH AR in mind — item sections are AR targets
- Matte/non-reflective print surface, 300+ DPI
- Test every design in MindAR compiler for feature point density

### Tracking Config
```javascript
filterMinCF: 0.001    // less jitter, more latency
filterBeta: 1000       // balance responsiveness
warmupTolerance: 5     // frames to confirm "found"
missTolerance: 5       // frames to confirm "lost"
maxTrack: 1            // one target at a time (performance)
```

### iOS Gating
- Feature-detect MindAR compatibility before showing "Scan Menu" button
- If iOS 17+ detected, attempt initialization in a try/catch
- On crash/error, hide Layer 3 UI, log for analytics
- Revisit when MindAR issue #478 is resolved

---

## QR Code Strategy

- One QR code per menu (links to full AR menu experience)
- URL format: `https://ar.domain.com/{restaurant-slug}`
- Dynamic QR codes (redirect-based) so URL can change without reprinting
- Minimum 2cm × 2cm physical size
- High contrast, error correction level H
- Text label next to QR: "Scan to see dishes in 3D"

---

## Demo Scope (v0.1.0)

For the initial demo/proof-of-concept:

- [ ] 1 demo restaurant ("Demo Pizza Co")
- [ ] 5-8 stock food models from Sketchfab (optimized)
- [ ] Layer 1: 3D viewer with swipe carousel
- [ ] Layer 2: Native AR buttons (Quick Look / Scene Viewer)
- [ ] Layer 3: MindAR image tracking with sticky mode
- [ ] Loading screen with progress bar
- [ ] In-app browser detection
- [ ] Device feature detection for layer availability
- [ ] Mobile-first responsive design
- [ ] Deployed to Vercel (free tier)
- [ ] Models served from public/ (move to R2 in production)

### NOT in v0.1.0
- CMS / admin dashboard
- Analytics / tracking
- Multi-restaurant support (architecture supports it, not wired up)
- Custom 3D models (stock only)
- Payment integration
- USDZ conversion pipeline (manual for demo)

---

## Cost (Demo Phase)

| Item | Monthly Cost |
|------|-------------|
| Hosting (Vercel free tier) | $0 |
| Models (Sketchfab CC-licensed) | $0 |
| CDN (served from Vercel for demo) | $0 |
| Domain (optional, .vercel.app works) | $0 |
| **Total** | **$0** |
