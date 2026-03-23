import React from 'react';
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../primitives/QualityContext';
import { mediaUrl } from '../SafeMedia';
import type { OverlayProps } from '../overlays';
import { AnimatedBG } from '../cards/AnimatedBG';

interface WindowDef {
  type: 'photo_viewer' | 'video_player' | 'notepad' | 'phone_mockup' | 'document';
  name?: string;
  title?: string;
  src?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  zIndex?: number;
}

export interface DesktopMontageData {
  windows: WindowDef[];
  background: string;
  blur: boolean;
}

// Default layout positions for N windows
const LAYOUTS: Record<number, Array<{ x: number; y: number; w: number; h: number }>> = {
  1: [{ x: 350, y: 100, w: 500, h: 400 }],
  2: [{ x: 100, y: 120, w: 420, h: 360 }, { x: 580, y: 120, w: 420, h: 360 }],
  3: [
    { x: 60, y: 80, w: 380, h: 320 },
    { x: 480, y: 60, w: 380, h: 320 },
    { x: 270, y: 280, w: 380, h: 320 },
  ],
  5: [
    { x: 40, y: 40, w: 340, h: 280 },
    { x: 420, y: 20, w: 340, h: 280 },
    { x: 800, y: 40, w: 340, h: 280 },
    { x: 120, y: 340, w: 340, h: 280 },
    { x: 520, y: 360, w: 340, h: 280 },
  ],
};

function getDefaultLayout(count: number): Array<{ x: number; y: number; w: number; h: number }> {
  if (LAYOUTS[count]) return LAYOUTS[count];
  // Fallback: grid layout
  const cols = Math.ceil(Math.sqrt(count));
  const cellW = Math.floor(1100 / cols);
  const cellH = Math.floor(600 / Math.ceil(count / cols));
  return Array.from({ length: count }, (_, i) => ({
    x: 60 + (i % cols) * cellW,
    y: 60 + Math.floor(i / cols) * cellH,
    w: cellW - 40,
    h: cellH - 40,
  }));
}

export function parseDesktopMontageData(
  content: string,
  metadata?: Record<string, any> | null,
): DesktopMontageData {
  let windows: WindowDef[] = [];

  try {
    const parsed = JSON.parse(content);
    if (Array.isArray(parsed)) {
      const layout = getDefaultLayout(parsed.length);
      windows = parsed.map((w: any, i: number) => ({
        type: w.type || 'photo_viewer',
        name: w.name,
        title: w.title,
        src: w.src,
        x: w.x ?? layout[i]?.x ?? 100,
        y: w.y ?? layout[i]?.y ?? 100,
        width: w.width ?? layout[i]?.w ?? 360,
        height: w.height ?? layout[i]?.h ?? 300,
        zIndex: w.zIndex ?? i,
      }));
    }
  } catch {
    // non-JSON content -> empty
  }

  return {
    windows,
    background: (metadata?.background as string) || 'animated-blue',
    blur: metadata?.blur === true,
  };
}

const MENU_ITEMS: Record<string, string[]> = {
  photo_viewer: ['File', 'Edit', 'Image', 'View', 'Help'],
  video_player: ['File', 'Edit', 'Playback', 'Audio', 'Video', 'View', 'Help'],
  notepad: ['File', 'Edit', 'Search', 'View', 'Help'],
  document: ['File', 'Edit', 'View', 'Help'],
  phone_mockup: [],
};

const WINDOW_TITLES: Record<string, string> = {
  photo_viewer: 'Photo Viewer',
  video_player: 'Video Player',
  notepad: 'Notepad',
  document: 'Photo Viewer',
  phone_mockup: '',
};

