import { describe, test, expect } from 'vitest';
import { parsePhotoViewerData } from './PhotoViewerCard';

describe('parsePhotoViewerData', () => {
  test('parses "Name — Role" content as single card', () => {
    const result = parsePhotoViewerData('Craig Thetford — Victim', { src: 'photo.jpg' });
    expect(result.cards).toEqual([{ name: 'Craig Thetford', role: 'Victim', src: 'photo.jpg' }]);
  });

  test('parses name-only content (no role)', () => {
    const result = parsePhotoViewerData('John Doe');
    expect(result.cards).toEqual([{ name: 'John Doe', role: undefined, src: undefined }]);
  });

  test('parses JSON array content as multiple cards', () => {
    const json = JSON.stringify([
      { name: 'Bill', role: 'Ex-husband', src: 'bill.jpg' },
      { name: 'Scott', src: 'scott.jpg' },
    ]);
    const result = parsePhotoViewerData(json);
    expect(result.cards).toHaveLength(2);
    expect(result.cards[0]).toEqual({ name: 'Bill', role: 'Ex-husband', src: 'bill.jpg' });
    expect(result.cards[1]).toEqual({ name: 'Scott', role: undefined, src: 'scott.jpg' });
  });

  test('defaults animation to slide-up and windowTitle to Photo Viewer', () => {
    const result = parsePhotoViewerData('Name');
    expect(result.animation).toBe('slide-up');
    expect(result.windowTitle).toBe('Photo Viewer');
  });

  test('reads animation and windowTitle from metadata', () => {
    const result = parsePhotoViewerData('Name', { animation: 'scale', windowTitle: 'Evidence' });
    expect(result.animation).toBe('scale');
    expect(result.windowTitle).toBe('Evidence');
  });

  test('malformed JSON falls back to single card with content as name', () => {
    const result = parsePhotoViewerData('[invalid json');
    expect(result.cards).toEqual([{ name: '[invalid json', role: undefined, src: undefined }]);
  });

  test('empty content with metadata fallback', () => {
    const result = parsePhotoViewerData('', { name: 'From Meta', role: 'Suspect', src: 'meta.jpg' });
    expect(result.cards).toEqual([{ name: 'From Meta', role: 'Suspect', src: 'meta.jpg' }]);
  });

  test('handles null metadata', () => {
    const result = parsePhotoViewerData('Name', null);
    expect(result.cards).toEqual([{ name: 'Name', role: undefined, src: undefined }]);
  });
});
