# AR Smart Menu Bug Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 8 bugs found during Chrome testing — 2 critical (crashes/stuck state), 2 major (broken UX), 4 moderate/minor (security, polish).

**Architecture:** File-grouped fixes. Each task touches one source file + its test file. All fixes are backward-compatible — no API changes, no new dependencies.

**Tech Stack:** Vanilla JS, Three.js, MindAR.js, Vitest

---

### Task 1: Fix device detection — "View in AR" incorrectly shows on desktop

Desktop Chrome has `navigator.xr` (for VR headsets), which makes `canNativeAR` true even though Scene Viewer/Quick Look won't work. The fix: require mobile platform detection, not just WebXR presence.

**Files:**
- Modify: `src/utils/device.js:21` (the `canNativeAR` formula)
- Modify: `tests/utils/device.test.js` (add desktop Chrome test case)

- [ ] **Step 1: Write failing test — desktop Chrome with WebXR should NOT get canNativeAR**

Add to `tests/utils/device.test.js` inside the `detectFeatures` describe block:

```js
it('marks canNativeAR false for desktop Chrome with WebXR', () => {
  const features = detectFeatures({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    mediaDevices: { getUserMedia: () => {} },
    xrSystem: { isSessionSupported: () => Promise.resolve(true) },
    platform: 'MacIntel',
  });
  expect(features.canNativeAR).toBe(false);
});

it('marks canNativeAR true for Android with camera (no WebXR needed)', () => {
  const features = detectFeatures({
    userAgent: 'Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36',
    mediaDevices: { getUserMedia: () => {} },
    xrSystem: null,
    platform: 'Linux armv8l',
  });
  expect(features.canNativeAR).toBe(true);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/mk/work/bee-revenue/bee-restaurant-project && npm test -- tests/utils/device.test.js`
Expected: FAIL — desktop Chrome test expects `false` but gets `true`

- [ ] **Step 3: Fix canNativeAR formula**

In `src/utils/device.js`, change line 21 from:
```js
canNativeAR: canQuickLook || hasWebXR || (isAndroid && hasCamera),
```
to:
```js
canNativeAR: (isIOS && canQuickLook) || (isAndroid && hasCamera),
```

This removes the `hasWebXR` check entirely. Native AR on Android uses Scene Viewer (intent URL), which doesn't need WebXR — it just needs to be Android with a camera. iOS uses Quick Look. Desktop gets neither.

Also rename the existing test at line 93 from `'marks canNativeAR true for Android with WebXR'` to `'marks canNativeAR true for Android with camera'` — the test still passes but the name was misleading (it passes because of Android+camera, not WebXR).

- [ ] **Step 4: Run tests to verify all pass**

Run: `cd /Users/mk/work/bee-revenue/bee-restaurant-project && npm test -- tests/utils/device.test.js`
Expected: All PASS

---

### Task 2: Fix carousel — add keyboard and clickable dot navigation for desktop

The carousel only has `touchstart`/`touchend` handlers. Desktop users can't navigate between menu items at all.

**Files:**
- Modify: `src/ui/menu-carousel.js` (add keyboard + dot click listeners)
- Create: `tests/ui/menu-carousel.test.js`

- [ ] **Step 1: Write failing tests for keyboard and dot click navigation**

Create `tests/ui/menu-carousel.test.js`:

