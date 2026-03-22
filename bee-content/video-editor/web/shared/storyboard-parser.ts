import type {
  BeeProject,
  BeeSegment,
  VisualEntry,
  AudioEntry,
  OverlayEntry,
  MusicEntry,
  TransitionEntry,
  ProductionState,
} from './types';

// ---------- Timecode helper ----------

function parseTimecode(tc: string): number {
  const parts = tc.trim().split(':').map(Number);
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return 0;
}

// ---------- Visual type normalization ----------

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
  // Text overlays
  'QUOTE-CARD': 'GRAPHIC', 'TIMELINE-MARKER': 'GRAPHIC',
  'TIMELINE-SEQUENCE': 'GRAPHIC', 'FINANCIAL-CARD': 'GRAPHIC',
  'NEWS-MONTAGE': 'GRAPHIC', 'CAPTION-ANIMATED': 'GRAPHIC',
  // Transitions (handle gracefully)
  'TR-HARD': 'BLACK', 'TR-GLITCH': 'BLACK', 'TR-FLASH': 'BLACK',
  'TR-FADE': 'BLACK', 'TR-DISSOLVE': 'BLACK', 'TR-ZOOM': 'BLACK',
  'TR-SMASH': 'BLACK', 'TR-LCUT': 'BLACK',
  // Standard types pass through
  'FOOTAGE': 'FOOTAGE', 'STOCK': 'STOCK', 'PHOTO': 'PHOTO',
  'MAP': 'MAP', 'GRAPHIC': 'GRAPHIC', 'WAVEFORM': 'WAVEFORM',
  'BLACK': 'BLACK', 'GENERATED': 'GENERATED',
};

function normalizeVisualType(code: string): string {
  return VISUAL_TYPE_MAP[code] ?? VISUAL_TYPE_MAP[code.toUpperCase()] ?? 'GRAPHIC';
}

// ---------- Duration helpers ----------

/** Accept seconds (number) or timecode string (e.g. "1:30") → seconds */
function parseDuration(raw: number | string): number {
  if (typeof raw === 'number') return raw;
  if (typeof raw === 'string' && raw.includes(':')) return parseTimecode(raw);
  return Number(raw) || 0;
}

// ---------- Slug helper ----------

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// ---------- Default production state ----------

function defaultProduction(): ProductionState {
  return {
    narrationEngine: 'edge',
    narrationVoice: 'en-US-GuyNeural',
    transitionMode: 'overlap',
    status: {
      narration: null,
      stock: null,
      render: null,
    },
    renders: [],
  };
}

// ---------- Raw segment JSON shape ----------

interface RawSegmentJson {
  duration?: number | string;
  visual?: Array<Record<string, any>>;
  audio?: Array<Record<string, any>>;
  overlay?: Array<Record<string, any>>;
  music?: Array<Record<string, any>>;
  transition?: { type: string; duration: number } | null;
  [key: string]: any;
}

// ---------- Main parser ----------

/**
 * Parse a storyboard markdown file (v2 format) into a BeeProject.
 *
 * Extracts:
 * - `bee-video:project` JSON block → project config
 * - `bee-video:segment` JSON blocks → segments (paired with ## / ### headers)
 */
