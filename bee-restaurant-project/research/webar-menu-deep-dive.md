# WebAR Restaurant Menu: Deep Research Report

**Date:** 2026-03-17
**Status:** Research complete

---

## 1. MindAR.js -- Current State & Capabilities

### Project Health

| Metric | Value |
|--------|-------|
| Version | **1.2.5** (npm, published Jan 16, 2024) |
| GitHub Stars | 2.6k |
| Open Issues | ~100 |
| Forks | 502 |
| Maintainer | Single developer (hiukim) |
| License | MIT |

MindAR describes itself as "the only actively maintained web AR SDK offering comparable features to commercial alternatives." The maintainer also runs Pictarize (image tracking platform) and has a Udemy course. The maintainer has explicitly asked for "help from computer vision experts" to improve tracking accuracy -- a candid signal about where the library stands.

Last npm publish was **January 2024**, so updates have been infrequent. The GitHub repo shows ~100 open issues with limited triage velocity. Not abandoned, but a one-person project with all the associated risks.

### Technical Architecture

- **Image tracking**: Feature point detection + matching using TensorFlow.js (v4.16.0) running in WebGL-accelerated web workers
- **Face tracking**: MediaPipe Tasks Vision (v0.10.9)
- **Math**: ml-matrix, mathjs, svd-js for pose estimation
- **Data format**: MessagePack (@msgpack/msgpack) for .mind files
- **Framework bindings**: A-Frame components + native Three.js API

### Dependencies (from package.json)

```
@mediapipe/tasks-vision ^0.10.9
@tensorflow/tfjs ^4.16.0
@msgpack/msgpack ^2.8.0
canvas ^2.10.2
mathjs ^11.6.0
ml-matrix ^6.10.4
svd-js ^1.1.1
tinyqueue ^2.0.3
```

### .mind Target File Compilation

The .mind file stores extracted feature points from target images in a compact binary format (MessagePack). Three ways to compile:

**1. Web-based compiler tool** (easiest)
- Upload images to the online Image Targets Compiler
- Visual feedback shows feature point distribution
- Download resulting `targets.mind` file
- Multiple images can be compiled into a single .mind file (multi-target)

**2. Programmatic Compiler API** (for automation)
```javascript
const compiler = new window.MINDAR.IMAGE.Compiler();
const dataList = await compiler.compileImageTargets(images, progressCallback);
const exportedBuffer = await compiler.exportData();
// images = array of HTML Image elements
// progressCallback = optional (progress: number) => void
```

**3. Node.js server-side** (community-requested, partially supported)
- Issue #499 discusses using @tensorflow/tfjs-node for server-side compilation
- Issue #575 asks about server-side compilation -- no official API documented
- The Compiler class exists in the codebase but has browser dependencies (canvas, DOM)
- Workaround: headless browser (Puppeteer) running the web compiler

### Target Image Quality Guidelines

What makes a GOOD target image:
- **High contrast** with lots of detail
- **Dense, evenly distributed feature points** across the entire image
- **No large blank/uniform areas** (the compiler visualizes this -- blank corners = bad)
- **Asymmetric patterns** (symmetric images confuse the tracker)
- **Matte/non-reflective** print surface
- **Minimum ~300 DPI** print resolution for stable tracking

What makes a BAD target image:
- Solid colors or gradients
- Repetitive patterns (tiles, stripes)
- Very simple geometric shapes
- Low contrast (light gray on white)
- Glossy/reflective printed surface

**Practical implication for restaurant menus**: Menu item photos themselves can serve as targets IF they have enough visual complexity. A photo of a colorful biryani dish = good target. A plain white plate = terrible target. Custom-designed menu graphics with text + images + decorative elements work best.

### Tracking Configuration

```javascript
// Smoothing (OneEuroFilter) -- balance jitter vs latency
filterMinCF: 0.001  // lower = less jitter, more latency (default)
filterBeta: 1000    // higher = less latency, more jitter (default)

// Detection tolerance
warmupTolerance: 5  // frames needed to confirm "found" (default)
missTolerance: 5    // frames needed to confirm "lost" (default)

// Multi-target simultaneous tracking
maxTrack: 1         // default. WARNING: "great impact on performance"
```

