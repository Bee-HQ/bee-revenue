# AR Smart Menu Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a progressive WebAR restaurant menu with 3D model viewer, native AR, and MindAR image tracking.

**Architecture:** Three-layer progressive enhancement — Layer 1 (3D viewer, always works) → Layer 2 (native AR via Quick Look/Scene Viewer) → Layer 3 (MindAR image tracking, feature-detected). Vanilla JS + Vite, config-driven menu system.

**Tech Stack:** Three.js (v0.160.0), MindAR.js (v1.2.5), Vite, Vitest, vanilla JS

**Spec:** `docs/superpowers/specs/2026-03-17-ar-smart-menu-design.md`

---

## File Map

```
bee-restaurant-project/
├── public/
│   ├── index.html                 # Entry HTML — canvas container, UI overlays
│   ├── models/                    # Stock .glb/.usdz for demo
│   │   ├── margherita.glb
│   │   ├── margherita.usdz
│   │   ├── ... (5-8 items)
│   └── targets/
│       └── menu.mind              # Compiled MindAR target
├── src/
│   ├── utils/
│   │   ├── device.js              # In-app browser detection, feature detection
│   │   └── state.js               # Finite state machine
│   ├── config/
│   │   └── menu-loader.js         # Fetch + validate menu.json
│   ├── viewer/
│   │   ├── scene.js               # Three.js scene, renderer, camera, lighting
│   │   ├── model-loader.js        # GLB loading, cache, swap with crossfade
│   │   └── controls.js            # OrbitControls wrapper, touch gesture config
│   ├── native-ar/
│   │   └── launcher.js            # Quick Look / Scene Viewer detection + launch
│   ├── ar/
│   │   ├── mind-ar.js             # MindAR init, start/stop, anchor management
│   │   ├── sticky-mode.js         # Hold position on target lost, auto-pause timer
│   │   └── hud.js                 # AR overlay: bottom bar, swipe dots
│   ├── ui/
│   │   ├── menu-carousel.js       # Swipe navigation, dot indicators, item switching
│   │   ├── loading.js             # Loading screen: progress bar, branding
│   │   └── item-info.js           # Name, price, description panel
│   └── main.js                    # Entry: orchestration, state transitions, init
├── tests/
│   ├── utils/
│   │   ├── device.test.js
│   │   └── state.test.js
│   ├── config/
│   │   └── menu-loader.test.js
│   ├── native-ar/
│   │   └── launcher.test.js
│   └── ar/
│       └── sticky-mode.test.js
├── menu.json                      # Demo restaurant config
├── package.json
├── vite.config.js
└── vitest.config.js
```

**Testing strategy:** Unit test all pure logic (state machine, device detection, config parsing, native AR detection, sticky mode timer). Three.js rendering and MindAR tracking require visual verification on real devices — each task includes manual verification steps.

---

## Task 1: Project Scaffolding

**Files:**
- Create: `package.json`
- Create: `vite.config.js`
- Create: `vitest.config.js`
- Create: `public/index.html`
- Create: `.gitignore`

- [ ] **Step 1: Initialize package.json**

```bash
cd /Users/mk/work/bee-revenue/bee-restaurant-project
npm init -y
```

Then edit `package.json`:

```json
{
  "name": "bee-ar-menu",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

- [ ] **Step 2: Install dependencies**

```bash
npm install three@0.160.0
npm install -D vite vitest
```

Note: MindAR is installed in Task 10 (Layer 3) — it's code-split and only needed then.

- [ ] **Step 3: Create vite.config.js**

```javascript
import { defineConfig } from 'vite';

export default defineConfig({
  root: '.',
  publicDir: 'public',
  build: {
    outDir: 'dist',
    target: 'es2020',
  },
  server: {
    https: false, // localhost is treated as secure context
    host: true,   // expose to local network for mobile testing
  },
});
```

- [ ] **Step 4: Create vitest.config.js**

```javascript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['tests/**/*.test.js'],
  },
});
```

- [ ] **Step 5: Create public/index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <title>AR Menu</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 100%; height: 100%; overflow: hidden; background: #0a0a0a; color: #fff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    #app { width: 100%; height: 100%; position: relative; }
  </style>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 6: Create .gitignore**

```
node_modules/
dist/
.DS_Store
*.local
.superpowers/
```

- [ ] **Step 7: Create src/main.js placeholder**

```javascript
console.log('AR Menu v0.1.0');
```

- [ ] **Step 8: Verify dev server starts**

Run: `npm run dev`
Expected: Vite dev server starts, accessible at `http://localhost:5173`. Console shows "AR Menu v0.1.0".

- [ ] **Step 9: Commit**

```bash
git add package.json package-lock.json vite.config.js vitest.config.js public/index.html .gitignore src/main.js
git commit -m "scaffold project with Vite, Three.js, and Vitest"
```

---

## Task 2: State Machine

**Files:**
- Create: `src/utils/state.js`
- Create: `tests/utils/state.test.js`

- [ ] **Step 1: Write failing tests**

```javascript
// tests/utils/state.test.js
import { describe, it, expect, vi } from 'vitest';
import { createStateMachine } from '../../src/utils/state.js';

describe('createStateMachine', () => {
  const config = {
    initial: 'LOADING',
    states: {
      LOADING:   { LOADED: 'VIEWING' },
      VIEWING:   { START_AR: 'SCANNING', START_NATIVE: 'NATIVE_AR' },
      NATIVE_AR: { BACK: 'VIEWING' },
      SCANNING:  { TARGET_FOUND: 'TRACKING', BACK: 'VIEWING' },
      TRACKING:  { TARGET_LOST: 'STICKY', BACK: 'VIEWING' },
      STICKY:    { TARGET_FOUND: 'TRACKING', TIMEOUT: 'VIEWING', BACK: 'VIEWING' },
    },
  };

  it('starts in initial state', () => {
    const sm = createStateMachine(config);
    expect(sm.current()).toBe('LOADING');
  });

  it('transitions on valid event', () => {
    const sm = createStateMachine(config);
    sm.send('LOADED');
    expect(sm.current()).toBe('VIEWING');
  });

  it('ignores invalid event for current state', () => {
    const sm = createStateMachine(config);
    sm.send('TARGET_FOUND'); // not valid in LOADING
    expect(sm.current()).toBe('LOADING');
  });

  it('calls listeners on transition', () => {
    const sm = createStateMachine(config);
    const listener = vi.fn();
    sm.on(listener);
    sm.send('LOADED');
    expect(listener).toHaveBeenCalledWith('VIEWING', 'LOADING');
  });

  it('removes listener with off', () => {
    const sm = createStateMachine(config);
    const listener = vi.fn();
    sm.on(listener);
    sm.off(listener);
    sm.send('LOADED');
    expect(listener).not.toHaveBeenCalled();
  });

  it('supports full Layer 3 flow', () => {
    const sm = createStateMachine(config);
    sm.send('LOADED');
    sm.send('START_AR');
    expect(sm.current()).toBe('SCANNING');
    sm.send('TARGET_FOUND');
    expect(sm.current()).toBe('TRACKING');
    sm.send('TARGET_LOST');
    expect(sm.current()).toBe('STICKY');
    sm.send('TIMEOUT');
    expect(sm.current()).toBe('VIEWING');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run tests/utils/state.test.js`
Expected: FAIL — module not found

- [ ] **Step 3: Implement state machine**