export function parseStoryboardMarkdown(markdown: string): BeeProject {
  const now = new Date().toISOString();

  // ---- Extract project block ----
  const projectMatch = markdown.match(
    /```bee-video:project\s*\n([\s\S]*?)\n```/
  );
  let projectConfig: { title?: string; fps?: number; resolution?: [number, number] } = {};
  if (projectMatch) {
    try {
      projectConfig = JSON.parse(projectMatch[1]);
    } catch {
      // malformed JSON — use defaults
    }
  }

  const title = projectConfig.title ?? 'Untitled';
  const fps = projectConfig.fps ?? 30;
  const resolution: [number, number] = projectConfig.resolution ?? [1920, 1080];

  // ---- Walk lines, collecting section headers + segment headers + segment blocks ----

  type PendingSegment = {
    id: string | null;
    title: string;
    section: string;
    rawJson: string;
  };

  const pending: PendingSegment[] = [];
  let currentSection = '';
  let currentSegmentHeader: { id: string | null; title: string } | null = null;
  let inSegmentBlock = false;
  let inProjectBlock = false;
  let blockLines: string[] = [];

  const lines = markdown.split('\n');
  for (const line of lines) {
    // Detect opening code fence
    if (!inSegmentBlock && !inProjectBlock) {
      if (line.startsWith('```bee-video:project')) {
        inProjectBlock = true;
        continue;
      }
      if (line.startsWith('```bee-video:segment')) {
        inSegmentBlock = true;
        blockLines = [];
        continue;
      }

      // Section header (## ...)
      const sectionMatch = line.match(/^##\s+(.+)$/);
      if (sectionMatch) {
        currentSection = sectionMatch[1].trim();
        continue;
      }

      // Segment header (### id | Title  or  ### Title)
      const segHeaderMatch = line.match(/^###\s+(.+)$/);
      if (segHeaderMatch) {
        const raw = segHeaderMatch[1].trim();
        const pipeIdx = raw.indexOf('|');
        if (pipeIdx !== -1) {
          const idPart = raw.slice(0, pipeIdx).trim();
          const titlePart = raw.slice(pipeIdx + 1).trim();
          currentSegmentHeader = { id: idPart || null, title: titlePart };
        } else {
          currentSegmentHeader = { id: null, title: raw };
        }
        continue;
      }

      continue;
    }

    // Inside project block — skip until closing fence
    if (inProjectBlock) {
      if (line.startsWith('```')) {
        inProjectBlock = false;
      }
      continue;
    }

    // Inside segment block
    if (inSegmentBlock) {
      if (line.startsWith('```')) {
        // End of block — save it
        inSegmentBlock = false;
        const rawJson = blockLines.join('\n');
        const header = currentSegmentHeader ?? { id: null, title: 'Segment' };
        pending.push({
          id: header.id,
          title: header.title,
          section: currentSection,
          rawJson,
        });
        currentSegmentHeader = null;
        blockLines = [];
      } else {
        blockLines.push(line);
      }
    }
  }

  // ---- Parse each pending segment into BeeSegment ----

  const segments: BeeSegment[] = [];
  let cumulativeStart = 0;

  for (const p of pending) {
    let raw: RawSegmentJson = {};
    try {
      raw = JSON.parse(p.rawJson);
    } catch {
      // Skip malformed segments
      continue;
    }

    const duration = parseDuration(raw.duration ?? 0);

    // Visual entries
    const visual: VisualEntry[] = (raw.visual ?? []).map((v: Record<string, any>): VisualEntry => {
      const { type, src, trim, color, kenBurns, query, lat, lng, ...rest } = v;
      return {
        type: normalizeVisualType(String(type ?? 'FOOTAGE')),
        src: src ?? null,
        ...(trim !== undefined && { trim }),
        ...(color !== undefined && { color }),
        ...(kenBurns !== undefined && { kenBurns }),
        ...(query !== undefined && { query }),
        ...(lat !== undefined && { lat }),
        ...(lng !== undefined && { lng }),
        ...rest,
      };
    });

    // Audio entries
    const audio: AudioEntry[] = (raw.audio ?? []).map((a: Record<string, any>): AudioEntry => ({
      type: String(a.type ?? 'NAR'),
      src: a.src ?? null,
      ...(a.text !== undefined && { text: a.text }),
      ...(a.volume !== undefined && { volume: a.volume }),
    }));

    // Overlay entries
    const overlay: OverlayEntry[] = (raw.overlay ?? []).map((o: Record<string, any>): OverlayEntry => {
      const { type, content, startOffset, duration: oDur, platform, animation, ...rest } = o;
      return {
        type: String(type ?? 'LOWER_THIRD'),
        content: String(content ?? ''),
        ...(startOffset !== undefined && { startOffset }),
        ...(oDur !== undefined && { duration: oDur }),
        ...(platform !== undefined && { platform }),
        ...(animation !== undefined && { animation }),
        ...rest,
      };
    });

    // Music entries
    const music: MusicEntry[] = (raw.music ?? []).map((m: Record<string, any>): MusicEntry => ({
      type: String(m.type ?? 'MUSIC'),
      src: m.src ?? null,
      ...(m.volume !== undefined && { volume: m.volume }),
    }));

    // Transition
    let transition: TransitionEntry | null = null;
    if (raw.transition && typeof raw.transition === 'object') {
      transition = {
        type: String(raw.transition.type),
        duration: Number(raw.transition.duration),
      };
    }

    const id = p.id ?? (slugify(p.title) || `seg-${segments.length + 1}`);

    segments.push({
      id,
      title: p.title,
      section: p.section,
      start: cumulativeStart,
      duration,
      visual,
      audio,
      overlay,
      music,
      transition,
    });

    cumulativeStart += duration;
  }

  return {
    version: 1,
    title,
    fps,
    resolution,
    createdAt: now,
    updatedAt: now,
    segments,
    production: defaultProduction(),
  };
}
