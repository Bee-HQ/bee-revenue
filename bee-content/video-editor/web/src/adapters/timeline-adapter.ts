import type { Storyboard, Segment, LayerEntry } from '../types';
import { parseTimecode } from './time-utils';
import type { TimelineAction, TimelineRow, TimelineEffect } from '@xzdarcy/timeline-engine';

/** Map formula production codes to base visual categories for timeline rendering */
const VISUAL_TYPE_MAP: Record<string, string> = {
  // Maps
  'MAP-FLAT': 'MAP', 'MAP-3D': 'MAP', 'MAP-TACTICAL': 'MAP',
  'MAP-PULSE': 'MAP', 'MAP-ROUTE': 'MAP',
  // Stock footage
  'BROLL-DARK': 'STOCK', 'BROLL-LIGHT': 'STOCK', 'BROLL': 'STOCK',
  // Real footage
  'COURTROOM': 'FOOTAGE', 'INTERROGATION': 'FOOTAGE', 'BODYCAM': 'FOOTAGE',
  // Generated graphics
  'PIP-SINGLE': 'GRAPHIC', 'PIP-DUAL': 'GRAPHIC', 'MUGSHOT-CARD': 'GRAPHIC',
  'POLICE-DB': 'GRAPHIC', 'DESKTOP-PHOTOS': 'GRAPHIC',
  'EVIDENCE-CLOSEUP': 'GRAPHIC', 'EVIDENCE-DISPLAY': 'GRAPHIC',
  'BODY-DIAGRAM': 'GRAPHIC', 'DOCUMENT-MOCKUP': 'GRAPHIC',
  'TEXT-CHAT': 'GRAPHIC', 'SOCIAL-POST': 'GRAPHIC',
  'EVIDENCE-BOARD': 'GRAPHIC', 'FLOW-DIAGRAM': 'GRAPHIC',
  'CENSOR-BLUR': 'GRAPHIC', 'SPLIT-INFO': 'GRAPHIC',
  'BRAND-STING': 'GRAPHIC', 'DISCLAIMER': 'GRAPHIC', 'TRAILER': 'GRAPHIC',
  // Audio visualization
  'WAVEFORM-AERIAL': 'WAVEFORM', 'WAVEFORM-DARK': 'WAVEFORM',
  // Text overlays (these go to OV track, but if in visual array, treat as GRAPHIC)
  'QUOTE-CARD': 'GRAPHIC', 'TIMELINE-MARKER': 'GRAPHIC',
  'TIMELINE-SEQUENCE': 'GRAPHIC', 'FINANCIAL-CARD': 'GRAPHIC',
  'NEWS-MONTAGE': 'GRAPHIC', 'CAPTION-ANIMATED': 'GRAPHIC',
  // Transitions (shouldn't be in visual array but handle gracefully)
  'TR-HARD': 'BLACK', 'TR-GLITCH': 'BLACK', 'TR-FLASH': 'BLACK',
  'TR-FADE': 'BLACK', 'TR-DISSOLVE': 'BLACK', 'TR-ZOOM': 'BLACK',
  'TR-SMASH': 'BLACK', 'TR-LCUT': 'BLACK',
  // Standard types pass through
  'FOOTAGE': 'FOOTAGE', 'STOCK': 'STOCK', 'PHOTO': 'PHOTO',
  'MAP': 'MAP', 'GRAPHIC': 'GRAPHIC', 'WAVEFORM': 'WAVEFORM',
  'BLACK': 'BLACK', 'GENERATED': 'GENERATED',
};

function normalizeVisualType(formulaCode: string): string {
  return VISUAL_TYPE_MAP[formulaCode] || VISUAL_TYPE_MAP[formulaCode.toUpperCase()] || 'GRAPHIC';
}

