/** Parse "M:SS" or "H:MM:SS" timecode to seconds. */
export function parseTimecode(tc: string): number {
  const parts = tc.trim().split(':').map(Number);
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return 0;
}

/** Format seconds to "M:SS" or "H:MM:SS". */
export function formatTimecode(seconds: number): string {
  const total = Math.round(seconds);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (h > 0)
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

/** Seconds to frame count. */
export function timeToFrames(seconds: number, fps: number): number {
  return Math.round(seconds * fps);
}

/** Frame count to seconds. */
export function framesToTime(frames: number, fps: number): number {
  return frames / fps;
}

/** Seconds to milliseconds. */
export function timeToMs(seconds: number): number {
  return Math.round(seconds * 1000);
}

/** Milliseconds to seconds. */
export function msToTime(ms: number): number {
  return ms / 1000;
}

/** Format seconds to "M:SS" (simple display). */
export function formatSeconds(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
