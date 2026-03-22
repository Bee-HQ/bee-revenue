// web/src/components/remotion/QuoteCard.tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from './overlays';
import { parseQuoteContent } from './overlays';

const ACCENT_COLORS: Record<string, string> = {
  red: '#dc2626', teal: '#0d9488', gold: '#d97706',
};

export const QuoteCard: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { quote, author } = parseQuoteContent(content, metadata);
  const accentColor = ACCENT_COLORS[metadata?.color || 'red'] || ACCENT_COLORS.red;

  const backdropOpacity = interpolate(frame, [0, 10], [0, 0.8], { extrapolateRight: 'clamp' });
  const barX = spring({ frame: frame - 5, fps, config: { stiffness: 200, damping: 20 } });
  const quoteOpacity = interpolate(frame, [15, 30], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const authorOpacity = interpolate(frame, [25, 40], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ opacity: exitOpacity, maxWidth: 800, padding: '0 60px' }}>
        <div style={{ background: `rgba(0,0,0,${backdropOpacity})`, padding: '40px 48px', borderRadius: 4, position: 'relative' }}>
          <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 6, background: accentColor, transform: `scaleY(${barX})`, transformOrigin: 'top' }} />
          <div style={{ opacity: quoteOpacity, color: '#fff', fontSize: 36, fontWeight: 300, fontFamily: 'Georgia, serif', fontStyle: 'italic', lineHeight: 1.4 }}>
            {quote}
          </div>
          {author && (
            <div style={{ opacity: authorOpacity, color: '#d1d5db', fontSize: 20, fontFamily: 'Arial', marginTop: 16 }}>
              — {author}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
