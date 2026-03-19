import { useCallback, useRef } from 'react';
import { useProjectStore } from '../stores/project';

interface Props {
  segmentId: string;
  currentType: string | null;
  currentDuration: number;
  transitions: string[];
}

export function TransitionPicker({ segmentId, currentType, currentDuration, transitions }: Props) {
  const updateSegmentConfig = useProjectStore(s => s.updateSegmentConfig);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleTypeChange = useCallback((type: string) => {
    if (type === '') {
      updateSegmentConfig(segmentId, { transition_in: null });
    } else {
      updateSegmentConfig(segmentId, {
        transition_in: { type, duration: currentDuration || 1.0 },
      });
    }
  }, [segmentId, currentDuration, updateSegmentConfig]);

  const handleDurationChange = useCallback((duration: number) => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      if (currentType) {
        updateSegmentConfig(segmentId, {
          transition_in: { type: currentType, duration },
        });
      }
    }, 300);
  }, [segmentId, currentType, updateSegmentConfig]);

  return (
    <div className="flex items-center gap-2 py-1">
      <span className="text-[10px] text-gray-500 w-14 shrink-0">Transition</span>
      <select
        className="bg-editor-bg text-xs text-gray-300 border border-editor-border rounded px-1.5 py-0.5 focus:border-editor-accent outline-none"
        value={currentType?.toLowerCase() ?? ''}
        onChange={e => handleTypeChange(e.target.value)}
        onClick={e => e.stopPropagation()}
      >
        <option value="">None</option>
        {transitions.map(t => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>
      {currentType && (
        <>
          <input
            type="range"
            min={0.5}
            max={3.0}
            step={0.1}
            defaultValue={currentDuration}
            className="w-20 accent-blue-500"
            onChange={e => handleDurationChange(parseFloat(e.target.value))}
            onClick={e => e.stopPropagation()}
          />
          <span className="text-[10px] text-gray-500 w-6">{currentDuration.toFixed(1)}s</span>
        </>
      )}
    </div>
  );
}
