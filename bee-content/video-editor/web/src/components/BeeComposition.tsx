import { AbsoluteFill, Sequence, Video, Img, useVideoConfig } from 'remotion';
import type { Storyboard } from '../types';
import { parseTimecode, timeToFrames } from '../adapters/time-utils';
import { LowerThird } from './remotion/LowerThird';
import { CaptionOverlay } from './remotion/CaptionOverlay';
import { KenBurns } from './remotion/KenBurns';

// Remotion renders inside an iframe — media URLs must be same-origin accessible.
// In dev, Vite proxies /api to the backend.
function mediaUrl(path: string): string {
  return `/api/media/file?path=${encodeURIComponent(path)}`;
}

/** Check if a src path looks like an actual file (not a description or query) */
function isRealFile(src: string | undefined): boolean {
  if (!src) return false;
  // Must contain a slash or end with a media extension
  const hasPath = src.includes('/');
  const hasExt = /\.(mp4|mov|mkv|webm|avi|jpg|jpeg|png|webp|gif|mp3|wav|m4a)$/i.test(src);
  return hasPath || hasExt;
}

function PlaceholderFrame({ type, title }: { type: string; title: string }) {
  const typeColors: Record<string, string> = {
    STOCK: '#1e40af', MAP: '#166534', GRAPHIC: '#86198f',
    GENERATED: '#7c2d12', WAVEFORM: '#065f46', PHOTO: '#6b21a8',
  };
  const bg = typeColors[type] || '#1a1a1a';
  return (
    <AbsoluteFill style={{ backgroundColor: bg, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
      <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 48 }}>
        {type === 'STOCK' ? '📦' : type === 'MAP' ? '🗺️' : type === 'GRAPHIC' ? '🎨' : type === 'GENERATED' ? '🤖' : '🎬'}
      </span>
      <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: 16, fontFamily: 'Arial' }}>{type}</span>
      <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12, fontFamily: 'Arial' }}>{title}</span>
    </AbsoluteFill>
  );
}

function BlackFrame() {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#0f0f0f',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <span style={{ color: '#333', fontSize: 14 }}>No media</span>
    </AbsoluteFill>
  );
}

const IMAGE_EXTS = new Set(['jpg', 'jpeg', 'png', 'webp', 'gif']);

const COLOR_FILTERS: Record<string, string> = {
  dark_crime: 'brightness(0.85) saturate(0.6) contrast(1.2) sepia(0.1)',
  surveillance: 'brightness(0.8) saturate(0.3) contrast(1.1) hue-rotate(90deg)',
  noir: 'brightness(0.9) saturate(0) contrast(1.3)',
  bodycam: 'brightness(0.85) saturate(0.5) contrast(1.1) sepia(0.15)',
  cold_blue: 'brightness(0.9) saturate(0.7) contrast(1.1) hue-rotate(200deg)',
  warm_victim: 'brightness(0.9) saturate(0.8) sepia(0.2)',
  sepia: 'brightness(0.95) saturate(0.5) sepia(0.6)',
  vintage: 'brightness(0.9) saturate(0.7) sepia(0.3) contrast(1.1)',
  bleach_bypass: 'brightness(1.1) saturate(0.4) contrast(1.4)',
  night_vision: 'brightness(0.7) saturate(0.3) hue-rotate(90deg) contrast(1.3)',
  golden_hour: 'brightness(1.05) saturate(1.2) sepia(0.15)',
  vhs: 'brightness(0.95) saturate(0.8) contrast(0.9)',
};

export const BeeComposition: React.FC<{ storyboard: Storyboard }> = ({
  storyboard,
}) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {storyboard.segments.map((seg) => {
        const src = seg.assigned_media['visual:0'];
        const from = timeToFrames(parseTimecode(seg.start), fps);
        const duration = timeToFrames(seg.duration_seconds, fps);

        if (duration <= 0) return null;

        const ext = src?.split('.').pop()?.toLowerCase() ?? '';
        const isImage = IMAGE_EXTS.has(ext);

        // Color grade from visual metadata
        const colorPreset = seg.visual[0]?.metadata?.color;
        const colorFilter = colorPreset ? COLOR_FILTERS[colorPreset] : undefined;

        // Ken Burns effect
        const kenBurns = seg.visual[0]?.metadata?.ken_burns;

        // Overlays
        const lowerThirds = seg.overlay.filter(
          (o) => o.content_type === 'LOWER_THIRD',
        );
        const timelineMarkers = seg.overlay.filter(
          (o) => o.content_type === 'TIMELINE_MARKER',
        );

        // Narration for captions
        const narEntry = seg.audio.find((a) => a.content_type === 'NAR');
        const narrationText = narEntry?.content || '';

        return (
          <Sequence
            key={seg.id}
            from={from}
            durationInFrames={duration}
            name={seg.title}
          >
            {/* Base visual with color grade + Ken Burns */}
            {!isRealFile(src) ? (
              <PlaceholderFrame type={seg.visual[0]?.content_type || 'NONE'} title={seg.title} />
            ) : (() => {
              const visualContent = isImage ? (
                <Img
                  src={mediaUrl(src)}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : (
                <Video
                  src={mediaUrl(src)}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              );

              const graded = (
                <AbsoluteFill style={{ filter: colorFilter }}>
                  {visualContent}
                </AbsoluteFill>
              );

              return kenBurns ? (
                <KenBurns effect={kenBurns}>{graded}</KenBurns>
              ) : graded;
            })()}

            {/* Lower thirds */}
            {lowerThirds.map((lt, i) => {
              const parts = lt.content.split(/\s*[—–-]\s*/);
              const name = parts[0]?.trim() || lt.content;
              const role = parts[1]?.trim() || '';
              const ltDuration = Math.min(4 * fps, duration);
              return (
                <Sequence
                  key={`lt-${i}`}
                  from={0}
                  durationInFrames={ltDuration}
                >
                  <LowerThird
                    name={name}
                    role={role || undefined}
                    durationInFrames={ltDuration}
                  />
                </Sequence>
              );
            })}

            {/* Timeline markers */}
            {timelineMarkers.map((tm, i) => (
              <Sequence
                key={`tm-${i}`}
                from={0}
                durationInFrames={Math.min(3 * fps, duration)}
              >
                <AbsoluteFill
                  style={{
                    justifyContent: 'flex-start',
                    alignItems: 'flex-end',
                    padding: '40px 60px',
                  }}
                >
                  <div
                    style={{
                      background: 'rgba(220, 38, 38, 0.9)',
                      padding: '8px 20px',
                      color: '#fff',
                      fontSize: 24,
                      fontWeight: 700,
                      fontFamily: 'Arial, Helvetica, sans-serif',
                    }}
                  >
                    {tm.content}
                  </div>
                </AbsoluteFill>
              </Sequence>
            ))}

            {/* Captions */}
            {narrationText && (
              <CaptionOverlay text={narrationText} style="karaoke" />
            )}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
