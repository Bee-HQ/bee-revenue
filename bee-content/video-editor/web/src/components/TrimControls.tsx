import { useCallback, useState } from 'react';
import { useProjectStore } from '../stores/project';

const TC_PATTERN = /^\d{2}:\d{2}:\d{2}\.\d{3}$/;

interface Props {
  segmentId: string;
  visualIndex: number;
  currentIn: string | null;
  currentOut: string | null;
}

export function TrimControls({ segmentId, visualIndex, currentIn, currentOut }: Props) {
  const updateSegmentConfig = useProjectStore(s => s.updateSegmentConfig);
  const [tcIn, setTcIn] = useState(currentIn ?? '');
  const [tcOut, setTcOut] = useState(currentOut ?? '');

  const handleBlur = useCallback((field: 'tc_in' | 'out', value: string) => {
    if (value === '' || TC_PATTERN.test(value)) {
      updateSegmentConfig(segmentId, {
        visual_updates: [{ index: visualIndex, [field]: value || null }],
      });
    }
  }, [segmentId, visualIndex, updateSegmentConfig]);

  // Compute a visual bar showing the trim region
  const hasRange = tcIn || tcOut;

  return (
    <div className="py-1">
      <div className="flex items-center gap-2">
        <span className="text-[10px] text-gray-500 w-14 shrink-0">Trim</span>
        <label className="flex items-center gap-1 text-[10px] text-gray-500">
          In
          <input
            type="text"
            value={tcIn}
            placeholder="HH:MM:SS.mmm"
            className="w-24 bg-editor-bg text-gray-300 border border-editor-border rounded px-1.5 py-0.5 text-[10px] font-mono focus:border-editor-accent outline-none"
            onChange={e => setTcIn(e.target.value)}
            onBlur={e => handleBlur('tc_in', e.target.value)}
            onClick={e => e.stopPropagation()}
          />
        </label>
        <label className="flex items-center gap-1 text-[10px] text-gray-500">
          Out
          <input
            type="text"
            value={tcOut}
            placeholder="HH:MM:SS.mmm"
            className="w-24 bg-editor-bg text-gray-300 border border-editor-border rounded px-1.5 py-0.5 text-[10px] font-mono focus:border-editor-accent outline-none"
            onChange={e => setTcOut(e.target.value)}
            onBlur={e => handleBlur('out', e.target.value)}
            onClick={e => e.stopPropagation()}
          />
        </label>
      </div>
      {hasRange && (
        <div className="flex items-center gap-2 mt-1 ml-16">
          <div className="h-1.5 flex-1 bg-editor-border rounded overflow-hidden">
            <div className="h-full bg-blue-500/40 rounded" style={{ width: '60%', marginLeft: '10%' }} />
          </div>
        </div>
      )}
    </div>
  );
}
