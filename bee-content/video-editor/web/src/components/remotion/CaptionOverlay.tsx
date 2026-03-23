import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { resolveColor } from './overlays';

export interface CaptionWord {
  text: string;
  color?: string;
}

export function parseCaptionWords(text: string): CaptionWord[] {
  if (!text) return [];
  const result: CaptionWord[] = [];
  const regex = /\{([^:}]+):([^}]+)\}|(\S+)/g;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match[1] !== undefined && match[2] !== undefined) {
      const color = resolveColor(match[1]);
      for (const word of match[2].split(/\s+/)) {
        if (word) result.push({ text: word, color });
      }
    } else if (match[3] !== undefined) {
      result.push({ text: match[3], color: undefined });
    }
  }

  return result;
}

interface Props {
  text: string;
  style?: 'karaoke' | 'phrase';
}

export const CaptionOverlay: React.FC<Props> = ({ text, style = 'karaoke' }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  if (!text) return null;
  const captionWords = parseCaptionWords(text);
  if (captionWords.length === 0) return null;

  if (style === 'phrase') {
    const chunkSize = Math.min(5, Math.max(3, Math.ceil(captionWords.length / Math.ceil(captionWords.length / 4))));
    const chunks: CaptionWord[][] = [];
    for (let i = 0; i < captionWords.length; i += chunkSize) {
      chunks.push(captionWords.slice(i, i + chunkSize));
    }
    const framesPerChunk = Math.floor(durationInFrames / chunks.length);
    const currentChunkIndex = Math.min(Math.floor(frame / framesPerChunk), chunks.length - 1);
    const currentChunk = chunks[currentChunkIndex];

    return (
      <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', padding: '0 0 120px' }}>
        <div style={{
          background: 'rgba(0, 0, 0, 0.7)',
          padding: '10px 28px',
          borderRadius: 8,
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: '0 8px',
        }}>
          {currentChunk.map((cw, i) => (
            <span key={i} style={{
              color: cw.color || '#fff',
              fontSize: 42,
              fontWeight: 700,
              fontFamily: 'Arial, Helvetica, sans-serif',
              textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
            }}>
              {cw.text}
            </span>
          ))}
        </div>
      </AbsoluteFill>
    );
  }

  // Karaoke: highlight word by word
  const plainText = captionWords.map(w => w.text).join(' ');
  const totalChars = plainText.length;
  let charsSoFar = 0;

  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', padding: '0 40px 120px' }}>
      <div style={{
        background: 'rgba(0, 0, 0, 0.7)',
        padding: '10px 28px',
        borderRadius: 8,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: '0 8px',
        maxWidth: '80%',
      }}>
        {captionWords.map((cw, i) => {
          if (i > 0) charsSoFar += 1;
          const wordStart = (charsSoFar / totalChars) * durationInFrames;
          const wordEnd = ((charsSoFar + cw.text.length) / totalChars) * durationInFrames;
          charsSoFar += cw.text.length;

          const isActive = frame >= wordStart && frame <= wordEnd;
          const isPast = frame > wordEnd;
          const highlightColor = cw.color || '#fbbf24';

          return (
            <span
              key={i}
              style={{
                color: isPast || isActive ? highlightColor : '#ffffff',
                fontSize: 42,
                fontWeight: 700,
                fontFamily: 'Arial, Helvetica, sans-serif',
                textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
                opacity: isPast || isActive ? 1 : 0.6,
                transform: isActive ? 'scale(1.05)' : 'scale(1)',
              }}
            >
              {cw.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
