// web/src/components/remotion/overlays.ts

export interface OverlayProps {
  content: string;
  metadata?: Record<string, any> | null;
  durationInFrames: number;
}

export const DEFAULT_DURATIONS: Record<string, number> = {
  LOWER_THIRD: 4,      // seconds
  TIMELINE_MARKER: 3,
  QUOTE_CARD: 4,
  FINANCIAL_CARD: 3,
  TEXT_OVERLAY: 3,
  TEXT_CHAT: 5,
  EVIDENCE_BOARD: 8,
  MAP: 6,
  SOCIAL_POST: 5,
  PIP: 10,
  AUDIO_VIS: 8,
  WAVEFORM: 8,
  CALLOUT: 4,
  KINETIC_TEXT: 5,
  SOURCE_BADGE: 30,
  BULLET_LIST: 6,
  PHOTO_VIEWER: 5,
  INFO_CARD: 6,
  LOTTIE: 4,
  ATMOSPHERE: 10,
  GLITCH: 3,
  INFOGRAPHIC: 8,
  DATA_VIZ: 6,
  TITLE_CARD: 4,
  SCREEN_MOCKUP: 10,
  THREE_D: 8,
  NOTEPAD: 6,
  MAP_ANNOTATION: 6,
};

export const NAMED_COLORS: Record<string, string> = {
  red: '#dc2626',
  teal: '#0d9488',
  gold: '#d97706',
  green: '#16a34a',
  white: '#ffffff',
};

export function resolveColor(color: string): string {
  return NAMED_COLORS[color] || color;
}

/** Parse "quote text — Author" into parts */
export function parseQuoteContent(content: string, metadata?: Record<string, any> | null): { quote: string; author: string } {
  if (!content && metadata) {
    return { quote: metadata.quote || metadata.text || '', author: metadata.author || '' };
  }
  const parts = content.split(/\s*[—–]\s*/);
  return { quote: parts[0]?.trim() || content, author: parts[1]?.trim() || '' };
}

/** Parse "$1.4 million — Description" into parts */
export function parseDollarAmount(text: string, metadata?: Record<string, any> | null): { displayValue: string; numericValue: number; description: string } {
  if (!text && metadata) {
    const amount = metadata.amount || metadata.value || '';
    const desc = metadata.description || '';
    text = desc ? `${amount} — ${desc}` : amount;
  }
  const parts = text.split(/\s*[—–]\s*/);
  const dollarPart = parts[0]?.trim() || text;
  const description = parts[1]?.trim() || '';

  const cleaned = dollarPart.replace(/[$,]/g, '').trim();
  const match = cleaned.match(/^([\d.]+)\s*(million|billion|thousand|k|m|b)?/i);
  if (!match) return { displayValue: dollarPart, numericValue: 0, description };

  const num = parseFloat(match[1]);
  const multipliers: Record<string, number> = { thousand: 1e3, k: 1e3, million: 1e6, m: 1e6, billion: 1e9, b: 1e9 };
  const mult = match[2] ? (multipliers[match[2].toLowerCase()] || 1) : 1;
  const numericValue = num * mult;
  return { displayValue: dollarPart, numericValue, description };
}

/** Parse "Name — Role" for LowerThird adapter */
export function parseLowerThirdContent(content: string, metadata?: Record<string, any> | null): { name: string; role?: string } {
  if (!content && metadata) {
    return { name: metadata.text || metadata.name || '', role: metadata.subtext || metadata.role || undefined };
  }
  const parts = content.split(/\s*[—–]\s*/);
  return { name: parts[0]?.trim() || content, role: parts[1]?.trim() || undefined };
}

import type { BeeSegment } from '../../types';

export interface TransitionInfo {
  type: string;
  durationInFrames: number;
}

export interface SegmentPosition {
  segId: string;
  from: number;
  duration: number;
  transitionIn?: TransitionInfo;
}

export function getTransitionInfo(seg: BeeSegment, fps: number): TransitionInfo | null {
  if (!seg.transition) return null;
  return { type: seg.transition.type, durationInFrames: Math.round(seg.transition.duration * fps) };
}

export function calculateSegmentPositions(
  segments: BeeSegment[],
  fps: number,
  mode: 'overlap' | 'fade',
): { positions: SegmentPosition[]; totalFrames: number } {
  const positions: SegmentPosition[] = [];

  if (mode === 'fade') {
    // Absolute positioning from start seconds
    let maxFrame = 0;
    for (const seg of segments) {
      const from = Math.round(seg.start * fps);
      const duration = Math.round(seg.duration * fps);
      if (duration <= 0) continue;
      const transInfo = getTransitionInfo(seg, fps);
      positions.push({ segId: seg.id, from, duration, transitionIn: transInfo || undefined });
      maxFrame = Math.max(maxFrame, from + duration);
    }
    return { positions, totalFrames: Math.max(1, maxFrame) };
  }

  // Overlap mode: sequential, transitions eat into the preceding segment's advance
  let currentFrame = 0;
  for (let i = 0; i < segments.length; i++) {
    const seg = segments[i];
    const duration = Math.round(seg.duration * fps);
    if (duration <= 0) continue;
    const transInfo = getTransitionInfo(seg, fps);
    // Clamp transition to segment duration
    if (transInfo && transInfo.durationInFrames > duration) {
      transInfo.durationInFrames = duration;
    }
    positions.push({ segId: seg.id, from: currentFrame, duration, transitionIn: transInfo || undefined });
    // The next segment's transition (transitionIn) causes it to overlap with this segment,
    // so we look ahead: if the next segment has a transition, subtract its duration from our advance.
    const nextSeg = segments[i + 1];
    const nextTransInfo = nextSeg ? getTransitionInfo(nextSeg, fps) : null;
    const nextDuration = nextSeg ? Math.round(nextSeg.duration * fps) : 0;
    let overlap = 0;
    if (nextTransInfo && nextDuration > 0) {
      const clampedNext = Math.min(nextTransInfo.durationInFrames, nextDuration);
      overlap = clampedNext;
    }
    currentFrame += duration - overlap;
  }
  return { positions, totalFrames: Math.max(1, currentFrame) };
}
