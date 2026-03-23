import { describe, test, expect } from 'vitest';
import { parseMapAnnotationData } from './MapAnnotation';

describe('parseMapAnnotationData', () => {
  test('parses circle shape', () => {
    const content = JSON.stringify([{ type: 'circle', x: 0.5, y: 0.5, r: 0.1 }]);
    const result = parseMapAnnotationData(content);
    expect(result.shapes).toEqual([{ type: 'circle', x: 0.5, y: 0.5, r: 0.1 }]);
  });

  test('parses path shape', () => {
    const content = JSON.stringify([{ type: 'path', points: [[0.1, 0.2], [0.3, 0.4]] }]);
    const result = parseMapAnnotationData(content);
    expect(result.shapes).toEqual([{ type: 'path', points: [[0.1, 0.2], [0.3, 0.4]] }]);
  });

  test('parses rect shape', () => {
    const content = JSON.stringify([{ type: 'rect', x: 0.2, y: 0.3, w: 0.4, h: 0.2 }]);
    const result = parseMapAnnotationData(content);
    expect(result.shapes).toEqual([{ type: 'rect', x: 0.2, y: 0.3, w: 0.4, h: 0.2 }]);
  });

  test('parses mixed shapes array', () => {
    const content = JSON.stringify([
      { type: 'circle', x: 0.5, y: 0.5, r: 0.1 },
      { type: 'path', points: [[0.1, 0.2], [0.3, 0.4]] },
    ]);
    const result = parseMapAnnotationData(content);
    expect(result.shapes).toHaveLength(2);
  });

  test('defaults color to red (#dc2626)', () => {
    const result = parseMapAnnotationData('[]');
    expect(result.color).toBe('#dc2626');
  });

  test('resolves named color from metadata', () => {
    const result = parseMapAnnotationData('[]', { color: 'teal' });
    expect(result.color).toBe('#0d9488');
  });

  test('passes through hex color from metadata', () => {
    const result = parseMapAnnotationData('[]', { color: '#ff00ff' });
    expect(result.color).toBe('#ff00ff');
  });

  test('malformed JSON returns empty shapes', () => {
    const result = parseMapAnnotationData('[invalid');
    expect(result.shapes).toEqual([]);
  });

  test('skips invalid shape entries', () => {
    const content = JSON.stringify([
      { type: 'circle', x: 0.5, y: 0.5, r: 0.1 },
      { type: 'unknown' },
      { type: 'circle' },
      { type: 'path', points: [[0.1, 0.2]] },
    ]);
    const result = parseMapAnnotationData(content);
    expect(result.shapes).toHaveLength(2);
  });

  test('handles null metadata', () => {
    const result = parseMapAnnotationData('[]', null);
    expect(result.color).toBe('#dc2626');
  });
});
