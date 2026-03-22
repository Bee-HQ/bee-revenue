import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from './QualityContext';

type Direction = 'left' | 'right' | 'up' | 'down' | 'scale' | 'none';

interface Props {
  direction?: Direction;
  delay?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}

const OFFSETS: Record<Direction, { x: number; y: number; scale: number }> = {
  left:  { x: -100, y: 0, scale: 1 },
  right: { x: 100,  y: 0, scale: 1 },
  up:    { x: 0, y: -80,  scale: 1 },
  down:  { x: 0, y: 80,   scale: 1 },
  scale: { x: 0, y: 0,    scale: 0 },
  none:  { x: 0, y: 0,    scale: 1 },
};

export const SpringReveal: React.FC<Props> = ({
  direction = 'up',
  delay = 0,
  style,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig } = useQuality();

  const progress = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: springConfig,
  });

  const offset = OFFSETS[direction];
  const x = offset.x * (1 - progress);
  const y = offset.y * (1 - progress);
  const scale = direction === 'scale' ? progress : 1;

  return (
    <AbsoluteFill
      style={{
        transform: `translate(${x}px, ${y}px) scale(${scale})`,
        opacity: progress,
        ...style,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
