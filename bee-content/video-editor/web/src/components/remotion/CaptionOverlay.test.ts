import { describe, test, expect } from 'vitest';
import { parseCaptionWords } from './CaptionOverlay';

describe('parseCaptionWords', () => {
  test('plain text returns words with no color', () => {
    const result = parseCaptionWords('plain text here');
    expect(result).toEqual([
      { text: 'plain', color: undefined },
      { text: 'text', color: undefined },
      { text: 'here', color: undefined },
    ]);
  });

  test('parses named color markup', () => {
    const result = parseCaptionWords('is that {red:blood}');
    expect(result).toEqual([
      { text: 'is', color: undefined },
      { text: 'that', color: undefined },
      { text: 'blood', color: '#dc2626' },
    ]);
  });

  test('handles multi-word color spans', () => {
    const result = parseCaptionWords('{teal:DNA evidence}');
    expect(result).toEqual([
      { text: 'DNA', color: '#0d9488' },
      { text: 'evidence', color: '#0d9488' },
    ]);
  });

  test('handles hex color', () => {
    const result = parseCaptionWords('{#ff00ff:custom}');
    expect(result).toEqual([
      { text: 'custom', color: '#ff00ff' },
    ]);
  });

  test('handles unclosed markup gracefully', () => {
    const result = parseCaptionWords('no {invalid markup');
    expect(result).toEqual([
      { text: 'no', color: undefined },
      { text: '{invalid', color: undefined },
      { text: 'markup', color: undefined },
    ]);
  });

  test('empty string returns empty array', () => {
    const result = parseCaptionWords('');
    expect(result).toEqual([]);
  });

  test('mixed colored and plain words', () => {
    const result = parseCaptionWords('She had {red:multiple injuries} on the {teal:property}');
    expect(result).toEqual([
      { text: 'She', color: undefined },
      { text: 'had', color: undefined },
      { text: 'multiple', color: '#dc2626' },
      { text: 'injuries', color: '#dc2626' },
      { text: 'on', color: undefined },
      { text: 'the', color: undefined },
      { text: 'property', color: '#0d9488' },
    ]);
  });
});
