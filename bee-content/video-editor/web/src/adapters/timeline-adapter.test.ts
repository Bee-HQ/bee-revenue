import { describe, test, expect } from 'vitest';
import { projectToTimeline, timelineToProject, storyboardToTimeline, timelineToStoryboard } from './timeline-adapter';
import type { BeeProject, BeeSegment } from '../types';

const mockSegment: BeeSegment = {
  id: 'cold-open',
  start: 0,
  duration: 15,
  title: 'Cold Open',
  section: 'Act 1',
  visual: [
    { type: 'FOOTAGE', src: 'footage/clip.mp4' },
  ],
  audio: [
    { type: 'NAR', text: 'narration text', src: null },
  ],
  overlay: [
    { type: 'LOWER_THIRD', content: 'Colleton County' },
  ],
  music: [
    { type: 'MUSIC', src: 'music/bg.mp3', volume: 0.2 },
  ],
  transition: null,
};

const mockProject: BeeProject = {
  version: 1,
  title: 'Test',
  fps: 30,
  resolution: [1920, 1080],
  createdAt: '',
  updatedAt: '',
  segments: [mockSegment],
  production: {
    narrationEngine: 'edge',
    narrationVoice: '',
    transitionMode: 'overlap',
    status: { narration: null, stock: null, render: null },
    renders: [],
  },
};

describe('projectToTimeline', () => {
  test('creates dynamic rows — only tracks with content', () => {
    const { rows } = projectToTimeline(mockProject);
    const ids = rows.map(r => r.id);
    expect(ids).toContain('V1');
    expect(ids).toContain('A1');
    expect(ids).toContain('A3');
    expect(ids).toContain('OV1');
    expect(ids).not.toContain('A2');
  });

  test('V1 always present even with empty project', () => {
    const empty = { ...mockProject, segments: [] };
    const { rows } = projectToTimeline(empty);
    expect(rows.some(r => r.id === 'V1')).toBe(true);
  });

  test('times are in seconds (start=0, end=15 for 0+15 duration)', () => {
    const { rows } = projectToTimeline(mockProject);
    const v1 = rows.find(r => r.id === 'V1')!;
    const action = v1.actions[0];
    expect(action.start).toBe(0);
    expect(action.end).toBe(15);
  });

  test('actions have correct effectId per track', () => {
    const { rows } = projectToTimeline(mockProject);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect(v1.actions[0].effectId).toBe('video');
    const a1 = rows.find(r => r.id === 'A1')!;
    expect(a1.actions[0].effectId).toBe('narration');
  });

  test('actions carry segment metadata in data field', () => {
    const { rows } = projectToTimeline(mockProject);
    const v1 = rows.find(r => r.id === 'V1')!;
    const data = (v1.actions[0] as any).data;
    expect(data.segmentId).toBe('cold-open');
    expect(data.contentType).toBe('FOOTAGE');
    expect(data.src).toBe('footage/clip.mp4');
  });

  test('returns effects map', () => {
    const { effects } = projectToTimeline(mockProject);
    expect(effects.video).toBeDefined();
    expect(effects.narration).toBeDefined();
    expect(effects.overlay).toBeDefined();
  });

  test('creates placeholder for segment with no visuals', () => {
    const noVisual: BeeSegment = { ...mockSegment, visual: [] };
    const project = { ...mockProject, segments: [noVisual] };
    const { rows } = projectToTimeline(project);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect(v1.actions.length).toBe(1);
    expect((v1.actions[0] as any).data.empty).toBe(true);
  });

  test('normalizes formula codes to base types', () => {
    const brollSeg: BeeSegment = {
      ...mockSegment,
      visual: [{ type: 'BROLL-DARK', src: null }],
    };
    const project = { ...mockProject, segments: [brollSeg] };
    const { rows } = projectToTimeline(project);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect((v1.actions[0] as any).data.contentType).toBe('STOCK');
  });

  test('reads src directly from visual entry (not assigned_media)', () => {
    const seg: BeeSegment = {
      ...mockSegment,
      visual: [{ type: 'FOOTAGE', src: 'footage/direct.mp4' }],
    };
    const project = { ...mockProject, segments: [seg] };
    const { rows } = projectToTimeline(project);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect((v1.actions[0] as any).data.src).toBe('footage/direct.mp4');
  });

  test('music src read from entry.src', () => {
    const { rows } = projectToTimeline(mockProject);
    const a3 = rows.find(r => r.id === 'A3')!;
    expect((a3.actions[0] as any).data.src).toBe('music/bg.mp3');
  });

  test('round-trip mid-point segment (start=90, duration=30 → actions at 90-120)', () => {
    const seg: BeeSegment = { ...mockSegment, id: 'mid', start: 90, duration: 30 };
    const project = { ...mockProject, segments: [seg] };
    const { rows } = projectToTimeline(project);
    const v1 = rows.find(r => r.id === 'V1')!;
    expect(v1.actions[0].start).toBe(90);
    expect(v1.actions[0].end).toBe(120);
  });
});

describe('timelineToProject', () => {
  test('preserves segment count and metadata', () => {
    const { rows } = projectToTimeline(mockProject);
    const result = timelineToProject(rows, mockProject);
    expect(result.segments.length).toBe(1);
    expect(result.title).toBe('Test');
  });

  test('maps changed src back to visual entry src (not assigned_media)', () => {
    const { rows } = projectToTimeline(mockProject);
    const v1 = rows.find(r => r.id === 'V1')!;
    (v1.actions[0] as any).data.src = 'footage/new-clip.mp4';
    const result = timelineToProject(rows, mockProject);
    expect(result.segments[0].visual[0].src).toBe('footage/new-clip.mp4');
  });

  test('does not produce assigned_media on segments', () => {
    const { rows } = projectToTimeline(mockProject);
    const result = timelineToProject(rows, mockProject);
    expect((result.segments[0] as any).assigned_media).toBeUndefined();
  });

  test('preserves start and duration on segments', () => {
    const { rows } = projectToTimeline(mockProject);
    const result = timelineToProject(rows, mockProject);
    expect(result.segments[0].start).toBe(0);
    expect(result.segments[0].duration).toBe(15);
  });
});

describe('backward-compat exports', () => {
  test('storyboardToTimeline is the same as projectToTimeline', () => {
    const r1 = projectToTimeline(mockProject);
    const r2 = storyboardToTimeline(mockProject);
    expect(r1.rows.length).toBe(r2.rows.length);
    expect(r1.rows[0].id).toBe(r2.rows[0].id);
  });

  test('timelineToStoryboard is the same as timelineToProject', () => {
    const { rows } = projectToTimeline(mockProject);
    const r1 = timelineToProject(rows, mockProject);
    const r2 = timelineToStoryboard(rows, mockProject);
    expect(r1.segments.length).toBe(r2.segments.length);
  });
});