```javascript
// src/utils/state.js
export function createStateMachine({ initial, states }) {
  let state = initial;
  const listeners = new Set();

  return {
    current() {
      return state;
    },

    send(event) {
      const transitions = states[state];
      if (!transitions || !(event in transitions)) return;
      const prev = state;
      state = transitions[event];
      for (const fn of listeners) fn(state, prev);
    },

    on(fn) {
      listeners.add(fn);
    },

    off(fn) {
      listeners.delete(fn);
    },
  };
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run tests/utils/state.test.js`
Expected: 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/utils/state.js tests/utils/state.test.js
git commit -m "add finite state machine for AR layer transitions"
```

---

## Task 3: Device Detection Utilities

**Files:**
- Create: `src/utils/device.js`
- Create: `tests/utils/device.test.js`

- [ ] **Step 1: Write failing tests**

```javascript
// tests/utils/device.test.js
import { describe, it, expect, vi } from 'vitest';
import { isInAppBrowser, detectFeatures } from '../../src/utils/device.js';

describe('isInAppBrowser', () => {
  it('detects Instagram in-app browser', () => {
    expect(isInAppBrowser('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Instagram')).toBe(true);
  });

  it('detects Facebook in-app browser', () => {
    expect(isInAppBrowser('Mozilla/5.0 (Linux; Android 13) FBAN/FB4A')).toBe(true);
  });

  it('detects Twitter in-app browser', () => {
    expect(isInAppBrowser('Mozilla/5.0 (iPhone) Twitter for iPhone')).toBe(true);
  });

  it('detects TikTok in-app browser', () => {
    expect(isInAppBrowser('Mozilla/5.0 (iPhone) BytedanceWebview')).toBe(true);
  });

  it('detects LinkedIn in-app browser', () => {
    expect(isInAppBrowser('Mozilla/5.0 (iPhone) LinkedInApp')).toBe(true);
  });

  it('returns false for Safari', () => {
    expect(isInAppBrowser('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')).toBe(false);
  });

  it('returns false for Chrome', () => {
    expect(isInAppBrowser('Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36')).toBe(false);
  });
});

