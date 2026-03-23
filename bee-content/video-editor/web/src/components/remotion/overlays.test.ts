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
import type { BeeSegment } from '../../types';

const makeSeg = (id: string, start: number, dur: number, trans?: { type: string; duration: number }): BeeSegment => ({
  id, start, duration: dur, title: id, section: '',
  visual: [], audio: [], overlay: [], music: [],
  transition: trans ? { type: trans.type, duration: trans.duration } : null,
});

describe('getTransitionInfo', () => {
  test('parses 1.0s dissolve', () => {
    const seg = makeSeg('s1', 0, 15, { type: 'DISSOLVE', duration: 1.0 });
    const info = getTransitionInfo(seg, 30);
    expect(info).toEqual({ type: 'DISSOLVE', durationInFrames: 30 });
  });
  test('returns null when no transition', () => {
    const seg = makeSeg('s1', 0, 15);
    expect(getTransitionInfo(seg, 30)).toBeNull();
  });
});

describe('calculateSegmentPositions', () => {
  test('fade mode uses absolute timecodes', () => {
    const segs = [makeSeg('s1', 0, 15), makeSeg('s2', 15, 15)];
    const { positions, totalFrames } = calculateSegmentPositions(segs, 30, 'fade');
    expect(positions[0].from).toBe(0);
    expect(positions[1].from).toBe(450); // 15s * 30fps
    expect(totalFrames).toBe(900);
  });

  test('overlap mode shrinks total duration', () => {
    const segs = [
      makeSeg('s1', 0, 15),
      makeSeg('s2', 15, 15, { type: 'DISSOLVE', duration: 1.0 }),
    ];
    const { positions, totalFrames } = calculateSegmentPositions(segs, 30, 'overlap');
    expect(positions[0].from).toBe(0);
    expect(positions[1].from).toBe(420); // 450 - 30 (1s overlap)
    expect(totalFrames).toBe(870); // 900 - 30
  });

  test('skips zero-duration segments', () => {
    const segs = [makeSeg('s1', 0, 15), makeSeg('s2', 15, 0), makeSeg('s3', 15, 10)];
    const { positions } = calculateSegmentPositions(segs, 30, 'fade');
    expect(positions).toHaveLength(2);
  });

  test('clamps transition longer than segment', () => {
    const segs = [
      makeSeg('s1', 0, 2),
      makeSeg('s2', 2, 1, { type: 'DISSOLVE', duration: 5.0 }),
    ];
    const { positions } = calculateSegmentPositions(segs, 30, 'overlap');
    expect(positions[1].transitionIn!.durationInFrames).toBe(30); // clamped to 1s segment
  });
});

// EvidenceBoard parser tests
import { parseBoardData } from './visuals/EvidenceBoard';

describe('parseBoardData', () => {
  test('parses valid JSON', () => {
    const content = JSON.stringify({
      people: [{ name: 'Alex' }, { name: 'Maggie' }],
      connections: [{ from: 'Alex', to: 'Maggie', label: 'married' }],
    });
    const result = parseBoardData(content);
    expect(result.people).toHaveLength(2);
    expect(result.connections).toHaveLength(1);
    expect(result.connections[0].label).toBe('married');
  });

  test('falls back to comma-separated names', () => {
    const result = parseBoardData('Alex, Maggie, Paul');
    expect(result.people).toHaveLength(3);
    expect(result.people[0].name).toBe('Alex');
    expect(result.connections).toHaveLength(0);
  });

  test('handles invalid JSON', () => {
    const result = parseBoardData('not json at all');
    expect(result.people).toHaveLength(1);
    expect(result.people[0].name).toBe('not json at all');
  });
});

// PictureInPicture parser tests
import { parsePipData } from './visuals/PictureInPicture';

describe('parsePipData', () => {
  test('parses valid JSON', () => {
    const content = JSON.stringify({
      main: { type: 'video', src: 'bodycam.mp4' },
      pip: { type: 'image', src: 'map.png' },
      layout: 'top-right',
    });
    const result = parsePipData(content);
    expect(result.main.type).toBe('video');
    expect(result.pip.type).toBe('image');
    expect(result.layout).toBe('top-right');
  });

  test('falls back to placeholder', () => {
    const result = parsePipData('not json');
    expect(result.main.type).toBe('color');
    expect(result.pip.type).toBe('color');
  });
});

// AudioVisualization parser tests
import { parseAudioVisData } from './visuals/AudioVisualization';

describe('parseAudioVisData', () => {
  test('parses valid JSON', () => {
    const content = JSON.stringify({ label: '911 Call', style: 'pulse', color: '#ff0000' });
    const result = parseAudioVisData(content);
    expect(result.label).toBe('911 Call');
    expect(result.style).toBe('pulse');
  });

  test('falls back to label from plain text', () => {
    const result = parseAudioVisData('Emergency call recording');
    expect(result.label).toBe('Emergency call recording');
    expect(result.style).toBe('bars');
  });
});

// SocialPost parser tests
import { parsePostData } from './visuals/SocialPost';

describe('parsePostData', () => {
  test('parses valid JSON post', () => {
    const content = JSON.stringify({ author: 'Alex M', text: 'Just arrived at Moselle', handle: '@alexm' });
    const result = parsePostData(content);
    expect(result.author).toBe('Alex M');
    expect(result.text).toBe('Just arrived at Moselle');
    expect(result.handle).toBe('@alexm');
  });

  test('falls back to plain text', () => {
    const result = parsePostData('Just a status update');
    expect(result.author).toBe('Unknown');
    expect(result.text).toBe('Just a status update');
  });
});

// TextChat parser tests
import { parseMessages } from './visuals/TextChat';

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

import { DEFAULT_DURATIONS } from './overlays';

describe('DEFAULT_DURATIONS for new components', () => {
  test('CALLOUT has a default duration', () => {
    expect(DEFAULT_DURATIONS.CALLOUT).toBe(4);
  });
  test('KINETIC_TEXT has a default duration', () => {
    expect(DEFAULT_DURATIONS.KINETIC_TEXT).toBe(5);
  });
  test('ATMOSPHERE has long default', () => {
    expect(DEFAULT_DURATIONS.ATMOSPHERE).toBe(10);
  });
});
