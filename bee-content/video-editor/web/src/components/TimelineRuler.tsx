import { useRef, useCallback, useState, useEffect } from 'react';
import { useProjectStore } from '../stores/project';
import { formatTimecode, msToTime } from '../adapters/time-utils';

interface Props {
  durationMs: number;
  zoom: number; // pixels per millisecond
  scrollLeft: number;
  onSeek: (ms: number) => void;
}

export function TimelineRuler({ durationMs, zoom, scrollLeft, onSeek }: Props) {
  const rulerRef = useRef<HTMLDivElement>(null);
  const currentTimeMs = useProjectStore((s) => s.currentTimeMs);
  const dragging = useRef(false);
  const [, forceRender] = useState(0);

  // Force a render once the ref is available so ticks can use clientWidth
  useEffect(() => {
    forceRender((n) => n + 1);
  }, []);

  const msToPixel = useCallback(
    (ms: number) => ms * zoom - scrollLeft,
    [zoom, scrollLeft],
  );
  const pixelToMs = useCallback(
    (px: number) => (px + scrollLeft) / zoom,
    [zoom, scrollLeft],
  );

  // Generate tick marks
  const tickInterval = getTickInterval(zoom);
  const ticks: { ms: number; major: boolean }[] = [];
  const width = rulerRef.current?.clientWidth || 1000;
  const startMs = Math.floor(pixelToMs(0) / tickInterval) * tickInterval;
  const endMs = pixelToMs(width);
  for (
    let ms = Math.max(0, startMs);
    ms <= Math.min(durationMs, endMs + tickInterval);
    ms += tickInterval
  ) {
    ticks.push({ ms, major: ms % (tickInterval * 5) === 0 });
  }

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      dragging.current = true;
      const ms = pixelToMs(e.nativeEvent.offsetX);
      onSeek(Math.max(0, Math.min(durationMs, ms)));
    },
    [pixelToMs, durationMs, onSeek],
  );

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!dragging.current || !rulerRef.current) return;
      const rect = rulerRef.current.getBoundingClientRect();
      const px = e.clientX - rect.left;
      const ms = pixelToMs(px);
      onSeek(Math.max(0, Math.min(durationMs, ms)));
    };
    const handleMouseUp = () => {
      dragging.current = false;
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [pixelToMs, durationMs, onSeek]);

  const playheadX = msToPixel(currentTimeMs);

  return (
    <div
      ref={rulerRef}
      className="h-6 bg-editor-surface border-b border-editor-border relative overflow-hidden cursor-pointer select-none shrink-0"
      onMouseDown={handleMouseDown}
    >
      {/* Tick marks */}
      {ticks.map(({ ms, major }) => (
        <div
          key={ms}
          className="absolute top-0 bottom-0"
          style={{ left: msToPixel(ms) }}
        >
          <div
            className={`w-px ${major ? 'h-full bg-gray-600' : 'h-2 bg-gray-700'}`}
          />
          {major && (
            <span
              className="absolute top-2 text-[8px] text-gray-500 font-mono whitespace-nowrap"
              style={{ transform: 'translateX(-50%)' }}
            >
              {formatTimecode(msToTime(ms))}
            </span>
          )}
        </div>
      ))}

      {/* Playhead */}
      {playheadX >= 0 && (
        <div
          className="absolute top-0 bottom-0 pointer-events-none"
          style={{ left: playheadX }}
        >
          <div className="w-px h-full bg-blue-500" />
          <div
            className="absolute top-0 w-3 h-3 bg-blue-500"
            style={{
              left: -6,
              clipPath: 'polygon(0 0, 100% 0, 50% 100%)',
            }}
          />
        </div>
      )}
    </div>
  );
}

function getTickInterval(zoom: number): number {
  // Auto-scale tick interval based on zoom level
  const pixelsPerSecond = zoom * 1000;
  if (pixelsPerSecond > 100) return 1000; // every second
  if (pixelsPerSecond > 20) return 5000; // every 5 seconds
  if (pixelsPerSecond > 5) return 15000; // every 15 seconds
  return 30000; // every 30 seconds
}
