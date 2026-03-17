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
