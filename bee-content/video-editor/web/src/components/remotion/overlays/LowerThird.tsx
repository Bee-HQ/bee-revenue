import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';

interface Props {
  name: string;
  role?: string;
  durationInFrames?: number;
}

export const LowerThird: React.FC<Props> = ({ name, role, durationInFrames = 120 }) => {
  const frame = useCurrentFrame();

  // Slide in from left over 15 frames, hold, fade out over last 15 frames
  const slideIn = interpolate(frame, [0, 15], [100, 0], { extrapolateRight: 'clamp' });
  const opacity = interpolate(
    frame,
    [0, 10, durationInFrames - 15, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', padding: '0 60px 80px' }}>
      <div style={{
        transform: `translateX(${slideIn}%)`,
        opacity,
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
      }}>
        {/* Background bar */}
        <div style={{
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          padding: '12px 24px',
          borderLeft: '4px solid #dc2626',
          maxWidth: 500,
        }}>
          <div style={{
            color: '#ffffff',
            fontSize: 32,
            fontWeight: 700,
            fontFamily: 'Arial, Helvetica, sans-serif',
            letterSpacing: 0.5,
          }}>
            {name}
          </div>
          {role && (
            <div style={{
              color: '#d1d5db',
              fontSize: 20,
              fontFamily: 'Arial, Helvetica, sans-serif',
              marginTop: 2,
            }}>
              {role}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
