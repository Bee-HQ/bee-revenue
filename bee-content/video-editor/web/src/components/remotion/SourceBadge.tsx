import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import type { OverlayProps } from './overlays';

export interface SourceBadgeData {
  label: string;
  position: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right';
}

export function parseSourceBadgeData(
  content: string,
  metadata?: Record<string, any> | null,
): SourceBadgeData {
  return {
    label: content || metadata?.text || '',
    position: (metadata?.position as SourceBadgeData['position']) || 'bottom-left',
  };
}

const POSITION_STYLES: Record<SourceBadgeData['position'], React.CSSProperties> = {
  'bottom-left': { bottom: 24, left: 24 },
  'bottom-right': { bottom: 24, right: 24 },
  'top-left': { top: 24, left: 24 },
  'top-right': { top: 24, right: 24 },
};

export const SourceBadge: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { label, position } = parseSourceBadgeData(content, metadata);

  const fadeIn = interpolate(frame, [0, 10], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const fadeOut = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const opacity = fadeIn * fadeOut;

  return (
    <AbsoluteFill>
      <div style={{
        position: 'absolute',
        ...POSITION_STYLES[position],
        opacity,
        background: 'rgba(0, 0, 0, 0.6)',
        padding: '4px 10px',
        borderRadius: 3,
      }}>
        <span style={{
          color: '#cccccc',
          fontSize: 13,
          fontFamily: "'Courier New', monospace",
          letterSpacing: 0.5,
        }}>
          [{label}]
        </span>
      </div>
    </AbsoluteFill>
  );
};
