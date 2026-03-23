import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from '../overlays';

interface BoardPerson {
  name: string;
  photo_path?: string;
}

interface BoardConnection {
  from: string;
  to: string;
  label: string;
}

interface BoardData {
  people: BoardPerson[];
  connections: BoardConnection[];
}

export function parseBoardData(content: string): BoardData {
  try {
    const parsed = JSON.parse(content);
    if (parsed.people && Array.isArray(parsed.people)) {
      return {
        people: parsed.people,
        connections: Array.isArray(parsed.connections) ? parsed.connections : [],
      };
    }
  } catch {}
  // Fallback: treat content as comma-separated names, no connections
  const names = content.split(',').map(s => s.trim()).filter(Boolean);
  return { people: names.map(name => ({ name })), connections: [] };
}

// Arrange people in a circle
function circleLayout(count: number, cx: number, cy: number, radius: number): { x: number; y: number }[] {
  const positions: { x: number; y: number }[] = [];
  for (let i = 0; i < count; i++) {
    const angle = (i / count) * Math.PI * 2 - Math.PI / 2;
    positions.push({
      x: cx + Math.cos(angle) * radius,
      y: cy + Math.sin(angle) * radius,
    });
  }
  return positions;
}

// Person card component
function PersonCard({
  person, x, y, opacity, scale, index,
}: {
  person: BoardPerson; x: number; y: number; opacity: number; scale: number; index: number;
}) {
  const cardW = 120;
  const cardH = 140;

  return (
    <div style={{
      position: 'absolute',
      left: x - cardW / 2,
      top: y - cardH / 2,
      width: cardW,
      height: cardH,
      opacity,
      transform: `scale(${scale})`,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 4,
    }}>
      {/* Pin */}
      <div style={{
        width: 12, height: 12, borderRadius: '50%',
        background: 'radial-gradient(circle at 4px 4px, #e74c3c, #c0392b)',
        boxShadow: '0 2px 4px rgba(0,0,0,0.5)',
        position: 'absolute', top: -6, zIndex: 2,
      }} />
      {/* Card */}
      <div style={{
        background: '#f5f0e8',
        border: '1px solid #d4c9b8',
        borderRadius: 4,
        padding: '8px 6px',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 6,
        boxShadow: '2px 3px 8px rgba(0,0,0,0.4)',
        transform: `rotate(${((index * 17) % 7) - 3}deg)`,
      }}>
        {/* Photo placeholder */}
        <div style={{
          width: 80, height: 80, borderRadius: 4,
          background: '#888',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 28, color: '#ccc',
          border: '2px solid #aaa',
        }}>
          👤
        </div>
        {/* Name */}
        <div style={{
          color: '#1a1a1a',
          fontSize: 11,
          fontWeight: 700,
          fontFamily: 'Arial',
          textAlign: 'center',
          lineHeight: 1.2,
          maxWidth: '100%',
          overflow: 'hidden',
        }}>
          {person.name}
        </div>
      </div>
    </div>
  );
}

// Red string connection (SVG line)
function RedString({
  x1, y1, x2, y2, label, drawProgress, labelOpacity,
}: {
  x1: number; y1: number; x2: number; y2: number;
  label: string; drawProgress: number; labelOpacity: number;
}) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.sqrt(dx * dx + dy * dy);
  const drawnLength = length * drawProgress;

  // End point based on progress
  const ex = x1 + (dx / length) * drawnLength;
  const ey = y1 + (dy / length) * drawnLength;

  // Midpoint for label
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;

  return (
    <>
      <line
        x1={x1} y1={y1} x2={ex} y2={ey}
        stroke="#DC3232"
        strokeWidth={2}
        strokeDasharray="6,4"
        opacity={0.8}
      />
      {/* Small circles at endpoints */}
      <circle cx={x1} cy={y1} r={3} fill="#DC3232" opacity={drawProgress > 0 ? 0.8 : 0} />
      {drawProgress >= 1 && <circle cx={x2} cy={y2} r={3} fill="#DC3232" opacity={0.8} />}
      {/* Label */}
      {labelOpacity > 0 && (
        <g transform={`translate(${mx}, ${my})`}>
          <rect x={-label.length * 3.5 - 6} y={-10} width={label.length * 7 + 12} height={20} rx={3}
            fill="rgba(0,0,0,0.7)" />
          <text
            textAnchor="middle" dominantBaseline="central"
            fill="#fff" fontSize={11} fontFamily="Arial" fontWeight={600}
            opacity={labelOpacity}
          >
            {label}
          </text>
        </g>
      )}
    </>
  );
}

