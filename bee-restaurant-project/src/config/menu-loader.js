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
