import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import type { OverlayProps } from '../overlays';
import { CornerBrackets } from '../primitives';

export const TextOverlay: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const frame = useCurrentFrame();
  const displayText = content || metadata?.text || '';
  const brackets = metadata?.brackets === true;
  const position = (metadata?.position as string) || 'center';
  const animation = (metadata?.animation as string) || 'typewriter';

  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Position styles
  const positionMap: Record<string, React.CSSProperties> = {
    center: { justifyContent: 'center', alignItems: 'center' },
    'top-left': { justifyContent: 'flex-start', alignItems: 'flex-start', padding: '80px 60px' },
    'top-right': { justifyContent: 'flex-start', alignItems: 'flex-end', padding: '80px 60px' },
    'bottom-left': { justifyContent: 'flex-end', alignItems: 'flex-start', padding: '0 60px 80px' },
    'bottom-right': { justifyContent: 'flex-end', alignItems: 'flex-end', padding: '0 60px 80px' },
  };
  const posStyle = positionMap[position] || positionMap.center;

  // Typewriter animation
  let visibleText = displayText;
  let cursorVisible = false;
  if (animation === 'typewriter') {
    const typingEnd = Math.floor(durationInFrames * 0.6);
    const charsToShow = Math.floor(interpolate(frame, [0, typingEnd], [0, displayText.length], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }));
    visibleText = displayText.slice(0, charsToShow);
    cursorVisible = frame < typingEnd ? Math.floor(frame / 8) % 2 === 0 : false;
  }

  const textContent = (
    <>
      <span style={{
        color: '#fff', fontSize: brackets ? 28 : 36, fontWeight: brackets ? 800 : 600,
        fontFamily: brackets ? "'Arial Black', Arial, sans-serif" : 'Arial',
        lineHeight: 1.4, letterSpacing: brackets ? 2 : 0,
        textTransform: brackets ? 'uppercase' : undefined,
      }}>
        {visibleText}
      </span>
      {cursorVisible && <span style={{ color: '#3b82f6', fontSize: 36, fontWeight: 300 }}>|</span>}
    </>
  );

  return (
    <AbsoluteFill style={{ ...posStyle, opacity: exitOpacity }}>
      <div style={{ background: 'rgba(0,0,0,0.7)', padding: brackets ? '14px 24px' : '20px 40px', borderRadius: brackets ? 0 : 8, maxWidth: '70%' }}>
        {brackets ? <CornerBrackets>{textContent}</CornerBrackets> : textContent}
      </div>
    </AbsoluteFill>
  );
};
