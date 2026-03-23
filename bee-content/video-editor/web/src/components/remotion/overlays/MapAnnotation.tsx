import { resolveColor } from '../overlays';

export type AnnotationShape =
  | { type: 'circle'; x: number; y: number; r: number }
  | { type: 'path'; points: [number, number][] }
  | { type: 'rect'; x: number; y: number; w: number; h: number };

export interface MapAnnotationData {
  shapes: AnnotationShape[];
  color: string;
}

function isValidShape(s: any): s is AnnotationShape {
  if (!s || typeof s.type !== 'string') return false;
  if (s.type === 'circle') return typeof s.x === 'number' && typeof s.y === 'number' && typeof s.r === 'number';
  if (s.type === 'path') return Array.isArray(s.points) && s.points.length >= 1;
  if (s.type === 'rect') return typeof s.x === 'number' && typeof s.y === 'number' && typeof s.w === 'number' && typeof s.h === 'number';
  return false;
}

export function parseMapAnnotationData(
  content: string,
  metadata?: Record<string, any> | null,
): MapAnnotationData {
  let shapes: AnnotationShape[] = [];
  try {
    const parsed = JSON.parse(content);
    if (Array.isArray(parsed)) {
      shapes = parsed.filter(isValidShape);
    }
  } catch {}

  return {
    shapes,
    color: resolveColor(metadata?.color || 'red'),
  };
}

import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../primitives/QualityContext';
import { DrawPath } from '../primitives/DrawPath';
import type { OverlayProps } from '../overlays';

function pathSvgD(points: [number, number][]): string {
  if (points.length === 0) return '';
  const mapped = points.map(([x, y]) => [Math.round(x * 1920), Math.round(y * 1080)]);
  const [first, ...rest] = mapped;
  if (rest.length === 0) return `M ${first[0]} ${first[1]}`;
  let d = `M ${first[0]} ${first[1]}`;
  for (const [x, y] of rest) {
    d += ` L ${x} ${y}`;
  }
  return d;
}

export const MapAnnotation: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();
  const { shapes, color } = parseMapAnnotationData(content, metadata);
  const staggerInterval = Math.round(10 * timingMultiplier);

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  if (shapes.length === 0) return null;

  return (
    <AbsoluteFill style={{ opacity: exitOpacity }}>
      <svg viewBox="0 0 1920 1080" style={{
        position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none',
      }}>
        {shapes.map((shape, i) => {
          const delay = i * staggerInterval;
          const progress = spring({
            frame: Math.max(0, frame - delay), fps, config: springConfig,
          });

          if (shape.type === 'circle') {
            const cx = Math.round(shape.x * 1920);
            const cy = Math.round(shape.y * 1080);
            const r = Math.round(shape.r * Math.min(1920, 1080));
            const scale = interpolate(progress, [0, 1], [0, 1]);
            const pulseScale = interpolate(frame % 30, [0, 15, 30], [1, 1.5, 1], {
              extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
            });

            return (
              <g key={i} transform={`translate(${cx}, ${cy}) scale(${scale}) translate(${-cx}, ${-cy})`}>
                {/* Glow ring */}
                <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={20} opacity={0.3} />
                {/* Main ring */}
                <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={3} />
                {/* Pulsing center dot */}
                <circle cx={cx} cy={cy} r={6} fill={color}
                  transform={`translate(${cx}, ${cy}) scale(${pulseScale}) translate(${-cx}, ${-cy})`} />
              </g>
            );
          }

          if (shape.type === 'rect') {
            const x = Math.round(shape.x * 1920);
            const y = Math.round(shape.y * 1080);
            const w = Math.round(shape.w * 1920);
            const h = Math.round(shape.h * 1080);
            const rectOpacity = interpolate(progress, [0, 1], [0, 1]);

            return (
              <rect key={i} x={x} y={y} width={w} height={h}
                stroke={color} strokeWidth={2} fill={color} fillOpacity={0.1}
                opacity={rectOpacity} />
            );
          }

          return null; // paths handled below
        })}
      </svg>

      {/* DrawPath for path shapes (rendered outside SVG since DrawPath has its own SVG) */}
      {shapes.map((shape, i) => {
        if (shape.type !== 'path') return null;
        const delay = i * staggerInterval;
        const d = pathSvgD(shape.points);
        if (!d) return null;

        return (
          <DrawPath
            key={`path-${i}`}
            d={d}
            fromFrame={delay}
            toFrame={delay + 30}
            strokeWidth={4}
            color={color}
          />
        );
      })}
    </AbsoluteFill>
  );
};