### Three.js Integration (Native, without A-Frame)

```javascript
import { MindARThree } from 'mindar-image-three';

const mindarThree = new MindARThree({
  container: document.querySelector("#container"),
  imageTargetSrc: "/path/to/targets.mind"
});

const { renderer, scene, camera } = mindarThree;

// Create anchor for target index 0
const anchor = mindarThree.addAnchor(0);
// Add 3D content to anchor.group (a THREE.Group)
anchor.group.add(myModel);

// Start AR
await mindarThree.start();
renderer.setAnimationLoop(() => {
  renderer.render(scene, camera);
});

// Stop AR
mindarThree.stop();
renderer.setAnimationLoop(null);
```

Version compatibility:
- Three.js >= v137 (docs recommend v0.160.0)
- Three.js is externalized since MindAR v1.2.0 (you control the version)
- Uses ES module imports with import maps

### iOS Safari Issues (Critical)

Known problems from GitHub issues:

| Issue | iOS Version | Problem |
|-------|-------------|---------|
| #478 | iOS 17 | Page crashes/reloads after granting camera permission with Three.js integration |
| #210 | Various | Camera viewpoint zoom issues, display problems |
| #370 | iOS 16.4 | Front camera fails to open (resolved) |
| #351 | Various | PWA loading failures on iOS |
| #145 | Various | Black bars on Safari display (closed, not planned) |

