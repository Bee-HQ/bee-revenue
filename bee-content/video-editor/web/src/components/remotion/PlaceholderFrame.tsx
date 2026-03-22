import { AbsoluteFill } from 'remotion';

const TYPE_COLORS: Record<string, string> = {
  STOCK: '#1e40af', MAP: '#166534', GRAPHIC: '#86198f',
  GENERATED: '#7c2d12', WAVEFORM: '#065f46', PHOTO: '#6b21a8',
};

const TYPE_ICONS: Record<string, string> = {
  STOCK: '📦', MAP: '🗺️', GRAPHIC: '🎨', GENERATED: '🤖',
};

export function PlaceholderFrame({ type, title }: { type: string; title: string }) {
  return (
    <AbsoluteFill style={{ backgroundColor: TYPE_COLORS[type] || '#1a1a1a', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
      <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 48 }}>{TYPE_ICONS[type] || '🎬'}</span>
      <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: 16, fontFamily: 'Arial' }}>{type}</span>
      <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12, fontFamily: 'Arial' }}>{title}</span>
    </AbsoluteFill>
  );
}

export function isRealFile(src: string | undefined): boolean {
  if (!src) return false;
  return src.includes('/') || /\.(mp4|mov|mkv|webm|avi|jpg|jpeg|png|webp|gif|mp3|wav|m4a)$/i.test(src);
}
