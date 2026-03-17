// @vitest-environment jsdom
import { describe, it, expect } from 'vitest';
import { getNativeARUrl } from '../../src/native-ar/launcher.js';

describe('getNativeARUrl', () => {
  it('returns Scene Viewer URL for Android', () => {
    const url = getNativeARUrl({
      glb: 'models/pizza.glb',
      title: 'Margherita',
      isIOS: false,
    });
    expect(url).toContain('intent://arvr.google.com/scene-viewer');
    expect(url).toContain('pizza.glb');
    expect(url).toContain('Margherita');
  });

  it('returns null for iOS without USDZ', () => {
    const url = getNativeARUrl({
      glb: 'models/pizza.glb',
      usdz: null,
      title: 'Margherita',
      isIOS: true,
    });
    expect(url).toBeNull();
  });

  it('returns USDZ data URL for iOS with USDZ', () => {
    const url = getNativeARUrl({
      glb: 'models/pizza.glb',
      usdz: 'models/pizza.usdz',
      title: 'Margherita',
      isIOS: true,
    });
    expect(url).toContain('pizza.usdz');
  });
});
