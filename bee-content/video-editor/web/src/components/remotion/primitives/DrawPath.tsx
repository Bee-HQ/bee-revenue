import { useId } from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { getLength } from '@remotion/paths';
import { useQuality } from './QualityContext';

interface Props {
  d: string;
  fromFrame?: number;
  toFrame?: number;
  strokeWidth?: number;
  color?: string;
  style?: React.CSSProperties;
}

export const DrawPath: React.FC<Props> = ({
  d,
  fromFrame = 0,
  toFrame,
  strokeWidth = 3,
  color = '#dc2626',
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { tier } = useQuality();
  const filterId = useId();

  const pathLength = getLength(d);
  const endFrame = toFrame ?? Math.round(fps * 0.8);

  const progress = interpolate(
    frame,
    [fromFrame, endFrame],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  const dashOffset = pathLength * (1 - progress);

  return (
    <svg
      viewBox="0 0 1920 1080"
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        ...style,
      }}
    >
      {tier === 'premium' && (
        <path
          d={d}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth * 3}
          strokeDasharray={pathLength}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          opacity={0.2}
          filter={`url(#glow-${filterId})`}
        />
      )}
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeDasharray={pathLength}
        strokeDashoffset={dashOffset}
        strokeLinecap="round"
      />
      {tier === 'premium' && (
        <defs>
          <filter id={`glow-${filterId}`}>
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      )}
    </svg>
  );
};