**The iOS 17 crash (#478) is still open and directly affects our Three.js use case.** This is a significant risk factor.

### Verdict on MindAR.js

**Strengths:**
- Only serious open-source image tracking for web
- Clean Three.js API
- Multi-target support (compile multiple images into one .mind file)
- GPU-accelerated via WebGL + web workers
- Programmatic compilation API exists
- MIT licensed

**Weaknesses:**
- Single maintainer, infrequent updates
- iOS Safari crash on camera permission (open issue)
- Tracking accuracy is acknowledged as needing improvement
- ~100 open issues with slow triage
- Performance degrades with maxTrack > 1
- TensorFlow.js dependency adds significant bundle weight

---

## 2. Alternatives to MindAR.js

### AR.js (v3.4.7)

| Aspect | Details |
|--------|---------|
| Stars | 5.9k (more than MindAR) |
| Open Issues | 225 |
| Image Tracking | NFT (Natural Feature Tracking) via jsartoolkit5 |
| Marker Tracking | Yes (Hiro markers, custom patterns) |
| Location-based | Yes (GPS) |
| Three.js Support | Yes (separate build from A-Frame) |

**Image Tracking Quality**: AR.js NFT requires **300+ DPI** for stable tracking. At 72 DPI, users must stay very still and close. The docs explicitly recommend using `smooth`, `smoothCount`, and `smoothTolerance` "because of weak stabilization." NFT generates three descriptor files (.fset, .fset3, .iset) instead of MindAR's single .mind file.

**Key Difference**: AR.js also supports traditional black-and-white **marker tracking** (like Hiro markers), which is the most stable tracking mode but requires ugly markers. For a restaurant, marker-based tracking with a custom-designed marker could actually be more reliable than NFT/image tracking.

**Verdict**: More mature community (5.9k stars) but image tracking quality is weaker than MindAR. Better suited if you want marker-based tracking (custom restaurant marker printed on the table tent/menu). NFT image tracking is inferior to MindAR's approach.

### 8th Wall (Now Open Source)

Major shift: **8th Wall discontinued its paid hosted platform on February 28, 2026.** The XR Engine is now distributed under a limited commercial use binary license (NOT fully open source like MIT). Example code and tools are MIT.

**Capabilities** (when it was active):
- World tracking (SLAM)
- Image targets
- Face effects
- Hand tracking
- Sky effects
- Lightship VPS (Visual Positioning System)

**Integration**: A-Frame, Three.js, Babylon.js, PlayCanvas

**Current Status**: The XR engine binary is available but the hosted platform is gone. Self-hosting is possible but you're on your own for support. The community may maintain it, but it's early days for the open-source transition.

**Verdict**: Powerful tech but uncertain future. The binary license is restrictive. For a new project in March 2026, the risk of building on a recently-abandoned commercial platform is too high.

### WebXR Device API (W3C Standard)

**Browser Support (March 2026):**

| Browser | Status |
|---------|--------|
| iOS Safari | **NOT SUPPORTED** (3.2 - 26.4: No support) |
| Android Chrome | Partial support (v145+) |
| Samsung Internet | Partial support (v12.0+) |
| Firefox (any) | Disabled by default |
| Desktop Safari | Disabled by default |

**The iOS Safari blocker is fatal.** WebXR's `immersive-ar` session mode does not work on iOS Safari at all. Apple has chosen to promote their native Quick Look/AR Quick Look instead of implementing WebXR. This means ~50% of restaurant customers (iPhone users) cannot use WebXR-based AR.

WebXR features on Android Chrome:
- Hit-test API (surface detection)
- DOM Overlay
- Lighting estimation
- Hand input (limited)

**Verdict**: Not viable as a standalone solution due to zero iOS support. Can be used as an enhancement layer on Android only.

### Google model-viewer (Web Component)

```html
<model-viewer src="dish.glb"
              ios-src="dish.usdz"
              ar
              ar-modes="webxr scene-viewer quick-look"
              camera-controls>
</model-viewer>
```

**How it handles the iOS problem:**
- Android: WebXR first, falls back to Scene Viewer (native app)
- iOS: Triggers **Quick Look** (native AR viewer) using USDZ files
- Both platforms get AR, through different native paths

**Key features:**
- Apache 2.0 license (free)
- Auto-generates USDZ if `ios-src` not specified
- `ar-placement="floor"` or `"wall"`
- `ar-scale="fixed"` prevents user scaling
- `xr-environment` for estimated lighting in WebXR mode
- Custom AR button via slots
- Supports last 2 major versions of all browsers + Safari

**Limitations:**
- **No marker/image tracking** -- this is surface-placement AR only
- User manually places the model in their space
- No camera feed overlay with tracking
- The 3D model just sits on a surface, not anchored to a menu image

**Verdict**: Excellent for "view dish in your space" (place food model on your table). NOT suitable for marker-based "scan the menu to see AR" experience. Different use case entirely, but very polished and cross-platform.

### Comparison Matrix for Restaurant AR Menu

| Feature | MindAR.js | AR.js | 8th Wall | WebXR | model-viewer |
|---------|-----------|-------|----------|-------|-------------|
| Image tracking | Yes (best OSS) | Yes (NFT, weaker) | Yes (best quality) | No | No |
| Marker tracking | No | Yes | No | No | No |
| Surface tracking | No | No | Yes (SLAM) | Yes (Android only) | Yes (via native) |
| iOS Safari | Works* (bugs) | Works | Works | NO | Yes (Quick Look) |
| Android Chrome | Yes | Yes | Yes | Yes | Yes (Scene Viewer) |
| Three.js native | Yes | Yes | Yes | N/A | Built-in |
| License | MIT | MIT | Binary (restricted) | N/A | Apache 2.0 |
| Maintenance | Low (1 dev) | Moderate | Uncertain | Browser vendors | Google |
| Bundle size | Heavy (TF.js) | Moderate | Heavy | None | Light |

*MindAR on iOS 17+ has an open crash bug with Three.js integration

---

## 3. GLB Model Loading in Three.js

### Loading .glb Models

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/');

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

gltfLoader.load('dish.glb', (gltf) => {
  const model = gltf.scene;
  // GLTFLoader auto-converts PBR materials to MeshStandardMaterial
  anchor.group.add(model);
});
```

### Making Food Look Realistic

**Environment Maps (Critical for PBR)**

Food models use PBR materials (metalness/roughness workflow). Without an environment map, MeshStandardMaterial renders as flat black because it needs something to reflect.

```javascript
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { PMREMGenerator } from 'three';

// Option 1: RoomEnvironment (no external files needed, ~zero cost)
const pmremGenerator = new PMREMGenerator(renderer);
scene.environment = pmremGenerator.fromScene(new RoomEnvironment()).texture;

// Option 2: HDR environment map (more realistic but adds file download)
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
new RGBELoader().load('studio.hdr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture;
});
```

**Lighting Setup for Food**

```javascript
// Soft ambient fill
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

