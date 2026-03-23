import { describe, test, expect } from 'vitest';
import { parseWords, parseKineticData } from './KineticText';

describe('parseWords', () => {
  test('splits plain text into words', () => {
    const words = parseWords('Hello world');
    expect(words).toEqual([
      { text: 'Hello', emphasis: 'none' },
      { text: 'world', emphasis: 'none' },
    ]);
  });

  test('detects *single* emphasis', () => {
    const words = parseWords('This is *important* stuff');
    expect(words[2]).toEqual({ text: 'important', emphasis: 'light' });
  });

  test('detects **double** emphasis', () => {
    const words = parseWords('This is **critical** stuff');
    expect(words[2]).toEqual({ text: 'critical', emphasis: 'heavy' });
  });

  test('handles mixed emphasis', () => {
    const words = parseWords('The *quick* **brown** fox');
    expect(words).toHaveLength(4);
    expect(words[1].emphasis).toBe('light');
    expect(words[2].emphasis).toBe('heavy');
  });

  test('handles empty string', () => {
    const words = parseWords('');
    expect(words).toEqual([{ text: '', emphasis: 'none' }]);
  });

  test('handles multi-word *light* emphasis', () => {
    const words = parseWords('The *DNA evidence* proved it');
    expect(words).toHaveLength(5);
    expect(words[1]).toEqual({ text: 'DNA', emphasis: 'light' });
    expect(words[2]).toEqual({ text: 'evidence', emphasis: 'light' });
    expect(words[3]).toEqual({ text: 'proved', emphasis: 'none' });
  });

  test('handles multi-word **heavy** emphasis', () => {
    const words = parseWords('Meet **Alex Murdaugh** now');
    expect(words).toHaveLength(4);
    expect(words[1]).toEqual({ text: 'Alex', emphasis: 'heavy' });
    expect(words[2]).toEqual({ text: 'Murdaugh', emphasis: 'heavy' });
    expect(words[3]).toEqual({ text: 'now', emphasis: 'none' });
  });
});

describe('parseKineticData', () => {
  test('reads preset from metadata', () => {
    const result = parseKineticData('text', { preset: 'flow' });
    expect(result.preset).toBe('flow');
  });

  test('defaults to punch', () => {
    const result = parseKineticData('text', {});
    expect(result.preset).toBe('punch');
  });

  test('unknown preset stored as-is (fallback at render time)', () => {
    const result = parseKineticData('text', { preset: 'scatter' });
    expect(result.preset).toBe('scatter');
  });
});
