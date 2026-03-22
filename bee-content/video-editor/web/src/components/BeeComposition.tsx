import { useEffect } from 'react';
import { AbsoluteFill, Sequence, useVideoConfig } from 'remotion';
import type { Storyboard, BeeSegment } from '../types';
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
import { TextChat, TextChatOverlay } from './remotion/TextChat';
import { EvidenceBoard, EvidenceBoardOverlay } from './remotion/EvidenceBoard';
import { AnimatedMap, AnimatedMapOverlay } from './remotion/AnimatedMap';
import { SocialPost, SocialPostOverlay } from './remotion/SocialPost';
import { PictureInPictureOverlay } from './remotion/PictureInPicture';
import { AudioVisualization, AudioVisualizationOverlay } from './remotion/AudioVisualization';
import { calculateSegmentPositions, parseLowerThirdContent, DEFAULT_DURATIONS } from './remotion/overlays';
import type { OverlayProps } from './remotion/overlays';

const OVERLAY_COMPONENTS: Record<string, React.FC<OverlayProps>> = {
  QUOTE_CARD: QuoteCard,
  FINANCIAL_CARD: FinancialCard,
  TEXT_OVERLAY: TextOverlay,
  TIMELINE_MARKER: TimelineMarker,
  TEXT_CHAT: TextChatOverlay,
  EVIDENCE_BOARD: EvidenceBoardOverlay,
  MAP: AnimatedMapOverlay,
  SOCIAL_POST: SocialPostOverlay,
  PIP: PictureInPictureOverlay,
  AUDIO_VIS: AudioVisualizationOverlay,
  WAVEFORM: AudioVisualizationOverlay,
};

// Renders the visual layer for a single segment (video/image/placeholder + color grade + Ken Burns)
function SegmentVisual({ seg, knownFiles }: { seg: BeeSegment; knownFiles: Set<string> }) {
  const src = seg.visual[0]?.src;
  const ext = src?.split('.').pop()?.toLowerCase() ?? '';
  const isImage = IMAGE_EXTS.has(ext);
  const contentType = seg.visual[0]?.type || 'NONE';
  const colorPreset = seg.visual[0]?.color;
  const colorFilter = colorPreset ? COLOR_FILTERS[colorPreset] : undefined;
  const kenBurns = seg.visual[0]?.kenBurns;
  const mediaStyle = { width: '100%' as const, height: '100%' as const, objectFit: 'cover' as const };

  // TEXT_CHAT visual: render as full-screen chat conversation
  if (contentType === 'TEXT_CHAT') {
    const visual = seg.visual[0];
    return <TextChat content={visual?.content || '[]'} metadata={visual} durationInFrames={Math.round(seg.duration * 30)} mode="visual" />;
  }

  // WAVEFORM visual: render as audio visualization (911 calls, etc.)
  if (contentType === 'WAVEFORM' || contentType === 'WAVEFORM-AERIAL' || contentType === 'WAVEFORM-DARK') {
    const visual = seg.visual[0];
    return <AudioVisualization content={visual?.content || '{}'} metadata={visual} durationInFrames={Math.round(seg.duration * 30)} mode="visual" />;
  }

  // SOCIAL_POST visual: render as full-screen social media post
  if (contentType === 'SOCIAL_POST' || contentType === 'SOCIAL-POST') {
    const visual = seg.visual[0];
    return <SocialPost content={visual?.content || '{}'} metadata={visual} durationInFrames={Math.round(seg.duration * 30)} mode="visual" />;
  }

  // MAP visual: render as animated map
  const MAP_TYPES = new Set(['MAP', 'MAP-FLAT', 'MAP-3D', 'MAP-TACTICAL', 'MAP-PULSE', 'MAP-ROUTE']);
  if (MAP_TYPES.has(contentType)) {
    const visual = seg.visual[0];
    return <AnimatedMap content={visual?.content || ''} metadata={visual} durationInFrames={Math.round(seg.duration * 30)} mode="visual" />;
  }

  // EVIDENCE_BOARD visual: render as full-screen evidence board
  if (contentType === 'EVIDENCE_BOARD' || contentType === 'EVIDENCE-BOARD') {
    const visual = seg.visual[0];
    return <EvidenceBoard content={visual?.content || '{}'} metadata={visual} durationInFrames={Math.round(seg.duration * 30)} mode="visual" />;
  }

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
function SegmentOverlays({ seg, segDuration, fps }: { seg: BeeSegment; segDuration: number; fps: number }) {
  return (
    <>
      {/* LowerThird -- special case (different props interface) */}
      {seg.overlay.filter(o => o.type === 'LOWER_THIRD').map((lt, i) => {
        const { name, role } = parseLowerThirdContent(lt.content);
        const defaultDur = Math.min(DEFAULT_DURATIONS.LOWER_THIRD * fps, segDuration);
        const offset = lt.startOffset ? Math.round(lt.startOffset * fps) : 0;
        const clampedDur = Math.min(defaultDur, segDuration - offset);
        return (
          <Sequence key={`lt-${i}`} from={offset} durationInFrames={clampedDur}>
            <LowerThird name={name} role={role} durationInFrames={clampedDur} />
          </Sequence>
        );
      })}

      {/* Registry-based overlays */}
      {seg.overlay.filter(o => o.type !== 'LOWER_THIRD').map((entry, i) => {
        const Component = OVERLAY_COMPONENTS[entry.type];
        if (!Component) return null;
        const defaultDur = (DEFAULT_DURATIONS[entry.type] || 3) * fps;
        const dur = Math.min(defaultDur, segDuration);
        const offset = entry.startOffset ? Math.round(entry.startOffset * fps) : 0;
        const clampedDur = Math.min(dur, segDuration - offset);
        return (
          <Sequence key={`ov-${i}`} from={offset} durationInFrames={clampedDur}>
            <Component content={entry.content} metadata={entry} durationInFrames={clampedDur} />
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

        const narEntry = seg.audio.find(a => a.type === 'NAR');
        const narrationText = narEntry?.text || '';

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
