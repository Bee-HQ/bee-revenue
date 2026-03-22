import { useCurrentFrame, interpolate } from 'remotion';

interface Props {
  value: number;
  fromFrame?: number;
  toFrame?: number;
  format?: 'number' | 'currency' | 'percent';
  style?: React.CSSProperties;
}

export const CountUp: React.FC<Props> = ({
  value,
  fromFrame = 0,
  toFrame = 60,
  format = 'number',
  style,
}) => {
  const frame = useCurrentFrame();

  const progress = interpolate(
    frame,
    [fromFrame, toFrame],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  const current = Math.round(value * progress);

  let display: string;
  switch (format) {
    case 'currency':
      display = '$' + current.toLocaleString();
      break;
    case 'percent':
      display = current + '%';
      break;
    default:
      display = current.toLocaleString();
  }

  return <span style={style}>{display}</span>;
};
