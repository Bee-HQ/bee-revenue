# AR Smart Menu

WebAR restaurant menu — customers scan a QR code, browse 3D food models, and view them in AR on their table.

**Status:** v0.1.0 (demo)
**Stack:** Three.js, MindAR.js, Vite, vanilla JS

## Quick Start

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`. Use the **Network** URL (e.g., `http://192.168.x.x:5173`) to test on your phone.

## Architecture

Three-layer progressive enhancement — each layer works independently, higher layers enhance but never gate the experience.

| Layer | What | Camera? | Works On |
|-------|------|---------|----------|
| **1. 3D Viewer** | Interactive model — rotate, zoom, pinch. Swipe to browse menu. | No | Everything |
| **2. Native AR** | "View in AR" button — places food on your table via OS | Yes (OS-managed) | Most modern phones |
| **3. Image Tracking** | "Scan Menu" — camera recognizes the physical menu, food appears anchored | Yes | Android (reliable), iOS (limited) |

### User Flow

```
QR Code on menu
  -> Browser opens (HTTPS)
  -> Loading screen
  -> Layer 1: 3D Viewer (default)
     - Swipe left/right to browse items
     - Rotate/zoom the 3D model
     -> "View in AR" -> Layer 2: Native AR
     -> "Scan Menu" -> Layer 3: MindAR tracking
```

## Commands

```bash
npm run dev        # Dev server (with mobile network access)
npm run build      # Production build -> dist/
npm run preview    # Preview production build
npm test           # Run all tests
npm run test:watch # Watch mode
```

## Adding a Menu Item

No code changes needed. Edit `menu.json`:

```json
{
  "id": "butter-chicken",
  "name": "Butter Chicken",
  "price": "₹549",
  "description": "Creamy tomato curry, tender chicken",
  "category": "main",
  "models": {
    "glb": "models/butter-chicken.glb",
    "usdz": "models/butter-chicken.usdz"
  },
  "transform": {
    "scale": [0.25, 0.25, 0.25],
    "position": [0, 0.03, 0],
    "rotation": [0, 0, 0]
  }
}
```

Then place `butter-chicken.glb` (and `.usdz` for iOS native AR) in `public/models/`.

### Model Requirements

| Metric | Target |
|--------|--------|
| File size | < 2 MB |
| Polygons | < 50K triangles |
| Textures | 512x512 max, WebP |

Optimize with [glTF-Transform](https://gltf-transform.dev/):

```bash
npx @gltf-transform/cli optimize input.glb output.glb \
  --texture-resize 512 --simplify --simplify-ratio 0.5 --dedup --prune
```

### Transform Guide

- `scale`: `[x, y, z]` — a 12-inch pizza is roughly `[0.3, 0.3, 0.3]` in meters
- `position`: `[x, y, z]` — small positive `y` lifts the model off the surface
- `rotation`: `[x, y, z]` — in radians

## Setting Up a New Restaurant

1. Copy and edit `menu.json` with your restaurant's details:
   - `restaurant.name`, `restaurant.slug`, `restaurant.branding.primaryColor`
   - Menu items with model paths and transforms

2. Upload 3D models (`.glb` + `.usdz`) to `public/models/`

3. (Optional) Compile a MindAR target image:
   - Design a high-contrast menu with dense visual detail
   - Use the [MindAR Image Target Compiler](https://hiukim.github.io/mind-ar-js-doc/tools/compile)
   - Save as `public/targets/menu.mind`

4. Generate a QR code pointing to your deployed URL

## MindAR Image Targets

The "Scan Menu" feature (Layer 3) requires a compiled `.mind` target file. What makes a good target:

- High contrast with lots of detail (photos, text, decorative elements)
- Dense, evenly distributed feature points
- Asymmetric patterns (no repeating tiles)
- Printed on matte paper at 300+ DPI

Use the [online compiler](https://hiukim.github.io/mind-ar-js-doc/tools/compile) to test your menu design before printing.

## Deployment

### Vercel (recommended)

```bash
npx vercel --prod
```

HTTPS is auto-configured (required for camera access).

### Any Static Host

Run `npm run build`, deploy the `dist/` folder. Must be served over HTTPS.

## Known Limitations

- **MindAR + iOS 17+:** Open crash bug ([#478](https://github.com/nicolo-ribaudo/nicolo-ribaudo.github.io/issues/478)) with Three.js integration. Layer 3 is feature-gated on iOS.
- **In-app browsers:** Instagram, Facebook, Twitter, TikTok open links in WKWebView which blocks camera access. The app detects this and shows "Open in Safari/Chrome" instructions.
- **USDZ files:** Currently placeholders. Real USDZ conversion needed for iOS native AR (Layer 2). Use Apple's Reality Converter on macOS.
- **Stock models:** Demo uses placeholder 3D models (DamagedHelmet). Replace with real food models from [Sketchfab](https://sketchfab.com) or AI-generated.

## Project Structure

```
src/
  ar/              # Layer 3: MindAR image tracking
    mind-ar.js     # MindAR session management
    sticky-mode.js # Hold model when target lost
    hud.js         # AR overlay UI
  viewer/          # Layer 1: 3D viewer
    scene.js       # Three.js scene, renderer, lighting
    model-loader.js# GLB loading, caching, preloading
    controls.js    # OrbitControls with mobile touch
  native-ar/       # Layer 2: Native AR
    launcher.js    # Quick Look / Scene Viewer launch
  ui/              # Shared UI components
    menu-carousel.js
    loading.js
    item-info.js
  config/
    menu-loader.js # Fetch + validate menu.json
  utils/
    device.js      # In-app browser + feature detection
    state.js       # Finite state machine
  main.js          # Entry point, orchestration
```

## Testing

```bash
npm test
```

34 tests covering: state machine transitions, device detection (in-app browsers, iOS/Android, camera/WebXR), menu config validation, native AR URL generation, sticky mode timer logic.

Three.js rendering and MindAR tracking are verified visually on real devices.