// Key light (warm, from above-front -- like restaurant lighting)
const keyLight = new THREE.DirectionalLight(0xfff4e6, 1.0);
keyLight.position.set(0.5, 1.5, 1.0);
scene.add(keyLight);

// Subtle fill from the side
const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
fillLight.position.set(-1, 0.5, 0.5);
scene.add(fillLight);
```

Key material properties for food:
- **Roughness**: 0.7-0.9 for matte food (bread, rice), 0.3-0.5 for glossy food (sauces, glazed meat)
- **Metalness**: 0.0 for all food (food is not metallic)
- **Normal maps**: Add surface texture detail (bread crust, grill marks) without extra geometry
- **AO maps**: Ground the model, add depth to crevices

### Mobile Optimization Targets

| Metric | Target | Aggressive Target |
|--------|--------|-------------------|
| File size (GLB) | < 5 MB | < 2 MB |
| Polygon count | < 100K triangles | < 50K triangles |
| Texture size | 1024x1024 max | 512x512 |
| Draw calls | < 10 per model | < 5 |
| Texture format | WebP in GLB or KTX2/Basis | KTX2 with ETC1S |

### GLB Optimization Pipeline

Using **glTF-Transform** (the standard tool):

```bash
# Install
npm install -g @gltf-transform/cli

# Full optimization pipeline
gltf-transform optimize input.glb output.glb \
  --compress draco \           # Draco mesh compression (can reach <10% of original)
  --texture-compress webp \    # WebP texture compression
  --texture-size 1024 \        # Cap texture dimensions
  --simplify \                 # Reduce polygon count
  --dedup \                    # Remove duplicate data
  --prune                      # Remove unused assets

# Or step by step:
gltf-transform dedup input.glb deduped.glb
gltf-transform simplify deduped.glb simplified.glb --ratio 0.5
gltf-transform draco simplified.glb compressed.glb
gltf-transform webp compressed.glb final.glb --quality 80
```

Alternative tools:
- **meshoptimizer / gltfpack**: Another compression codec, sometimes smaller than Draco
- **Blender**: Manual simplification with more control
- **RapidCompact**: Cloud-based, auto-optimization

### Three.js Renderer Config for AR

```javascript
const renderer = new THREE.WebGLRenderer({
  alpha: true,                    // Transparent background (camera shows through)
  antialias: true,                // Smooth edges
  premultipliedAlpha: true,       // Proper alpha blending
  powerPreference: 'high-performance'
});

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));  // Cap at 2x for perf
renderer.outputColorSpace = THREE.SRGBColorSpace;               // Correct colors
renderer.toneMapping = THREE.ACESFilmicToneMapping;             // Cinematic look
renderer.toneMappingExposure = 1.0;
```

---

## 4. Mobile Browser WebAR Constraints

### iOS Safari Specifics

**Camera Access:**
- Requires HTTPS (or localhost for dev)
- getUserMedia is supported since iOS 11+
- Must use `facingMode: { exact: "environment" }` for rear camera
- **Critical quirk**: Must stop existing tracks before switching cameras -- call `track.stop()` on all existing tracks first
- Camera permission prompt appears once; subsequent visits may auto-grant if user previously allowed
- **No persistent permission grant** like Android -- Safari may re-prompt after clearing site data

**Known iOS AR Issues:**
- iOS 17+ crash with MindAR Three.js integration (issue #478)
- Video autoplay restrictions (must be triggered by user interaction)
- `playsinline` attribute required on video elements
- Safari has aggressive tab suspension -- AR experiences may be killed if user switches tabs
- WKWebView (in-app browsers like Instagram, Facebook) may not support getUserMedia at all
- Safari's `navigator.mediaDevices` returns `undefined` on HTTP (no fallback, just broken)

**iOS PWA Limitations:**
- PWA (Add to Home Screen) on iOS has restricted camera access in some versions
- In-app browsers (Twitter, LinkedIn, Instagram) often block camera entirely
- Must open in Safari proper for reliable camera access

### Android Chrome

- getUserMedia well-supported
- HTTPS required for camera (except localhost)
- `facingMode: "environment"` works reliably
- Some multi-camera devices (e.g., Samsung ultra-wide) may cause Chrome to select the wrong camera
- WebXR `immersive-ar` available on ARCore-supported devices

### HTTPS Requirements (All Browsers)

- **Mandatory** for getUserMedia (camera access)
- **Mandatory** for WebXR sessions
- `localhost` and `file:///` are treated as secure contexts (dev convenience)
- Self-signed certs work for development but cause warnings
- Free certs via Let's Encrypt for production

