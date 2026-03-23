import { describe, test, expect } from 'vitest';
import { parseDramaticQuoteData } from './DramaticQuote';

describe('parseDramaticQuoteData', () => {
  test('parses content as text', () => {
    const result = parseDramaticQuoteData("I'm gonna need a lawyer");
    expect(result.text).toBe("I'm gonna need a lawyer");
  });

  test('defaults color to resolved red (#dc2626)', () => {
    const result = parseDramaticQuoteData('test');
    expect(result.color).toBe('#dc2626');
  });

  test('resolves named color from metadata', () => {
    const result = parseDramaticQuoteData('test', { color: 'teal' });
    expect(result.color).toBe('#0d9488');
  });

  test('passes through hex color from metadata', () => {
    const result = parseDramaticQuoteData('test', { color: '#ff00ff' });
    expect(result.color).toBe('#ff00ff');
  });

  test('defaults italic to true', () => {
    const result = parseDramaticQuoteData('test');
    expect(result.italic).toBe(true);
  });

  test('reads italic false from metadata', () => {
    const result = parseDramaticQuoteData('test', { italic: false });
    expect(result.italic).toBe(false);
  });

  test('defaults position to center', () => {
    const result = parseDramaticQuoteData('test');
    expect(result.position).toBe('center');
  });

  test('reads position from metadata', () => {
    const result = parseDramaticQuoteData('test', { position: 'top' });
    expect(result.position).toBe('top');
  });

  test('reads position bottom from metadata', () => {
    const result = parseDramaticQuoteData('test', { position: 'bottom' });
    expect(result.position).toBe('bottom');
  });

  test('handles null metadata', () => {
    const result = parseDramaticQuoteData('test', null);
    expect(result).toEqual({
      text: 'test',
      color: '#dc2626',
      italic: true,
      position: 'center',
    });
  });

  test('handles empty content with metadata text', () => {
    const result = parseDramaticQuoteData('', { text: 'fallback text' });
    expect(result.text).toBe('fallback text');
  });

  test('handles undefined metadata', () => {
    const result = parseDramaticQuoteData('hello');
    expect(result).toEqual({
      text: 'hello',
      color: '#dc2626',
      italic: true,
      position: 'center',
    });
  });
});
