import { describe, test, expect } from 'vitest';
import { resolveTransformStyle } from './TransformWrapper';

describe('resolveTransformStyle', () => {
  test('returns identity styles for undefined transform', () => {
    const result = resolveTransformStyle(undefined);
    expect(result.outer.justifyContent).toBe('center');
    expect(result.outer.alignItems).toBe('center');
    expect(result.outer.opacity).toBe(1);
    expect(result.inner.transform).toBeUndefined();
  });

  test('returns identity styles for null transform', () => {
    const result = resolveTransformStyle(null);
    expect(result.outer.opacity).toBe(1);
  });

  test('maps position preset to flexbox styles', () => {
    const result = resolveTransformStyle({ position: 'top-left' });
    expect(result.outer.justifyContent).toBe('flex-start');
    expect(result.outer.alignItems).toBe('flex-start');
    expect(result.outer.padding).toBe('80px 60px 0');
  });

  test('maps bottom-right position', () => {
    const result = resolveTransformStyle({ position: 'bottom-right' });
    expect(result.outer.justifyContent).toBe('flex-end');
    expect(result.outer.alignItems).toBe('flex-end');
    expect(result.outer.padding).toBe('0 60px 80px');
  });

  test('applies offset as translate', () => {
    const result = resolveTransformStyle({ x: 10, y: -5 });
    expect(result.inner.transform).toBe('translate(10%, -5%) scale(1) rotate(0deg)');
  });

  test('applies scale and rotation', () => {
    const result = resolveTransformStyle({ scale: 1.5, rotation: 45 });
    expect(result.inner.transform).toBe('translate(0%, 0%) scale(1.5) rotate(45deg)');
  });

  test('applies opacity', () => {
    const result = resolveTransformStyle({ opacity: 0.5 });
    expect(result.outer.opacity).toBe(0.5);
  });

  test('combines all properties', () => {
    const result = resolveTransformStyle({
      position: 'top-right', x: 5, y: 3, scale: 0.8, rotation: -10, opacity: 0.9,
    });
    expect(result.outer.justifyContent).toBe('flex-start');
    expect(result.outer.alignItems).toBe('flex-end');
    expect(result.outer.opacity).toBe(0.9);
    expect(result.inner.transform).toBe('translate(5%, 3%) scale(0.8) rotate(-10deg)');
  });

  test('defaults position to center when not specified', () => {
    const result = resolveTransformStyle({ scale: 2 });
    expect(result.outer.justifyContent).toBe('center');
    expect(result.outer.alignItems).toBe('center');
  });
});
