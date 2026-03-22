// web/src/components/remotion/KineticText.tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from './primitives/QualityContext';
import type { OverlayProps } from './overlays';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type Emphasis = 'none' | 'light' | 'heavy';

export interface ParsedWord {
  text: string;
  emphasis: Emphasis;
}

export interface KineticData {
  words: ParsedWord[];
  preset: string;
  color: string;
  accentColor: string;
  background: 'none' | 'dark' | 'blur';
  position: 'center' | 'top' | 'bottom' | 'lower-third';
  align: 'center' | 'left' | 'right';
}

// ---------------------------------------------------------------------------
// Pure parsers (exported for testing)
// ---------------------------------------------------------------------------

/**
 * Parse text with **heavy** and *light* emphasis markers into word objects.
 * Handles multi-word spans like *DNA evidence* and **Alex Murdaugh**.
 * Returns { text, emphasis } objects with markers stripped.
 */
export function parseWords(content: string): ParsedWord[] {
  if (content === '') return [{ text: '', emphasis: 'none' }];

  const result: ParsedWord[] = [];
  // Match **heavy spans**, *light spans*, or plain words
  const regex = /\*\*(.+?)\*\*|\*(.+?)\*|(\S+)/g;
  let match;

  while ((match = regex.exec(content)) !== null) {
    if (match[1] !== undefined) {
      // **heavy** — split into individual words, all heavy
      for (const word of match[1].split(/\s+/)) {
        if (word) result.push({ text: word, emphasis: 'heavy' });
      }
    } else if (match[2] !== undefined) {
      // *light* — split into individual words, all light
      for (const word of match[2].split(/\s+/)) {
        if (word) result.push({ text: word, emphasis: 'light' });
      }
    } else if (match[3] !== undefined) {
      result.push({ text: match[3], emphasis: 'none' });
    }
  }

  return result.length > 0 ? result : [{ text: '', emphasis: 'none' }];
}

/**
 * Read kinetic typography config from content + metadata.
 * Unknown presets are stored as-is (fallback at render time).
 */
export function parseKineticData(
  content: string,
  metadata?: Record<string, any> | null,
): KineticData {
  return {
    words: parseWords(content),
    preset: (metadata?.preset as string) || 'punch',
    color: (metadata?.color as string) || '#ffffff',
    accentColor: (metadata?.accentColor as string) || '#dc2626',
    background: (metadata?.background as KineticData['background']) || 'none',
    position: (metadata?.position as KineticData['position']) || 'center',
    align: (metadata?.align as KineticData['align']) || 'center',
  };
}

// ---------------------------------------------------------------------------
// Position helpers
// ---------------------------------------------------------------------------

function positionStyle(position: KineticData['position']): React.CSSProperties {
  switch (position) {
    case 'top':
      return { justifyContent: 'flex-start', paddingTop: 80 };
    case 'bottom':
      return { justifyContent: 'flex-end', paddingBottom: 80 };
    case 'lower-third':
      return { justifyContent: 'flex-end', paddingBottom: 160 };
    case 'center':
    default:
      return { justifyContent: 'center' };
  }
}

function backgroundStyle(bg: KineticData['background']): React.CSSProperties {
  switch (bg) {
    case 'dark':
      return { backgroundColor: 'rgba(0, 0, 0, 0.6)' };
    case 'blur':
      return { backdropFilter: 'blur(12px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' };
    case 'none':
    default:
      return {};
  }
}

// ---------------------------------------------------------------------------
// Preset: Punch — words slam in one at a time with spring scale + overshoot
// ---------------------------------------------------------------------------

