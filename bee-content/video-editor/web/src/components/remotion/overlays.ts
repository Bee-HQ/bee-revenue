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
  const parts = content.split(/\s*[—–-]\s*/);
  return { name: parts[0]?.trim() || content, role: parts[1]?.trim() || undefined };
}
