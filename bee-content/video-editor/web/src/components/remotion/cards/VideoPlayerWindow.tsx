import React from 'react';
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../primitives/QualityContext';
import { mediaUrl } from '../SafeMedia';
import type { OverlayProps } from '../overlays';
import { AnimatedBG } from './AnimatedBG';

export interface VideoPlayerData {
  title: string;
  description?: string;
  src?: string;
  windowTitle: string;
  scrubberPosition: number;
  background: string;
}

export function parseVideoPlayerData(
  content: string,
  metadata?: Record<string, any> | null,
): VideoPlayerData {
  let title: string;
  let description: string | undefined;

  if (!content && metadata) {
    title = metadata.title || '';
    description = metadata.description || undefined;
  } else {
    const parts = content.split(/\s*[—–]\s*/);
    title = parts[0]?.trim() || content;
    description = parts[1]?.trim() || undefined;
  }

  return {
    title,
    description,
    src: metadata?.src || undefined,
    windowTitle: (metadata?.windowTitle as string) || 'Video Player',
    scrubberPosition: metadata?.scrubberPosition ?? 0.4,
    background: (metadata?.background as string) || '#000',
  };
}

function PlaybackControls({ scrubberPosition }: { scrubberPosition: number }) {
  const barWidth = 400;
  const filledWidth = barWidth * scrubberPosition;

  return (
    <div style={{
      height: 36, background: '#1a1a1a', display: 'flex',
      alignItems: 'center', padding: '0 12px', gap: 10,
    }}>
      {/* Play button */}
      <svg width="16" height="16" viewBox="0 0 16 16" fill="white">
        <path d="M4 2l10 6-10 6V2z" />
      </svg>
      {/* Scrubber bar */}
      <div style={{
        flex: 1, height: 4, background: '#444', borderRadius: 2,
        position: 'relative',
      }}>
        <div style={{
          width: `${scrubberPosition * 100}%`, height: '100%',
          background: '#28c840', borderRadius: 2,
        }} />
        <div style={{
          position: 'absolute', top: -4, left: `${scrubberPosition * 100}%`,
          width: 12, height: 12, borderRadius: '50%', background: '#28c840',
          transform: 'translateX(-50%)',
        }} />
      </div>
      {/* Volume icon */}
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
        <path d="M11 5L6 9H2v6h4l5 4V5z" />
        <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
        <path d="M15.54 8.46a5 5 0 0 1 0 7.08" />
      </svg>
    </div>
  );
}

function VideoPlayerChrome({ title, children, scrubberPosition }: {
  title: string;
  children: React.ReactNode;
  scrubberPosition: number;
}) {
  return (
    <div style={{
      background: '#1e1e1e', borderRadius: 10, overflow: 'hidden',
      boxShadow: '0 20px 60px rgba(0,0,0,0.6)', width: '100%', maxWidth: 640,
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
        {['File', 'Edit', 'Playback', 'Audio', 'Video', 'View', 'Help'].map(m => (
          <span key={m} style={{ color: '#aaa', fontSize: 11, fontFamily: 'system-ui, Arial, sans-serif' }}>{m}</span>
        ))}
      </div>
      {/* Content area */}
      <div style={{ position: 'relative' }}>
        {children}
        {/* Title overlay at bottom of content */}
      </div>
      {/* Playback controls */}
      <PlaybackControls scrubberPosition={scrubberPosition} />
    </div>
  );
}

function ContentArea({ src, title, description }: { src?: string; title: string; description?: string }) {
  if (src) {
    return (
      <div style={{ height: 320, background: '#000', overflow: 'hidden', position: 'relative' }}>
        <Img src={mediaUrl(src)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        <div style={{
          position: 'absolute', bottom: 0, left: 0, right: 0,
          background: 'linear-gradient(transparent, rgba(0,0,0,0.8))',
          padding: '24px 16px 12px',
        }}>
          <div style={{
            color: '#fff', fontSize: 20, fontWeight: 700,
            fontFamily: 'Arial, Helvetica, sans-serif',
            textShadow: '0 2px 8px rgba(0,0,0,0.7)',
          }}>{title}</div>
          {description && (
            <div style={{
              color: '#ccc', fontSize: 13, fontFamily: 'Arial, Helvetica, sans-serif', marginTop: 2,
              textShadow: '0 1px 4px rgba(0,0,0,0.6)',
            }}>{description}</div>
          )}
        </div>
      </div>
    );
  }
  // Placeholder play icon
  return (
    <div style={{
      height: 320, background: '#000', display: 'flex',
      flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12,
    }}>
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <circle cx="32" cy="32" r="30" stroke="#666" strokeWidth="2" />
        <path d="M26 20l20 12-20 12V20z" fill="#666" />
      </svg>
      <div style={{
        color: '#fff', fontSize: 20, fontWeight: 700,
        fontFamily: 'Arial, Helvetica, sans-serif',
      }}>{title}</div>
      {description && (
        <div style={{
          color: '#ccc', fontSize: 13, fontFamily: 'Arial, Helvetica, sans-serif',
        }}>{description}</div>
      )}
    </div>
  );
}

function VideoPlayerVisual({
  data, durationInFrames, background,
}: { data: VideoPlayerData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig } = useQuality();

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  // Entrance spring (scale 0.9→1, opacity 0→1)
  const enterProgress = spring({ frame, fps, config: springConfig });
  const enterScale = interpolate(enterProgress, [0, 1], [0.9, 1]);
  const enterOpacity = interpolate(enterProgress, [0, 1], [0, 1]);

  const bgStyle = background?.startsWith('animated-') ? undefined : { backgroundColor: background };

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', ...bgStyle }}>
      {background?.startsWith('animated-') && (
        <AbsoluteFill>
          <AnimatedBG preset={background} />
        </AbsoluteFill>
      )}
      <div style={{
        opacity: exitOpacity * enterOpacity,
        transform: `scale(${enterScale})`,
        width: '100%', maxWidth: 640,
      }}>
        <VideoPlayerChrome title={data.windowTitle} scrubberPosition={data.scrubberPosition}>
          <ContentArea src={data.src} title={data.title} description={data.description} />
        </VideoPlayerChrome>
      </div>
    </AbsoluteFill>
  );
}

export const VideoPlayerWindowOverlay: React.FC<OverlayProps> = (props) => {
  const data = parseVideoPlayerData(props.content, props.metadata);
  return <VideoPlayerVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const VideoPlayerWindow: React.FC<OverlayProps> = (props) => {
  const data = parseVideoPlayerData(props.content, props.metadata);
  return <VideoPlayerVisual data={data} durationInFrames={props.durationInFrames} background={data.background} />;
};
