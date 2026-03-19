import { useCallback } from 'react';
import { useProjectStore } from '../stores/project';

const PRESET_COLORS: Record<string, string> = {
  dark_crime: '#1a1a2e',
  surveillance: '#2d5016',
  noir: '#333333',
  bodycam: '#3d3520',
  cold_blue: '#1a2a3a',
  warm_victim: '#4a3020',
  sepia: '#704214',
  vintage: '#5a4a3a',
  bleach_bypass: '#555555',
  night_vision: '#003300',
  golden_hour: '#6a4a00',
  vhs: '#4a2a4a',
};

interface Props {
  segmentId: string;
  visualIndex: number;
  currentColor: string | null;
  presets: string[];
}

export function ColorGradePicker({ segmentId, visualIndex, currentColor, presets }: Props) {
  const updateSegmentConfig = useProjectStore(s => s.updateSegmentConfig);

  const handleSelect = useCallback((preset: string | null) => {
    updateSegmentConfig(segmentId, {
      visual_updates: [{ index: visualIndex, color: preset }],
    });
  }, [segmentId, visualIndex, updateSegmentConfig]);

  return (
    <div className="flex items-center gap-1.5 py-1">
      <span className="text-[10px] text-gray-500 w-14 shrink-0">Color</span>
      {/* None swatch */}
      <button
        className={`w-4 h-4 rounded border-2 transition-colors ${
          currentColor === null
            ? 'border-editor-accent'
            : 'border-editor-border hover:border-gray-500'
        }`}
        style={{ background: 'linear-gradient(135deg, #222 45%, #f44 50%, #222 55%)' }}
        title="None"
        onClick={e => { e.stopPropagation(); handleSelect(null); }}
      />
      {presets.map(preset => (
        <button
          key={preset}
          className={`w-4 h-4 rounded border-2 transition-colors ${
            currentColor === preset
              ? 'border-editor-accent ring-1 ring-editor-accent/50'
              : 'border-editor-border hover:border-gray-500'
          }`}
          style={{ backgroundColor: PRESET_COLORS[preset] || '#444' }}
          title={preset}
          onClick={e => { e.stopPropagation(); handleSelect(preset); }}
        />
      ))}
    </div>
  );
}