```js
// @vitest-environment jsdom
import { describe, it, expect, vi } from 'vitest';
import { createMenuCarousel } from '../../src/ui/menu-carousel.js';

describe('createMenuCarousel', () => {
  function setup(total = 5) {
    const container = document.createElement('div');
    const onChange = vi.fn();
    const carousel = createMenuCarousel(container, { total, onChange });
    return { container, onChange, carousel };
  }

  it('navigates forward on ArrowRight key', () => {
    const { onChange } = setup();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }));
    expect(onChange).toHaveBeenCalledWith(1);
  });

  it('navigates backward on ArrowLeft key', () => {
    const { onChange, carousel } = setup();
    carousel.goTo(2);
    onChange.mockClear();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }));
    expect(onChange).toHaveBeenCalledWith(1);
  });

  it('wraps around from last to first on ArrowRight', () => {
    const { onChange, carousel } = setup(3);
    carousel.goTo(2);
    onChange.mockClear();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }));
    expect(onChange).toHaveBeenCalledWith(0);
  });

  it('wraps around from first to last on ArrowLeft', () => {
    const { onChange } = setup(3);
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }));
    expect(onChange).toHaveBeenCalledWith(2);
  });

  it('navigates to item when dot is clicked', () => {
    const { container, onChange } = setup(5);
    const dots = container.querySelectorAll('#carousel-dots div');
    dots[3].click();
    expect(onChange).toHaveBeenCalledWith(3);
  });

  it('updates dot styles on navigation', () => {
    const { container, carousel } = setup(3);
    carousel.goTo(1);
    const dots = container.querySelectorAll('#carousel-dots div');
    expect(dots[1].style.background).toBe('#7a7aff');
    expect(dots[0].style.background).toBe('#444');
  });

  it('renders correct number of dots', () => {
    const { container } = setup(5);
    const dots = container.querySelectorAll('#carousel-dots div');
    expect(dots).toHaveLength(5);
  });

  it('cleans up keyboard listener on destroy', () => {
    const { onChange, carousel } = setup();
    carousel.destroy();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }));
    expect(onChange).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/mk/work/bee-revenue/bee-restaurant-project && npm test -- tests/ui/menu-carousel.test.js`
Expected: FAIL — no keyboard handling, no dot click, no destroy method

- [ ] **Step 3: Implement keyboard, dot click, and destroy in menu-carousel.js**

Replace `src/ui/menu-carousel.js` with:

```js
// src/ui/menu-carousel.js
export function createMenuCarousel(container, { total, onChange }) {
  let current = 0;

  const dotsEl = document.createElement('div');
  dotsEl.id = 'carousel-dots';
  dotsEl.style.cssText = `
    position: fixed; bottom: 5.5rem; left: 0; right: 0; z-index: 100;
    display: flex; justify-content: center; gap: 6px;
  `;
  for (let i = 0; i < total; i++) {
    const dot = document.createElement('div');
    dot.style.cssText = `width:8px;height:8px;border-radius:50%;background:${i === 0 ? '#7a7aff' : '#444'};transition:background 0.2s;cursor:pointer;`;
    dot.dataset.index = i;
    dot.addEventListener('click', () => goTo(i));
    dotsEl.appendChild(dot);
  }
  container.appendChild(dotsEl);

  const hint = document.createElement('div');
  hint.id = 'swipe-hint';
  hint.textContent = '\u2190 swipe to browse \u2192';
  hint.style.cssText = `
    position: fixed; bottom: 4.75rem; left: 0; right: 0; z-index: 100;
    text-align: center; font-size: 0.7rem; color: #444;
    pointer-events: none; transition: opacity 0.5s;
  `;
  container.appendChild(hint);

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
    if (Math.abs(dx) > SWIPE_THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
      if (dx < 0) goTo(current + 1);
      else goTo(current - 1);
      hint.style.opacity = '0';
    }
  }, { passive: true });

  function onKeyDown(e) {
    if (e.key === 'ArrowRight') { goTo(current + 1); hint.style.opacity = '0'; }
    else if (e.key === 'ArrowLeft') { goTo(current - 1); hint.style.opacity = '0'; }
  }
  window.addEventListener('keydown', onKeyDown);

  function goTo(index) {
    const len = total;
    current = ((index % len) + len) % len;
    dotsEl.querySelectorAll('div').forEach((dot, i) => {
      dot.style.background = i === current ? '#7a7aff' : '#444';
    });
    onChange(current);
  }

  function destroy() {
    window.removeEventListener('keydown', onKeyDown);
  }

  return {
    current() { return current; },
    goTo,
    destroy,
  };
}
```

Key changes: dots are clickable (removed `pointer-events: none` from dotsEl, added `cursor:pointer` + click listener to each dot), ArrowLeft/ArrowRight keyboard handler on window, `destroy()` method for cleanup.

- [ ] **Step 4: Run tests to verify all pass**

Run: `cd /Users/mk/work/bee-revenue/bee-restaurant-project && npm test -- tests/ui/menu-carousel.test.js`
Expected: All PASS

---

### Task 3: Fix XSS in loading screen

`loading.js` uses `innerHTML` with the restaurant name from `menu.json`. If the name contains HTML, it executes.

