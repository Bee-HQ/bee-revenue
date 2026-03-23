import { useRef, useEffect, useState, useCallback } from 'react';
import type { TimelineAction, TimelineRow } from '@xzdarcy/timeline-engine';
import type { BeeTimelineAction } from '../adapters/timeline-adapter';
import { useProjectStore } from '../stores/project';
import { WaveformRenderer } from './WaveformRenderer';

const TRACK_COLORS: Record<string, { bg: string; border: string; wave: string }> = {
  video:      { bg: '#a16207', border: '#ca8a04', wave: '#ca8a04' },
  narration:  { bg: '#166534', border: '#22c55e', wave: '#22c55e' },
  audio:      { bg: '#0f766e', border: '#14b8a6', wave: '#14b8a6' },
  music:      { bg: '#6b21a8', border: '#a855f7', wave: '#a855f7' },
  overlay:    { bg: '#9d174d', border: '#f472b6', wave: '#f472b6' },
};

const AUDIO_EFFECTS = new Set(['narration', 'audio', 'music']);

function ActionClip({ action, row }: { action: BeeTimelineAction; row: TimelineRow }) {
  const effectId = action.effectId || 'video';
  const colors = TRACK_COLORS[effectId] || TRACK_COLORS.video;
  const data = action.data;
  const isFirstAction = row.actions.length > 0 && row.actions[0].id === action.id;
  const containerRef = useRef<HTMLDivElement>(null);
  const [clipWidth, setClipWidth] = useState(100);

  const handleClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    useProjectStore.getState().selectAction(action.id, e.shiftKey);
  }, [action.id]);

  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(entries => {
      for (const entry of entries) {
        setClipWidth(entry.contentRect.width);
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  let label = data?.title || '';
  if (effectId === 'narration') label = `NAR: ${data?.title || ''}`;
  else if (effectId === 'overlay') label = data?.title || data?.contentType || 'Overlay';
  else if (effectId === 'music') label = data?.src?.split('/').pop() || 'Music';
  else if (effectId === 'audio') label = data?.contentType || 'Audio';
  else if (data?.src) label = data.src.split('/').pop() || data.title;

  const isAudio = AUDIO_EFFECTS.has(effectId);
  // Show waveform for all audio clips — real src or placeholder from title
  const waveformSrc = isAudio ? (data?.src || `placeholder:${data?.title || action.id}`) : '';

  return (
    <div
      ref={containerRef}
      data-action-id={action.id}
      onClick={handleClick}
      style={{
        background: colors.bg,
        borderLeft: `2px solid ${colors.border}`,
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        padding: '0 6px',
        overflow: 'hidden',
        borderRadius: 2,
        cursor: 'pointer',
        outline: action.selected ? '2px solid #3b82f6' : 'none',
        outlineOffset: -1,
        position: 'relative',
      }}
    >
      {waveformSrc && (
        <WaveformRenderer
          src={waveformSrc}
          width={clipWidth}
          height={28}
          color={colors.wave}
        />
      )}
      {isFirstAction && (
        <span style={{ fontSize: 8, color: '#999', marginRight: 4, fontFamily: 'monospace', flexShrink: 0, position: 'relative', zIndex: 1 }}>
          {row.id}
        </span>
      )}
      <span style={{ fontSize: 10, color: '#fff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', position: 'relative', zIndex: 1 }}>
        {label}
      </span>
    </div>
  );
}

export function renderTimelineAction(action: TimelineAction, row: TimelineRow) {
  return <ActionClip action={action as BeeTimelineAction} row={row} />;
}