const PunchPreset: React.FC<{
  words: ParsedWord[];
  color: string;
  accentColor: string;
  durationInFrames: number;
}> = ({ words, color, accentColor, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();

  const stagger = Math.round(6 * timingMultiplier);
  const visibleWords = words.filter((w) => w.text !== '');

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0 16px',
        justifyContent: 'center',
        alignItems: 'center',
        maxWidth: '80%',
      }}
    >
      {visibleWords.map((word, i) => {
        const delay = i * stagger;
        const progress = spring({
          frame: Math.max(0, frame - delay),
          fps,
          config: { ...springConfig, overshootClamping: false },
        });

        const wordColor = word.emphasis !== 'none' ? accentColor : color;
        // Use fontSize for emphasis instead of scale — scale doesn't affect layout
        const baseFontSize = 68;
        const emphasisSize =
          word.emphasis === 'heavy' ? baseFontSize * 1.3 :
          word.emphasis === 'light' ? baseFontSize * 1.15 :
          baseFontSize;

        // Exit fade
        const exitOpacity = interpolate(
          frame,
          [durationInFrames - 15, durationInFrames],
          [1, 0],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
        );

        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              fontSize: emphasisSize,
              fontWeight: 800,
              fontFamily: 'Arial, Helvetica, sans-serif',
              color: wordColor,
              opacity: progress * exitOpacity,
              transform: `scale(${progress})`,
              textShadow: '0 4px 12px rgba(0,0,0,0.6)',
            }}
          >
            {word.text}
          </span>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Preset: Flow — words slide in from right with smooth spring
// ---------------------------------------------------------------------------

const FlowPreset: React.FC<{
  words: ParsedWord[];
  color: string;
  accentColor: string;
  durationInFrames: number;
}> = ({ words, color, accentColor, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();

  const stagger = Math.round(5 * timingMultiplier);
  const visibleWords = words.filter((w) => w.text !== '');

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0 14px',
        justifyContent: 'center',
        alignItems: 'center',
        maxWidth: '80%',
      }}
    >
      {visibleWords.map((word, i) => {
        const delay = i * stagger;
        const progress = spring({
          frame: Math.max(0, frame - delay),
          fps,
          config: { ...springConfig, overshootClamping: true },
        });

        const translateX = interpolate(progress, [0, 1], [80, 0]);
        const wordColor = word.emphasis !== 'none' ? accentColor : color;

        const exitOpacity = interpolate(
          frame,
          [durationInFrames - 15, durationInFrames],
          [1, 0],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
        );

        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              fontSize: 64,
              fontWeight: 700,
              fontFamily: 'Arial, Helvetica, sans-serif',
              color: wordColor,
              opacity: progress * exitOpacity,
              transform: `translateX(${translateX}px)`,
              textShadow: '0 2px 8px rgba(0,0,0,0.5)',
            }}
          >
            {word.text}
          </span>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Preset: Stack — words grouped into lines of ~4, each line springs up
// ---------------------------------------------------------------------------

function chunkArray<T>(arr: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

const StackPreset: React.FC<{
  words: ParsedWord[];
  color: string;
  accentColor: string;
  durationInFrames: number;
}> = ({ words, color, accentColor, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();

  const visibleWords = words.filter((w) => w.text !== '');
  const lines = chunkArray(visibleWords, 4);
  const lineStagger = Math.round(12 * timingMultiplier);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 12,
        maxWidth: '85%',
      }}
    >
      {lines.map((line, lineIdx) => {
        const delay = lineIdx * lineStagger;
        const progress = spring({
          frame: Math.max(0, frame - delay),
          fps,
          config: springConfig,
        });

        const translateY = interpolate(progress, [0, 1], [60, 0]);

        const exitOpacity = interpolate(
          frame,
          [durationInFrames - 15, durationInFrames],
          [1, 0],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
        );

        return (
          <div
            key={lineIdx}
            style={{
              display: 'flex',
              gap: '0 14px',
              justifyContent: 'center',
              opacity: progress * exitOpacity,
              transform: `translateY(${translateY}px)`,
            }}
          >
            {line.map((word, wi) => (
              <span
                key={wi}
                style={{
                  fontSize: 66,
                  fontWeight: 700,
                  fontFamily: 'Arial, Helvetica, sans-serif',
                  color: word.emphasis !== 'none' ? accentColor : color,
                  textShadow: '0 3px 10px rgba(0,0,0,0.5)',
                }}
              >
                {word.text}
              </span>
            ))}
          </div>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Preset: Highlight — text fades in, emphasized words get colored bg wipe
// ---------------------------------------------------------------------------

const HighlightPreset: React.FC<{
  words: ParsedWord[];
  color: string;
  accentColor: string;
  durationInFrames: number;
}> = ({ words, color, accentColor, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { timingMultiplier } = useQuality();

  const visibleWords = words.filter((w) => w.text !== '');
  const fadeInEnd = Math.round(20 * timingMultiplier);
  const highlightStart = fadeInEnd + 5;
  const highlightStagger = Math.round(8 * timingMultiplier);

  const textOpacity = interpolate(frame, [0, fadeInEnd], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const exitOpacity = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  // Count how many emphasized words have appeared before this one
  let emphasisIdx = 0;

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '4px 14px',
        justifyContent: 'center',
        alignItems: 'center',
        maxWidth: '80%',
        opacity: exitOpacity,
      }}
    >
      {visibleWords.map((word, i) => {
        let highlightProgress = 0;
        if (word.emphasis !== 'none') {
          const delay = highlightStart + emphasisIdx * highlightStagger;
          highlightProgress = spring({
            frame: Math.max(0, frame - delay),
            fps,
            config: { mass: 1, damping: 15, stiffness: 120, overshootClamping: true },
          });
          emphasisIdx++;
        }

        const bgWidth = `${highlightProgress * 100}%`;

        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              position: 'relative',
              fontSize: 66,
              fontWeight: 700,
              fontFamily: 'Arial, Helvetica, sans-serif',
              color: color,
              opacity: textOpacity,
              textShadow: '0 2px 8px rgba(0,0,0,0.5)',
              padding: word.emphasis !== 'none' ? '2px 8px' : '2px 0',
            }}
          >
            {word.emphasis !== 'none' && (
              <span
                style={{
                  position: 'absolute',
                  left: 0,
                  top: 0,
                  bottom: 0,
                  width: bgWidth,
                  background: accentColor,
                  borderRadius: 4,
                  zIndex: -1,
                  opacity: 0.85,
                }}
              />
            )}
            {word.text}
          </span>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Preset registry
// ---------------------------------------------------------------------------

type PresetComponent = React.FC<{
  words: ParsedWord[];
  color: string;
  accentColor: string;
  durationInFrames: number;
}>;

const PRESETS: Record<string, PresetComponent> = {
  punch: PunchPreset,
  flow: FlowPreset,
  stack: StackPreset,
  highlight: HighlightPreset,
};

// ---------------------------------------------------------------------------
// Shared visual renderer
// ---------------------------------------------------------------------------

function KineticTextVisual({
  data,
  durationInFrames,
  solidBackground,
}: {
  data: KineticData;
  durationInFrames: number;
  solidBackground?: string;
}) {
  const frame = useCurrentFrame();
  const PresetComp = PRESETS[data.preset] || PRESETS.punch;

  // Exit fade over last 15 frames (container-level)
  const exitOpacity = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  return (
    <AbsoluteFill
      style={{
        ...positionStyle(data.position),
        ...backgroundStyle(data.background),
        alignItems: data.align === 'left' ? 'flex-start' : data.align === 'right' ? 'flex-end' : 'center',
        paddingLeft: data.align === 'left' ? 60 : 0,
        paddingRight: data.align === 'right' ? 60 : 0,
        opacity: exitOpacity,
        background: solidBackground || backgroundStyle(data.background).backgroundColor,
      }}
    >
      <PresetComp
        words={data.words}
        color={data.color}
        accentColor={data.accentColor}
        durationInFrames={durationInFrames}
      />
    </AbsoluteFill>
  );
}

// ---------------------------------------------------------------------------
// Exported components
// ---------------------------------------------------------------------------

/** KineticTextOverlay: for use in OVERLAY_COMPONENTS registry (transparent bg) */
export const KineticTextOverlay: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const data = parseKineticData(content, metadata);
  return <KineticTextVisual data={data} durationInFrames={durationInFrames} />;
};

/** KineticText: visual mode with black background */
export const KineticText: React.FC<OverlayProps> = ({ content, metadata, durationInFrames }) => {
  const data = parseKineticData(content, metadata);
  return <KineticTextVisual data={data} durationInFrames={durationInFrames} solidBackground="#000" />;
};
