// src/ui/item-info.js
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
