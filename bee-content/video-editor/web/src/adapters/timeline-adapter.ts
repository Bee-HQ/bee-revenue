import type { BeeProject, BeeSegment, VisualEntry, AudioEntry, MusicEntry, OverlayEntry } from '../types';
import type { TimelineAction, TimelineRow, TimelineEffect } from '@xzdarcy/timeline-engine';

/** Map formula production codes to base visual categories for timeline rendering */
export const VISUAL_TYPE_MAP: Record<string, string> = {
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
  // New component types (pass through)
  'KINETIC_TEXT': 'KINETIC_TEXT', 'KINETIC-TEXT': 'KINETIC_TEXT',
  'INFOGRAPHIC': 'INFOGRAPHIC',
  'SCREEN_MOCKUP': 'SCREEN_MOCKUP', 'SCREEN-MOCKUP': 'SCREEN_MOCKUP',
  'DATA_VIZ': 'DATA_VIZ', 'DATA-VIZ': 'DATA_VIZ',
  'TITLE_CARD': 'TITLE_CARD', 'TITLE-CARD': 'TITLE_CARD',
  'THREE_D': 'THREE_D', 'THREE-D': 'THREE_D',
  'LOTTIE': 'LOTTIE',
  // Standard types pass through
  'FOOTAGE': 'FOOTAGE', 'STOCK': 'STOCK', 'PHOTO': 'PHOTO',
  'MAP': 'MAP', 'GRAPHIC': 'GRAPHIC', 'WAVEFORM': 'WAVEFORM',
  'BLACK': 'BLACK', 'GENERATED': 'GENERATED',
};

export function normalizeVisualType(formulaCode: string): string {
  return VISUAL_TYPE_MAP[formulaCode] || VISUAL_TYPE_MAP[formulaCode.toUpperCase()] || 'GRAPHIC';
}

export function cleanPath(path: string): string {
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

export { EFFECTS };

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

export { TRACK_DEFS };

// ---------- projectToTimeline ----------

export function projectToTimeline(project: BeeProject): {
  rows: TimelineRow[];
  effects: Record<string, TimelineEffect>;
} {
  // Collect actions per track id
  const trackActions: Record<string, BeeTimelineAction[]> = {};
  for (const def of TRACK_DEFS) {
    trackActions[def.id] = [];
  }

  for (const seg of project.segments) {
    const startSec = seg.start;                   // already seconds
    const endSec = seg.start + seg.duration;      // start + duration

    // V1: Visual entries
    if (seg.visual.length > 0) {
      seg.visual.forEach((entry: VisualEntry, i: number) => {
        const rawSrc = entry.src || '';
        const src = cleanPath(rawSrc);
        const baseType = normalizeVisualType(entry.type);

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
            formulaCode: entry.type,
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

    // A1: Narration (NAR entries from audio array — use original index)
    seg.audio.forEach((entry: AudioEntry, origIndex: number) => {
      if (normalizeAudioType(entry.type) !== 'NAR') return;
      trackActions['A1'].push({
        id: `${seg.id}-nar-${origIndex}`,
        start: startSec,
        end: endSec,
        effectId: 'narration',
        data: {
          segmentId: seg.id,
          contentType: 'NAR',
          src: entry.src ? cleanPath(entry.src) : '',
          title: seg.title,
          layerIndex: origIndex,
        },
      });
    });

    // A2: Real audio / SFX (non-NAR, non-MUSIC audio — use original index)
    seg.audio.forEach((entry: AudioEntry, origIndex: number) => {
      const audioType = normalizeAudioType(entry.type);
      if (audioType === 'NAR' || audioType === 'MUSIC') return;
      const srcStr = entry.src ? cleanPath(entry.src) : '';
      trackActions['A2'].push({
        id: `${seg.id}-audio-${origIndex}`,
        start: startSec,
        end: endSec,
        effectId: 'audio',
        data: {
          segmentId: seg.id,
          contentType: audioType,
          src: srcStr,
          title: srcStr || audioType,
          layerIndex: origIndex,
        },
      });
    });

    // A3: Music (from music[] array + MUSIC-type entries in audio[])
    seg.music.forEach((entry: MusicEntry, i: number) => {
      const srcStr = entry.src ? cleanPath(entry.src) : '';
      trackActions['A3'].push({
        id: `${seg.id}-music-${i}`,
        start: startSec,
        end: endSec,
        effectId: 'music',
        data: {
          segmentId: seg.id,
          contentType: 'MUSIC',
          src: srcStr,
          title: srcStr || 'Music',
          layerIndex: i,
        },
      });
    });
    seg.audio.forEach((entry: AudioEntry, origIndex: number) => {
      if (normalizeAudioType(entry.type) !== 'MUSIC') return;
      const srcStr = entry.src ? cleanPath(entry.src) : '';
      trackActions['A3'].push({
        id: `${seg.id}-amusic-${origIndex}`,
        start: startSec,
        end: endSec,
        effectId: 'music',
        data: {
          segmentId: seg.id,
          contentType: 'MUSIC',
          src: srcStr,
          title: srcStr || 'Music',
          layerIndex: origIndex,
        },
      });
    });

    // OV1: Overlays
    seg.overlay.forEach((entry: OverlayEntry, i: number) => {
      trackActions['OV1'].push({
        id: `${seg.id}-ov-${i}`,
        start: startSec,
        end: Math.min(startSec + 4, endSec), // overlays default 4s, capped to segment end
        effectId: 'overlay',
        data: {
          segmentId: seg.id,
          contentType: entry.type,
          src: entry.content || '',
          title: `${entry.type}: ${entry.content || ''}`.substring(0, 40),
          layerIndex: i,
        },
      });
    });

    // Transitions are metadata (stored in seg.transition) — not rendered on timeline
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

// ---------- timelineToProject ----------

export function timelineToProject(
  rows: TimelineRow[],
  original: BeeProject,
): BeeProject {
  // Collect all non-empty actions with src paths
  const allActions: BeeTimelineAction[] = [];
  for (const row of rows) {
    for (const action of row.actions) {
      const bee = action as BeeTimelineAction;
      if (bee.data && bee.data.empty !== true) {
        allActions.push(bee);
      }
    }
  }

  const segments = original.segments.map((seg: BeeSegment) => {
    // Clone arrays so we can mutate entries
    const visual = seg.visual.map(e => ({ ...e }));
    const audio = seg.audio.map(e => ({ ...e }));
    const music = seg.music.map(e => ({ ...e }));

    for (const action of allActions) {
      if (action.data.segmentId !== seg.id) continue;
      const src = action.data.src || '';
      if (!src) continue;
      const idx = action.data.layerIndex;

      switch (action.effectId) {
        case 'video':
          if (visual[idx]) visual[idx].src = src;
          break;
        case 'narration':
        case 'audio':
          if (audio[idx]) audio[idx].src = src;
          break;
        case 'music':
          if (music[idx]) music[idx].src = src;
          break;
        // overlays have no src to write back
      }
    }

    return { ...seg, visual, audio, music };
  });

  return { ...original, segments };
}

// ---------- Backward-compatible aliases ----------

/** @deprecated use projectToTimeline */
export const storyboardToTimeline = projectToTimeline;

/** @deprecated use timelineToProject */
export const timelineToStoryboard = timelineToProject;
