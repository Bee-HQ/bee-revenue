import { AbsoluteFill, Sequence, useVideoConfig } from 'remotion';
import type { Storyboard } from '../types';
import { parseTimecode, timeToFrames } from '../adapters/time-utils';
import { LowerThird } from './remotion/LowerThird';
import { CaptionOverlay } from './remotion/CaptionOverlay';
import { KenBurns } from './remotion/KenBurns';
import { PlaceholderFrame, isRealFile } from './remotion/PlaceholderFrame';
import { SafeVideo, SafeImg, mediaUrl, IMAGE_EXTS, COLOR_FILTERS } from './remotion/SafeMedia';

export const BeeComposition: React.FC<{ storyboard: Storyboard; mediaFiles?: string[]; showCaptions?: boolean }> = ({
  storyboard,
  mediaFiles = [],
  showCaptions = true,
}) => {
  const { fps } = useVideoConfig();

  // Build a set of known file paths for fast lookup
  const knownFiles = new Set(mediaFiles);

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
            {!isRealFile(src) || !knownFiles.has(src!) ? (
              <PlaceholderFrame type={seg.visual[0]?.content_type || 'NONE'} title={seg.title} />
            ) : (() => {
              const contentType = seg.visual[0]?.content_type || 'NONE';
              const mediaStyle = { width: '100%' as const, height: '100%' as const, objectFit: 'cover' as const };
              const visualContent = isImage ? (
                <SafeImg
                  src={mediaUrl(src)}
                  type={contentType}
                  title={seg.title}
                  style={mediaStyle}
                />
              ) : (
                <SafeVideo
                  src={mediaUrl(src)}
                  type={contentType}
                  title={seg.title}
                  style={mediaStyle}
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
            {showCaptions && narrationText && (
              <CaptionOverlay text={narrationText} style="karaoke" />
            )}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