export const EvidenceBoard: React.FC<EvidenceBoardProps> = ({
  content, durationInFrames, mode = 'overlay',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const data = parseBoardData(content);
  const { people, connections } = data;

  if (people.length === 0) return null;

  // Layout
  const w = mode === 'visual' ? 1920 : 1200;
  const h = mode === 'visual' ? 1080 : 700;
  const cx = w / 2;
  const cy = h / 2;
  const radius = Math.min(w, h) * 0.3;
  const positions = circleLayout(people.length, cx, cy, radius);

  // Animation timing
  const bgFadeFrames = 15;
  const framesPerPerson = Math.floor((durationInFrames * 0.4) / Math.max(1, people.length));
  const connectionStartFrame = people.length * framesPerPerson + 10;
  const framesPerConnection = connections.length > 0
    ? Math.floor((durationInFrames * 0.35) / connections.length)
    : 0;

  // Exit
  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Background fade
  const bgOpacity = interpolate(frame, [0, bgFadeFrames], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Build connection position lookup
  const nameToPos = new Map(people.map((p, i) => [p.name, positions[i]]));

  return (
    <AbsoluteFill style={{
      justifyContent: 'center', alignItems: 'center',
      opacity: exitOpacity,
    }}>
      <div style={{
        width: mode === 'visual' ? '100%' : '65%',
        height: mode === 'visual' ? '100%' : undefined,
        aspectRatio: mode === 'overlay' ? '16/9' : undefined,
        position: 'relative',
        opacity: bgOpacity,
        borderRadius: mode === 'overlay' ? 12 : 0,
        overflow: 'hidden',
      }}>
        {/* Corkboard background */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(135deg, #3d2b1f 0%, #2a1f14 50%, #1f1610 100%)',
        }} />

        {/* Subtle texture overlay */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px)',
          backgroundSize: '20px 20px',
        }} />

        {/* SVG layer for red strings */}
        <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
          viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="xMidYMid meet"
        >
          {connections.map((conn, i) => {
            const fromPos = nameToPos.get(conn.from);
            const toPos = nameToPos.get(conn.to);
            if (!fromPos || !toPos) return null;

            const connFrame = connectionStartFrame + i * framesPerConnection;
            const drawProgress = interpolate(frame, [connFrame, connFrame + framesPerConnection * 0.7], [0, 1], {
              extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
            });
            const labelOpacity = interpolate(frame, [connFrame + framesPerConnection * 0.6, connFrame + framesPerConnection], [0, 1], {
              extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
            });

            return (
              <RedString
                key={`conn-${i}`}
                x1={fromPos.x} y1={fromPos.y}
                x2={toPos.x} y2={toPos.y}
                label={conn.label}
                drawProgress={drawProgress}
                labelOpacity={labelOpacity}
              />
            );
          })}
        </svg>

        {/* Person cards */}
        <div style={{ position: 'absolute', inset: 0 }}>
          <div style={{ position: 'relative', width: w, height: h, margin: '0 auto' }}>
            {people.map((person, i) => {
              const personFrame = i * framesPerPerson;
              const appear = spring({
                frame: frame - personFrame,
                fps,
                config: { stiffness: 200, damping: 18 },
              });
              const scale = interpolate(appear, [0, 1], [0.3, 1]);

              return (
                <PersonCard
                  key={person.name}
                  person={person}
                  index={i}
                  x={positions[i].x}
                  y={positions[i].y}
                  opacity={appear}
                  scale={scale}
                />
              );
            })}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export interface EvidenceBoardProps {
  content: string;
  metadata?: Record<string, any> | null;
  durationInFrames: number;
  mode?: 'visual' | 'overlay';
}

// Overlay wrapper
export const EvidenceBoardOverlay: React.FC<OverlayProps> = (props) => (
  <EvidenceBoard {...props} mode="overlay" />
);
