// web/src/components/remotion/FinancialCard.tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from './overlays';
import { parseDollarAmount } from './overlays';

export const FinancialCard: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { displayValue, numericValue, description } = parseDollarAmount(content, metadata);

  const slideUp = spring({ frame, fps, config: { stiffness: 180, damping: 18 } });
  const translateY = interpolate(slideUp, [0, 1], [100, 0]);

  // Count up animation
  const countProgress = interpolate(frame, [10, 60], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const currentValue = numericValue > 0 ? Math.round(numericValue * countProgress) : 0;
  const formattedValue = numericValue > 0 ? `$${currentValue.toLocaleString()}` : displayValue;

  const descOpacity = interpolate(frame, [40, 55], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const exitY = interpolate(frame, [durationInFrames - 15, durationInFrames], [0, 100], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', padding: '0 0 120px' }}>
      <div style={{ transform: `translateY(${translateY + exitY}%)`, background: 'rgba(220, 38, 38, 0.9)', padding: '24px 48px', borderRadius: 4, textAlign: 'center' }}>
        <div style={{ color: '#fff', fontSize: 56, fontWeight: 800, fontFamily: 'Arial', letterSpacing: -1 }}>
          {formattedValue}
        </div>
        {description && (
          <div style={{ opacity: descOpacity, color: 'rgba(255,255,255,0.8)', fontSize: 20, fontFamily: 'Arial', marginTop: 8 }}>
            {description}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
