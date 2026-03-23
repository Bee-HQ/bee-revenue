import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from '../overlays';
import { resolveColor } from '../overlays';

export interface DramaticQuoteData {
  text: string;
  color: string;
  italic: boolean;
  position: 'center' | 'bottom' | 'top';
}

export function parseDramaticQuoteData(
  content: string,
  metadata?: Record<string, any> | null,
): DramaticQuoteData {
  return {
    text: content || metadata?.text || '',
    color: resolveColor(metadata?.color || 'red'),
    italic: metadata?.italic !== undefined ? Boolean(metadata.italic) : true,
    position: (metadata?.position as DramaticQuoteData['position']) || 'center',
  };
}

const POSITION_STYLES: Record<DramaticQuoteData['position'], React.CSSProperties> = {
  center: { justifyContent: 'center' },
  top: { justifyContent: 'flex-start', paddingTop: 80 },
  bottom: { justifyContent: 'flex-end', paddingBottom: 120 },
};

export const DramaticQuote: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { text, color, italic, position } = parseDramaticQuoteData(content, metadata);

  if (!text) return null;

  // Scale spring: 0.8 -> 1.0 over first 20 frames
  const scaleRaw = spring({ frame, fps, config: { stiffness: 120, damping: 14 }, durationInFrames: 20 });
  const scale = interpolate(scaleRaw, [0, 1], [0.8, 1]);

  // Opacity fade in over 10 frames
  const fadeIn = interpolate(frame, [0, 10], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Exit fade over last 15 frames
  const fadeOut = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const opacity = fadeIn * fadeOut;

  return (
    <AbsoluteFill style={{
      alignItems: 'center',
      ...POSITION_STYLES[position],
    }}>
      <div style={{
        opacity,
        transform: `scale(${scale})`,
        maxWidth: '80%',
        textAlign: 'center',
        lineHeight: 1.2,
      }}>
        <span style={{
          color,
          fontSize: 60,
          fontWeight: 800,
          fontFamily: 'Arial, Helvetica, sans-serif',
          fontStyle: italic ? 'italic' : 'normal',
          textTransform: 'uppercase',
          WebkitTextStroke: '1px rgba(0,0,0,0.3)',
          textShadow: `0 0 20px ${color}80, 0 4px 12px rgba(0,0,0,0.8)`,
        }}>
          &ldquo;{text}&rdquo;
        </span>
      </div>
    </AbsoluteFill>
  );
};
