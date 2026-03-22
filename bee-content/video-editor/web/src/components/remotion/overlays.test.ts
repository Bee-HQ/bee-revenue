// web/src/components/remotion/overlays.test.ts
import { describe, test, expect } from 'vitest';
import { parseQuoteContent, parseDollarAmount, parseLowerThirdContent } from './overlays';

describe('parseQuoteContent', () => {
  test('splits on em dash', () => {
    const r = parseQuoteContent('"Justice was served" — Prosecutor');
    expect(r.quote).toBe('"Justice was served"');
    expect(r.author).toBe('Prosecutor');
  });
  test('handles missing author', () => {
    const r = parseQuoteContent('Just a quote');
    expect(r.quote).toBe('Just a quote');
    expect(r.author).toBe('');
  });
});

describe('parseDollarAmount', () => {
  test('parses $1.4 million', () => {
    const r = parseDollarAmount('$1.4 million — Insurance payout');
    expect(r.numericValue).toBe(1400000);
    expect(r.description).toBe('Insurance payout');
  });
  test('parses $14,000', () => {
    const r = parseDollarAmount('$14,000 — Legal fees');
    expect(r.numericValue).toBe(14000);
    expect(r.description).toBe('Legal fees');
  });
  test('parses $500K', () => {
    const r = parseDollarAmount('$500K');
    expect(r.numericValue).toBe(500000);
  });
  test('handles unparseable', () => {
    const r = parseDollarAmount('a lot of money');
    expect(r.numericValue).toBe(0);
    expect(r.displayValue).toBe('a lot of money');
  });
});

describe('parseLowerThirdContent', () => {
  test('splits name and role', () => {
    const r = parseLowerThirdContent('Alex Murdaugh — Defendant');
    expect(r.name).toBe('Alex Murdaugh');
    expect(r.role).toBe('Defendant');
  });
  test('name only', () => {
    const r = parseLowerThirdContent('Moselle Estate');
    expect(r.name).toBe('Moselle Estate');
    expect(r.role).toBeUndefined();
  });
});
