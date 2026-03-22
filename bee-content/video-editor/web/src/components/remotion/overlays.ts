// web/src/components/remotion/overlays.ts
import type { LayerEntryMetadata } from '../../types';

export interface OverlayProps {
  content: string;
  metadata?: LayerEntryMetadata | null;
  durationInFrames: number;
}

export const DEFAULT_DURATIONS: Record<string, number> = {
  LOWER_THIRD: 4,      // seconds
  TIMELINE_MARKER: 3,
  QUOTE_CARD: 4,
  FINANCIAL_CARD: 3,
  TEXT_OVERLAY: 3,
  TEXT_CHAT: 5,
};

/** Parse "quote text — Author" into parts */
export function parseQuoteContent(content: string): { quote: string; author: string } {
  const parts = content.split(/\s*[—–]\s*/);
  return { quote: parts[0]?.trim() || content, author: parts[1]?.trim() || '' };
}

/** Parse "$1.4 million — Description" into parts */
export function parseDollarAmount(text: string): { displayValue: string; numericValue: number; description: string } {
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
export function parseLowerThirdContent(content: string): { name: string; role?: string } {
  const parts = content.split(/\s*[—–]\s*/);
  return { name: parts[0]?.trim() || content, role: parts[1]?.trim() || undefined };
}

import type { Segment } from '../../types';
import { parseTimecode } from '../../adapters/time-utils';

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

export function getTransitionInfo(seg: Segment, fps: number): TransitionInfo | null {
  const trans = seg.transition[0];
  if (!trans) return null;
  const durationSec = parseFloat(trans.content?.replace('s', '') || '1');
  return { type: trans.content_type, durationInFrames: Math.round(durationSec * fps) };
}

export function calculateSegmentPositions(
  segments: Segment[],
  fps: number,
  mode: 'overlap' | 'fade',
): { positions: SegmentPosition[]; totalFrames: number } {
  const positions: SegmentPosition[] = [];

  if (mode === 'fade') {
    // Absolute positioning from timecodes
    let maxFrame = 0;
    for (const seg of segments) {
      const from = Math.round(parseTimecode(seg.start) * fps);
      const duration = Math.round(seg.duration_seconds * fps);
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
    const duration = Math.round(seg.duration_seconds * fps);
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
    const nextDuration = nextSeg ? Math.round(nextSeg.duration_seconds * fps) : 0;
    let overlap = 0;
    if (nextTransInfo && nextDuration > 0) {
      const clampedNext = Math.min(nextTransInfo.durationInFrames, nextDuration);
      overlap = clampedNext;
    }
    currentFrame += duration - overlap;
  }
  return { positions, totalFrames: Math.max(1, currentFrame) };
}