function MiniWindow({ win, progress }: { win: WindowDef; progress: number }) {
  const opacity = interpolate(progress, [0, 1], [0, 1]);
  const scale = interpolate(progress, [0, 1], [0.85, 1]);
  const menuItems = MENU_ITEMS[win.type] || MENU_ITEMS.photo_viewer;
  const title = win.title || win.name || WINDOW_TITLES[win.type] || 'Window';

  if (win.type === 'phone_mockup') {
    return (
      <div style={{
        position: 'absolute', left: win.x, top: win.y,
        width: win.width, opacity, transform: `scale(${scale})`,
        zIndex: win.zIndex ?? 0,
      }}>
        <div style={{
          borderRadius: 16, background: '#1a1a1a', padding: '20px 4px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
        }}>
          <div style={{
            borderRadius: 12, overflow: 'hidden', background: '#fff',
            height: win.height - 40,
          }}>
            {win.src ? (
              <Img src={mediaUrl(win.src)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            ) : (
              <div style={{ width: '100%', height: '100%', background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999', fontSize: 11 }}>
                {title}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      position: 'absolute', left: win.x, top: win.y,
      width: win.width, opacity, transform: `scale(${scale})`,
      zIndex: win.zIndex ?? 0,
    }}>
      <div style={{
        background: '#1e1e1e', borderRadius: 8, overflow: 'hidden',
        boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
      }}>
        {/* Title bar */}
        <div style={{ height: 24, background: '#2d2d2d', display: 'flex', alignItems: 'center', padding: '0 8px', gap: 6 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#ff5f57' }} />
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#febc2e' }} />
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#28c840' }} />
          <span style={{ flex: 1, textAlign: 'center', color: '#999', fontSize: 9, fontFamily: 'system-ui' }}>
            {WINDOW_TITLES[win.type] || title}
          </span>
        </div>
        {/* Menu bar */}
        {menuItems.length > 0 && (
          <div style={{ height: 18, background: '#252525', display: 'flex', alignItems: 'center', padding: '0 8px', gap: 10 }}>
            {menuItems.map(m => (
              <span key={m} style={{ color: '#aaa', fontSize: 8, fontFamily: 'system-ui' }}>{m}</span>
            ))}
          </div>
        )}
        {/* Content */}
        <div style={{ height: win.height - (menuItems.length > 0 ? 42 : 24), background: '#111', overflow: 'hidden' }}>
          {win.src ? (
            <Img src={mediaUrl(win.src)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          ) : (
            <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ color: '#555', fontSize: 12 }}>{title}</span>
            </div>
          )}
        </div>
        {/* Playback controls for video player */}
        {win.type === 'video_player' && (
          <div style={{ height: 20, background: '#1a1a1a', display: 'flex', alignItems: 'center', padding: '0 8px', gap: 4 }}>
            <svg width="8" height="8" viewBox="0 0 24 24" fill="#ccc"><polygon points="5,3 19,12 5,21" /></svg>
            <div style={{ flex: 1, height: 3, background: '#444', borderRadius: 1 }}>
              <div style={{ width: '40%', height: '100%', background: '#16a34a', borderRadius: 1 }} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function DesktopMontageVisual({
  data, durationInFrames, background,
}: { data: DesktopMontageData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  const staggerDelay = Math.round(6 * timingMultiplier);
  const blurStart = data.windows.length * staggerDelay + 30;
  const blurAmount = data.blur
    ? interpolate(frame, [blurStart, blurStart + 15], [0, 8], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
    : 0;

  const bgStyle = background?.startsWith('animated-') ? undefined : { backgroundColor: background };

  return (
    <AbsoluteFill style={{ ...bgStyle }}>
      {background?.startsWith('animated-') && (
        <AbsoluteFill><AnimatedBG preset={background} /></AbsoluteFill>
      )}
      <div style={{
        width: '100%', height: '100%', position: 'relative',
        opacity: exitOpacity, filter: blurAmount > 0 ? `blur(${blurAmount}px)` : undefined,
      }}>
        {data.windows.map((win, i) => {
          const delay = i * staggerDelay;
          const progress = spring({
            frame: Math.max(0, frame - delay), fps, config: springConfig,
          });
          return <MiniWindow key={i} win={win} progress={progress} />;
        })}
      </div>
    </AbsoluteFill>
  );
}

export const DesktopMontageOverlay: React.FC<OverlayProps> = (props) => {
  const data = parseDesktopMontageData(props.content, props.metadata);
  return <DesktopMontageVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const DesktopMontage: React.FC<OverlayProps> = (props) => {
  const data = parseDesktopMontageData(props.content, props.metadata);
  return <DesktopMontageVisual data={data} durationInFrames={props.durationInFrames} background={data.background} />;
};
