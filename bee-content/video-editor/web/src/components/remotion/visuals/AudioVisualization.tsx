import { AbsoluteFill, Video, Img, interpolate, useCurrentFrame } from 'remotion';
import type { OverlayProps } from '../overlays';

interface AudioVisData {
  style?: 'bars' | 'waveform' | 'pulse';
  background?: {
    type: 'image' | 'video' | 'color' | 'map';
    src?: string;
    color?: string;
  };
  label?: string;         // e.g., "911 Emergency Call"
  sublabel?: string;      // e.g., "June 7, 2021 — 10:07 PM"
  color?: string;         // visualization color (default: red)
  barCount?: number;      // number of bars (default: 32)
}

export function parseAudioVisData(content: string): AudioVisData {
  try {
    const parsed = JSON.parse(content);
    if (typeof parsed === 'object' && parsed !== null) return parsed;
  } catch {}
  return { label: content, style: 'bars' };
}

function mediaUrl(path: string): string {
  return `/api/media/file?path=${encodeURIComponent(path)}`;
}

// Generate pseudo-random bar heights that vary per frame (simulates audio reactivity)
function generateBars(frame: number, count: number, seed: number): number[] {
  const bars: number[] = [];
  for (let i = 0; i < count; i++) {
    // Multi-frequency noise for organic movement
    const f1 = Math.sin((frame * 0.08 + i * 0.7 + seed) * 1.3) * 0.3;
    const f2 = Math.sin((frame * 0.15 + i * 1.1 + seed * 2) * 0.9) * 0.25;
    const f3 = Math.sin((frame * 0.22 + i * 0.5 + seed * 3) * 1.7) * 0.15;
    // Center bars are generally taller (speech pattern)
    const center = 1 - Math.abs(i - count / 2) / (count / 2) * 0.4;
    const height = Math.max(0.05, (0.3 + f1 + f2 + f3) * center);
    bars.push(height);
  }
  return bars;
}

// Background renderer
function Background({ bg }: { bg?: AudioVisData['background'] }) {
  if (!bg) return <div style={{ position: 'absolute', inset: 0, backgroundColor: '#0a0a0f' }} />;

  if (bg.type === 'video' && bg.src) {
    return (
      <AbsoluteFill>
        <Video src={mediaUrl(bg.src)} style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'brightness(0.3) blur(2px)' }} />
      </AbsoluteFill>
    );
  }
  if (bg.type === 'image' && bg.src) {
    return (
      <AbsoluteFill>
        <Img src={mediaUrl(bg.src)} style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'brightness(0.3) blur(2px)' }} />
      </AbsoluteFill>
    );
  }
  if (bg.type === 'color') {
    return <div style={{ position: 'absolute', inset: 0, backgroundColor: bg.color || '#0a0a0f' }} />;
  }
  // map placeholder
  return (
    <div style={{ position: 'absolute', inset: 0, backgroundColor: '#0a1a0a' }}>
      <div style={{ position: 'absolute', inset: 0, opacity: 0.15, backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
    </div>
  );
}

export const AudioVisualization: React.FC<AudioVisProps> = ({
  content, metadata: _metadata, durationInFrames, mode: _mode = 'visual',
}) => {
  const frame = useCurrentFrame();
  void _metadata; void _mode; // used by overlay wrapper
  const data = parseAudioVisData(content);
  const visStyle = data.style || 'bars';
  const visColor = data.color || '#DC3232';
  const barCount = data.barCount || 32;
  const label = data.label || '';
  const sublabel = data.sublabel || '';

  // Seed from label for deterministic but unique patterns
  let seed = 0;
  for (let i = 0; i < label.length; i++) seed = ((seed << 5) - seed + label.charCodeAt(i)) | 0;

  const bars = generateBars(frame, barCount, seed);

  // Entry animation
  const entryOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Label animation
  const labelOpacity = interpolate(frame, [10, 25], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Pulse animation for the "pulse" style
  const pulseScale = visStyle === 'pulse' ? 1 + Math.sin(frame * 0.12) * 0.15 : 1;

  return (
    <AbsoluteFill style={{ opacity: entryOpacity * exitOpacity }}>
      {/* Background */}
      <Background bg={data.background} />

      {/* Dark overlay for contrast */}
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.4)' }} />

      {/* Visualization */}
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
        {/* Phone icon / call indicator */}
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24,
          transform: `scale(${pulseScale})`,
        }}>
          {/* Call icon */}
          <div style={{
            width: 80, height: 80, borderRadius: '50%',
            background: `radial-gradient(circle, ${visColor}40, ${visColor}10)`,
            border: `2px solid ${visColor}80`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 36,
          }}>
            📞
          </div>

          {/* Label */}
          {label && (
            <div style={{ opacity: labelOpacity, textAlign: 'center' }}>
              <div style={{ color: '#fff', fontSize: 28, fontWeight: 700, fontFamily: 'Arial', letterSpacing: 1 }}>
                {label}
              </div>
              {sublabel && (
                <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: 16, fontFamily: 'Arial', marginTop: 4 }}>
                  {sublabel}
                </div>
              )}
            </div>
          )}

          {/* Audio bars */}
          {(visStyle === 'bars' || visStyle === 'waveform') && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: visStyle === 'waveform' ? 1 : 3,
              height: 80, marginTop: 12,
            }}>
              {bars.map((h, i) => {
                const barH = h * 80;
                return (
                  <div key={i} style={{
                    width: visStyle === 'waveform' ? 2 : Math.max(3, 200 / barCount),
                    height: barH,
                    backgroundColor: visColor,
                    borderRadius: visStyle === 'waveform' ? 1 : 2,
                    opacity: 0.8,
                    boxShadow: `0 0 ${barH / 4}px ${visColor}40`,
                  }} />
                );
              })}
            </div>
          )}

          {/* Pulse rings for "pulse" style */}
          {visStyle === 'pulse' && (
            <div style={{ position: 'relative', width: 200, height: 200, marginTop: -40 }}>
              {[0, 1, 2].map(ring => {
                const ringProgress = ((frame + ring * 20) % 60) / 60;
                const ringScale = 0.5 + ringProgress * 1.5;
                const ringOpacity = 1 - ringProgress;
                return (
                  <div key={ring} style={{
                    position: 'absolute', inset: 0,
                    borderRadius: '50%',
                    border: `2px solid ${visColor}`,
                    transform: `scale(${ringScale})`,
                    opacity: ringOpacity * 0.5,
                  }} />
                );
              })}
            </div>
          )}
        </div>
      </AbsoluteFill>

      {/* Recording indicator */}
      <div style={{
        position: 'absolute', top: 30, right: 30,
        display: 'flex', alignItems: 'center', gap: 8,
        opacity: Math.floor(frame / 15) % 2 === 0 ? 1 : 0.3,
      }}>
        <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#DC3232' }} />
        <span style={{ color: '#DC3232', fontSize: 14, fontFamily: 'monospace', fontWeight: 600 }}>
          REC
        </span>
      </div>
    </AbsoluteFill>
  );
};

export interface AudioVisProps {
  content: string;
  metadata?: Record<string, any> | null;
  durationInFrames: number;
  mode?: 'visual' | 'overlay';
}

// Overlay wrapper
export const AudioVisualizationOverlay: React.FC<OverlayProps> = (props) => (
  <AudioVisualization {...props} mode="overlay" />
);
