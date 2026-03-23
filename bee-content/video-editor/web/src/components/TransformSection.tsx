import { useState, useEffect, useRef } from 'react';
import { useProjectStore } from '../stores/project';
import { api } from '../api/client';
import { toast } from '../stores/toast';
import type { TransformConfig, PositionPreset } from '../../shared/transform';
import { TRANSFORM_DEFAULTS } from '../../shared/transform';

const GRID_LABELS: PositionPreset[] = [
  'top-left', 'top', 'top-right',
  'left', 'center', 'right',
  'bottom-left', 'bottom', 'bottom-right',
];

const GRID_SHORT: Record<PositionPreset, string> = {
  'top-left': 'TL', 'top': 'T', 'top-right': 'TR',
  'left': 'L', 'center': 'C', 'right': 'R',
  'bottom-left': 'BL', 'bottom': 'B', 'bottom-right': 'BR',
};

interface Props {
  segmentId: string;
  clipType: 'v' | 'ov';
  layerIndex: number;
  segment: any;
}

export function TransformSection({ segmentId, clipType, layerIndex, segment }: Props) {
  const entry = clipType === 'v' ? segment.visual[layerIndex] : segment.overlay[layerIndex];
  if (!entry) return null;

  const current: TransformConfig = entry.transform || {};
  const pos = current.position || 'center';
  const [x, setX] = useState(current.x ?? 0);
  const [y, setY] = useState(current.y ?? 0);
  const [scale, setScale] = useState(current.scale ?? 1);
  const [rotation, setRotation] = useState(current.rotation ?? 0);
  const [opacity, setOpacity] = useState(current.opacity ?? 1);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync local state when segment data changes
  useEffect(() => {
    const t = entry.transform || {};
    setX(t.x ?? 0);
    setY(t.y ?? 0);
    setScale(t.scale ?? 1);
    setRotation(t.rotation ?? 0);
    setOpacity(t.opacity ?? 1);
  }, [entry.transform]);

  useEffect(() => {
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, []);

  const updateTransform = async (patch: Partial<TransformConfig>) => {
    try {
      const updateKey = clipType === 'v' ? 'visual_updates' : 'overlay_updates';
      await api.updateSegment(segmentId, {
        [updateKey]: [{ index: layerIndex, transform: patch }],
      });
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  const debouncedUpdate = (patch: Partial<TransformConfig>) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => updateTransform(patch), 500);
  };

  const handleReset = async () => {
    try {
      const updateKey = clipType === 'v' ? 'visual_updates' : 'overlay_updates';
      await api.updateSegment(segmentId, {
        [updateKey]: [{ index: layerIndex, transform: null }],
      });
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
      toast.success('Transform reset');
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  const [hiddenControls, setHiddenControls] = useState<Set<string>>(() => {
    try {
      const stored = localStorage.getItem('bee-transform-hidden');
      return stored ? new Set(JSON.parse(stored)) : new Set();
    } catch { return new Set(); }
  });
  const [configuring, setConfiguring] = useState(false);

  const toggleControl = (key: string) => {
    const next = new Set(hiddenControls);
    if (next.has(key)) next.delete(key); else next.add(key);
    setHiddenControls(next);
    localStorage.setItem('bee-transform-hidden', JSON.stringify([...next]));
  };

  const isVisible = (key: string) => !hiddenControls.has(key);

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <div className="text-[9px] text-gray-500 uppercase tracking-wider">Transform</div>
        <button
          onClick={() => setConfiguring(!configuring)}
          className="text-[8px] text-gray-600 hover:text-gray-400"
        >
          ⚙ Configure
        </button>
      </div>

      {configuring && (
        <div className="mb-2 p-1.5 bg-editor-bg rounded border border-editor-border">
          {['position', 'offsetX', 'offsetY', 'scale', 'rotation', 'opacity'].map(key => (
            <label key={key} className="flex items-center gap-1.5 text-[8px] text-gray-500 cursor-pointer">
              <input
                type="checkbox"
                checked={isVisible(key)}
                onChange={() => toggleControl(key)}
                className="w-3 h-3"
              />
              {key}
            </label>
          ))}
        </div>
      )}

      <div className="flex gap-3">
        {/* Position grid */}
        {isVisible('position') && (
          <div>
            <div className="text-[9px] text-gray-600 mb-1">Position</div>
            <div className="grid grid-cols-3 gap-0.5" style={{ width: 78 }}>
              {GRID_LABELS.map(p => (
                <button
                  key={p}
                  onClick={() => updateTransform({ position: p })}
                  className={`h-5 rounded text-[7px] font-mono ${
                    pos === p
                      ? 'bg-blue-600 border-blue-500 text-white'
                      : 'bg-editor-bg border-editor-border text-gray-600 hover:text-gray-400'
                  } border`}
                >
                  {GRID_SHORT[p]}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Sliders */}
        <div className="flex-1 space-y-1.5">
          {isVisible('offsetX') && (
            <SliderControl
              label="Offset X" value={x} min={-100} max={100} step={1}
              format={v => `${v > 0 ? '+' : ''}${v}%`}
              onChange={v => { setX(v); debouncedUpdate({ x: v }); }}
            />
          )}
          {isVisible('offsetY') && (
            <SliderControl
              label="Offset Y" value={y} min={-100} max={100} step={1}
              format={v => `${v > 0 ? '+' : ''}${v}%`}
              onChange={v => { setY(v); debouncedUpdate({ y: v }); }}
            />
          )}
          {isVisible('scale') && (
            <SliderControl
              label="Scale" value={scale} min={0.1} max={3} step={0.05}
              format={v => `${v.toFixed(2)}x`}
              onChange={v => { setScale(v); debouncedUpdate({ scale: v }); }}
            />
          )}
          {isVisible('rotation') && (
            <SliderControl
              label="Rotation" value={rotation} min={-180} max={180} step={1}
              format={v => `${v}°`}
              onChange={v => { setRotation(v); debouncedUpdate({ rotation: v }); }}
            />
          )}
          {isVisible('opacity') && (
            <SliderControl
              label="Opacity" value={opacity} min={0} max={1} step={0.05}
              format={v => `${Math.round(v * 100)}%`}
              onChange={v => { setOpacity(v); debouncedUpdate({ opacity: v }); }}
            />
          )}
        </div>
      </div>

      <div className="mt-2">
        <button
          onClick={handleReset}
          className="bg-editor-bg border border-editor-border text-gray-600 text-[8px] px-2 py-0.5 rounded hover:text-gray-400"
        >
          Reset All
        </button>
      </div>
    </div>
  );
}

function SliderControl({ label, value, min, max, step, format, onChange }: {
  label: string; value: number; min: number; max: number; step: number;
  format: (v: number) => string; onChange: (v: number) => void;
}) {
  return (
    <div>
      <div className="flex justify-between items-center">
        <span className="text-[8px] text-gray-600">{label}</span>
        <span className="text-[9px] text-gray-500 font-mono">{format(value)}</span>
      </div>
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        className="w-full"
      />
    </div>
  );
}
