import { AbsoluteFill, Sequence, Video, Img, useVideoConfig } from 'remotion';
import type { Storyboard } from '../types';
import { parseTimecode, timeToFrames } from '../adapters/time-utils';

// Remotion renders inside an iframe — media URLs must be same-origin accessible.
// In dev, Vite proxies /api to the backend.
function mediaUrl(path: string): string {
  return `/api/media/file?path=${encodeURIComponent(path)}`;
}

function BlackFrame() {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#0f0f0f',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <span style={{ color: '#333', fontSize: 14 }}>No media</span>
    </AbsoluteFill>
  );
}

const IMAGE_EXTS = new Set(['jpg', 'jpeg', 'png', 'webp', 'gif']);

export const BeeComposition: React.FC<{ storyboard: Storyboard }> = ({
  storyboard,
}) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {storyboard.segments.map((seg) => {
        const src = seg.assigned_media['visual:0'];
        const from = timeToFrames(parseTimecode(seg.start), fps);
        const duration = timeToFrames(seg.duration_seconds, fps);

        if (duration <= 0) return null;

        const ext = src?.split('.').pop()?.toLowerCase() ?? '';
        const isImage = IMAGE_EXTS.has(ext);

        return (
          <Sequence
            key={seg.id}
            from={from}
            durationInFrames={duration}
            name={seg.title}
          >
            {!src ? (
              <BlackFrame />
            ) : isImage ? (
              <AbsoluteFill>
                <Img
                  src={mediaUrl(src)}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                />
              </AbsoluteFill>
            ) : (
              <Video
                src={mediaUrl(src)}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                }}
              />
            )}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
