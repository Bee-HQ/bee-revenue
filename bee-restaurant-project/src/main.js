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
  // 1. Detect features first (in-app browser gate)
  const features = await detectLiveFeatures();

  // In-app browser gate (before any heavy loading)
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

  // 2. Load config
  const config = await loadMenuConfig('/menu.json');
  const { restaurant, items } = config;

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

    if (currentModel) {
      scene.remove(currentModel);
      currentModel = null;
    }

    const model = await loadModel(item.models.glb, (p) => loading.setProgress(p));
    applyTransform(model, item.transform);
    scene.add(model);
    currentModel = model;
    currentIndex = index;

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

  // 10. Store references for later use by Layer 2 and Layer 3
  window.__arMenu = { config, features, sm, scene, camera, renderer, controls, items, currentIndex, showItem, getItemByIndex };
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
