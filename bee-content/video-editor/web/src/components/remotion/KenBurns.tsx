import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

interface Props {
  effect: string;
  children: React.ReactNode;
}

const EFFECTS: Record<string, { startScale: number; endScale: number; startX: number; endX: number; startY: number; endY: number }> = {
  zoom_in:           { startScale: 1,   endScale: 1.3, startX: 0,  endX: 0,  startY: 0,  endY: 0 },
  zoom_out:          { startScale: 1.3, endScale: 1,   startX: 0,  endX: 0,  startY: 0,  endY: 0 },
  pan_left:          { startScale: 1.1, endScale: 1.1, startX: 5,  endX: -5, startY: 0,  endY: 0 },
  pan_right:         { startScale: 1.1, endScale: 1.1, startX: -5, endX: 5,  startY: 0,  endY: 0 },
  pan_up:            { startScale: 1.1, endScale: 1.1, startX: 0,  endX: 0,  startY: 5,  endY: -5 },
  pan_down:          { startScale: 1.1, endScale: 1.1, startX: 0,  endX: 0,  startY: -5, endY: 5 },
  zoom_in_pan_right: { startScale: 1,   endScale: 1.3, startX: -3, endX: 3,  startY: 0,  endY: 0 },
};

export const KenBurns: React.FC<Props> = ({ effect, children }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const config = EFFECTS[effect] || EFFECTS.zoom_in;

  const scale = interpolate(frame, [0, durationInFrames], [config.startScale, config.endScale], { extrapolateRight: 'clamp' });
  const x = interpolate(frame, [0, durationInFrames], [config.startX, config.endX], { extrapolateRight: 'clamp' });
  const y = interpolate(frame, [0, durationInFrames], [config.startY, config.endY], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ overflow: 'hidden' }}>
      <div style={{
        width: '100%',
        height: '100%',
        transform: `scale(${scale}) translate(${x}%, ${y}%)`,
        transformOrigin: 'center center',
      }}>
        {children}
      </div>
    </AbsoluteFill>
  );
};