### Performance Considerations

**Memory:**
- Mobile Safari has aggressive memory limits (~1.4 GB on recent iPhones, less on older)
- Large GLB models + camera feed + TensorFlow.js (MindAR) can approach limits
- Texture memory is the biggest consumer -- keep textures small

**Frame Rate:**
- Target 30fps minimum for smooth AR (60fps ideal)
- MindAR image tracking runs at ~15-30fps depending on device
- Avoid PointLight shadows (renders 6x vs 1x for DirectionalLight)
- `MeshPhongMaterial` > `MeshPhysicalMaterial` for performance
- `alphaTest` > `transparent` when possible

**Battery:**
- Camera + GPU rendering = heavy battery drain
- Typical AR session should be < 2-3 minutes to avoid user annoyance
- Consider auto-pausing tracking when target is lost for > 10 seconds

### Camera Permission Flow Best Practices

```
1. Show explanation screen BEFORE triggering permission prompt
   "We need your camera to show the dish in AR"
   [Continue] button

2. On button click: navigator.mediaDevices.getUserMedia(...)

3. Handle errors gracefully:
   - NotAllowedError: "Camera access denied. Please allow camera in Settings > Safari > [site]"
   - NotFoundError: "No camera found"
   - NotReadableError: "Camera is in use by another app"
   - OverconstrainedError: fall back to any camera (remove facingMode constraint)

4. On success: transition to AR view
```

---

## 5. Real-World WebAR Menu Implementations

### Existing Projects Found

**1. webar-restaurant (Mutasem04)** -- Most relevant
- **Stack**: MindAR.js + Node.js/Express + SQLite + Stripe
- **Approach**: Menu photos as AR triggers, rich media overlays (video, images, 3D models)
- **Features**: Analytics tracking, QR scan counting, restaurant admin dashboard
- **Deployment**: Railway/Render/Docker ready
- **Status**: Active (last updated Jan 2026)

**2. PlatAR-ar-menu (Juanpavilla27)**
- **Stack**: Vue.js + Vite + Tailwind CSS + Firebase Hosting
- **Status**: University hackathon project (2nd place), AR implementation incomplete
- **Note**: Good architecture (Vue + Firebase) but AR part not finished

**3. restaurant-ar-gva (JeevarathinamSenthilkumar)**
- **Stack**: AR.js (marker-based) with custom marker pattern
- **Approach**: Query parameter selects dish model (`?dish=pizza`)
- **Note**: Separate 3D model directories for Android and iOS
- **Status**: 128 commits, actively developed (Oct 2025)

**4. WebAR-Restaurant-Menu (figonzal1)**
- **Stack**: Unity + C# (NOT web-native)
- **Status**: Minimal (1 star, last updated Jul 2023)

### Key Lessons from Existing Projects

1. **Marker-based (AR.js) is simpler to implement** than image tracking (MindAR) -- restaurant-ar-gva uses a custom marker pattern which is more reliable
2. **Admin dashboards matter** -- webar-restaurant includes restaurant management, analytics, and Stripe billing
3. **Dual format models needed** -- restaurant-ar-gva maintains separate Android/iOS model directories
4. **Nobody has nailed this yet** -- all projects are either incomplete, low-star hobbyist work, or academic. No production-grade WebAR restaurant menu exists in the open source space

### The model-viewer Approach (Most Practical)

The ar-menu-research repository's conclusion is notable: **"You don't need expensive WebAR platforms for menu visualization. Google's free model-viewer solution provides 95% of what customers want."**

Their recommended flow:
1. Customer scans QR code -> opens web page
2. Page shows 3D model viewer (interactive, rotatable)
3. "View in AR" button triggers native AR viewer (Scene Viewer on Android, Quick Look on iOS)
4. Model places on real surface (table)

This bypasses the entire marker-tracking problem. The tradeoff: no "magic" of scanning a menu item and seeing food pop up from the page. Instead, it's a curated experience per dish with its own QR code.

