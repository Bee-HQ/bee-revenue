import { describe, test, expect } from 'vitest';
import {
  storyboardToDesignCombo,
  designComboToStoryboard,
} from './timeline-adapter';
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
    {
      content: 'footage/clip.mp4',
      content_type: 'FOOTAGE',
      time_start: null,
      time_end: null,
      raw: '',
      metadata: null,
    },
  ],
  audio: [
    {
      content: 'narration text',
      content_type: 'NAR',
      time_start: null,
      time_end: null,
      raw: '',
      metadata: null,
    },
  ],
  overlay: [
    {
      content: 'Colleton County',
      content_type: 'LOWER_THIRD',
      time_start: null,
      time_end: null,
      raw: '',
      metadata: null,
    },
  ],
  music: [
    {
      content: 'music/bg.mp3',
      content_type: 'MUSIC',
      time_start: null,
      time_end: null,
      raw: '',
      metadata: { volume: 0.2 },
    },
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

describe('storyboardToDesignCombo', () => {
  test('creates 5 tracks', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    expect(state.tracks).toHaveLength(5);
    expect(state.tracks.map((t) => t.id)).toEqual([
      'V1',
      'A1',
      'A2',
      'A3',
      'OV1',
    ]);
  });

  test('creates V1 item for visual', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    const v1 = state.tracks[0];
    expect(v1.items.length).toBe(1);
    const item = state.trackItemsMap[v1.items[0]];
    expect(item.type).toBe('video');
    expect(item.display.from).toBe(0);
    expect(item.display.to).toBe(15000);
  });

  test('creates A1 item for narration', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    const a1 = state.tracks[1];
    expect(a1.items.length).toBe(1);
  });

  test('creates A3 item for music', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    const a3 = state.tracks[3];
    expect(a3.items.length).toBe(1);
    const item = state.trackItemsMap[a3.items[0]];
    expect(item.details.volume).toBe(0.2);
  });

  test('creates OV1 item for overlay', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    const ov = state.tracks[4];
    expect(ov.items.length).toBe(1);
  });

  test('handles empty storyboard', () => {
    const empty = {
      ...mockStoryboard,
      segments: [],
      total_segments: 0,
      total_duration_seconds: 0,
    };
    const state = storyboardToDesignCombo(empty);
    expect(state.tracks).toHaveLength(5);
    expect(state.trackItemIds).toHaveLength(0);
  });

  test('creates placeholder for segment with no visuals', () => {
    const noVisual = { ...mockSegment, visual: [], assigned_media: {} };
    const sb = { ...mockStoryboard, segments: [noVisual] };
    const state = storyboardToDesignCombo(sb);
    const v1 = state.tracks[0];
    expect(v1.items.length).toBe(1);
    const item = state.trackItemsMap[v1.items[0]];
    expect(item.metadata.empty).toBe(true);
  });

  test('stores segment metadata on items', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    const item = state.trackItemsMap[state.trackItemIds[0]];
    expect(item.metadata.segmentId).toBe('cold-open');
  });

  test('duration in milliseconds', () => {
    const state = storyboardToDesignCombo(mockStoryboard);
    expect(state.duration).toBe(15000);
  });
});

describe('designComboToStoryboard', () => {
  test('preserves segment count', () => {
    const dc = storyboardToDesignCombo(mockStoryboard);
    const result = designComboToStoryboard(dc, mockStoryboard);
    expect(result.segments.length).toBe(1);
  });

  test('preserves title and metadata', () => {
    const dc = storyboardToDesignCombo(mockStoryboard);
    const result = designComboToStoryboard(dc, mockStoryboard);
    expect(result.title).toBe('Test');
    expect(result.sections).toEqual(['Act 1']);
  });
});
