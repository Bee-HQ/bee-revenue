// src/ar/hud.js
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
