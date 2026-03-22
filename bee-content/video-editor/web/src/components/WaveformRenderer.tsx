import { useEffect, useRef, useState } from 'react';

// Module-level cache: src → peaks array
const waveformCache = new Map<string, number[]>();

// Shared AudioContext (created lazily)
let audioCtx: AudioContext | null = null;
function getAudioContext(): AudioContext {
  if (!audioCtx) audioCtx = new AudioContext();
  return audioCtx;
}

/** Generate a pseudo-random waveform that looks organic (speech-like or music-like) */
function generatePlaceholder(seed: string, numBuckets: number): number[] {
  // Simple hash from string for deterministic randomness
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = ((h << 5) - h + seed.charCodeAt(i)) | 0;
  const rand = () => { h = (h * 1103515245 + 12345) & 0x7fffffff; return (h % 1000) / 1000; };

  const peaks: number[] = [];
  let level = 0.3 + rand() * 0.3;
  for (let i = 0; i < numBuckets; i++) {
    // Smooth random walk with occasional dips (simulates speech pauses)
    level += (rand() - 0.48) * 0.15;
    level = Math.max(0.05, Math.min(0.85, level));
    // Add small jitter for realism
    const jitter = (rand() - 0.5) * 0.1;
    peaks.push(Math.max(0.02, level + jitter));
  }
  return peaks;
}

async function decodeAndExtract(src: string, numBuckets: number): Promise<number[]> {
  const cached = waveformCache.get(src);
  if (cached && cached.length === numBuckets) return cached;

  // Placeholder sources skip the fetch entirely
  if (src.startsWith('placeholder:')) {
    const placeholder = generatePlaceholder(src, numBuckets);
    waveformCache.set(src, placeholder);
    return placeholder;
  }

  const url = `/api/media/file?path=${encodeURIComponent(src)}`;
  const response = await fetch(url);
  if (!response.ok) {
    // Generate a realistic-looking placeholder waveform from src hash
    const placeholder = generatePlaceholder(src, numBuckets);
    waveformCache.set(src, placeholder);
    return placeholder;
  }

  const arrayBuffer = await response.arrayBuffer();
  const ctx = getAudioContext();
  const audioBuffer = await ctx.decodeAudioData(arrayBuffer);
  const channelData = audioBuffer.getChannelData(0);

  const bucketSize = Math.floor(channelData.length / numBuckets);
  const peaks: number[] = [];
  for (let i = 0; i < numBuckets; i++) {
    let max = 0;
    const start = i * bucketSize;
    const end = Math.min(start + bucketSize, channelData.length);
    for (let j = start; j < end; j++) {
      const abs = Math.abs(channelData[j]);
      if (abs > max) max = abs;
    }
    peaks.push(max);
  }

  waveformCache.set(src, peaks);
  return peaks;
}

interface Props {
  src: string;
  width: number;
  height: number;
  color: string;
}

export function WaveformRenderer({ src, width, height, color }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [peaks, setPeaks] = useState<number[] | null>(null);

  const numBuckets = Math.max(10, Math.floor(width / 2));

  useEffect(() => {
    if (!src) return;
    let cancelled = false;
    decodeAndExtract(src, numBuckets).then(p => {
      if (!cancelled) setPeaks(p);
    }).catch(() => {});
    return () => { cancelled = true; };
  }, [src, numBuckets]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !peaks) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = width;
    canvas.height = height;
    ctx.clearRect(0, 0, width, height);

    const barWidth = width / peaks.length;
    const midY = height / 2;

    ctx.fillStyle = color;
    ctx.globalAlpha = 0.6;

    for (let i = 0; i < peaks.length; i++) {
      const barHeight = peaks[i] * height * 0.8;
      const x = i * barWidth;
      ctx.fillRect(x, midY - barHeight / 2, Math.max(1, barWidth - 0.5), barHeight);
    }
  }, [peaks, width, height, color]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
      }}
    />
  );
}
