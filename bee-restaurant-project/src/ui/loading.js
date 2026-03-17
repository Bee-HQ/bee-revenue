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
