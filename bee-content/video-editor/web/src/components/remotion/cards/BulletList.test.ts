import { describe, test, expect } from 'vitest';
import { parseBulletListData } from './BulletList';

describe('parseBulletListData', () => {
  test('parses newline-separated content into items', () => {
    const result = parseBulletListData('Line one\nLine two\nLine three');
    expect(result.items).toEqual(['Line one', 'Line two', 'Line three']);
  });

  test('parses JSON array content', () => {
    const result = parseBulletListData('["First", "Second", "Third"]');
    expect(result.items).toEqual(['First', 'Second', 'Third']);
  });

  test('filters empty lines', () => {
    const result = parseBulletListData('Line one\n\nLine two\n  \nLine three');
    expect(result.items).toEqual(['Line one', 'Line two', 'Line three']);
  });

  test('defaults accent to red and style to stagger', () => {
    const result = parseBulletListData('Item');
    expect(result.accent).toBe('red');
    expect(result.style).toBe('stagger');
  });

  test('reads accent and style from metadata', () => {
    const result = parseBulletListData('Item', { accent: 'teal', style: 'cascade' });
    expect(result.accent).toBe('teal');
    expect(result.style).toBe('cascade');
  });

  test('malformed JSON falls back to newline split', () => {
    const result = parseBulletListData('[invalid json');
    expect(result.items).toEqual(['[invalid json']);
  });

  test('handles null metadata', () => {
    const result = parseBulletListData('Item', null);
    expect(result.accent).toBe('red');
    expect(result.style).toBe('stagger');
  });
});
