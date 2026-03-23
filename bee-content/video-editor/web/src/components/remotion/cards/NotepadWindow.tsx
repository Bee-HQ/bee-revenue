import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../primitives/QualityContext';
import type { OverlayProps } from '../overlays';

export interface NotepadData {
  lines: string[];
  animation: 'typewriter' | 'lines' | 'instant';
  windowTitle: string;
  background: string;
}

export function parseNotepadData(
  content: string,
  metadata?: Record<string, any> | null,
): NotepadData {
  return {
    lines: content.split('\n'),
    animation: (metadata?.animation as NotepadData['animation']) || 'typewriter',
    windowTitle: (metadata?.windowTitle as string) || 'Notepad',
    background: (metadata?.background as string) || '#000',
  };
}

function NotepadChrome({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{
      background: '#1e1e1e', borderRadius: 10, overflow: 'hidden',
      boxShadow: '0 20px 60px rgba(0,0,0,0.6)', width: '100%', maxWidth: 600,
    }}>
      {/* Title bar */}
      <div style={{
        height: 32, background: '#2d2d2d', display: 'flex',
        alignItems: 'center', padding: '0 12px', gap: 8,
      }}>
        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ff5f57' }} />
        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#febc2e' }} />
        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#28c840' }} />
        <span style={{
          flex: 1, textAlign: 'center', color: '#999', fontSize: 12,
          fontFamily: 'system-ui, Arial, sans-serif',
        }}>{title}</span>
      </div>
      {/* Menu bar */}
      <div style={{
        height: 24, background: '#252525', display: 'flex',
        alignItems: 'center', padding: '0 12px', gap: 16,
      }}>
        {['File', 'Edit', 'Search', 'View', 'Help'].map(m => (
          <span key={m} style={{ color: '#aaa', fontSize: 11, fontFamily: 'system-ui, Arial, sans-serif' }}>{m}</span>
        ))}
      </div>
      {/* Text body */}
      {children}
    </div>
  );
}

function NotepadWindowVisual({
  data, durationInFrames, background,
}: { data: NotepadData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  // Entrance spring
  const enterProgress = spring({ frame, fps, config: springConfig });
  const enterScale = interpolate(enterProgress, [0, 1], [0.9, 1]);
  const enterOpacity = interpolate(enterProgress, [0, 1], [0, 1]);

  // Blinking cursor (toggles every 15 frames)
  const cursorVisible = Math.floor(frame / 15) % 2 === 0;

  const fullText = data.lines.join('\n');
  const totalChars = fullText.length;

  // Determine visible text based on animation mode
  let visibleLines: { text: string; opacity: number }[];

  if (data.animation === 'instant') {
    visibleLines = data.lines.map(line => ({ text: line, opacity: 1 }));
  } else if (data.animation === 'lines') {
    const staggerInterval = Math.round(12 * timingMultiplier);
    visibleLines = data.lines.map((line, i) => {
      const delay = i * staggerInterval;
      const progress = spring({
        frame: Math.max(0, frame - delay), fps, config: springConfig,
      });
      return { text: line, opacity: interpolate(progress, [0, 1], [0, 1]) };
    });
  } else {
    // typewriter: show chars progressively
    const charsToShow = Math.min(Math.floor((frame / (durationInFrames - 15)) * totalChars), totalChars);
    let charsRemaining = charsToShow;
    visibleLines = data.lines.map(line => {
      if (charsRemaining <= 0) return { text: '', opacity: 1 };
      const visible = line.slice(0, charsRemaining);
      charsRemaining -= line.length + 1; // +1 for newline
      return { text: visible, opacity: 1 };
    });
  }

  // Find cursor position (end of last visible non-empty line)
  const lastVisibleIdx = visibleLines.findLastIndex(l => l.text.length > 0);

  const bgStyle = background?.startsWith('animated-') ? undefined : { backgroundColor: background };

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', ...bgStyle }}>
      {background?.startsWith('animated-') && (
        <AbsoluteFill>
          {/* AnimatedBG will be integrated in Task 8 */}
          <div style={{ position: 'absolute', inset: 0, backgroundColor: '#0a1628' }} />
        </AbsoluteFill>
      )}
      <div style={{
        opacity: exitOpacity * enterOpacity,
        transform: `scale(${enterScale})`,
        width: '100%', maxWidth: 600,
      }}>
        <NotepadChrome title={data.windowTitle}>
          <div style={{
            padding: '20px 24px', minHeight: 160,
            fontFamily: "'Courier New', monospace", fontSize: 15,
            color: '#e5e5e5', lineHeight: 1.8,
          }}>
            {visibleLines.map((vl, i) => (
              <div key={i} style={{ opacity: vl.opacity, minHeight: '1.8em' }}>
                {vl.text}
                {i === lastVisibleIdx && cursorVisible && data.animation === 'typewriter' && (
                  <span style={{ borderRight: '2px solid #e5e5e5', marginLeft: 1 }}>{'\u200B'}</span>
                )}
              </div>
            ))}
          </div>
        </NotepadChrome>
      </div>
    </AbsoluteFill>
  );
}

export const NotepadWindowOverlay: React.FC<OverlayProps> = (props) => {
  const data = parseNotepadData(props.content, props.metadata);
  return <NotepadWindowVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const NotepadWindow: React.FC<OverlayProps> = (props) => {
  const data = parseNotepadData(props.content, props.metadata);
  return <NotepadWindowVisual data={data} durationInFrames={props.durationInFrames} background={data.background} />;
};
