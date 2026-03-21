import type { TimelineAction, TimelineRow } from '@xzdarcy/timeline-engine';
import type { BeeTimelineAction } from '../adapters/timeline-adapter';

const TRACK_COLORS: Record<string, { bg: string; border: string }> = {
  video:      { bg: '#a16207', border: '#ca8a04' },
  narration:  { bg: '#166534', border: '#22c55e' },
  audio:      { bg: '#0f766e', border: '#14b8a6' },
  music:      { bg: '#6b21a8', border: '#a855f7' },
  overlay:    { bg: '#9d174d', border: '#f472b6' },
};

export function renderTimelineAction(action: TimelineAction, row: TimelineRow) {
  const beeAction = action as BeeTimelineAction;
  const effectId = beeAction.effectId || 'video';
  const colors = TRACK_COLORS[effectId] || TRACK_COLORS.video;
  const data = beeAction.data;
  const isFirstAction = row.actions.length > 0 && row.actions[0].id === action.id;

  let label = data?.title || '';
  if (effectId === 'narration') label = `NAR: ${data?.title || ''}`;
  else if (effectId === 'overlay') label = `${data?.contentType || ''}: ${data?.title || ''}`;
  else if (effectId === 'music') label = data?.src?.split('/').pop() || 'Music';
  else if (effectId === 'audio') label = data?.contentType || 'Audio';
  else if (data?.src) label = data.src.split('/').pop() || data.title;

  return (
    <div
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
      }}
    >
      {isFirstAction && (
        <span style={{ fontSize: 8, color: '#999', marginRight: 4, fontFamily: 'monospace', flexShrink: 0 }}>
          {row.id}
        </span>
      )}
      <span style={{ fontSize: 10, color: '#fff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
        {label}
      </span>
    </div>
  );
}
