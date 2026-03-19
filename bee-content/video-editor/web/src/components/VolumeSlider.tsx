import { useCallback, useRef, useState } from 'react';
import { useProjectStore } from '../stores/project';

interface Props {
  segmentId: string;
  audioIndex: number;
  currentVolume: number;
  currentFadeIn?: number;
  currentFadeOut?: number;
  showFades?: boolean;
}

export function VolumeSlider({
  segmentId,
  audioIndex,
  currentVolume,
  currentFadeIn,
  currentFadeOut,
  showFades = false,
}: Props) {
  const updateSegmentConfig = useProjectStore(s => s.updateSegmentConfig);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [localVolume, setLocalVolume] = useState(currentVolume);

  const sendUpdate = useCallback((updates: Record<string, unknown>) => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      updateSegmentConfig(segmentId, {
        audio_updates: [{ index: audioIndex, ...updates }],
      });
    }, 300);
  }, [segmentId, audioIndex, updateSegmentConfig]);

  const handleVolumeChange = useCallback((vol: number) => {
    setLocalVolume(vol);
    sendUpdate({ volume: vol });
  }, [sendUpdate]);

  const handleFadeChange = useCallback((field: 'fade_in' | 'fade_out', value: string) => {
    const num = parseFloat(value);
    if (!isNaN(num) && num >= 0) {
      sendUpdate({ [field]: num });
    }
  }, [sendUpdate]);

  return (
    <div className="flex items-center gap-2 py-1 flex-wrap">
      <span className="text-[10px] text-gray-500 w-14 shrink-0">Volume</span>
      <input
        type="range"
        min={0}
        max={1}
        step={0.05}
        value={localVolume}
        className="w-20 accent-blue-500"
        onChange={e => handleVolumeChange(parseFloat(e.target.value))}
        onClick={e => e.stopPropagation()}
      />
      <span className="text-[10px] text-gray-400 w-8">{localVolume.toFixed(2)}</span>
      {showFades && (
        <>
          <label className="flex items-center gap-1 text-[10px] text-gray-500">
            In
            <input
              type="number"
              min={0}
              step={0.5}
              defaultValue={currentFadeIn ?? 0}
              className="w-10 bg-editor-bg text-gray-300 border border-editor-border rounded px-1 py-0.5 text-[10px] focus:border-editor-accent outline-none"
              onBlur={e => handleFadeChange('fade_in', e.target.value)}
              onClick={e => e.stopPropagation()}
            />
          </label>
          <label className="flex items-center gap-1 text-[10px] text-gray-500">
            Out
            <input
              type="number"
              min={0}
              step={0.5}
              defaultValue={currentFadeOut ?? 0}
              className="w-10 bg-editor-bg text-gray-300 border border-editor-border rounded px-1 py-0.5 text-[10px] focus:border-editor-accent outline-none"
              onBlur={e => handleFadeChange('fade_out', e.target.value)}
              onClick={e => e.stopPropagation()}
            />
          </label>
        </>
      )}
    </div>
  );
}
