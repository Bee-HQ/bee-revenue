import { AbsoluteFill, Video, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from './overlays';

interface PipSource {
  type: 'video' | 'image' | 'map' | 'color';
  src?: string;      // file path for video/image
  color?: string;     // for color type
  label?: string;     // optional label overlay
  lat?: number;       // for map type (renders static placeholder — AnimatedMap is separate)
  lng?: number;
}

interface PipData {
  main: PipSource;
  pip: PipSource;
  layout?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'side-by-side' | 'top-bottom';
  pipSize?: number;   // percentage of screen width (default 30)
  animation?: 'slide' | 'fade' | 'none';
}

export function parsePipData(content: string): PipData {
  try {
    const parsed = JSON.parse(content);
    if (parsed.main && parsed.pip) return parsed;
  } catch {}
  return {
    main: { type: 'color', color: '#1a1a1a', label: content },
    pip: { type: 'color', color: '#333', label: 'PiP' },
  };
}

function mediaUrl(path: string): string {
  return `/api/media/file?path=${encodeURIComponent(path)}`;
}

function SourceRenderer({ source, style }: { source: PipSource; style?: React.CSSProperties }) {
  const baseStyle: React.CSSProperties = {
    width: '100%', height: '100%', objectFit: 'cover', ...style,
  };

  if (source.type === 'video' && source.src) {
    return <Video src={mediaUrl(source.src)} style={baseStyle} />;
  }
  if (source.type === 'image' && source.src) {
    return <Img src={mediaUrl(source.src)} style={baseStyle} />;
  }
  if (source.type === 'color') {
    return (
      <div style={{
        ...baseStyle, backgroundColor: source.color || '#1a1a1a',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {source.label && (
          <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 24, fontFamily: 'Arial' }}>
            {source.label}
          </span>
        )}
      </div>
    );
  }
  // map placeholder
  return (
    <div style={{
      ...baseStyle, backgroundColor: '#166534',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 32 }}>🗺️</span>
    </div>
  );
}

// Layout positions for PiP window
const POSITIONS: Record<string, { top?: string; bottom?: string; left?: string; right?: string }> = {
  'bottom-right': { bottom: '5%', right: '3%' },
  'bottom-left': { bottom: '5%', left: '3%' },
  'top-right': { top: '5%', right: '3%' },
  'top-left': { top: '5%', left: '3%' },
};

export const PictureInPicture: React.FC<PipProps> = ({
  content, metadata: _metadata, durationInFrames, mode: _mode = 'visual',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const data = parsePipData(content);
  const layout = data.layout || 'bottom-right';
  const pipSize = data.pipSize || 30;
  const animation = data.animation || 'slide';

  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Side-by-side and top-bottom are split-screen layouts
  if (layout === 'side-by-side') {
    const dividerX = interpolate(
      spring({ frame, fps, config: { stiffness: 100, damping: 20 } }),
      [0, 1], [100, 50],
    );
    return (
      <AbsoluteFill style={{ opacity: exitOpacity }}>
        <div style={{ position: 'absolute', left: 0, top: 0, width: `${dividerX}%`, height: '100%', overflow: 'hidden' }}>
          <SourceRenderer source={data.main} />
          {data.main.label && (
            <div style={{ position: 'absolute', bottom: 12, left: 12, background: 'rgba(0,0,0,0.6)', padding: '4px 12px', borderRadius: 4, color: '#fff', fontSize: 12, fontFamily: 'Arial' }}>
              {data.main.label}
            </div>
          )}
        </div>
        <div style={{ position: 'absolute', right: 0, top: 0, width: `${100 - dividerX}%`, height: '100%', overflow: 'hidden' }}>
          <SourceRenderer source={data.pip} />
          {data.pip.label && (
            <div style={{ position: 'absolute', bottom: 12, right: 12, background: 'rgba(0,0,0,0.6)', padding: '4px 12px', borderRadius: 4, color: '#fff', fontSize: 12, fontFamily: 'Arial' }}>
              {data.pip.label}
            </div>
          )}
        </div>
        {/* Divider line */}
        <div style={{ position: 'absolute', left: `${dividerX}%`, top: 0, width: 2, height: '100%', background: 'rgba(255,255,255,0.5)' }} />
      </AbsoluteFill>
    );
  }

  if (layout === 'top-bottom') {
    const dividerY = interpolate(
      spring({ frame, fps, config: { stiffness: 100, damping: 20 } }),
      [0, 1], [100, 50],
    );
    return (
      <AbsoluteFill style={{ opacity: exitOpacity }}>
        <div style={{ position: 'absolute', left: 0, top: 0, width: '100%', height: `${dividerY}%`, overflow: 'hidden' }}>
          <SourceRenderer source={data.main} />
        </div>
        <div style={{ position: 'absolute', left: 0, bottom: 0, width: '100%', height: `${100 - dividerY}%`, overflow: 'hidden' }}>
          <SourceRenderer source={data.pip} />
        </div>
        <div style={{ position: 'absolute', top: `${dividerY}%`, left: 0, height: 2, width: '100%', background: 'rgba(255,255,255,0.5)' }} />
      </AbsoluteFill>
    );
  }

  // Corner PiP layout
  const pos = POSITIONS[layout] || POSITIONS['bottom-right'];

  // PiP window animation
  let pipOpacity = 1;
  let pipTranslate = '0px';
  if (animation === 'slide') {
    const appear = spring({ frame: frame - 15, fps, config: { stiffness: 200, damping: 20 } });
    pipOpacity = appear;
    const direction = layout.includes('right') ? 50 : -50;
    pipTranslate = `${interpolate(appear, [0, 1], [direction, 0])}px`;
  } else if (animation === 'fade') {
    pipOpacity = interpolate(frame, [15, 30], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  }

  return (
    <AbsoluteFill style={{ opacity: exitOpacity }}>
      {/* Main source — full screen */}
      <AbsoluteFill>
        <SourceRenderer source={data.main} />
      </AbsoluteFill>

      {/* PiP window */}
      <div style={{
        position: 'absolute', ...pos,
        width: `${pipSize}%`,
        aspectRatio: '16/9',
        borderRadius: 8,
        overflow: 'hidden',
        border: '2px solid rgba(255,255,255,0.3)',
        boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
        opacity: pipOpacity,
        transform: `translateX(${pipTranslate})`,
      }}>
        <SourceRenderer source={data.pip} />
        {data.pip.label && (
          <div style={{
            position: 'absolute', bottom: 6, left: 8,
            background: 'rgba(0,0,0,0.6)', padding: '2px 8px', borderRadius: 3,
            color: '#fff', fontSize: 10, fontFamily: 'Arial',
          }}>
            {data.pip.label}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

export interface PipProps {
  content: string;
  metadata?: Record<string, any> | null;
  durationInFrames: number;
  mode?: 'visual' | 'overlay';
}

// Overlay wrapper
export const PictureInPictureOverlay: React.FC<OverlayProps> = (props) => (
  <PictureInPicture {...props} mode="overlay" />
);
