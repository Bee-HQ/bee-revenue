// src/ui/menu-carousel.js
export function createMenuCarousel(container, { total, onChange }) {
  let current = 0;

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

  function goTo(index) {
    const len = total;
    current = ((index % len) + len) % len;
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
