import { describe, test, expect } from 'vitest';
import { parsePhoneMockupData } from './PhoneMockup';

describe('parsePhoneMockupData', () => {
  test('parses content as title', () => {
    const result = parsePhoneMockupData('Missing Person Alert');
    expect(result.title).toBe('Missing Person Alert');
  });

  test('defaults phone color to black and tilt to 0', () => {
    const result = parsePhoneMockupData('content');
    expect(result.phoneColor).toBe('black');
    expect(result.tilt).toBe(0);
  });

  test('reads metadata overrides', () => {
    const result = parsePhoneMockupData('content', {
      phoneColor: 'red',
      tilt: -5,
      src: 'screenshot.png',
      background: 'animated-blue',
    });
    expect(result.phoneColor).toBe('red');
    expect(result.tilt).toBe(-5);
    expect(result.src).toBe('screenshot.png');
    expect(result.background).toBe('animated-blue');
  });

  test('empty content with metadata fallback', () => {
    const result = parsePhoneMockupData('', { title: 'From Meta' });
    expect(result.title).toBe('From Meta');
  });
});