**Files:**
- Modify: `src/ui/loading.js:6-15` (use textContent for the name)
- Create: `tests/ui/loading.test.js`

- [ ] **Step 1: Write failing test proving the XSS vulnerability**

Create `tests/ui/loading.test.js`:

```js
// @vitest-environment jsdom
import { describe, it, expect } from 'vitest';
import { createLoadingScreen } from '../../src/ui/loading.js';

describe('createLoadingScreen', () => {
  it('does not execute HTML in restaurant name', () => {
    const container = document.createElement('div');
    createLoadingScreen(container, { name: '<img src=x onerror=alert(1)>' });
    const title = container.querySelector('.loading-title');
    expect(title.textContent).toBe('<img src=x onerror=alert(1)>');
    expect(title.innerHTML).not.toContain('<img');
  });

  it('displays plain text restaurant name correctly', () => {
    const container = document.createElement('div');
    createLoadingScreen(container, { name: 'Demo Pizza Co' });
    const title = container.querySelector('.loading-title');
    expect(title.textContent).toBe('Demo Pizza Co');
  });
});
```

- [ ] **Step 2: Run test to verify the XSS test fails (HTML is currently injected)**

Run: `cd /Users/mk/work/bee-revenue/bee-restaurant-project && npm test -- tests/ui/loading.test.js`
Expected: FAIL — `title.innerHTML` contains `<img` because name is interpolated into innerHTML

- [ ] **Step 3: Fix the loading screen to use textContent for the restaurant name**

In `src/ui/loading.js`, change the `overlay.innerHTML` block (lines 6-15) to build elements safely:

```js
export function createLoadingScreen(container, branding = {}) {
  const { name = 'AR Menu', primaryColor = '#ff6b35' } = branding;

  const overlay = document.createElement('div');
  overlay.id = 'loading-screen';
  overlay.innerHTML = `
    <div class="loading-content">
      <h1 class="loading-title"></h1>
      <p class="loading-subtitle">AR Menu</p>
      <div class="loading-bar-track">
        <div class="loading-bar-fill"></div>
      </div>
      <p class="loading-status">Loading 3D models...</p>
    </div>
  `;
  overlay.querySelector('.loading-title').textContent = name;
  overlay.style.cssText = `
    position: fixed; inset: 0; z-index: 1000;
    display: flex; align-items: center; justify-content: center;
    background: #0a0a0a;
    transition: opacity 0.4s ease;
  `;
```

The rest of the function stays the same. The only change is removing `${name}` from innerHTML and setting it via `textContent` after.

- [ ] **Step 4: Run tests to verify XSS fix and no regressions**

Run: `cd /Users/mk/work/bee-revenue/bee-restaurant-project && npm test`
Expected: All tests PASS (including new loading tests)

---

### Task 4: Fix MindAR crash, UI hiding, canvas cleanup, model swap, and title

This task addresses the remaining bugs, all in `main.js`:
- **Critical:** Close button crash — wrap `session.stop()` in try/catch, use finally for cleanup
- **Major:** UI not hidden during AR — hide buttons/carousel/info when entering AR, show when leaving
- **Moderate:** MindAR canvas leak — remove extra canvas on AR exit
- **Minor:** Model flash — load new model before removing old
- **Minor:** Page title — set `document.title` after config loads

**Files:**
- Modify: `src/main.js`

- [ ] **Step 1: Fix model swap — load before remove**

In `src/main.js`, change the `showItem` function (around lines 73-91). Move `scene.remove(currentModel)` to AFTER the new model loads:

```js
  async function showItem(index) {
    const item = getItemByIndex(items, index);

    const model = await loadModel(item.models.glb, (p) => loading.setProgress(p));
    applyTransform(model, item.transform);

    if (currentModel) {
      scene.remove(currentModel);
    }

    scene.add(model);
    currentModel = model;
    currentIndex = index;

    camera.position.set(0, 0.3, 0.6);
    camera.lookAt(0, 0, 0);
    controls.update();
  }
```

- [ ] **Step 2: Add document.title update after config loads**

After `const { restaurant, items } = config;` (line 44), add:

```js
  document.title = `${restaurant.name} — AR Menu`;
```

- [ ] **Step 3: Add UI hide/show helper and register all UI elements**

Add the helper and element registration at these exact insertion points in `main.js`:

