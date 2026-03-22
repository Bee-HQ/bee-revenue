// web/src/components/remotion/TextOverlay.tsx
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import type { OverlayProps } from './overlays';

export const TextOverlay: React.FC<OverlayProps> = ({ content, durationInFrames }) => {
  const frame = useCurrentFrame();

  // Typewriter: reveal characters over first 60% of duration
  const typingEnd = Math.floor(durationInFrames * 0.6);
  const charsToShow = Math.floor(interpolate(frame, [0, typingEnd], [0, content.length], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }));
  const visibleText = content.slice(0, charsToShow);

  // Blinking cursor
  const cursorVisible = frame < typingEnd ? Math.floor(frame / 8) % 2 === 0 : false;

  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', opacity: exitOpacity }}>
      <div style={{ background: 'rgba(0,0,0,0.7)', padding: '20px 40px', borderRadius: 8, maxWidth: '70%' }}>
        <span style={{ color: '#fff', fontSize: 36, fontWeight: 600, fontFamily: 'Arial', lineHeight: 1.4 }}>
          {visibleText}
        </span>
        {cursorVisible && <span style={{ color: '#3b82f6', fontSize: 36, fontWeight: 300 }}>|</span>}
      </div>
    </AbsoluteFill>
  );
};