### Hybrid Approach (Recommended)

Combine marker-based tracking (the "wow" factor) with model-viewer fallback (the reliable path):

```
If (MindAR loads && camera permission granted && tracking works):
    -> Full marker-based AR experience (scan menu, see 3D food)
Else:
    -> Fallback to model-viewer (3D viewer + native AR button)
```

---

## 6. QR Code -> AR Flow

### Best Practice User Flow

```
Physical Menu / Table Tent
    |
    v
[QR Code] -- one per dish, or one for full AR menu
    |
    v
Mobile Browser Opens (HTTPS required)
    |
    v
Landing Page (NOT directly into camera)
    - Shows dish name, description, price
    - Prominent "View in AR" button
    - Optional: 3D model viewer (drag to rotate) as preview
    |
    v
User taps "View in AR"
    |
    v
Camera permission prompt (browser-native)
    |
    v
AR Experience Starts
    - MindAR: point at menu target image
    - model-viewer: place on surface
    |
    v
"Back to Menu" button always visible
```

### Why NOT Direct-to-Camera

Going straight from QR scan to camera request is hostile UX:
- User has no context about what's happening
- Permission prompt feels invasive without explanation
- If denied, there's no fallback
- Violates Apple's Human Interface Guidelines and Google's Material Design guidance

### QR Code Design Best Practices

- **Dynamic QR codes** (can change URL without reprinting) -- QRCode Monkey ($5/month), or self-hosted with an open-source library
- **High contrast** (dark on light background)
- **Minimum 2cm x 2cm** physical size for reliable scanning
- **Include a short text label** next to QR: "Scan to see in 3D" or dish name
- **Error correction level H** (highest) -- allows up to 30% of the code to be obscured/damaged
- **No logo overlay** unless using high error correction (logos reduce scan reliability)
- **Test on multiple phones** before printing

### Camera Permission Handling

```javascript
async function startAR() {
  // Check if getUserMedia is available
  if (!navigator.mediaDevices?.getUserMedia) {
    showFallback("Your browser doesn't support camera access. Try opening in Safari/Chrome.");
    return;
  }

  try {
    // Request camera with rear-facing preference
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } }
    });

    // Got camera -- stop this test stream and init AR
    stream.getTracks().forEach(track => track.stop());
    initMindAR();

  } catch (err) {
    switch (err.name) {
      case 'NotAllowedError':
        showMessage("Camera access was denied. To use AR, please allow camera access in your browser settings.");
        showFallback(); // Show 3D viewer without AR
        break;
      case 'NotFoundError':
        showMessage("No camera found on this device.");
        showFallback();
        break;
      case 'NotReadableError':
        showMessage("Camera is in use by another app. Please close other camera apps and try again.");
        break;
      default:
        showMessage("Something went wrong with camera access.");
        showFallback();
    }
  }
}
```

### In-App Browser Problem

The biggest UX challenge: users scanning QR codes from Instagram, Twitter, TikTok, or other apps will open the link in an **in-app browser** (WKWebView on iOS), which often **blocks camera access entirely**.

Mitigations:
1. Detect in-app browser and show "Open in Safari/Chrome" button
2. Use `window.open()` to try to break out to the system browser
3. On iOS, a "Open in Safari" banner/instruction
4. Some apps support `x-callback-url` schemes, but it's unreliable

```javascript
// Detect common in-app browsers
function isInAppBrowser() {
  const ua = navigator.userAgent || navigator.vendor;
  return /FBAN|FBAV|Instagram|Twitter|Line|Snapchat|LinkedIn/i.test(ua);
}

if (isInAppBrowser()) {
  showMessage("For the best AR experience, please open this link in Safari or Chrome.");
  // Show "Copy Link" button + instructions
}
```

---

## 7. Recommended Architecture for Bee Restaurant AR Menu

### Option A: Marker-Based (MindAR + Three.js)

**The "wow factor" approach**: customer scans their physical menu and 3D food appears on top of it.