**A) After `startLoop()` call (after line 117), add the helper and collect existing UI elements:**

```js
  // UI visibility toggle for AR mode
  const uiElements = [];
  const itemInfoEl = document.getElementById('item-info');
  if (itemInfoEl) uiElements.push(itemInfoEl);
  const dotsEl = document.getElementById('carousel-dots');
  if (dotsEl) uiElements.push(dotsEl);
  const hintEl = document.getElementById('swipe-hint');
  if (hintEl) uiElements.push(hintEl);

  function setUIVisible(visible) {
    const display = visible ? '' : 'none';
    uiElements.forEach((el) => { el.style.display = display; });
  }
```

**B) Inside the `if (features.canNativeAR)` block, after `app.appendChild(arBtn);` (line 143), add:**

```js
    uiElements.push(arBtn);
```

**C) Inside the `if (features.canMindAR)` block, after `scanBtn.style.cssText = ...;` and before the click handler, add:**

```js
    uiElements.push(scanBtn);
```

- [ ] **Step 4: Rewrite the "Scan Menu" click handler with crash fix + UI hiding + canvas cleanup**

Replace the entire "Scan Menu" click handler (lines 157-224) with:

```js
    scanBtn.addEventListener('click', async () => {
      try {
        const { createMindARSession } = await import('./ar/mind-ar.js');
        const { createARHud } = await import('./ar/hud.js');
        const { createStickyMode } = await import('./ar/sticky-mode.js');

        controls.enabled = false;
        setUIVisible(false);

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

        function exitAR() {
          try { session.stop(); } catch (_) { /* MindAR may not have fully started */ }
          sticky.stop();
          hud.hide();
          controls.enabled = true;
          setUIVisible(true);
          // Clean up any extra canvases MindAR created
          const canvases = app.querySelectorAll('canvas');
          if (canvases.length > 1) {
            for (let i = 1; i < canvases.length; i++) canvases[i].remove();
          }
        }

        const sticky = createStickyMode({
          timeoutMs: 10000,
          onTimeout: () => {
            sm.send('TIMEOUT');
            exitAR();
          },
        });

        let arModel = null;
        session.onTargetFound(() => {
          sm.send('TARGET_FOUND');
          sticky.stop();
          hud.showTracking();
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
          exitAR();
        });

        sm.send('START_AR');
        await session.start();
      } catch (err) {
        console.error('MindAR failed:', err);
        scanBtn.style.display = 'none';
        controls.enabled = true;
        setUIVisible(true);
      }
    });
```

Key changes:
- `exitAR()` centralizes cleanup with try/catch around `session.stop()`
- `setUIVisible(false)` hides all UI on AR entry, `setUIVisible(true)` restores on exit
- Extra canvases removed on AR exit
- Error catch also restores UI visibility

- [ ] **Step 5: Run all tests to verify nothing breaks**

Run: `cd /Users/mk/work/bee-revenue/bee-restaurant-project && npm test`
Expected: All tests PASS

- [ ] **Step 6: Manual verification in Chrome**

Open `http://localhost:5174/` in Chrome and verify:
1. "View in AR" button does NOT appear on desktop
2. Arrow keys navigate the carousel, dots are clickable
3. "Scan Menu" → "Close" does not crash (no console errors)
4. Page title shows "Demo Pizza Co — AR Menu"

---

### Task 5: Commit all changes

- [ ] **Step 1: Stage and commit**

```bash
cd /Users/mk/work/bee-revenue/bee-restaurant-project
git add src/utils/device.js src/ui/menu-carousel.js src/ui/loading.js src/main.js \
        tests/utils/device.test.js tests/ui/menu-carousel.test.js tests/ui/loading.test.js
git commit -m "fix: patch 8 bugs found during Chrome testing

- fix(device): canNativeAR no longer true on desktop Chrome (WebXR != mobile AR)
- fix(carousel): add ArrowLeft/ArrowRight keyboard nav + clickable dots for desktop
- fix(loading): XSS via restaurant name — use textContent instead of innerHTML
- fix(main): MindAR Close crash — try/catch session.stop(), centralized exitAR()
- fix(main): hide UI elements during AR scanning mode
- fix(main): clean up leaked MindAR canvas on AR exit
- fix(main): load new model before removing old (no flash)
- fix(main): set document.title to restaurant name after config loads"
```