describe('detectFeatures', () => {
  it('returns object with expected keys', () => {
    const features = detectFeatures({
      userAgent: 'Mozilla/5.0 Chrome',
      mediaDevices: { getUserMedia: () => {} },
      xrSystem: null,
      platform: 'Android',
    });
    expect(features).toHaveProperty('hasCamera');
    expect(features).toHaveProperty('hasWebXR');
    expect(features).toHaveProperty('isIOS');
    expect(features).toHaveProperty('isAndroid');
    expect(features).toHaveProperty('isInAppBrowser');
    expect(features).toHaveProperty('canMindAR');
    expect(features).toHaveProperty('canNativeAR');
  });

  it('detects iOS from user agent', () => {
    const features = detectFeatures({
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)',
      mediaDevices: null,
      xrSystem: null,
      platform: 'iPhone',
    });
    expect(features.isIOS).toBe(true);
    expect(features.isAndroid).toBe(false);
  });

  it('marks canMindAR false when no camera', () => {
    const features = detectFeatures({
      userAgent: 'Chrome Android',
      mediaDevices: null,
      xrSystem: null,
      platform: 'Android',
    });
    expect(features.canMindAR).toBe(false);
  });

  it('marks canMindAR false for in-app browsers', () => {
    const features = detectFeatures({
      userAgent: 'FBAN/FB4A',
      mediaDevices: { getUserMedia: () => {} },
      xrSystem: null,
      platform: 'Android',
    });
    expect(features.canMindAR).toBe(false);
  });

  it('marks canNativeAR true for iOS (Quick Look)', () => {
    const features = detectFeatures({
      userAgent: 'iPhone OS 17',
      mediaDevices: null,
      xrSystem: null,
      platform: 'iPhone',
      canQuickLook: true,
    });
    expect(features.canNativeAR).toBe(true);
  });

  it('marks canNativeAR true for Android with WebXR', () => {
    const features = detectFeatures({
      userAgent: 'Chrome Android',
      mediaDevices: { getUserMedia: () => {} },
      xrSystem: { isSessionSupported: () => Promise.resolve(true) },
      platform: 'Android',
    });
    expect(features.canNativeAR).toBe(true);
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run tests/utils/device.test.js`
Expected: FAIL — module not found

- [ ] **Step 3: Implement device detection**

```javascript
// src/utils/device.js
const IN_APP_PATTERNS = /FBAN|FBAV|Instagram|Twitter|BytedanceWebview|Snapchat|LinkedInApp|Line\//i;

export function isInAppBrowser(ua) {
  return IN_APP_PATTERNS.test(ua);
}

export function detectFeatures({ userAgent, mediaDevices, xrSystem, platform, canQuickLook = false }) {
  const isIOS = /iPhone|iPad|iPod/i.test(userAgent) || /iPhone|iPad/i.test(platform);
  const isAndroid = /Android/i.test(userAgent) || /Android/i.test(platform);
  const hasCamera = !!(mediaDevices && mediaDevices.getUserMedia);
  const hasWebXR = !!xrSystem;
  const inApp = isInAppBrowser(userAgent);

  return {
    isIOS,
    isAndroid,
    hasCamera,
    hasWebXR,
    isInAppBrowser: inApp,
    canMindAR: hasCamera && !inApp,
    canNativeAR: canQuickLook || hasWebXR || (isAndroid && hasCamera),
  };
}

/**
 * Detect features from the live browser environment.
 * Call this from main.js — not from tests.
 */
export async function detectLiveFeatures() {
  const ua = navigator.userAgent || '';
  const mediaDevices = navigator.mediaDevices || null;
  const xrSystem = navigator.xr || null;
  const platform = navigator.platform || '';

  // Quick Look detection: check if an <a> with rel="ar" is supported
  const canQuickLook = (() => {
    const a = document.createElement('a');
    return a.relList && a.relList.supports && a.relList.supports('ar');
  })();

  return detectFeatures({ userAgent: ua, mediaDevices, xrSystem, platform, canQuickLook });
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run tests/utils/device.test.js`
Expected: 12 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/utils/device.js tests/utils/device.test.js
git commit -m "add device detection and in-app browser check"
```

---

## Task 4: Menu Config Loader

**Files:**
- Create: `src/config/menu-loader.js`
- Create: `tests/config/menu-loader.test.js`
- Create: `menu.json`

- [ ] **Step 1: Create demo menu.json**

```json
{
  "restaurant": {
    "name": "Demo Pizza Co",
    "slug": "demo-pizza",
    "branding": {
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
        "glb": "models/margherita.glb",
        "usdz": "models/margherita.usdz"
      },
      "transform": {
        "scale": [0.3, 0.3, 0.3],
        "position": [0, 0.05, 0],
        "rotation": [0, 0, 0]
      }
    },
    {
      "id": "pepperoni",
      "name": "Pepperoni Pizza",
      "price": "₹599",
      "description": "Spicy pepperoni, mozzarella, tomato sauce",
      "category": "pizza",
      "models": {
        "glb": "models/pepperoni.glb",
        "usdz": "models/pepperoni.usdz"
      },
      "transform": {
        "scale": [0.3, 0.3, 0.3],
        "position": [0, 0.05, 0],
        "rotation": [0, 0, 0]
      }
    },
    {
      "id": "pasta-carbonara",
      "name": "Pasta Carbonara",
      "price": "₹449",
      "description": "Creamy egg sauce, pancetta, parmesan",
      "category": "pasta",
      "models": {
        "glb": "models/pasta-carbonara.glb",
        "usdz": "models/pasta-carbonara.usdz"
      },
      "transform": {
        "scale": [0.25, 0.25, 0.25],
        "position": [0, 0.03, 0],
        "rotation": [0, 0, 0]
      }
    },
    {
      "id": "tiramisu",
      "name": "Tiramisu",
      "price": "₹349",
      "description": "Classic Italian coffee-flavored dessert",
      "category": "dessert",
      "models": {
        "glb": "models/tiramisu.glb",
        "usdz": "models/tiramisu.usdz"
      },
      "transform": {
        "scale": [0.2, 0.2, 0.2],
        "position": [0, 0.02, 0],
        "rotation": [0, 0, 0]
      }
    },
    {
      "id": "bruschetta",
      "name": "Bruschetta",
      "price": "₹299",
      "description": "Grilled bread, tomatoes, garlic, fresh basil",
      "category": "appetizer",
      "models": {
        "glb": "models/bruschetta.glb",
        "usdz": "models/bruschetta.usdz"
      },
      "transform": {
        "scale": [0.2, 0.2, 0.2],
        "position": [0, 0.02, 0],
        "rotation": [0, 0, 0]
      }
    }
  ]
}
```

- [ ] **Step 2: Write failing tests**

```javascript
// tests/config/menu-loader.test.js
import { describe, it, expect } from 'vitest';
import { validateMenuConfig, getItemById, getItemByIndex } from '../../src/config/menu-loader.js';

const validConfig = {
  restaurant: { name: 'Test', slug: 'test', branding: { primaryColor: '#000' } },
  targetImage: 'targets/menu.mind',
  items: [
    { id: 'a', name: 'Item A', price: '₹100', description: 'Desc', category: 'cat', models: { glb: 'a.glb', usdz: 'a.usdz' }, transform: { scale: [1,1,1], position: [0,0,0], rotation: [0,0,0] } },
    { id: 'b', name: 'Item B', price: '₹200', description: 'Desc', category: 'cat', models: { glb: 'b.glb', usdz: 'b.usdz' }, transform: { scale: [1,1,1], position: [0,0,0], rotation: [0,0,0] } },
  ],
};

describe('validateMenuConfig', () => {
  it('returns true for valid config', () => {
    expect(validateMenuConfig(validConfig)).toBe(true);
  });

  it('throws if restaurant is missing', () => {
    expect(() => validateMenuConfig({ items: [] })).toThrow('restaurant');
  });

  it('throws if items is empty', () => {
    expect(() => validateMenuConfig({ ...validConfig, items: [] })).toThrow('items');
  });

  it('throws if item missing glb model', () => {
    const bad = { ...validConfig, items: [{ ...validConfig.items[0], models: { usdz: 'a.usdz' } }] };
    expect(() => validateMenuConfig(bad)).toThrow('glb');
  });
});

describe('getItemById', () => {
  it('returns item by id', () => {
    expect(getItemById(validConfig.items, 'b').name).toBe('Item B');
  });

  it('returns undefined for missing id', () => {
    expect(getItemById(validConfig.items, 'z')).toBeUndefined();
  });
});

describe('getItemByIndex', () => {
  it('wraps around to first item', () => {
    expect(getItemByIndex(validConfig.items, 2).id).toBe('a');
  });

  it('wraps around to last item', () => {
    expect(getItemByIndex(validConfig.items, -1).id).toBe('b');
  });
});
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `npx vitest run tests/config/menu-loader.test.js`
Expected: FAIL

- [ ] **Step 4: Implement menu loader**

```javascript
// src/config/menu-loader.js
export function validateMenuConfig(config) {
  if (!config.restaurant || !config.restaurant.name) {
    throw new Error('Menu config missing "restaurant" with "name"');
  }
  if (!config.items || config.items.length === 0) {
    throw new Error('Menu config must have at least one item in "items"');
  }
  for (const item of config.items) {
    if (!item.models || !item.models.glb) {
      throw new Error(`Item "${item.id || item.name}" missing "glb" model path`);
    }
  }
  return true;
}

export function getItemById(items, id) {
  return items.find((item) => item.id === id);
}

export function getItemByIndex(items, index) {
  const len = items.length;
  return items[((index % len) + len) % len];
}

export async function loadMenuConfig(url = '/menu.json') {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Failed to load menu: ${response.status}`);
  const config = await response.json();
  validateMenuConfig(config);
  return config;
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `npx vitest run tests/config/menu-loader.test.js`
Expected: 7 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/config/menu-loader.js tests/config/menu-loader.test.js menu.json
git commit -m "add menu config loader with validation and demo menu.json"
```

---

## Task 5: Three.js Scene Setup (Layer 1 Foundation)

**Files:**
- Create: `src/viewer/scene.js`

This task builds the Three.js scene — renderer, camera, lighting, environment map. No tests for WebGL code — verified visually.

- [ ] **Step 1: Create scene.js**

```javascript
// src/viewer/scene.js
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export function createScene(container) {
  // Renderer
  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: true,
    powerPreference: 'high-performance',
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  container.appendChild(renderer.domElement);

  // Scene
  const scene = new THREE.Scene();

  // Environment map (PBR lighting, no file download)
  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  scene.environment = pmremGenerator.fromScene(new RoomEnvironment()).texture;
  pmremGenerator.dispose();

  // Camera
  const camera = new THREE.PerspectiveCamera(
    45,
    container.clientWidth / container.clientHeight,
    0.01,
    100
  );
  camera.position.set(0, 0.3, 0.6);
  camera.lookAt(0, 0, 0);

  // Lighting — warm restaurant ambiance
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xfff4e6, 1.0);
  keyLight.position.set(0.5, 1.5, 1.0);
  scene.add(keyLight);

  // Resize handler
  const onResize = () => {
    const w = container.clientWidth;
    const h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  };
  window.addEventListener('resize', onResize);

  // Render loop
  let animationId = null;
  const clock = new THREE.Clock();

  function startLoop(onFrame) {
    function loop() {
      animationId = requestAnimationFrame(loop);
      const delta = clock.getDelta();
      if (onFrame) onFrame(delta);
      renderer.render(scene, camera);
    }
    loop();
  }

  function stopLoop() {
    if (animationId) cancelAnimationFrame(animationId);
    animationId = null;
  }

  function dispose() {
    stopLoop();
    window.removeEventListener('resize', onResize);
    renderer.dispose();
  }

  return { renderer, scene, camera, startLoop, stopLoop, dispose };
}
```

- [ ] **Step 2: Wire into main.js for visual verification**

```javascript
// src/main.js
import { createScene } from './viewer/scene.js';

const app = document.getElementById('app');
const { scene, startLoop } = createScene(app);

// Add a placeholder box to verify rendering
import * as THREE from 'three';
const box = new THREE.Mesh(
  new THREE.BoxGeometry(0.1, 0.1, 0.1),
  new THREE.MeshStandardMaterial({ color: 0xff6b35 })
);
scene.add(box);

startLoop((delta) => {
  box.rotation.y += delta;
});
```

- [ ] **Step 3: Verify visually**

Run: `npm run dev`
Expected: Orange spinning cube on dark background. Scene fills viewport. Resize browser — cube stays centered.

- [ ] **Step 4: Commit**

```bash
git add src/viewer/scene.js src/main.js
git commit -m "add Three.js scene with PBR environment and restaurant lighting"
```

---

## Task 6: GLB Model Loader

**Files:**
- Create: `src/viewer/model-loader.js`

- [ ] **Step 1: Create model-loader.js**

```javascript
// src/viewer/model-loader.js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const gltfLoader = new GLTFLoader();
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/');
gltfLoader.setDRACOLoader(dracoLoader);

const cache = new Map();

/**
 * Load a GLB model. Returns the scene (THREE.Group).
 * Caches by URL — second call returns clone from cache.
 * @param {string} url - path to .glb file
 * @param {(progress: number) => void} [onProgress] - 0 to 1
 * @returns {Promise<THREE.Group>}
 */
export function loadModel(url, onProgress) {
  if (cache.has(url)) {
    return Promise.resolve(cache.get(url).clone());
  }

  return new Promise((resolve, reject) => {
    gltfLoader.load(
      url,
      (gltf) => {
        cache.set(url, gltf.scene);
        resolve(gltf.scene.clone());
      },
      (event) => {
        if (onProgress && event.total > 0) {
          onProgress(event.loaded / event.total);
        }
      },
      (error) => reject(new Error(`Failed to load model ${url}: ${error.message}`)),
    );
  });
}

/**
 * Preload models without adding to scene.
 * @param {string[]} urls
 */
export async function preloadModels(urls) {
  await Promise.allSettled(urls.map((url) => loadModel(url)));
}

/**
 * Apply transform from menu config to a loaded model.
 */
export function applyTransform(model, transform) {
  if (transform.scale) model.scale.set(...transform.scale);
  if (transform.position) model.position.set(...transform.position);
  if (transform.rotation) model.rotation.set(...transform.rotation);
}
```

- [ ] **Step 2: Download a test GLB model**

We need at least one stock model to verify loading. Download a free food model from the Three.js examples or create a placeholder.

```bash
mkdir -p public/models
# Download a simple GLB for testing (Three.js example model)
curl -L -o public/models/test.glb "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/DamagedHelmet/glTF-Binary/DamagedHelmet.glb"
```

Note: This is a placeholder. Real food models are sourced in Task 12.

- [ ] **Step 3: Update main.js to test model loading**

```javascript
// src/main.js
import { createScene } from './viewer/scene.js';
import { loadModel, applyTransform } from './viewer/model-loader.js';

const app = document.getElementById('app');
const { scene, startLoop } = createScene(app);

// Test loading a GLB model
loadModel('/models/test.glb', (progress) => {
  console.log(`Loading: ${(progress * 100).toFixed(0)}%`);
}).then((model) => {
  applyTransform(model, { scale: [0.15, 0.15, 0.15], position: [0, 0, 0], rotation: [0, 0, 0] });
  scene.add(model);
  console.log('Model loaded');
});

startLoop();
```

- [ ] **Step 4: Verify visually**

Run: `npm run dev`
Expected: 3D model loads and renders with PBR materials. Console shows loading progress then "Model loaded".

- [ ] **Step 5: Commit**

```bash
git add src/viewer/model-loader.js src/main.js public/models/test.glb
git commit -m "add GLB model loader with Draco support and caching"
```

---

## Task 7: Orbit Controls (Touch Gestures)

**Files:**
- Create: `src/viewer/controls.js`

- [ ] **Step 1: Create controls.js**

```javascript
// src/viewer/controls.js
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/**
 * Set up orbit controls optimized for mobile food viewing.
 * Constrains rotation, enables touch pinch-zoom.
 */
export function createControls(camera, domElement) {
  const controls = new OrbitControls(camera, domElement);

  // Smooth damping
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;

  // Constrain vertical rotation (don't flip under the plate)
  controls.minPolarAngle = 0.2;     // ~11° from top
  controls.maxPolarAngle = Math.PI / 2; // horizon

  // Zoom limits
  controls.minDistance = 0.2;
  controls.maxDistance = 1.5;

  // Disable pan (keep food centered)
  controls.enablePan = false;

  // Touch config
  controls.touches = {
    ONE: 0, // ROTATE (OrbitControls.TOUCH.ROTATE = 0)
    TWO: 2, // DOLLY (OrbitControls.TOUCH.DOLLY_ROTATE = 2)
  };

  return controls;
}
```

- [ ] **Step 2: Wire into main.js**

```javascript
// src/main.js
import { createScene } from './viewer/scene.js';
import { loadModel, applyTransform } from './viewer/model-loader.js';
import { createControls } from './viewer/controls.js';

const app = document.getElementById('app');
const { scene, camera, renderer, startLoop } = createScene(app);
const controls = createControls(camera, renderer.domElement);

loadModel('/models/test.glb', (progress) => {
  console.log(`Loading: ${(progress * 100).toFixed(0)}%`);
}).then((model) => {
  applyTransform(model, { scale: [0.15, 0.15, 0.15], position: [0, 0, 0], rotation: [0, 0, 0] });
  scene.add(model);
});

startLoop((delta) => {
  controls.update();
});
```

- [ ] **Step 3: Verify on mobile**

Run: `npm run dev` — note the `Network` URL (e.g., `http://192.168.x.x:5173`)
Open on phone. Expected: drag to rotate model, pinch to zoom. Can't rotate below horizon. Smooth damping on release.

- [ ] **Step 4: Commit**

```bash
git add src/viewer/controls.js src/main.js
git commit -m "add orbit controls with mobile touch constraints"
```

---

## Task 8: Loading Screen

**Files:**
- Create: `src/ui/loading.js`

- [ ] **Step 1: Create loading.js**

```javascript
// src/ui/loading.js

/**
 * Create and manage a loading overlay.
 * @param {HTMLElement} container
 * @param {{ name: string, primaryColor: string }} branding
 */
export function createLoadingScreen(container, branding = {}) {
  const { name = 'AR Menu', primaryColor = '#ff6b35' } = branding;

  const overlay = document.createElement('div');
  overlay.id = 'loading-screen';
  overlay.innerHTML = `
    <div class="loading-content">
      <h1 class="loading-title">${name}</h1>
      <p class="loading-subtitle">AR Menu</p>
      <div class="loading-bar-track">
        <div class="loading-bar-fill"></div>
      </div>
      <p class="loading-status">Loading 3D models...</p>
    </div>
  `;
  overlay.style.cssText = `
    position: fixed; inset: 0; z-index: 1000;
    display: flex; align-items: center; justify-content: center;
    background: #0a0a0a;
    transition: opacity 0.4s ease;
  `;

  const style = document.createElement('style');
  style.textContent = `
    .loading-content { text-align: center; padding: 2rem; }
    .loading-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem; }
    .loading-subtitle { font-size: 0.9rem; color: #666; margin-bottom: 2rem; }
    .loading-bar-track { width: 200px; height: 4px; background: #222; border-radius: 2px; margin: 0 auto 0.75rem; }
    .loading-bar-fill { height: 100%; width: 0%; background: ${primaryColor}; border-radius: 2px; transition: width 0.2s ease; }
    .loading-status { font-size: 0.75rem; color: #555; }
  `;
  document.head.appendChild(style);
  container.appendChild(overlay);

  const fill = overlay.querySelector('.loading-bar-fill');
  const status = overlay.querySelector('.loading-status');

  return {
    setProgress(value) {
      fill.style.width = `${Math.min(100, Math.max(0, value * 100))}%`;
    },

    setStatus(text) {
      status.textContent = text;
    },

    hide() {
      overlay.style.opacity = '0';
      setTimeout(() => overlay.remove(), 400);
    },
  };
}
```

- [ ] **Step 2: Verify visually**

Update `main.js` temporarily to show loading screen, then hide after model loads:

```javascript
// Add to top of main.js init flow
import { createLoadingScreen } from './ui/loading.js';

const loading = createLoadingScreen(app, { name: 'Demo Pizza Co', primaryColor: '#ff6b35' });

loadModel('/models/test.glb', (progress) => {
  loading.setProgress(progress);
}).then((model) => {
  applyTransform(model, { ... });
  scene.add(model);
  loading.hide();
});
```

Run: `npm run dev`
Expected: Orange progress bar fills, "Loading 3D models..." text, fades out when model appears.

- [ ] **Step 3: Commit**

```bash
git add src/ui/loading.js
git commit -m "add branded loading screen with progress bar"
```

---

## Task 9: Menu Carousel & Item Info UI

**Files:**
- Create: `src/ui/menu-carousel.js`
- Create: `src/ui/item-info.js`

- [ ] **Step 1: Create item-info.js**

```javascript
// src/ui/item-info.js

/**
 * Bottom panel showing current item's name, price, description.
 */
export function createItemInfo(container) {
  const el = document.createElement('div');
  el.id = 'item-info';
  el.style.cssText = `
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
    background: linear-gradient(transparent, rgba(0,0,0,0.85) 30%);
    padding: 2.5rem 1.25rem 1.25rem;
    pointer-events: none;
  `;
  el.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
      <span id="item-name" style="font-weight:700;font-size:1.05rem;"></span>
      <span id="item-price" style="font-weight:700;font-size:1.05rem;color:#7aff7a;"></span>
    </div>
    <p id="item-desc" style="font-size:0.8rem;color:#999;margin:0;"></p>
  `;
  container.appendChild(el);

  const nameEl = el.querySelector('#item-name');
  const priceEl = el.querySelector('#item-price');
  const descEl = el.querySelector('#item-desc');

  return {
    update(item) {
      nameEl.textContent = item.name;
      priceEl.textContent = item.price;
      descEl.textContent = item.description;
    },
  };
}
```

- [ ] **Step 2: Create menu-carousel.js**

```javascript
// src/ui/menu-carousel.js

/**
 * Swipe navigation with dot indicators.
 * @param {HTMLElement} container
 * @param {{ total: number, onChange: (index: number) => void }} options
 */
export function createMenuCarousel(container, { total, onChange }) {
  let current = 0;

  // Dot indicators
  const dotsEl = document.createElement('div');
  dotsEl.id = 'carousel-dots';
  dotsEl.style.cssText = `
    position: fixed; bottom: 5.5rem; left: 0; right: 0; z-index: 100;
    display: flex; justify-content: center; gap: 6px;
    pointer-events: none;
  `;
  for (let i = 0; i < total; i++) {
    const dot = document.createElement('div');
    dot.style.cssText = `width:8px;height:8px;border-radius:50%;background:${i === 0 ? '#7a7aff' : '#444'};transition:background 0.2s;`;
    dot.dataset.index = i;
    dotsEl.appendChild(dot);
  }
  container.appendChild(dotsEl);

  // Swipe hint
  const hint = document.createElement('div');
  hint.id = 'swipe-hint';
  hint.textContent = '← swipe to browse →';
  hint.style.cssText = `
    position: fixed; bottom: 4.75rem; left: 0; right: 0; z-index: 100;
    text-align: center; font-size: 0.7rem; color: #444;
    pointer-events: none; transition: opacity 0.5s;
  `;
  container.appendChild(hint);

  // Touch swipe detection
  let touchStartX = 0;
  let touchStartY = 0;
  const SWIPE_THRESHOLD = 50;

  container.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
  }, { passive: true });

  container.addEventListener('touchend', (e) => {
    const dx = e.changedTouches[0].clientX - touchStartX;
    const dy = e.changedTouches[0].clientY - touchStartY;
    // Only register horizontal swipes
    if (Math.abs(dx) > SWIPE_THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
      if (dx < 0) goTo(current + 1); // swipe left → next
      else goTo(current - 1);        // swipe right → prev
      // Hide hint after first swipe
      hint.style.opacity = '0';
    }
  }, { passive: true });

  function goTo(index) {
    const len = total;
    current = ((index % len) + len) % len;
    // Update dots
    dotsEl.querySelectorAll('div').forEach((dot, i) => {
      dot.style.background = i === current ? '#7a7aff' : '#444';
    });
    onChange(current);
  }

  return {
    current() { return current; },
    goTo,
  };
}
```

- [ ] **Step 3: Verify visually**

Wire both into `main.js` — show item info and carousel dots. Swipe to cycle console logs.

Run: `npm run dev` on mobile.
Expected: Bottom bar shows item name + price. Dots visible. Swipe changes active dot and logs new index.

- [ ] **Step 4: Commit**

```bash
git add src/ui/menu-carousel.js src/ui/item-info.js
git commit -m "add menu carousel with swipe navigation and item info panel"
```

---

## Task 10: Layer 1 Integration — Full 3D Viewer

**Files:**
- Modify: `src/main.js`

Wire everything together: config → scene → model loading → carousel → item info. This is the Layer 1 complete experience.

- [ ] **Step 1: Implement main.js orchestration**

```javascript
// src/main.js
import { createScene } from './viewer/scene.js';
import { loadModel, applyTransform, preloadModels } from './viewer/model-loader.js';
import { createControls } from './viewer/controls.js';
import { createLoadingScreen } from './ui/loading.js';
import { createItemInfo } from './ui/item-info.js';
import { createMenuCarousel } from './ui/menu-carousel.js';
import { loadMenuConfig, getItemByIndex } from './config/menu-loader.js';
import { createStateMachine } from './utils/state.js';
import { detectLiveFeatures } from './utils/device.js';

const app = document.getElementById('app');

async function init() {
  // 1. Load config
  const config = await loadMenuConfig('/menu.json');
  const { restaurant, items } = config;

  // 2. Detect features
  const features = await detectLiveFeatures();

  // 3. Show loading screen
  const loading = createLoadingScreen(app, {
    name: restaurant.name,
    primaryColor: restaurant.branding.primaryColor,
  });

  // 4. State machine
  const sm = createStateMachine({
    initial: 'LOADING',
    states: {
      LOADING:   { LOADED: 'VIEWING' },
      VIEWING:   { START_AR: 'SCANNING', START_NATIVE: 'NATIVE_AR' },
      NATIVE_AR: { BACK: 'VIEWING' },
      SCANNING:  { TARGET_FOUND: 'TRACKING', BACK: 'VIEWING' },
      TRACKING:  { TARGET_LOST: 'STICKY', BACK: 'VIEWING' },
      STICKY:    { TARGET_FOUND: 'TRACKING', TIMEOUT: 'VIEWING', BACK: 'VIEWING' },
    },
  });

  // 5. Create scene
  const { scene, camera, renderer, startLoop } = createScene(app);
  const controls = createControls(camera, renderer.domElement);

  // 6. Load first model
  let currentModel = null;
  let currentIndex = 0;

  async function showItem(index) {
    const item = getItemByIndex(items, index);
    loading.setStatus(`Loading ${item.name}...`);

    // Remove old model
    if (currentModel) {
      scene.remove(currentModel);
      currentModel = null;
    }

    const model = await loadModel(item.models.glb, (p) => loading.setProgress(p));
    applyTransform(model, item.transform);
    scene.add(model);
    currentModel = model;
    currentIndex = index;

    // Reset camera for new model
    camera.position.set(0, 0.3, 0.6);
    camera.lookAt(0, 0, 0);
    controls.update();
  }

  await showItem(0);

  // 7. Hide loading, show UI
  loading.hide();
  sm.send('LOADED');

  const itemInfo = createItemInfo(app);
  itemInfo.update(getItemByIndex(items, 0));

  const carousel = createMenuCarousel(app, {
    total: items.length,
    onChange: async (index) => {
      await showItem(index);
      itemInfo.update(getItemByIndex(items, index));
    },
  });

  // 8. Preload adjacent models
  const preloadUrls = items.slice(1, 3).map((i) => i.models.glb);
  preloadModels(preloadUrls);

  // 9. Start render loop
  startLoop((delta) => {
    controls.update();
  });

  // 10. Log features for debugging
  console.log('Features:', features);
  console.log('State:', sm.current());
}

init().catch((err) => {
  console.error('Failed to initialize AR Menu:', err);
  document.getElementById('app').innerHTML = `
    <div style="display:flex;align-items:center;justify-content:center;height:100vh;text-align:center;padding:2rem;">
      <div>
        <h2>Something went wrong</h2>
        <p style="color:#666;margin-top:0.5rem;">${err.message}</p>
      </div>
    </div>
  `;
});
```

- [ ] **Step 2: Verify full Layer 1 flow**

Run: `npm run dev` on mobile.
Expected:
- Loading screen with "Demo Pizza Co" branding
- Progress bar fills
- 3D model appears (placeholder test.glb for now)
- Bottom bar shows item name + price
- Swipe changes item (model swaps, info updates)
- Pinch to zoom, drag to rotate
- Dots track current position

- [ ] **Step 3: Run all tests**

Run: `npm test`
Expected: All unit tests pass (state machine, device detection, menu config).

- [ ] **Step 4: Commit**

```bash
git add src/main.js
git commit -m "integrate Layer 1: full 3D viewer with carousel and item info"
```

---

## Task 11: Layer 2 — Native AR Launcher

**Files:**
- Create: `src/native-ar/launcher.js`
- Create: `tests/native-ar/launcher.test.js`

- [ ] **Step 1: Write failing tests**

```javascript
// tests/native-ar/launcher.test.js
import { describe, it, expect } from 'vitest';
import { getNativeARUrl, canQuickLook } from '../../src/native-ar/launcher.js';

describe('getNativeARUrl', () => {
  it('returns Scene Viewer URL for Android', () => {
    const url = getNativeARUrl({
      glb: 'models/pizza.glb',
      title: 'Margherita',
      isIOS: false,
    });
    expect(url).toContain('intent://arvr.google.com/scene-viewer');
    expect(url).toContain('pizza.glb');
    expect(url).toContain('Margherita');
  });

  it('returns null for iOS without USDZ', () => {
    const url = getNativeARUrl({
      glb: 'models/pizza.glb',
      usdz: null,
      title: 'Margherita',
      isIOS: true,
    });
    expect(url).toBeNull();
  });

  it('returns USDZ data URL for iOS with USDZ', () => {
    const url = getNativeARUrl({
      glb: 'models/pizza.glb',
      usdz: 'models/pizza.usdz',
      title: 'Margherita',
      isIOS: true,
    });
    expect(url).toContain('pizza.usdz');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run tests/native-ar/launcher.test.js`
Expected: FAIL

- [ ] **Step 3: Implement launcher**

```javascript
// src/native-ar/launcher.js

/**
 * Build the URL to launch native AR viewer.
 * Android → Scene Viewer intent URL.
 * iOS → USDZ file URL (triggers Quick Look via <a rel="ar">).
 */
export function getNativeARUrl({ glb, usdz, title, isIOS }) {
  if (isIOS) {
    if (!usdz) return null;
    return usdz;
  }

  // Android Scene Viewer intent
  const modelUrl = new URL(glb, window.location.href).href;
  return `intent://arvr.google.com/scene-viewer/1.0?file=${encodeURIComponent(modelUrl)}&mode=ar_preferred&title=${encodeURIComponent(title)}#Intent;scheme=https;package=com.google.android.googlequicksearchbox;action=android.intent.action.VIEW;end;`;
}

/**
 * Launch native AR for the given item.
 * iOS: creates a temporary <a rel="ar"> link and clicks it (Quick Look).
 * Android: navigates to Scene Viewer intent.
 */
export function launchNativeAR({ glb, usdz, title, isIOS }) {
  const url = getNativeARUrl({ glb, usdz, title, isIOS });
  if (!url) return false;

  if (isIOS && usdz) {
    // Quick Look requires <a rel="ar"> with a child <img>
    const a = document.createElement('a');
    a.rel = 'ar';
    a.href = new URL(usdz, window.location.href).href;
    const img = document.createElement('img'); // required child
    a.appendChild(img);
    document.body.appendChild(a);
    a.click();
    setTimeout(() => a.remove(), 100);
    return true;
  }

  // Android Scene Viewer
  window.location.href = url;
  return true;
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run tests/native-ar/launcher.test.js`
Expected: 3 tests PASS

- [ ] **Step 5: Add "View in AR" button to main.js**

Add after the carousel setup in `main.js`:

```javascript
// In init(), after carousel setup:

// Layer 2: Native AR button
if (features.canNativeAR) {
  const arBtn = document.createElement('button');
  arBtn.id = 'ar-button';
  arBtn.textContent = 'View in AR';
  arBtn.style.cssText = `
    position: fixed; bottom: 8rem; right: 1rem; z-index: 100;
    padding: 0.6rem 1.2rem; border: none; border-radius: 2rem;
    background: ${restaurant.branding.primaryColor}; color: #fff;
    font-size: 0.85rem; font-weight: 600; cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  `;
  arBtn.addEventListener('click', async () => {
    const { launchNativeAR } = await import('./native-ar/launcher.js');
    const item = getItemByIndex(items, currentIndex);
    sm.send('START_NATIVE');
    launchNativeAR({
      glb: item.models.glb,
      usdz: item.models.usdz,
      title: item.name,
      isIOS: features.isIOS,
    });
  });
  app.appendChild(arBtn);
}
```

- [ ] **Step 6: Verify on Android/iOS**

Run: `npm run dev` on mobile. Expected:
- Android: "View in AR" button visible. Tap → Scene Viewer opens (will fail without real model but intent URL is correct).
- iOS: "View in AR" button visible. Tap → Quick Look opens (will fail without .usdz but anchor click fires).

- [ ] **Step 7: Commit**

```bash
git add src/native-ar/launcher.js tests/native-ar/launcher.test.js src/main.js
git commit -m "add Layer 2: native AR launcher for Quick Look and Scene Viewer"
```

---

## Task 12: Demo Content — Stock 3D Models

**Files:**
- Modify: `public/models/` (add stock GLB files)
- Modify: `menu.json` (update paths if needed)

This task is partially manual — sourcing and downloading models from Sketchfab.

- [ ] **Step 1: Source free food models**

Search Sketchfab for CC-licensed food models. Target 5 items:
1. Pizza (margherita)
2. Pizza (pepperoni) or pasta
3. Pasta / noodle dish
4. Dessert (cake, tiramisu)
5. Appetizer (bruschetta, bread)

Download as `.glb` format. Prioritize models under 5MB — we'll optimize in the next step.

Place downloaded files in `public/models/` matching the `menu.json` IDs.

- [ ] **Step 2: Optimize models with glTF-Transform**

```bash
npm install -g @gltf-transform/cli

# For each model:
gltf-transform optimize public/models/margherita.glb public/models/margherita.glb \
  --texture-resize 512 \
  --simplify --simplify-ratio 0.5 \
  --dedup --prune
```

Verify each output is < 2MB. If still too large, reduce `--simplify-ratio` or `--texture-resize 256`.

- [ ] **Step 3: Create placeholder .usdz files**

For the demo, create empty placeholder text files so the JSON doesn't error. Real USDZ conversion is a manual step documented in the spec.

```bash
for item in margherita pepperoni pasta-carbonara tiramisu bruschetta; do
  echo "placeholder" > public/models/${item}.usdz
done
```

Note: Quick Look won't work with placeholders. This is expected for demo. Document in README.

- [ ] **Step 4: Create a placeholder menu target**

```bash
mkdir -p public/targets
echo "placeholder" > public/targets/menu.mind
```

Real `.mind` file is compiled in Task 13 when we set up MindAR.

- [ ] **Step 5: Update menu.json if model names differ**

If downloaded models have different filenames, update `menu.json` to match.

- [ ] **Step 6: Verify all models load**

Run: `npm run dev`. Swipe through all items. Each should render a 3D model with proper materials.

- [ ] **Step 7: Remove test.glb placeholder**

```bash
rm public/models/test.glb
```

- [ ] **Step 8: Commit**

```bash
git add public/models/ public/targets/ menu.json
git commit -m "add stock food models for demo menu"
```

---

## Task 13: Layer 3 — MindAR Image Tracking

**Files:**
- Create: `src/ar/mind-ar.js`
- Create: `src/ar/sticky-mode.js`
- Create: `src/ar/hud.js`
- Create: `tests/ar/sticky-mode.test.js`

- [ ] **Step 1: Install MindAR**

```bash
npm install mind-ar@1.2.5
```

- [ ] **Step 2: Write sticky mode tests**

```javascript
// tests/ar/sticky-mode.test.js
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createStickyMode } from '../../src/ar/sticky-mode.js';

describe('createStickyMode', () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  it('calls onTimeout after specified delay', () => {
    const onTimeout = vi.fn();
    const sticky = createStickyMode({ timeoutMs: 10000, onTimeout });
    sticky.start();
    vi.advanceTimersByTime(10000);
    expect(onTimeout).toHaveBeenCalledOnce();
  });

  it('cancels timeout on stop', () => {
    const onTimeout = vi.fn();
    const sticky = createStickyMode({ timeoutMs: 10000, onTimeout });
    sticky.start();
    vi.advanceTimersByTime(5000);
    sticky.stop();
    vi.advanceTimersByTime(10000);
    expect(onTimeout).not.toHaveBeenCalled();
  });

  it('resets timeout on restart', () => {
    const onTimeout = vi.fn();
    const sticky = createStickyMode({ timeoutMs: 10000, onTimeout });
    sticky.start();
    vi.advanceTimersByTime(8000);
    sticky.stop();
    sticky.start(); // restart
    vi.advanceTimersByTime(8000);
    expect(onTimeout).not.toHaveBeenCalled(); // only 8s into new timer
    vi.advanceTimersByTime(2000);
    expect(onTimeout).toHaveBeenCalledOnce();
  });

  it('reports active state', () => {
    const sticky = createStickyMode({ timeoutMs: 10000, onTimeout: () => {} });
    expect(sticky.isActive()).toBe(false);
    sticky.start();
    expect(sticky.isActive()).toBe(true);
    sticky.stop();
    expect(sticky.isActive()).toBe(false);
  });
});
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `npx vitest run tests/ar/sticky-mode.test.js`
Expected: FAIL

- [ ] **Step 4: Implement sticky mode**

```javascript
// src/ar/sticky-mode.js

/**
 * Manages the sticky mode timer.
 * When the AR target is lost, starts a countdown.
 * If the target isn't re-found within timeoutMs, calls onTimeout.
 */
export function createStickyMode({ timeoutMs = 10000, onTimeout }) {
  let timerId = null;
  let active = false;

  return {
    start() {
      this.stop();
      active = true;
      timerId = setTimeout(() => {
        active = false;
        onTimeout();
      }, timeoutMs);
    },

    stop() {
      if (timerId) clearTimeout(timerId);
      timerId = null;
      active = false;
    },

    isActive() {
      return active;
    },
  };
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `npx vitest run tests/ar/sticky-mode.test.js`
Expected: 4 tests PASS

- [ ] **Step 6: Create AR HUD**

```javascript
// src/ar/hud.js

/**
 * AR overlay UI — scanning indicator + bottom info bar.
 */
export function createARHud(container) {
  const overlay = document.createElement('div');
  overlay.id = 'ar-hud';
  overlay.style.cssText = `
    position: fixed; inset: 0; z-index: 200;
    pointer-events: none; display: none;
  `;
  overlay.innerHTML = `
    <div id="ar-scan-guide" style="
      position:absolute; top:30%; left:50%; transform:translateX(-50%);
      text-align:center;
    ">
      <div style="
        border: 2px dashed rgba(122,122,255,0.4); width:180px; height:120px;
        border-radius:8px; margin:0 auto 1rem;
      "></div>
      <p style="font-size:0.85rem;color:#999;">Point camera at the menu</p>
    </div>
    <button id="ar-back-btn" style="
      position:absolute; top:1rem; left:1rem; pointer-events:auto;
      background:rgba(0,0,0,0.5); border:none; color:#fff;
      padding:0.5rem 1rem; border-radius:2rem; font-size:0.85rem;
      cursor:pointer; backdrop-filter:blur(4px);
    ">✕ Close</button>
    <div id="ar-sticky-indicator" style="
      position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
      font-size:0.75rem; color:#ffaa55; display:none;
    ">Point at menu to continue</div>
  `;
  container.appendChild(overlay);

  const scanGuide = overlay.querySelector('#ar-scan-guide');
  const stickyIndicator = overlay.querySelector('#ar-sticky-indicator');
  const backBtn = overlay.querySelector('#ar-back-btn');

  return {
    show() { overlay.style.display = 'block'; },
    hide() { overlay.style.display = 'none'; },
    showScanning() { scanGuide.style.display = 'block'; stickyIndicator.style.display = 'none'; },
    showTracking() { scanGuide.style.display = 'none'; stickyIndicator.style.display = 'none'; },
    showSticky() { scanGuide.style.display = 'none'; stickyIndicator.style.display = 'block'; },
    onBack(fn) { backBtn.addEventListener('click', fn); },
  };
}
```

- [ ] **Step 7: Implement MindAR integration**

```javascript
// src/ar/mind-ar.js

/**
 * Initialize and manage MindAR image tracking session.
 * Dynamically imports MindAR to keep it out of the initial bundle.
 */
export async function createMindARSession({ container, targetSrc, renderer, scene, camera }) {
  const { MindARThree } = await import('mind-ar/dist/mindar-image-three.prod.js');

  const mindar = new MindARThree({
    container,
    imageTargetSrc: targetSrc,
    filterMinCF: 0.001,
    filterBeta: 1000,
    warmupTolerance: 5,
    missTolerance: 5,
    maxTrack: 1,
  });

  const anchor = mindar.addAnchor(0);
  let onFound = null;
  let onLost = null;

  anchor.onTargetFound = () => { if (onFound) onFound(); };
  anchor.onTargetLost = () => { if (onLost) onLost(); };

  return {
    anchor,

    async start() {
      await mindar.start();
    },

    stop() {
      mindar.stop();
    },

    onTargetFound(fn) { onFound = fn; },
    onTargetLost(fn) { onLost = fn; },

    getAnchorGroup() {
      return anchor.group;
    },
  };
}
```

- [ ] **Step 8: Add "Scan Menu" button to main.js**

Add after the native AR button in `main.js`:

```javascript
// Layer 3: MindAR button (feature-detected)
if (features.canMindAR) {
  const scanBtn = document.createElement('button');
  scanBtn.id = 'scan-button';
  scanBtn.textContent = 'Scan Menu';
  scanBtn.style.cssText = `
    position: fixed; bottom: 8rem; left: 1rem; z-index: 100;
    padding: 0.6rem 1.2rem; border: 1px solid #555; border-radius: 2rem;
    background: rgba(0,0,0,0.6); color: #fff;
    font-size: 0.85rem; font-weight: 600; cursor: pointer;
    backdrop-filter: blur(4px);
  `;
  scanBtn.addEventListener('click', async () => {
    try {
      const { createMindARSession } = await import('./ar/mind-ar.js');
      const { createARHud } = await import('./ar/hud.js');
      const { createStickyMode } = await import('./ar/sticky-mode.js');

      // Hide Layer 1 UI
      controls.enabled = false;

      const hud = createARHud(app);
      hud.show();
      hud.showScanning();

      const session = await createMindARSession({
        container: app,
        targetSrc: config.targetImage,
        renderer,
        scene,
        camera,
      });

      const sticky = createStickyMode({
        timeoutMs: 10000,
        onTimeout: () => {
          sm.send('TIMEOUT');
          session.stop();
          hud.hide();
          controls.enabled = true;
        },
      });

      let arModel = null;
      session.onTargetFound(() => {
        sm.send('TARGET_FOUND');
        sticky.stop();
        hud.showTracking();
        // Add current model to anchor (clear previous first)
        if (arModel) session.getAnchorGroup().remove(arModel);
        const item = getItemByIndex(items, currentIndex);
        loadModel(item.models.glb).then((model) => {
          applyTransform(model, item.transform);
          if (arModel) session.getAnchorGroup().remove(arModel);
          arModel = model;
          session.getAnchorGroup().add(model);
        });
      });

      session.onTargetLost(() => {
        sm.send('TARGET_LOST');
        sticky.start();
        hud.showSticky();
      });

      hud.onBack(() => {
        sm.send('BACK');
        session.stop();
        sticky.stop();
        hud.hide();
        controls.enabled = true;
      });

      sm.send('START_AR');
      await session.start();
    } catch (err) {
      console.error('MindAR failed:', err);
      scanBtn.style.display = 'none';
    }
  });
  app.appendChild(scanBtn);
}
```

- [ ] **Step 9: Run all tests**

Run: `npm test`
Expected: All tests pass (state machine, device detection, menu config, sticky mode, native AR launcher).

- [ ] **Step 10: Commit**

```bash
git add src/ar/mind-ar.js src/ar/sticky-mode.js src/ar/hud.js tests/ar/sticky-mode.test.js src/main.js package.json package-lock.json
git commit -m "add Layer 3: MindAR image tracking with sticky mode and AR HUD"
```

---

## Task 14: In-App Browser Warning

**Files:**
- Modify: `src/main.js`

- [ ] **Step 1: Add in-app browser detection to init**

At the very top of `init()` in `main.js`, before anything else:

```javascript
// In-app browser gate (before any heavy loading)
const features = await detectLiveFeatures();
if (features.isInAppBrowser) {
  app.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:center;height:100vh;text-align:center;padding:2rem;">
      <div>
        <h2 style="margin-bottom:0.5rem;">Open in your browser</h2>
        <p style="color:#999;margin-bottom:1.5rem;font-size:0.9rem;">
          This AR experience needs ${features.isIOS ? 'Safari' : 'Chrome'} to access your camera.
        </p>
        <button id="copy-link" style="
          padding:0.75rem 1.5rem;border:none;border-radius:2rem;
          background:#ff6b35;color:#fff;font-size:0.9rem;font-weight:600;cursor:pointer;
        ">Copy Link</button>
        <p id="copy-confirm" style="color:#7aff7a;font-size:0.8rem;margin-top:0.75rem;display:none;">Copied!</p>
      </div>
    </div>
  `;
  document.getElementById('copy-link').addEventListener('click', async () => {
    await navigator.clipboard.writeText(window.location.href);
    document.getElementById('copy-confirm').style.display = 'block';
  });
  return;
}
```

Move `detectLiveFeatures()` call to the very start of init, before loading screen.

- [ ] **Step 2: Verify**

Test by spoofing user agent in Chrome DevTools (set to include "FBAN" or "Instagram").
Expected: Shows "Open in your browser" screen with "Copy Link" button instead of the AR experience.

- [ ] **Step 3: Commit**

```bash
git add src/main.js
git commit -m "add in-app browser detection with copy-link fallback"
```

---

## Task 15: Mobile Polish & Error Handling

**Files:**
- Modify: `public/index.html`
- Modify: `src/main.js`

- [ ] **Step 1: Add mobile meta tags and global styles to index.html**

```html
<!-- Add to <head> -->
<meta name="theme-color" content="#0a0a0a">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="/manifest.json">
```

Add touch-action CSS to prevent accidental browser gestures:

```css
/* Add to existing <style> block */
#app { touch-action: none; }
canvas { display: block; }
```

- [ ] **Step 2: Create minimal manifest.json**

```json
{
  "name": "AR Menu",
  "short_name": "AR Menu",
  "display": "standalone",
  "background_color": "#0a0a0a",
  "theme_color": "#0a0a0a"
}
```

Place in `public/manifest.json`.

- [ ] **Step 3: Improve error handling in main.js**

The error catch in `init()` already shows a fallback screen. Add a network-aware loading message:

```javascript
// In init(), before loadMenuConfig:
if (!navigator.onLine) {
  loading.setStatus('Waiting for network...');
  await new Promise((resolve) => window.addEventListener('online', resolve, { once: true }));
}
```

- [ ] **Step 4: Verify on mobile**

Run: `npm run dev` on phone.
Expected:
- No bounce/scroll behavior
- Touch gestures work smoothly
- Status bar integrates with dark theme
- Offline state shows waiting message

- [ ] **Step 5: Commit**

```bash
git add public/index.html public/manifest.json src/main.js
git commit -m "add mobile polish: meta tags, manifest, touch handling, offline detection"
```

---

## Task 16: Final Integration Test & Cleanup

**Files:**
- Modify: `src/main.js` (cleanup temp code)

- [ ] **Step 1: Run full test suite**

```bash
npm test
```

Expected: All tests pass.

- [ ] **Step 2: Run production build**

```bash
npm run build
```

Expected: Build completes with no errors. Output in `dist/`.

- [ ] **Step 3: Preview production build**

```bash
npm run preview
```

Open on mobile. Verify the full flow:
1. Loading screen → 3D viewer
2. Swipe between items
3. Rotate/zoom model
4. "View in AR" button visible (if supported)
5. "Scan Menu" button visible (if supported)

- [ ] **Step 4: Clean up main.js**

Remove any console.log statements except error logging. Ensure no temp test code remains.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "final cleanup and production build verification"
```

---

## Task 17: Deploy to Vercel

**Files:**
- Create: `vercel.json` (optional, for config)

- [ ] **Step 1: Create vercel.json**

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": null
}
```

- [ ] **Step 2: Deploy**

```bash
npx vercel --prod
```

Follow prompts to link to Vercel project.

- [ ] **Step 3: Verify deployed URL**

Open the Vercel URL on a mobile device. Verify:
- HTTPS is active (required for camera)
- Loading screen appears
- 3D models load from the deployed static files
- Swipe/rotate work
- AR buttons appear on supported devices

- [ ] **Step 4: Commit deployment config**

```bash
git add vercel.json
git commit -m "add Vercel deployment config"
```

---

## Summary

| Task | What | Tests |
|------|------|-------|
| 1 | Project scaffolding (Vite + Three.js) | — |
| 2 | State machine | 6 unit tests |
| 3 | Device detection | 12 unit tests |
| 4 | Menu config loader | 7 unit tests |
| 5 | Three.js scene setup | Visual |
| 6 | GLB model loader | Visual |
| 7 | Orbit controls | Visual + mobile |
| 8 | Loading screen | Visual |
| 9 | Menu carousel & item info | Visual + mobile |
| 10 | Layer 1 full integration | Visual + mobile + unit tests |
| 11 | Layer 2: Native AR | 3 unit tests + mobile |
| 12 | Demo content (stock models) | Visual |
| 13 | Layer 3: MindAR + sticky + HUD | 4 unit tests + mobile |
| 14 | In-app browser warning | Manual |
| 15 | Mobile polish | Manual |
| 16 | Final integration test | All tests + build |
| 17 | Deploy to Vercel | Live URL |

**Total: 17 tasks, ~32 unit tests, 17 commits**
