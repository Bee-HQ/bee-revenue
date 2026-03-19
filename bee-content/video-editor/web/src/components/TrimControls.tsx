import { useCallback, useRef, useState, useEffect } from 'react';
import { useProjectStore } from '../stores/project';

const TC_PATTERN = /^\d{2}:\d{2}:\d{2}\.\d{3}$/;

interface Props {
  segmentId: string;
  visualIndex: number;
  currentIn: string | null;
  currentOut: string | null;
}

function tcToSeconds(tc: string): number {
  const parts = tc.split(':');
  if (parts.length !== 3) return 0;
  return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseFloat(parts[2]);
}

function secondsToTc(s: number): string {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s - h * 3600 - m * 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${sec.toFixed(3).padStart(6, '0')}`;
}

export function TrimControls({ segmentId, visualIndex, currentIn, currentOut }: Props) {
  const updateSegmentConfig = useProjectStore(s => s.updateSegmentConfig);
  const [tcIn, setTcIn] = useState(currentIn ?? '');
  const [tcOut, setTcOut] = useState(currentOut ?? '');
  const barRef = useRef<HTMLDivElement>(null);
  const dragging = useRef<'in' | 'out' | null>(null);
  const latestIn = useRef(tcIn);
  const latestOut = useRef(tcOut);
  latestIn.current = tcIn;
  latestOut.current = tcOut;

  // Sync with prop changes
  useEffect(() => { setTcIn(currentIn ?? ''); }, [currentIn]);
  useEffect(() => { setTcOut(currentOut ?? ''); }, [currentOut]);

  const inSec = tcIn && TC_PATTERN.test(tcIn) ? tcToSeconds(tcIn) : 0;
  const outSec = tcOut && TC_PATTERN.test(tcOut) ? tcToSeconds(tcOut) : 0;
  const hasRange = inSec > 0 || outSec > 0;

  // Bar range: 0 to max with padding
  const maxSec = hasRange ? Math.max(outSec, inSec) * 1.2 || 60 : 60;
  const leftPct = (inSec / maxSec) * 100;
  const rightPct = (outSec / maxSec) * 100;
  const widthPct = Math.max(rightPct - leftPct, 1);

  const commitChange = useCallback((field: 'tc_in' | 'out', value: string) => {
    if (value === '' || TC_PATTERN.test(value)) {
      updateSegmentConfig(segmentId, {
        visual_updates: [{ index: visualIndex, [field]: value || null }],
      });
    }
  }, [segmentId, visualIndex, updateSegmentConfig]);

  const handleMouseDown = useCallback((handle: 'in' | 'out', e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragging.current = handle;

    const onMove = (ev: MouseEvent) => {
      if (!barRef.current || !dragging.current) return;
      const rect = barRef.current.getBoundingClientRect();
      const pct = Math.max(0, Math.min(1, (ev.clientX - rect.left) / rect.width));
      const sec = pct * maxSec;
      const tc = secondsToTc(Math.max(0, sec));

      if (dragging.current === 'in') {
        setTcIn(tc);
      } else {
        setTcOut(tc);
      }
    };

    const onUp = () => {
      if (dragging.current === 'in') {
        commitChange('tc_in', latestIn.current);
      } else {
        commitChange('out', latestOut.current);
      }
      dragging.current = null;
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    };

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }, [maxSec, segmentId, visualIndex, commitChange, tcIn]);

  // Commit on blur for direct text editing
  const handleBlur = useCallback((field: 'tc_in' | 'out', value: string) => {
    commitChange(field, value);
  }, [commitChange]);

  return (
    <div className="py-1" onClick={e => e.stopPropagation()}>
      {/* Draggable trim bar */}
      <div className="flex items-center gap-2 mb-1">
        <span className="text-[10px] text-gray-500 w-14 shrink-0">Trim</span>
        <div
          ref={barRef}
          className="flex-1 h-5 bg-editor-bg border border-editor-border rounded relative cursor-crosshair select-none"
        >
          {/* Selected range */}
          {hasRange && (
            <div
              className="absolute top-0 bottom-0 bg-yellow-500/20 border-y border-yellow-500/40"
              style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
            />
          )}

          {/* In handle */}
          {hasRange && (
            <div
              className="absolute top-0 bottom-0 w-1.5 bg-yellow-400 rounded-sm cursor-ew-resize hover:bg-yellow-300 z-10"
              style={{ left: `${leftPct}%`, transform: 'translateX(-50%)' }}
              onMouseDown={e => handleMouseDown('in', e)}
              title={`In: ${tcIn}`}
            />
          )}

          {/* Out handle */}
          {hasRange && (
            <div
              className="absolute top-0 bottom-0 w-1.5 bg-yellow-400 rounded-sm cursor-ew-resize hover:bg-yellow-300 z-10"
              style={{ left: `${rightPct}%`, transform: 'translateX(-50%)' }}
              onMouseDown={e => handleMouseDown('out', e)}
              title={`Out: ${tcOut}`}
            />
          )}

          {/* Click to set position */}
          {!hasRange && (
            <div className="absolute inset-0 flex items-center justify-center text-[9px] text-gray-600">
              Set trim points below
            </div>
          )}
        </div>
      </div>

      {/* Timecode inputs */}
      <div className="flex items-center gap-2 ml-16">
        <label className="flex items-center gap-1 text-[10px] text-gray-500">
          In
          <input
            type="text"
            data-trim-in={`${segmentId}-${visualIndex}`}
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
            data-trim-out={`${segmentId}-${visualIndex}`}
            value={tcOut}
            placeholder="HH:MM:SS.mmm"
            className="w-24 bg-editor-bg text-gray-300 border border-editor-border rounded px-1.5 py-0.5 text-[10px] font-mono focus:border-editor-accent outline-none"
            onChange={e => setTcOut(e.target.value)}
            onBlur={e => handleBlur('out', e.target.value)}
            onClick={e => e.stopPropagation()}
          />
        </label>
        {hasRange && (
          <span className="text-[10px] text-gray-600 font-mono">
            {(outSec - inSec).toFixed(1)}s
          </span>
        )}
      </div>
    </div>
  );
}
