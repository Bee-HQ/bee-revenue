// src/ar/sticky-mode.js
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
