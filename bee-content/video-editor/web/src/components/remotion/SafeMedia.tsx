import { useState, useCallback } from 'react';
import { Video, Img } from 'remotion';
import { PlaceholderFrame } from './PlaceholderFrame';

export function mediaUrl(path: string): string {
  return `/api/media/file?path=${encodeURIComponent(path)}`;
}

export const IMAGE_EXTS = new Set(['jpg', 'jpeg', 'png', 'webp', 'gif']);

export const COLOR_FILTERS: Record<string, string> = {
  dark_crime: 'brightness(0.85) saturate(0.6) contrast(1.2) sepia(0.1)',
  surveillance: 'brightness(0.8) saturate(0.3) contrast(1.1) hue-rotate(90deg)',
  noir: 'brightness(0.9) saturate(0) contrast(1.3)',
  bodycam: 'brightness(0.85) saturate(0.5) contrast(1.1) sepia(0.15)',
  cold_blue: 'brightness(0.9) saturate(0.7) contrast(1.1) hue-rotate(200deg)',
  warm_victim: 'brightness(0.9) saturate(0.8) sepia(0.2)',
  sepia: 'brightness(0.95) saturate(0.5) sepia(0.6)',
  vintage: 'brightness(0.9) saturate(0.7) sepia(0.3) contrast(1.1)',
  bleach_bypass: 'brightness(1.1) saturate(0.4) contrast(1.4)',
  night_vision: 'brightness(0.7) saturate(0.3) hue-rotate(90deg) contrast(1.3)',
  golden_hour: 'brightness(1.05) saturate(1.2) sepia(0.15)',
  vhs: 'brightness(0.95) saturate(0.8) contrast(0.9)',
};

export function SafeVideo({ src, type, title, style }: { src: string; type: string; title: string; style?: React.CSSProperties }) {
  const [failed, setFailed] = useState(false);
  const handleError = useCallback(() => setFailed(true), []);
  if (failed) return <PlaceholderFrame type={type} title={`${title} (media unavailable)`} />;
  return <Video src={src} style={style} onError={handleError} />;
}

export function SafeImg({ src, type, title, style }: { src: string; type: string; title: string; style?: React.CSSProperties }) {
  const [failed, setFailed] = useState(false);
  const handleError = useCallback(() => setFailed(true), []);
  if (failed) return <PlaceholderFrame type={type} title={`${title} (media unavailable)`} />;
  return <Img src={src} style={style} onError={handleError} />;
}
