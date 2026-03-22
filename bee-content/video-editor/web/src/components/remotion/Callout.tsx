// web/src/components/remotion/Callout.tsx
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import { DrawPath } from './primitives/DrawPath';
import { SpringReveal } from './primitives/SpringReveal';
import type { OverlayProps } from './overlays';

// ---------------------------------------------------------------------------
// SVG path generators (pure functions, exported for testing)
// ---------------------------------------------------------------------------

/** Full circle at (cx, cy) with radius r, using two arcs */
export function circlePath(cx: number, cy: number, r: number): string {
  return `M ${cx - r} ${cy} A ${r} ${r} 0 1 1 ${cx + r} ${cy} A ${r} ${r} 0 1 1 ${cx - r} ${cy}`;
}

/** Arrow from an offset origin to (tx, ty) with quadratic bezier curve */
export function arrowPath(ox: number, oy: number, tx: number, ty: number): string {
  // Control point: midpoint shifted perpendicular for a slight curve
  const mx = (ox + tx) / 2;
  const my = (oy + ty) / 2;
  const dx = tx - ox;
  const dy = ty - oy;
  const perpX = -dy * 0.15;
  const perpY = dx * 0.15;
  return `M ${ox} ${oy} Q ${mx + perpX} ${my + perpY} ${tx} ${ty}`;
}

/** Rounded rectangle centered on (cx, cy) with half-widths hw/hh and corner radius r */
export function boxPath(cx: number, cy: number, hw: number, hh: number, r: number): string {
  const cr = Math.min(r, hw, hh);
  const x1 = cx - hw;
  const y1 = cy - hh;
  const x2 = cx + hw;
  const y2 = cy + hh;
  return [
    `M ${x1 + cr} ${y1}`,
    `L ${x2 - cr} ${y1}`,
    `Q ${x2} ${y1} ${x2} ${y1 + cr}`,
    `L ${x2} ${y2 - cr}`,
    `Q ${x2} ${y2} ${x2 - cr} ${y2}`,
    `L ${x1 + cr} ${y2}`,
    `Q ${x1} ${y2} ${x1} ${y2 - cr}`,
    `L ${x1} ${y1 + cr}`,
    `Q ${x1} ${y1} ${x1 + cr} ${y1}`,
    'Z',
  ].join(' ');
}

/** Horizontal underline starting at (x, y) with given width */
export function underlinePath(x: number, y: number, width: number): string {
  return `M ${x} ${y} L ${x + width} ${y}`;
}

/** Curly brace (vertical) at x, centered on cy with given height */
export function bracketPath(x: number, cy: number, height: number): string {
  const h = height / 2;
  const w = 20; // bracket width
  return [
    `M ${x + w} ${cy - h}`,
    `Q ${x} ${cy - h} ${x} ${cy - h / 2}`,
    `Q ${x} ${cy} ${x - w} ${cy}`,
    `Q ${x} ${cy} ${x} ${cy + h / 2}`,
    `Q ${x} ${cy + h} ${x + w} ${cy + h}`,
  ].join(' ');
}

// ---------------------------------------------------------------------------
// Data parser (pure function, exported for testing)
// ---------------------------------------------------------------------------

export interface CalloutData {
  targetX: number;
  targetY: number;
  style: 'circle' | 'arrow' | 'box' | 'underline' | 'bracket';
  animation: 'draw' | 'pop' | 'fade';
  label: string;
  color: string;
  targetSize: number;
  strokeWidth: number;
  labelPosition: 'auto' | 'top' | 'bottom' | 'left' | 'right';
}

const VALID_STYLES = new Set(['circle', 'arrow', 'box', 'underline', 'bracket']);
const VALID_ANIMATIONS = new Set(['draw', 'pop', 'fade']);

export function parseCalloutData(
  content: string,
  metadata?: Record<string, any> | null,
): CalloutData {
  const target = metadata?.target as [number, number] | undefined;
  const targetX = target ? Math.round(target[0] * 1920) : 960;
  const targetY = target ? Math.round(target[1] * 1080) : 540;

  const rawStyle = metadata?.style as string | undefined;
  const style = (rawStyle && VALID_STYLES.has(rawStyle) ? rawStyle : 'circle') as CalloutData['style'];

  const rawAnim = metadata?.animation as string | undefined;
  const animation = (rawAnim && VALID_ANIMATIONS.has(rawAnim) ? rawAnim : 'draw') as CalloutData['animation'];

  return {
    targetX,
    targetY,
    style,
    animation,
    label: content || '',
    color: (metadata?.color as string) || '#dc2626',
    targetSize: (metadata?.targetSize as number) || 100,
    strokeWidth: (metadata?.strokeWidth as number) || 4,
    labelPosition: (['auto', 'top', 'bottom', 'left', 'right'].includes(metadata?.labelPosition) ? metadata!.labelPosition : 'auto') as CalloutData['labelPosition'],
  };
}

