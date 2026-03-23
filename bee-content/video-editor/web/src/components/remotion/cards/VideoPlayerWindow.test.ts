import { describe, test, expect } from 'vitest';
import { parseVideoPlayerData } from './VideoPlayerWindow';

describe('parseVideoPlayerData', () => {
  test('parses "Title — Description" content', () => {
    const result = parseVideoPlayerData('Interview Tape — Cross examination');
    expect(result.title).toBe('Interview Tape');
    expect(result.description).toBe('Cross examination');
  });

  test('parses title-only content', () => {
    const result = parseVideoPlayerData('Bodycam Footage');
    expect(result.title).toBe('Bodycam Footage');
    expect(result.description).toBeUndefined();
  });

  test('defaults windowTitle and scrubberPosition', () => {
    const result = parseVideoPlayerData('clip');
    expect(result.windowTitle).toBe('Video Player');
    expect(result.scrubberPosition).toBe(0.4);
  });

  test('reads metadata overrides', () => {
    const result = parseVideoPlayerData('clip', {
      windowTitle: 'Media Player', scrubberPosition: 0.7, background: 'animated-blue',
    });
    expect(result.windowTitle).toBe('Media Player');
    expect(result.scrubberPosition).toBe(0.7);
    expect(result.background).toBe('animated-blue');
  });

  test('empty content with metadata fallback', () => {
    const result = parseVideoPlayerData('', { title: 'From Meta', description: 'desc' });
    expect(result.title).toBe('From Meta');
    expect(result.description).toBe('desc');
  });

  test('handles null metadata', () => {
    const result = parseVideoPlayerData('Title', null);
    expect(result.title).toBe('Title');
  });
});
