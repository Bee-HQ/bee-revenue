// web/src/components/remotion/TransitionRenderer.tsx
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import type { ReactNode } from 'react';

interface OverlapProps {
  type: string;
  durationInFrames: number;
  mode: 'overlap';
  outgoing: ReactNode;
  incoming: ReactNode;
}

interface FadeProps {
  type: string;
  durationInFrames: number;
  mode: 'fade';
  position: 'in' | 'out';
  children: ReactNode;
}

type Props = OverlapProps | FadeProps;

export const TransitionRenderer: React.FC<Props> = (props) => {
  const frame = useCurrentFrame();
  const { type, durationInFrames, mode } = props;

  if (mode === 'overlap') {
    const { outgoing, incoming } = props as OverlapProps;

    if (type === 'FADE_FROM_BLACK') {
      const incomingOpacity = interpolate(frame, [0, durationInFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
      return (
        <AbsoluteFill>
          <AbsoluteFill style={{ backgroundColor: '#000' }} />
          <AbsoluteFill style={{ opacity: incomingOpacity }}>{incoming}</AbsoluteFill>
        </AbsoluteFill>
      );
    }

    // DISSOLVE (default)
    const outgoingOpacity = interpolate(frame, [0, durationInFrames], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    const incomingOpacity = interpolate(frame, [0, durationInFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

    return (
      <AbsoluteFill>
        <AbsoluteFill style={{ opacity: outgoingOpacity }}>{outgoing}</AbsoluteFill>
        <AbsoluteFill style={{ opacity: incomingOpacity }}>{incoming}</AbsoluteFill>
      </AbsoluteFill>
    );
  }

  // Fade mode
  const { position, children } = props as FadeProps;
  const fadeFrames = Math.min(15, durationInFrames);

  if (type === 'FADE_FROM_BLACK' && position === 'in') {
    const opacity = interpolate(frame, [0, fadeFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
  }

  if (position === 'out') {
    const segDuration = durationInFrames;
    const opacity = interpolate(frame, [segDuration - fadeFrames, segDuration], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
  }

  // Default: fade in
  const opacity = interpolate(frame, [0, fadeFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
};
