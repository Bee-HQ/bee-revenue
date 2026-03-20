import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';

interface Props {
  text: string;
  style?: 'karaoke' | 'phrase';
}

export const CaptionOverlay: React.FC<Props> = ({ text, style = 'karaoke' }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const words = text.split(/\s+/).filter(Boolean);
  if (words.length === 0) return null;

  if (style === 'phrase') {
    // Show 3-5 words at a time
    const chunkSize = Math.min(5, Math.max(3, Math.ceil(words.length / Math.ceil(words.length / 4))));
    const chunks: string[][] = [];
    for (let i = 0; i < words.length; i += chunkSize) {
      chunks.push(words.slice(i, i + chunkSize));
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
        }}>
          <span style={{
            color: '#fff',
            fontSize: 42,
            fontWeight: 700,
            fontFamily: 'Arial, Helvetica, sans-serif',
            textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
          }}>
            {currentChunk.join(' ')}
          </span>
        </div>
      </AbsoluteFill>
    );
  }

  // Karaoke: highlight word by word
  const totalChars = words.reduce((sum, w) => sum + w.length, 0);
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
        {words.map((word, i) => {
          const wordStart = (charsSoFar / totalChars) * durationInFrames;
          const wordEnd = ((charsSoFar + word.length) / totalChars) * durationInFrames;
          charsSoFar += word.length;

          const isActive = frame >= wordStart && frame <= wordEnd;
          const isPast = frame > wordEnd;

          return (
            <span
              key={i}
              style={{
                color: isPast || isActive ? '#fbbf24' : '#ffffff',
                fontSize: 42,
                fontWeight: 700,
                fontFamily: 'Arial, Helvetica, sans-serif',
                textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
                opacity: isPast || isActive ? 1 : 0.6,
                transform: isActive ? 'scale(1.05)' : 'scale(1)',
              }}
            >
              {word}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
