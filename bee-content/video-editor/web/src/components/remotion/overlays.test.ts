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

import { calculateSegmentPositions, getTransitionInfo } from './overlays';
import type { Segment } from '../../types';

const makeSeg = (id: string, start: string, dur: number, trans?: { type: string; content: string }): Segment => ({
  id, start, end: '', title: id, section: '', section_time: '', subsection: '',
  duration_seconds: dur,
  visual: [], audio: [], overlay: [], music: [], source: [],
  transition: trans ? [{ content: trans.content, content_type: trans.type, time_start: null, time_end: null, raw: '', metadata: null }] : [],
  assigned_media: {},
});

describe('getTransitionInfo', () => {
  test('parses 1.0s dissolve', () => {
    const seg = makeSeg('s1', '0:00', 15, { type: 'DISSOLVE', content: '1.0s' });
    const info = getTransitionInfo(seg, 30);
    expect(info).toEqual({ type: 'DISSOLVE', durationInFrames: 30 });
  });
  test('returns null when no transition', () => {
    const seg = makeSeg('s1', '0:00', 15);
    expect(getTransitionInfo(seg, 30)).toBeNull();
  });
});

describe('calculateSegmentPositions', () => {
  test('fade mode uses absolute timecodes', () => {
    const segs = [makeSeg('s1', '0:00', 15), makeSeg('s2', '0:15', 15)];
    const { positions, totalFrames } = calculateSegmentPositions(segs, 30, 'fade');
    expect(positions[0].from).toBe(0);
    expect(positions[1].from).toBe(450); // 15s * 30fps
    expect(totalFrames).toBe(900);
  });

  test('overlap mode shrinks total duration', () => {
    const segs = [
      makeSeg('s1', '0:00', 15),
      makeSeg('s2', '0:15', 15, { type: 'DISSOLVE', content: '1.0s' }),
    ];
    const { positions, totalFrames } = calculateSegmentPositions(segs, 30, 'overlap');
    expect(positions[0].from).toBe(0);
    expect(positions[1].from).toBe(420); // 450 - 30 (1s overlap)
    expect(totalFrames).toBe(870); // 900 - 30
  });

  test('skips zero-duration segments', () => {
    const segs = [makeSeg('s1', '0:00', 15), makeSeg('s2', '0:15', 0), makeSeg('s3', '0:15', 10)];
    const { positions } = calculateSegmentPositions(segs, 30, 'fade');
    expect(positions).toHaveLength(2);
  });

  test('clamps transition longer than segment', () => {
    const segs = [
      makeSeg('s1', '0:00', 2),
      makeSeg('s2', '0:02', 1, { type: 'DISSOLVE', content: '5.0s' }),
    ];
    const { positions } = calculateSegmentPositions(segs, 30, 'overlap');
    expect(positions[1].transitionIn!.durationInFrames).toBe(30); // clamped to 1s segment
  });
});

// TextChat parser tests
import { parseMessages } from './TextChat';

describe('parseMessages', () => {
  test('parses valid JSON messages', () => {
    const content = JSON.stringify([
      { from: 'Alex', text: 'Hey' },
      { from: 'Maggie', text: 'Hi' },
    ]);
    const result = parseMessages(content);
    expect(result).toHaveLength(2);
    expect(result[0]).toEqual({ from: 'Alex', text: 'Hey' });
  });

  test('falls back to raw text on invalid JSON', () => {
    const result = parseMessages('just plain text');
    expect(result).toHaveLength(1);
    expect(result[0].from).toBe('Unknown');
    expect(result[0].text).toBe('just plain text');
  });

  test('falls back on wrong JSON shape', () => {
    const result = parseMessages('{"not": "an array"}');
    expect(result).toHaveLength(1);
    expect(result[0].text).toBe('{"not": "an array"}');
  });
});