```
Menu Design Requirements:
- Each menu item section designed as a high-contrast AR target
- Menu printed at 300+ DPI on matte paper
- Compile all menu item images into one targets.mind file

Tech Stack:
- MindAR.js v1.2.5 (Three.js integration)
- Three.js v0.160.0+
- GLB models (Draco compressed, <2MB each)
- RoomEnvironment for lighting (no HDR download needed)
- Hosted on any static host (Vercel, Cloudflare Pages)

Risk: iOS Safari crash bug (#478 on iOS 17+)
Mitigation: model-viewer fallback if AR fails
```

### Option B: model-viewer (Surface Placement)

**The reliable approach**: QR per dish, 3D viewer + native AR.

```
Stack:
- Google model-viewer web component
- GLB models for Android, USDZ for iOS
- QR code per menu item
- Static HTML/CSS (or Vue/React)
- Cloudflare R2 for model storage (no egress fees)

Pros: Works everywhere, no tracking bugs, native AR quality
Cons: No "scan the menu" magic, requires one QR per dish
```

### Option C: Hybrid (Recommended)

```
Default Path: model-viewer
- QR code -> landing page -> 3D viewer + "View in AR" button
- Works on ALL devices, ALL browsers
- Native AR via Quick Look (iOS) / Scene Viewer (Android)

Enhanced Path: MindAR overlay
- "Scan Your Menu" button on landing page
- Opens MindAR camera view
- Point at menu items to see food pop up
- Feature-detect and fail gracefully to model-viewer
- Only for customers who want the full experience
```

### Model Pipeline

```
3D Scanning (Polycam $12.50/mo or Scaniverse free)
    -> Export as GLB
    -> Optimize with glTF-Transform (Draco + WebP textures + simplify)
    -> Target: <2MB, <50K triangles, 512px textures
    -> Convert to USDZ for iOS (using Reality Converter or usdzconvert)
    -> Upload to Cloudflare R2
    -> Serve via CDN
```

### Cost Estimate (MVP)

| Item | Monthly Cost |
|------|-------------|
| 3D Scanning (Scaniverse) | $0 |
| Hosting (Vercel free tier) | $0 |
| Model storage (Cloudflare R2 free tier, 10GB) | $0 |
| QR codes (self-hosted, open source lib) | $0 |
| Domain name | ~$1 |
| **Total MVP** | **~$1/month** |

Scaling up:
| Item | Monthly Cost |
|------|-------------|
| 3D Scanning (Polycam) | $12.50 |
| Hosting (Vercel Pro) | $20 |
| Model storage (Cloudflare R2) | $1.50 |
| Dynamic QR service | $5 |
| **Total Growth** | **~$39/month** |

---

## 8. Key Decisions and Recommendations

1. **Start with model-viewer, add MindAR as an enhancement.** model-viewer works everywhere, today, with zero tracking bugs. MindAR adds the wow factor but has iOS risks.

2. **GLB + USDZ dual format is non-negotiable.** Android needs GLB, iOS needs USDZ for native AR. model-viewer handles this with `src` and `ios-src` attributes.

3. **Keep models under 2MB.** Draco compression + WebP textures + polygon simplification via glTF-Transform. Target 50K triangles max per dish model.

4. **Use RoomEnvironment for lighting.** Zero additional downloads, works well for food PBR materials. Add one warm DirectionalLight for restaurant ambiance.

5. **Handle in-app browsers explicitly.** Detect FBAN/Instagram/Twitter user agents and show "Open in Safari" instructions. This is the #1 real-world UX failure point.

6. **Dynamic QR codes.** Don't hardcode URLs into printed QR codes. Use a redirect service so you can update the AR experience without reprinting menus.

7. **Camera permission: always show context first.** Never auto-request camera. Show a landing page with dish info and a clear "View in AR" button. Handle denial gracefully with 3D viewer fallback.

8. **MindAR target design: design the menu FOR AR.** Don't treat AR as an afterthought. Design menu item sections with high-contrast, feature-rich graphics that double as great AR targets. Test every design in the MindAR compiler to verify feature point density before printing.

9. **maxTrack: 1.** Don't try to track multiple menu items simultaneously. Track one at a time. Performance is bad with maxTrack > 1.

10. **Test on real devices relentlessly.** Especially: iPhone with iOS 17+, iPhone SE (low-end), budget Android phones (Samsung A series), and various in-app browsers. The simulator lies.
