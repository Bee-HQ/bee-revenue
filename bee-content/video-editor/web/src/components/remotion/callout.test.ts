import { describe, test, expect } from 'vitest';
import { circlePath, arrowPath, boxPath, underlinePath, bracketPath, parseCalloutData } from './Callout';

describe('Callout path generators', () => {
  test('circlePath generates valid SVG path', () => {
    const d = circlePath(960, 540, 100);
    expect(d).toMatch(/^M/);
    expect(d).toContain('A');
  });

  test('arrowPath generates path from origin to target', () => {
    const d = arrowPath(100, 100, 500, 500);
    expect(d).toMatch(/^M/);
    expect(d).toContain('Q');
  });

  test('boxPath generates rect path', () => {
    const d = boxPath(400, 300, 300, 200, 8);
    expect(d).toMatch(/^M/);
  });

  test('underlinePath generates horizontal line', () => {
    const d = underlinePath(400, 600, 300);
    expect(d).toMatch(/^M/);
    expect(d).toContain('L');
  });

  test('bracketPath generates curly brace', () => {
    const d = bracketPath(400, 300, 200);
    expect(d).toMatch(/^M/);
  });
});

describe('parseCalloutData', () => {
  test('reads target from metadata (normalized 0-1 coords)', () => {
    const result = parseCalloutData('Label text', { target: [0.5, 0.5], style: 'circle' });
    expect(result.targetX).toBe(960);
    expect(result.targetY).toBe(540);
    expect(result.style).toBe('circle');
    expect(result.label).toBe('Label text');
  });

  test('defaults to center and circle', () => {
    const result = parseCalloutData('test', {});
    expect(result.targetX).toBe(960);
    expect(result.targetY).toBe(540);
    expect(result.style).toBe('circle');
  });

  test('reads animation mode', () => {
    const result = parseCalloutData('', { animation: 'pop' });
    expect(result.animation).toBe('pop');
  });
});
