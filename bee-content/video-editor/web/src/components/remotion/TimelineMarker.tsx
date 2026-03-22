// web/src/components/remotion/TimelineMarker.tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from './overlays';

export const TimelineMarker: React.FC<OverlayProps> = ({ content, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideIn = spring({ frame, fps, config: { stiffness: 200, damping: 20 } });
  const translateX = interpolate(slideIn, [0, 1], [100, 0]);

  const textOpacity = interpolate(frame, [10, 20], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const slideOut = interpolate(frame, [durationInFrames - 15, durationInFrames], [0, 100], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ justifyContent: 'flex-start', alignItems: 'flex-end', padding: '40px 0' }}>
      <div style={{ transform: `translateX(${translateX + slideOut}%)`, background: 'rgba(220, 38, 38, 0.9)', padding: '8px 24px 8px 20px', borderRadius: '4px 0 0 4px' }}>
        <span style={{ opacity: textOpacity, color: '#fff', fontSize: 24, fontWeight: 700, fontFamily: 'Arial' }}>
          {content}
        </span>
      </div>
    </AbsoluteFill>
  );
};
