import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../primitives/QualityContext';
import type { OverlayProps } from '../overlays';

export interface BulletListData {
  items: string[];
  accent: 'red' | 'teal' | 'gold' | 'white';
  style: 'stagger' | 'cascade' | 'instant';
}

const ACCENT_COLORS: Record<BulletListData['accent'], string> = {
  red: '#dc2626',
  teal: '#0d9488',
  gold: '#d97706',
  white: '#ffffff',
};

export { ACCENT_COLORS };

export function parseBulletListData(
  content: string,
  metadata?: Record<string, any> | null,
): BulletListData {
  let items: string[];

  if (content.trimStart().startsWith('[')) {
    try {
      const parsed = JSON.parse(content);
      items = Array.isArray(parsed) ? parsed.map(String) : [content];
    } catch {
      items = content.split('\n').map(s => s.trim()).filter(Boolean);
    }
  } else {
    items = content.split('\n').map(s => s.trim()).filter(Boolean);
  }

  return {
    items,
    accent: (metadata?.accent as BulletListData['accent']) || 'red',
    style: (metadata?.style as BulletListData['style']) || 'stagger',
  };
}

function BulletListVisual({
  data, durationInFrames, background,
}: { data: BulletListData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();
  const staggerFrames = Math.round(8 * timingMultiplier);
  const accentColor = ACCENT_COLORS[data.accent] || ACCENT_COLORS.red;
  const fontSize = data.items.length > 6 ? 18 : 22;

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  return (
    <AbsoluteFill style={{ backgroundColor: background, justifyContent: 'center', padding: '0 80px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16, opacity: exitOpacity }}>
        {data.items.map((item, i) => {
          const delay = data.style === 'instant' ? 0 : i * staggerFrames;
          const progress = data.style === 'instant' ? 1 : spring({
            frame: Math.max(0, frame - delay), fps, config: springConfig,
          });
          const translateX = interpolate(progress, [0, 1], [-600, 0]);
          const opacity = interpolate(progress, [0, 1], [0, 1]);
          const indent = data.style === 'cascade' ? Math.min(i * 20, 120) : 0;

          return (
            <div key={i} style={{
              transform: `translateX(${translateX}px)`,
              opacity,
              marginLeft: indent,
              background: 'rgba(0, 0, 0, 0.75)',
              padding: '14px 24px',
              borderLeft: `3px solid ${accentColor}`,
              alignSelf: 'flex-start',
            }}>
              <span style={{
                color: '#fff',
                fontSize,
                fontWeight: 800,
                fontFamily: "'Arial Black', Arial, sans-serif",
                letterSpacing: 2,
                textTransform: 'uppercase',
              }}>
                {item}
              </span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
}

export const BulletListOverlay: React.FC<OverlayProps> = (props) => {
  const data = parseBulletListData(props.content, props.metadata);
  return <BulletListVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const BulletList: React.FC<OverlayProps> = (props) => {
  const data = parseBulletListData(props.content, props.metadata);
  return <BulletListVisual data={data} durationInFrames={props.durationInFrames} background="#000" />;
};
