import { useEffect } from 'react';
import { AbsoluteFill, Sequence, useVideoConfig } from 'remotion';
import type { Storyboard, Segment } from '../types';
import { parseTimecode } from '../adapters/time-utils';
import { useProjectStore } from '../stores/project';
import { PlaceholderFrame, isRealFile } from './remotion/PlaceholderFrame';
import { SafeVideo, SafeImg, mediaUrl, IMAGE_EXTS, COLOR_FILTERS } from './remotion/SafeMedia';
import { KenBurns } from './remotion/KenBurns';
import { LowerThird } from './remotion/LowerThird';
import { CaptionOverlay } from './remotion/CaptionOverlay';
import { QuoteCard } from './remotion/QuoteCard';
import { FinancialCard } from './remotion/FinancialCard';
import { TextOverlay } from './remotion/TextOverlay';
import { TimelineMarker } from './remotion/TimelineMarker';
import { TransitionRenderer } from './remotion/TransitionRenderer';
import { calculateSegmentPositions, parseLowerThirdContent, DEFAULT_DURATIONS } from './remotion/overlays';
import type { OverlayProps } from './remotion/overlays';

const OVERLAY_COMPONENTS: Record<string, React.FC<OverlayProps>> = {
  QUOTE_CARD: QuoteCard,
  FINANCIAL_CARD: FinancialCard,
  TEXT_OVERLAY: TextOverlay,
  TIMELINE_MARKER: TimelineMarker,
};

// Renders the visual layer for a single segment (video/image/placeholder + color grade + Ken Burns)
function SegmentVisual({ seg, knownFiles }: { seg: Segment; knownFiles: Set<string> }) {
  const src = seg.assigned_media['visual:0'];
  const ext = src?.split('.').pop()?.toLowerCase() ?? '';
  const isImage = IMAGE_EXTS.has(ext);
  const contentType = seg.visual[0]?.content_type || 'NONE';
  const colorPreset = seg.visual[0]?.metadata?.color;
  const colorFilter = colorPreset ? COLOR_FILTERS[colorPreset] : undefined;
  const kenBurns = seg.visual[0]?.metadata?.ken_burns;
  const mediaStyle = { width: '100%' as const, height: '100%' as const, objectFit: 'cover' as const };

  if (!isRealFile(src) || !knownFiles.has(src!)) {
    return <PlaceholderFrame type={contentType} title={seg.title} />;
  }

  const visual = isImage
    ? <SafeImg src={mediaUrl(src)} type={contentType} title={seg.title} style={mediaStyle} />
    : <SafeVideo src={mediaUrl(src)} type={contentType} title={seg.title} style={mediaStyle} />;

  const graded = <AbsoluteFill style={{ filter: colorFilter }}>{visual}</AbsoluteFill>;
  return kenBurns ? <KenBurns effect={kenBurns}>{graded}</KenBurns> : graded;
}

// Renders all overlays for a segment using the registry
function SegmentOverlays({ seg, segDuration, fps }: { seg: Segment; segDuration: number; fps: number }) {
  return (
    <>
      {/* LowerThird -- special case (different props interface) */}
      {seg.overlay.filter(o => o.content_type === 'LOWER_THIRD').map((lt, i) => {
        const { name, role } = parseLowerThirdContent(lt.content);
        const defaultDur = Math.min(DEFAULT_DURATIONS.LOWER_THIRD * fps, segDuration);
        const offset = lt.time_start ? Math.round(parseTimecode(lt.time_start) * fps) : 0;
        const clampedDur = Math.min(defaultDur, segDuration - offset);
        return (
          <Sequence key={`lt-${i}`} from={offset} durationInFrames={clampedDur}>
            <LowerThird name={name} role={role} durationInFrames={clampedDur} />
          </Sequence>
        );
      })}

      {/* Registry-based overlays */}
      {seg.overlay.filter(o => o.content_type !== 'LOWER_THIRD').map((entry, i) => {
        const Component = OVERLAY_COMPONENTS[entry.content_type];
        if (!Component) return null;
        const defaultDur = (DEFAULT_DURATIONS[entry.content_type] || 3) * fps;
        const dur = Math.min(defaultDur, segDuration);
        const offset = entry.time_start ? Math.round(parseTimecode(entry.time_start) * fps) : 0;
        const clampedDur = Math.min(dur, segDuration - offset);
        return (
          <Sequence key={`ov-${i}`} from={offset} durationInFrames={clampedDur}>
            <Component content={entry.content} metadata={entry.metadata} durationInFrames={clampedDur} />
          </Sequence>
        );
      })}
    </>
  );
}

export const BeeComposition: React.FC<{
  storyboard: Storyboard;
  mediaFiles?: string[];
  showCaptions?: boolean;
  transitionMode?: 'overlap' | 'fade';
}> = ({ storyboard, mediaFiles = [], showCaptions = true, transitionMode = 'overlap' }) => {
  const { fps } = useVideoConfig();
  const knownFiles = new Set(mediaFiles);

  const { positions, totalFrames } = calculateSegmentPositions(storyboard.segments, fps, transitionMode);

  // Publish computed total frames so RemotionPreview can set Player duration
  useEffect(() => {
    useProjectStore.getState().setComputedTotalFrames(totalFrames);
  }, [totalFrames]);

  // Build segment lookup for transition rendering
  const segmentMap = new Map(storyboard.segments.map(s => [s.id, s]));

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {positions.map((pos) => {
        const seg = segmentMap.get(pos.segId);
        if (!seg) return null;

        const narEntry = seg.audio.find(a => a.content_type === 'NAR');
        const narrationText = narEntry?.content || '';

        // Segment content (visual + overlays + captions)
        const segmentContent = (
          <>
            <SegmentVisual seg={seg} knownFiles={knownFiles} />
            <SegmentOverlays seg={seg} segDuration={pos.duration} fps={fps} />
            {showCaptions && narrationText && <CaptionOverlay text={narrationText} style="karaoke" />}
          </>
        );

        // Apply transition if present
        if (pos.transitionIn && transitionMode === 'fade') {
          return (
            <Sequence key={seg.id} from={pos.from} durationInFrames={pos.duration} name={seg.title}>
              <TransitionRenderer type={pos.transitionIn.type} durationInFrames={pos.duration} mode="fade" position="in">
                {segmentContent}
              </TransitionRenderer>
            </Sequence>
          );
        }

        return (
          <Sequence key={seg.id} from={pos.from} durationInFrames={pos.duration} name={seg.title}>
            {segmentContent}
          </Sequence>
        );
      })}

      {/* Overlap mode: render TransitionRenderer during overlap windows */}
      {transitionMode === 'overlap' && positions.map((pos, i) => {
        if (i === 0 || !pos.transitionIn) return null;
        const prevPos = positions[i - 1];
        const prevSeg = segmentMap.get(prevPos.segId);
        const curSeg = segmentMap.get(pos.segId);
        if (!prevSeg || !curSeg) return null;

        const overlapStart = pos.from;
        const transDur = pos.transitionIn.durationInFrames;

        return (
          <Sequence key={`trans-${pos.segId}`} from={overlapStart} durationInFrames={transDur}>
            <TransitionRenderer
              type={pos.transitionIn.type}
              durationInFrames={transDur}
              mode="overlap"
              outgoing={<SegmentVisual seg={prevSeg} knownFiles={knownFiles} />}
              incoming={<SegmentVisual seg={curSeg} knownFiles={knownFiles} />}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
