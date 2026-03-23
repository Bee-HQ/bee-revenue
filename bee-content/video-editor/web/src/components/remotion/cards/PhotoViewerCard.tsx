import React from 'react';
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../primitives/QualityContext';
import { mediaUrl } from '../SafeMedia';
import type { OverlayProps } from '../overlays';

export interface PhotoViewerCardInfo {
  name: string;
  role?: string;
  src?: string;
}

export interface PhotoViewerData {
  cards: PhotoViewerCardInfo[];
  animation: 'slide-up' | 'slide-left' | 'scale';
  windowTitle: string;
}

export function parsePhotoViewerData(
  content: string,
  metadata?: Record<string, any> | null,
): PhotoViewerData {
  let cards: PhotoViewerCardInfo[];

  if (content.trimStart().startsWith('[')) {
    try {
      const parsed = JSON.parse(content);
      if (Array.isArray(parsed)) {
        cards = parsed.map((c: any) => ({
          name: c.name || '',
          role: c.role || undefined,
          src: c.src || undefined,
        }));
      } else {
        cards = [{ name: content, role: undefined, src: metadata?.src }];
      }
    } catch {
      cards = [{ name: content, role: undefined, src: metadata?.src }];
    }
  } else if (!content && metadata) {
    cards = [{
      name: metadata.name || metadata.text || '',
      role: metadata.role || metadata.subtext || undefined,
      src: metadata.src || undefined,
    }];
  } else {
    const parts = content.split(/\s*[—–]\s*/);
    cards = [{
      name: parts[0]?.trim() || content,
      role: parts[1]?.trim() || undefined,
      src: metadata?.src || undefined,
    }];
  }

  return {
    cards,
    animation: (metadata?.animation as PhotoViewerData['animation']) || 'slide-up',
    windowTitle: (metadata?.windowTitle as string) || 'Photo Viewer',
  };
}

function MacWindowChrome({ title, children, nameLabel, roleLabel, nameLabelStyle }: {
  title: string;
  children: React.ReactNode;
  nameLabel: string;
  roleLabel?: string;
  nameLabelStyle?: React.CSSProperties;
}) {
  return (
    <div style={{
      background: '#1e1e1e', borderRadius: 10, overflow: 'hidden',
      boxShadow: '0 20px 60px rgba(0,0,0,0.6)', width: '100%',
    }}>
      {/* Title bar */}
      <div style={{
        height: 32, background: '#2d2d2d', display: 'flex',
        alignItems: 'center', padding: '0 12px', gap: 8,
      }}>
        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ff5f57' }} />
        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#febc2e' }} />
        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#28c840' }} />
        <span style={{
          flex: 1, textAlign: 'center', color: '#999', fontSize: 12,
          fontFamily: 'system-ui, Arial, sans-serif',
        }}>{title}</span>
      </div>
      {/* Menu bar */}
      <div style={{
        height: 24, background: '#252525', display: 'flex',
        alignItems: 'center', padding: '0 12px', gap: 16,
      }}>
        {['File', 'Edit', 'Image', 'View', 'Help'].map(m => (
          <span key={m} style={{ color: '#aaa', fontSize: 11, fontFamily: 'system-ui, Arial, sans-serif' }}>{m}</span>
        ))}
      </div>
      {/* Photo area */}
      {children}
      {/* Name label */}
      <div style={{
        background: '#1a1a1a', padding: '10px 16px', borderTop: '1px solid #333',
        ...nameLabelStyle,
      }}>
        <div style={{
          color: '#fff', fontSize: 18, fontWeight: 700,
          fontFamily: 'Arial, Helvetica, sans-serif', letterSpacing: 1,
        }}>{nameLabel}</div>
        {roleLabel && (
          <div style={{
            color: '#999', fontSize: 12, fontFamily: 'Arial, Helvetica, sans-serif', marginTop: 2,
          }}>{roleLabel}</div>
        )}
      </div>
    </div>
  );
}

function PhotoArea({ src }: { src?: string }) {
  if (src) {
    return (
      <div style={{ height: 280, background: '#333', overflow: 'hidden' }}>
        <Img src={mediaUrl(src)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </div>
    );
  }
  // Placeholder silhouette
  return (
    <div style={{
      height: 280, background: '#333', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
    }}>
      <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#666" strokeWidth="1.5">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
    </div>
  );
}

function PhotoViewerCardVisual({
  data, durationInFrames, background,
}: { data: PhotoViewerData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  // Entrance animation for the whole container
  const enterProgress = spring({ frame, fps, config: springConfig });
  const enterTransform = data.animation === 'slide-up'
    ? `translateY(${interpolate(enterProgress, [0, 1], [200, 0])}px)`
    : data.animation === 'slide-left'
      ? `translateX(${interpolate(enterProgress, [0, 1], [-400, 0])}px)`
      : `scale(${interpolate(enterProgress, [0, 1], [0.5, 1])})`;

  // Photo fade in
  const photoOpacity = interpolate(frame, [10, 25].map(f => Math.round(f * timingMultiplier)), [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Name label slide up
  const nameLabelY = interpolate(frame, [20, 30].map(f => Math.round(f * timingMultiplier)), [20, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const nameLabelOpacity = interpolate(frame, [20, 30].map(f => Math.round(f * timingMultiplier)), [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  const cardWidth = data.cards.length === 1 ? 420 : 360;
  const staggerDelay = Math.round(8 * timingMultiplier);

  return (
    <AbsoluteFill style={{
      backgroundColor: background,
      justifyContent: 'center', alignItems: 'center',
    }}>
      <div style={{
        display: 'flex', gap: 24, opacity: exitOpacity,
        transform: enterTransform,
      }}>
        {data.cards.map((card, i) => {
          const cardProgress = i === 0 ? 1 : spring({
            frame: Math.max(0, frame - i * staggerDelay), fps, config: springConfig,
          });
          const cardOpacity = i === 0 ? 1 : interpolate(cardProgress, [0, 1], [0, 1]);

          return (
            <div key={i} style={{ width: cardWidth, opacity: cardOpacity }}>
              <MacWindowChrome title={data.windowTitle} nameLabel={card.name} roleLabel={card.role} nameLabelStyle={{ opacity: nameLabelOpacity, transform: `translateY(${nameLabelY}px)` }}>
                <div style={{ opacity: photoOpacity }}>
                  <PhotoArea src={card.src} />
                </div>
              </MacWindowChrome>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
}

export const PhotoViewerCardOverlay: React.FC<OverlayProps> = (props) => {
  const data = parsePhotoViewerData(props.content, props.metadata);
  return <PhotoViewerCardVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const PhotoViewerCard: React.FC<OverlayProps> = (props) => {
  const data = parsePhotoViewerData(props.content, props.metadata);
  return <PhotoViewerCardVisual data={data} durationInFrames={props.durationInFrames} background="#000" />;
};
