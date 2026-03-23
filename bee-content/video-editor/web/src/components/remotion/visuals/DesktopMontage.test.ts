import { describe, test, expect } from 'vitest';
import { parseDesktopMontageData } from './DesktopMontage';

describe('parseDesktopMontageData', () => {
  test('parses JSON array of windows from content', () => {
    const content = JSON.stringify([
      { type: 'photo_viewer', name: 'Craig', src: 'photo.jpg' },
      { type: 'video_player', title: 'Bodycam', src: 'clip.jpg' },
    ]);
    const result = parseDesktopMontageData(content);
    expect(result.windows).toHaveLength(2);
    expect(result.windows[0].type).toBe('photo_viewer');
    expect(result.windows[1].type).toBe('video_player');
  });

  test('defaults background and blur', () => {
    const result = parseDesktopMontageData('[]');
    expect(result.background).toBe('animated-blue');
    expect(result.blur).toBe(false);
  });

  test('reads metadata overrides', () => {
    const result = parseDesktopMontageData('[]', { background: 'animated-teal', blur: true });
    expect(result.background).toBe('animated-teal');
    expect(result.blur).toBe(true);
  });

  test('handles non-JSON content gracefully', () => {
    const result = parseDesktopMontageData('not json');
    expect(result.windows).toEqual([]);
  });

  test('assigns default positions when not provided', () => {
    const content = JSON.stringify([
      { type: 'photo_viewer', name: 'A' },
      { type: 'notepad', title: 'B' },
    ]);
    const result = parseDesktopMontageData(content);
    // Each window should have x, y, width, height
    expect(result.windows[0].x).toBeDefined();
    expect(result.windows[0].width).toBeDefined();
  });
});
