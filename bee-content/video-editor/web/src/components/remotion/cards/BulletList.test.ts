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

  test('defaults textColor to white', () => {
    const result = parseBulletListData('FIRST DEGREE MURDER');
    expect(result.textColor).toBe('#ffffff');
  });

  test('reads textColor from metadata', () => {
    const result = parseBulletListData('FIRST DEGREE MURDER', { textColor: 'red' });
    expect(result.textColor).toBe('#dc2626');
  });

  test('reads hex textColor from metadata', () => {
    const result = parseBulletListData('GUILTY', { textColor: '#00ff00' });
    expect(result.textColor).toBe('#00ff00');
  });

  test('reads barStyle from metadata', () => {
    const result = parseBulletListData('line1\nline2', { barStyle: 'none' });
    expect(result.barStyle).toBe('none');
  });

  test('defaults barStyle to solid', () => {
    const result = parseBulletListData('line1');
    expect(result.barStyle).toBe('solid');
  });

  test('single item still parses correctly (verdict mode)', () => {
    const result = parseBulletListData('FIRST DEGREE MURDER', { textColor: 'red', accent: 'red' });
    expect(result.items).toHaveLength(1);
    expect(result.items[0]).toBe('FIRST DEGREE MURDER');
    expect(result.textColor).toBe('#dc2626');
  });
});
