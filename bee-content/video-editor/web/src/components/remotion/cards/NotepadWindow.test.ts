import { describe, test, expect } from 'vitest';
import { parseNotepadData } from './NotepadWindow';

describe('parseNotepadData', () => {
  test('parses multiline content into lines array', () => {
    const result = parseNotepadData('Line one\nLine two\nLine three');
    expect(result.lines).toEqual(['Line one', 'Line two', 'Line three']);
  });

  test('single line content', () => {
    const result = parseNotepadData('Single line');
    expect(result.lines).toEqual(['Single line']);
  });

  test('defaults animation to typewriter, windowTitle to Notepad, background to #000', () => {
    const result = parseNotepadData('text');
    expect(result.animation).toBe('typewriter');
    expect(result.windowTitle).toBe('Notepad');
    expect(result.background).toBe('#000');
  });

  test('reads overrides from metadata', () => {
    const result = parseNotepadData('text', {
      animation: 'lines',
      windowTitle: 'Case Notes',
      background: 'animated-teal',
    });
    expect(result.animation).toBe('lines');
    expect(result.windowTitle).toBe('Case Notes');
    expect(result.background).toBe('animated-teal');
  });

  test('empty content produces single empty line', () => {
    const result = parseNotepadData('');
    expect(result.lines).toEqual(['']);
  });

  test('preserves blank lines', () => {
    const result = parseNotepadData('Line one\n\nLine three');
    expect(result.lines).toEqual(['Line one', '', 'Line three']);
  });

  test('handles null metadata', () => {
    const result = parseNotepadData('text', null);
    expect(result.animation).toBe('typewriter');
    expect(result.windowTitle).toBe('Notepad');
  });
});