function cleanPath(path: string): string {
  // Strip leading backtick from markdown formatting
  return path.replace(/^`+/, '').trim();
}

function normalizeAudioType(type: string): string {
  // Handle "REAL AUDIO" (space) → "REAL_AUDIO" (underscore)
  if (type === 'REAL AUDIO') return 'REAL_AUDIO';
  return type;
}

// ---------- Public types ----------

export interface BeeActionData {
  segmentId: string;
  contentType: string;
  src: string;
  title: string;
  layerIndex: number;
  formulaCode?: string;
  empty?: boolean;
  // transition-specific
  type?: string;
  duration?: number;
  fromSegId?: string;
  toSegId?: string;
}

export interface BeeTimelineAction extends TimelineAction {
  data: BeeActionData;
}

// ---------- Effect IDs ----------

type EffectId = 'video' | 'narration' | 'audio' | 'music' | 'overlay';

const EFFECTS: Record<EffectId, TimelineEffect> = {
  video:      { id: 'video',      name: 'Video' },
  narration:  { id: 'narration',  name: 'Narration' },
  audio:      { id: 'audio',      name: 'Audio' },
  music:      { id: 'music',      name: 'Music' },
  overlay:    { id: 'overlay',    name: 'Overlay' },
};

// ---------- Track definitions ----------

interface TrackDef {
  id: string;
  effectId: EffectId;
  alwaysPresent?: boolean;
}

const TRACK_DEFS: TrackDef[] = [
  { id: 'V1',  effectId: 'video',     alwaysPresent: true },
  { id: 'A1',  effectId: 'narration' },
  { id: 'A2',  effectId: 'audio' },
  { id: 'A3',  effectId: 'music' },
  { id: 'OV1', effectId: 'overlay' },
];

// ---------- Helpers ----------

/** Timecode string to seconds */
function tcToSec(tc: string): number {
  return parseTimecode(tc);
}


// ---------- storyboardToTimeline ----------

export function storyboardToTimeline(storyboard: Storyboard): {
  rows: TimelineRow[];
  effects: Record<string, TimelineEffect>;
} {
  // Collect actions per track id
  const trackActions: Record<string, BeeTimelineAction[]> = {};
  for (const def of TRACK_DEFS) {
    trackActions[def.id] = [];
  }

  for (const seg of storyboard.segments) {
    const startSec = tcToSec(seg.start);
    const endSec = tcToSec(seg.end);

    // V1: Visual entries
    if (seg.visual.length > 0) {
      seg.visual.forEach((entry: LayerEntry, i: number) => {
        const rawSrc = seg.assigned_media[`visual:${i}`] || entry.content || '';
        const src = cleanPath(rawSrc);
        const baseType = normalizeVisualType(entry.content_type);

        trackActions['V1'].push({
          id: `${seg.id}-v-${i}`,
          start: startSec,
          end: endSec,
          effectId: 'video',
          data: {
            segmentId: seg.id,
            contentType: baseType,
            src,
            title: seg.title,
            layerIndex: i,
            formulaCode: entry.content_type,
          },
        });
      });
    } else {
      // Placeholder for segment with no visuals
      trackActions['V1'].push({
        id: `${seg.id}-v-empty`,
        start: startSec,
        end: endSec,
        effectId: 'video',
        data: {
          segmentId: seg.id,
          contentType: 'EMPTY',
          src: '',
          title: seg.title,
          layerIndex: 0,
          empty: true,
        },
      });
    }

    // A1: Narration (NAR entries from audio array)
    const narEntries = seg.audio.filter(
      (a: LayerEntry) => normalizeAudioType(a.content_type) === 'NAR',
    );
    narEntries.forEach((_entry: LayerEntry, i: number) => {
      trackActions['A1'].push({
        id: `${seg.id}-nar-${i}`,
        start: startSec,
        end: endSec,
        effectId: 'narration',
        data: {
          segmentId: seg.id,
          contentType: 'NAR',
          src: '',
          title: seg.title,
          layerIndex: i,
        },
      });
    });

    // A2: Real audio / SFX (non-NAR audio)
    const realAudio = seg.audio.filter(
      (a: LayerEntry) => normalizeAudioType(a.content_type) !== 'NAR',
    );
    realAudio.forEach((entry: LayerEntry, i: number) => {
      const audioType = normalizeAudioType(entry.content_type);
      trackActions['A2'].push({
        id: `${seg.id}-audio-${i}`,
        start: startSec,
        end: endSec,
        effectId: 'audio',
        data: {
          segmentId: seg.id,
          contentType: audioType,
          src: cleanPath(entry.content || ''),
          title: entry.content || audioType,
          layerIndex: i,
        },
      });
    });

    // A3: Music
    seg.music.forEach((entry: LayerEntry, i: number) => {
      trackActions['A3'].push({
        id: `${seg.id}-music-${i}`,
        start: startSec,
        end: endSec,
        effectId: 'music',
        data: {
          segmentId: seg.id,
          contentType: 'MUSIC',
          src: cleanPath(entry.content || ''),
          title: entry.content || 'Music',
          layerIndex: i,
        },
      });
    });

    // OV1: Overlays
    seg.overlay.forEach((entry: LayerEntry, i: number) => {
      trackActions['OV1'].push({
        id: `${seg.id}-ov-${i}`,
        start: startSec,
        end: Math.min(startSec + 4, endSec), // overlays default 4s, capped to segment end
        effectId: 'overlay',
        data: {
          segmentId: seg.id,
          contentType: entry.content_type,
          src: entry.content || '',
          title: `${entry.content_type}: ${entry.content || ''}`.substring(0, 40),
          layerIndex: i,
        },
      });
    });

    // Transitions are metadata (stored in seg.transition[]) — not rendered on timeline
  }

  // Build rows: dynamic — only include tracks that have actions (V1 always present)
  const rows: TimelineRow[] = [];
  for (const def of TRACK_DEFS) {
    const actions = trackActions[def.id];
    if (actions.length > 0 || def.alwaysPresent) {
      rows.push({
        id: def.id,
        actions: actions as TimelineAction[],
      });
    }
  }

  return { rows, effects: { ...EFFECTS } };
}

// ---------- timelineToStoryboard ----------

export function timelineToStoryboard(
  rows: TimelineRow[],
  original: Storyboard,
): Storyboard {
  // Build a lookup: segmentId → list of BeeTimelineActions from video track
  const videoActions: BeeTimelineAction[] = [];
  for (const row of rows) {
    for (const action of row.actions) {
      const bee = action as BeeTimelineAction;
      if (bee.data && bee.effectId === 'video' && !bee.data.empty) {
        videoActions.push(bee);
      }
    }
  }

  const segments = original.segments.map((seg: Segment) => {
    const updatedMedia = { ...seg.assigned_media };

    // Find video actions for this segment and map src back
    for (const action of videoActions) {
      if (action.data.segmentId === seg.id) {
        const src = action.data.src || '';
        if (src) {
          updatedMedia[`visual:${action.data.layerIndex}`] = src;
        }
      }
    }

    return { ...seg, assigned_media: updatedMedia };
  });

  return { ...original, segments };
}
