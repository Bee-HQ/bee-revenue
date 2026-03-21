import { describe, test, expect } from 'vitest';
import { storyboardToTimeline, timelineToStoryboard } from './timeline-adapter';
import type { Storyboard, Segment } from '../types';

const mockSegment: Segment = {
  id: 'cold-open',
  start: '0:00',
  end: '0:15',
  title: 'Cold Open',
  section: 'Act 1',
  section_time: '',
  subsection: '',
  duration_seconds: 15,
  visual: [
    { content: 'footage/clip.mp4', content_type: 'FOOTAGE', time_start: null, time_end: null, raw: '', metadata: null },
  ],
  audio: [
    { content: 'narration text', content_type: 'NAR', time_start: null, time_end: null, raw: '', metadata: null },
  ],
  overlay: [
    { content: 'Colleton County', content_type: 'LOWER_THIRD', time_start: null, time_end: null, raw: '', metadata: null },
  ],
  music: [
    { content: 'music/bg.mp3', content_type: 'MUSIC', time_start: null, time_end: null, raw: '', metadata: { volume: 0.2 } },
  ],
  source: [],
  transition: [],
  assigned_media: { 'visual:0': 'footage/clip.mp4' },
};

const mockStoryboard: Storyboard = {
  title: 'Test',
  total_segments: 1,
  total_duration_seconds: 15,
  sections: ['Act 1'],
  segments: [mockSegment],
  stock_footage_needed: 0,
  photos_needed: 0,
  maps_needed: 0,
  production_rules: [],
};

describe('storyboardToTimeline', () => {
  test('creates dynamic rows — only tracks with content', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const ids = rows.map(r => r.id);
    expect(ids).toContain('V1');
    expect(ids).toContain('A1');
    expect(ids).toContain('A3');
    expect(ids).toContain('OV1');
    expect(ids).not.toContain('A2');
  });

  test('V1 always present even with empty storyboard', () => {
    const empty = { ...mockStoryboard, segments: [], total_segments: 0, total_duration_seconds: 0 };
    const { rows } = storyboardToTimeline(empty);
    expect(rows.some(r => r.id === 'V1')).toBe(true);
  });

  test('times are in seconds (not ms)', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const v1 = rows.find(r => r.id === 'V1')!;
    const action = v1.actions[0];
    expect(action.start).toBe(0);
    expect(action.end).toBe(15);
  });

  test('actions have correct effectId per track', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect(v1.actions[0].effectId).toBe('video');
    const a1 = rows.find(r => r.id === 'A1')!;
    expect(a1.actions[0].effectId).toBe('narration');
  });

  test('actions carry segment metadata in data field', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const v1 = rows.find(r => r.id === 'V1')!;
    const data = (v1.actions[0] as any).data;
    expect(data.segmentId).toBe('cold-open');
    expect(data.contentType).toBe('FOOTAGE');
    expect(data.src).toBe('footage/clip.mp4');
  });

  test('returns effects map', () => {
    const { effects } = storyboardToTimeline(mockStoryboard);
    expect(effects.video).toBeDefined();
    expect(effects.narration).toBeDefined();
    expect(effects.overlay).toBeDefined();
  });

  test('creates placeholder for segment with no visuals', () => {
    const noVisual = { ...mockSegment, visual: [], assigned_media: {} };
    const sb = { ...mockStoryboard, segments: [noVisual] };
    const { rows } = storyboardToTimeline(sb);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect(v1.actions.length).toBe(1);
    expect((v1.actions[0] as any).data.empty).toBe(true);
  });

  test('normalizes formula codes to base types', () => {
    const brollSeg = {
      ...mockSegment,
      visual: [{ content: '', content_type: 'BROLL-DARK', time_start: null, time_end: null, raw: '', metadata: null }],
    };
    const sb = { ...mockStoryboard, segments: [brollSeg] };
    const { rows } = storyboardToTimeline(sb);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect((v1.actions[0] as any).data.contentType).toBe('STOCK');
  });
});

describe('timelineToStoryboard', () => {
  test('preserves segment count and metadata', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const result = timelineToStoryboard(rows, mockStoryboard);
    expect(result.segments.length).toBe(1);
    expect(result.title).toBe('Test');
  });

  test('maps changed src back to assigned_media', () => {
    const { rows } = storyboardToTimeline(mockStoryboard);
    const v1 = rows.find(r => r.id === 'V1')!;
    (v1.actions[0] as any).data.src = 'footage/new-clip.mp4';
    const result = timelineToStoryboard(rows, mockStoryboard);
    expect(result.segments[0].assigned_media['visual:0']).toBe('footage/new-clip.mp4');
  });

  test('round-trips timecodes through seconds conversion', () => {
    const seg = { ...mockSegment, id: 'mid', start: '1:30', end: '2:00', duration_seconds: 30 };
    const sb = { ...mockStoryboard, segments: [seg] };
    const { rows } = storyboardToTimeline(sb);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect(v1.actions[0].start).toBe(90);
    expect(v1.actions[0].end).toBe(120);
    const result = timelineToStoryboard(rows, sb);
    expect(result.segments[0].start).toBe('1:30');
    expect(result.segments[0].end).toBe('2:00');
  });
});
