import type { Storyboard, Segment, LayerEntry } from '../types';
import { parseTimecode, timeToMs } from './time-utils';

// DesignCombo types (inline -- avoid importing from @designcombo/types to keep adapter testable)
export interface DCDisplay {
  from: number;
  to: number;
}
export interface DCTrackItem {
  id: string;
  name: string;
  type: 'video' | 'audio' | 'image' | 'text';
  display: DCDisplay;
  trim?: DCDisplay;
  duration?: number;
  metadata: Record<string, any>;
  details: Record<string, any>;
  playbackRate?: number;
}
export interface DCTrack {
  id: string;
  type: string;
  items: string[];
  muted: boolean;
  accepts?: string[];
  magnetic?: boolean;
  static?: boolean;
}
export interface DCState {
  tracks: DCTrack[];
  trackItemIds: string[];
  trackItemsMap: Record<string, DCTrackItem>;
  transitionIds: string[];
  transitionsMap: Record<string, any>;
  duration: number;
}

const TRACK_DEFS = [
  { id: 'V1', type: 'video', accepts: ['video', 'image'] },
  { id: 'A1', type: 'audio', accepts: ['audio'] }, // narration
  { id: 'A2', type: 'audio', accepts: ['audio'] }, // real audio / SFX
  { id: 'A3', type: 'audio', accepts: ['audio'] }, // music
  { id: 'OV1', type: 'text', accepts: ['text', 'image'] }, // overlays
];

export function storyboardToDesignCombo(storyboard: Storyboard): DCState {
  const tracks: DCTrack[] = TRACK_DEFS.map((def) => ({
    id: def.id,
    type: def.type,
    items: [],
    muted: false,
    accepts: def.accepts,
    magnetic: true,
  }));

  const trackItemsMap: Record<string, DCTrackItem> = {};
  const trackItemIds: string[] = [];

  for (const seg of storyboard.segments) {
    const fromMs = timeToMs(parseTimecode(seg.start));
    const toMs = timeToMs(parseTimecode(seg.end));

    // V1: Visual entries
    seg.visual.forEach((entry: LayerEntry, i: number) => {
      const id = `${seg.id}-v-${i}`;
      const src = seg.assigned_media[`visual:${i}`] || entry.content || '';
      const isImage = ['PHOTO'].includes(entry.content_type);

      trackItemsMap[id] = {
        id,
        name:
          entry.content_type === 'FOOTAGE'
            ? src.split('/').pop() || seg.title
            : seg.title,
        type: isImage ? 'image' : 'video',
        display: { from: fromMs, to: toMs },
        metadata: {
          segmentId: seg.id,
          layerIndex: i,
          contentType: entry.content_type,
          originalEntry: entry,
        },
        details: {
          src: src
            ? `/api/media/file?path=${encodeURIComponent(src)}`
            : '',
          width: 1920,
          height: 1080,
        },
      };
      trackItemIds.push(id);
      tracks[0].items.push(id); // V1
    });

    // If no visual entries, add a placeholder
    if (seg.visual.length === 0) {
      const id = `${seg.id}-v-empty`;
      trackItemsMap[id] = {
        id,
        name: seg.title,
        type: 'video',
        display: { from: fromMs, to: toMs },
        metadata: { segmentId: seg.id, empty: true },
        details: { src: '' },
      };
      trackItemIds.push(id);
      tracks[0].items.push(id);
    }

    // A1: Narration (NAR entries from audio array)
    const narEntries = seg.audio.filter(
      (a: LayerEntry) => a.content_type === 'NAR',
    );
    narEntries.forEach((entry: LayerEntry, i: number) => {
      const id = `${seg.id}-nar-${i}`;
      trackItemsMap[id] = {
        id,
        name: `Narration: ${seg.title}`,
        type: 'audio',
        display: { from: fromMs, to: toMs },
        metadata: { segmentId: seg.id, layerIndex: i, contentType: 'NAR' },
        details: { src: '', volume: 1.0 },
      };
      trackItemIds.push(id);
      tracks[1].items.push(id); // A1
    });

    // A2: Real audio / SFX
    const realAudio = seg.audio.filter(
      (a: LayerEntry) => a.content_type !== 'NAR',
    );
    realAudio.forEach((entry: LayerEntry, i: number) => {
      const id = `${seg.id}-audio-${i}`;
      trackItemsMap[id] = {
        id,
        name: entry.content || entry.content_type,
        type: 'audio',
        display: { from: fromMs, to: toMs },
        metadata: {
          segmentId: seg.id,
          layerIndex: i,
          contentType: entry.content_type,
        },
        details: {
          src: entry.content || '',
          volume: entry.metadata?.volume ?? 1.0,
        },
      };
      trackItemIds.push(id);
      tracks[2].items.push(id); // A2
    });

    // A3: Music
    seg.music.forEach((entry: LayerEntry, i: number) => {
      const id = `${seg.id}-music-${i}`;
      trackItemsMap[id] = {
        id,
        name: entry.content || 'Music',
        type: 'audio',
        display: { from: fromMs, to: toMs },
        metadata: {
          segmentId: seg.id,
          layerIndex: i,
          contentType: 'MUSIC',
        },
        details: {
          src: entry.content || '',
          volume: entry.metadata?.volume ?? 0.2,
        },
      };
      trackItemIds.push(id);
      tracks[3].items.push(id); // A3
    });

    // OV1: Overlays
    seg.overlay.forEach((entry: LayerEntry, i: number) => {
      const id = `${seg.id}-ov-${i}`;
      trackItemsMap[id] = {
        id,
        name: `${entry.content_type}: ${entry.content || ''}`.substring(0, 40),
        type: 'text',
        display: { from: fromMs, to: fromMs + 4000 }, // overlays default 4s
        metadata: {
          segmentId: seg.id,
          layerIndex: i,
          contentType: entry.content_type,
        },
        details: { text: entry.content || entry.content_type },
      };
      trackItemIds.push(id);
      tracks[4].items.push(id); // OV1
    });
  }

  return {
    tracks,
    trackItemIds,
    trackItemsMap,
    transitionIds: [],
    transitionsMap: {},
    duration: storyboard.total_duration_seconds * 1000,
  };
}

export function designComboToStoryboard(
  dcState: DCState,
  original: Storyboard,
): Storyboard {
  // For alpha: preserve the original storyboard structure.
  // Only update assigned_media based on track item positions/sources.
  // Full bidirectional sync is a beta feature.

  const segments = original.segments.map((seg: Segment) => {
    const updatedMedia = { ...seg.assigned_media };

    // Find V1 items for this segment
    for (const itemId of dcState.trackItemIds) {
      const item = dcState.trackItemsMap[itemId];
      if (
        item?.metadata?.segmentId === seg.id &&
        item.metadata?.contentType &&
        !item.metadata?.empty
      ) {
        if (item.type === 'video' || item.type === 'image') {
          const src = item.details?.src || '';
          // Strip API prefix to get relative path
          const match = src.match(/path=(.+)/);
          if (match) {
            updatedMedia[`visual:${item.metadata.layerIndex || 0}`] =
              decodeURIComponent(match[1]);
          }
        }
      }
    }

    return { ...seg, assigned_media: updatedMedia };
  });

  return { ...original, segments };
}
