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

  // 10. Layer 2: Native AR button
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

  // 11. Layer 3: MindAR button (feature-detected)
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
        controls.enabled = true;
      }
    });
    app.appendChild(scanBtn);
  }
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