// ---------------------------------------------------------------------------
// Internal: build SVG path string from callout data
// ---------------------------------------------------------------------------

function buildPath(data: CalloutData): string {
  const { targetX, targetY, targetSize, style } = data;
  switch (style) {
    case 'circle':
      return circlePath(targetX, targetY, targetSize);
    case 'arrow': {
      // Arrow from 200px offset (upper-left direction) toward target
      const ox = targetX - 200;
      const oy = targetY - 200;
      return arrowPath(ox, oy, targetX, targetY);
    }
    case 'box':
      return boxPath(targetX, targetY, targetSize, targetSize * 0.67, 8);
    case 'underline':
      return underlinePath(targetX - targetSize, targetY + 10, targetSize * 2);
    case 'bracket':
      return bracketPath(targetX - targetSize - 10, targetY, targetSize * 2);
    default:
      return circlePath(targetX, targetY, targetSize);
  }
}

// ---------------------------------------------------------------------------
// Label positioning
// ---------------------------------------------------------------------------

function computeLabelPosition(data: CalloutData): { top?: number; bottom?: number; left: number } {
  const { targetY, targetX, targetSize, labelPosition: pos, style } = data;

  // Arrow: label goes right at the arrow tip (the target point)
  if (style === 'arrow' && pos === 'auto') {
    return { top: targetY + 15, left: targetX };
  }

  switch (pos) {
    case 'top':
      return { top: targetY - targetSize - 60, left: targetX };
    case 'bottom':
      return { top: targetY + targetSize + 20, left: targetX };
    case 'left':
      return { top: targetY, left: targetX - targetSize - 120 };
    case 'right':
      return { top: targetY, left: targetX + targetSize + 20 };
    case 'auto':
    default:
      // Prefer below, flip above if near bottom edge
      if (targetY > 800) {
        return { top: targetY - targetSize - 60, left: targetX };
      }
      return { top: targetY + targetSize + 20, left: targetX };
  }
}

// ---------------------------------------------------------------------------
// Visual renderer (shared by both modes)
// ---------------------------------------------------------------------------

function CalloutVisual({
  data,
  durationInFrames,
  background,
}: {
  data: CalloutData;
  durationInFrames: number;
  background?: string;
}) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const d = buildPath(data);
  const drawEnd = Math.round(fps * 0.8);

  // Exit fade over last 15 frames
  const exitOpacity = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  // Label position
  const pos = computeLabelPosition(data);

  const labelEl = data.label ? (
    <div
      style={{
        position: 'absolute',
        top: pos.top,
        bottom: pos.bottom,
        left: pos.left,
        transform: 'translateX(-50%)',
        color: '#fff',
        fontSize: 28,
        fontWeight: 600,
        fontFamily: 'Arial, sans-serif',
        textShadow: '0 2px 8px rgba(0,0,0,0.8)',
        whiteSpace: 'nowrap',
      }}
    >
      {data.label}
    </div>
  ) : null;

  // Render based on animation mode
  if (data.animation === 'pop') {
    return (
      <AbsoluteFill style={{ opacity: exitOpacity, background }}>
        <SpringReveal direction="scale">
          <svg
            viewBox="0 0 1920 1080"
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}
          >
            <path
              d={d}
              fill="none"
              stroke={data.color}
              strokeWidth={data.strokeWidth}
              strokeLinecap="round"
            />
          </svg>
          {labelEl}
        </SpringReveal>
      </AbsoluteFill>
    );
  }

  if (data.animation === 'fade') {
    const fadeIn = interpolate(frame, [0, 15], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

    return (
      <AbsoluteFill style={{ opacity: fadeIn * exitOpacity, background }}>
        <svg
          viewBox="0 0 1920 1080"
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}
        >
          <path
            d={d}
            fill="none"
            stroke={data.color}
            strokeWidth={data.strokeWidth}
            strokeLinecap="round"
          />
        </svg>
        {labelEl}
      </AbsoluteFill>
    );
  }

  // Default: draw animation using DrawPath primitive
  return (
    <AbsoluteFill style={{ opacity: exitOpacity, background }}>
      <DrawPath
        d={d}
        toFrame={drawEnd}
        strokeWidth={data.strokeWidth}
        color={data.color}
      />
      {labelEl}
    </AbsoluteFill>
  );
}

// ---------------------------------------------------------------------------
// Exported components
// ---------------------------------------------------------------------------

/** CalloutOverlay: for use in OVERLAY_COMPONENTS registry (transparent bg) */
export const CalloutOverlay: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const data = parseCalloutData(content, metadata);
  return <CalloutVisual data={data} durationInFrames={durationInFrames} />;
};

/** Callout: visual mode with black background */
export const Callout: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const data = parseCalloutData(content, metadata);
  return <CalloutVisual data={data} durationInFrames={durationInFrames} background="#000" />;
};
