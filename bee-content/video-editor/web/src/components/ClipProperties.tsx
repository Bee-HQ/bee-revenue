import { useState, useEffect, useRef } from 'react';
import { useProjectStore } from '../stores/project';
import { api } from '../api/client';
import { toast } from '../stores/toast';
import { formatSeconds } from '../adapters/time-utils';
import { Check } from 'lucide-react';

const COLOR_PRESETS = [
  'dark_crime', 'surveillance', 'noir', 'bodycam', 'cold_blue',
  'warm_victim', 'sepia', 'vintage', 'bleach_bypass', 'night_vision',
  'golden_hour', 'vhs',
];

const PRESET_COLORS: Record<string, string> = {
  dark_crime: '#1a1a2e', surveillance: '#2d5016', noir: '#333',
  bodycam: '#3d3520', cold_blue: '#1a2a3a', warm_victim: '#4a3020',
  sepia: '#704214', vintage: '#5a4a3a', bleach_bypass: '#555',
  night_vision: '#003300', golden_hour: '#6a4a00', vhs: '#4a2a4a',
};

const TRANSITIONS = [
  'none', 'fade', 'dissolve', 'wipeleft', 'wiperight', 'wipeup', 'wipedown',
  'slideleft', 'slideright', 'circlecrop', 'rectcrop', 'fadeblack', 'fadewhite',
];

export function ClipProperties() {
  const activeClipId = useProjectStore(s => s.activeClipId);
  const project = useProjectStore(s => s.project);
  const effects = useProjectStore(s => s.effects);

  useEffect(() => {
    if (!effects) useProjectStore.getState().loadEffects();
  }, [effects]);

  if (!activeClipId || !project) {
    return (
      <div className="p-3 text-center text-[10px] text-gray-600">
        Select a clip on the timeline
      </div>
    );
  }

  // Parse clip ID: "{segmentId}-{type}-{index}" from timeline-adapter.ts
  const parts = activeClipId.match(/^(.+)-(v|nar|audio|music|ov)-(\d+|empty)$/);
  if (!parts) {
    return (
      <div className="p-3 text-center text-[10px] text-gray-600">
        Unknown clip: {activeClipId}
      </div>
    );
  }

  const segmentId = parts[1];
  const clipType = parts[2];
  const layerIndex = parts[3] === 'empty' ? -1 : parseInt(parts[3]);

  const segment = project.segments.find(s => s.id === segmentId);
  if (!segment) {
    return (
      <div className="p-3 text-center text-[10px] text-gray-600">
        Segment not found
      </div>
    );
  }

  return (
    <div className="border-t border-editor-border overflow-y-auto flex-1">
      <div className="px-3 py-2 bg-editor-surface border-b border-editor-border">
        <div className="text-[10px] font-bold text-gray-300">{segment.title}</div>
        <div className="text-[9px] text-gray-500">
          {formatSeconds(segment.start)} -- {formatSeconds(segment.start + segment.duration)} | {segment.duration}s
        </div>
      </div>

      <div className="p-3 space-y-3">
        {clipType === 'v' && layerIndex >= 0 && (
          <ColorGradeSection segmentId={segmentId} visualIndex={layerIndex} segment={segment} />
        )}

        {clipType === 'v' && layerIndex >= 0 && (
          <KenBurnsSection segmentId={segmentId} visualIndex={layerIndex} segment={segment} />
        )}

        {clipType === 'v' && layerIndex >= 0 && (
          <TrimSection segmentId={segmentId} visualIndex={layerIndex} segment={segment} />
        )}

        {(clipType === 'audio' || clipType === 'music' || clipType === 'nar') && (
          <VolumeSection segmentId={segmentId} clipType={clipType} layerIndex={layerIndex} segment={segment} />
        )}

        {clipType === 'v' && (
          <TransitionSection segmentId={segmentId} segment={segment} />
        )}
      </div>
    </div>
  );
}

// --- Sub-components ---

function ColorGradeSection({ segmentId, visualIndex, segment }: {
  segmentId: string; visualIndex: number; segment: any;
}) {
  const visual = segment.visual[visualIndex];
  const currentColor = visual?.color || null;

  const handleSelect = async (preset: string | null) => {
    try {
      await api.updateSegment(segmentId, {
        visual_updates: [{ index: visualIndex, color: preset }],
      });
      toast.success(preset ? `Color: ${preset}` : 'Color cleared');
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  return (
    <div>
      <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1.5">Color Grade</div>
      <div className="grid grid-cols-4 gap-1.5">
        <button
          onClick={() => handleSelect(null)}
          className={`flex flex-col items-center gap-0.5 rounded p-0.5 ${!currentColor ? 'ring-1 ring-blue-500' : ''}`}
          title="None"
        >
          <div className="w-7 h-7 rounded border border-editor-border flex items-center justify-center"
               style={{ background: 'linear-gradient(135deg, #888 50%, #aaa 50%)' }}>
            {!currentColor && <Check size={10} className="text-white drop-shadow" />}
          </div>
          <span className="text-[7px] text-gray-500 truncate w-full text-center">none</span>
        </button>
        {COLOR_PRESETS.map(p => (
          <button
            key={p}
            onClick={() => handleSelect(p)}
            className={`flex flex-col items-center gap-0.5 rounded p-0.5 ${currentColor === p ? 'ring-1 ring-blue-500' : ''}`}
            title={p}
          >
            <div className={`w-7 h-7 rounded border flex items-center justify-center ${currentColor === p ? 'border-blue-500' : 'border-editor-border'}`}
                 style={{ backgroundColor: PRESET_COLORS[p] }}>
              {currentColor === p && <Check size={10} className="text-white drop-shadow" />}
            </div>
            <span className="text-[7px] text-gray-500 truncate w-full text-center">{p.replace(/_/g, ' ')}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

const KEN_BURNS_EFFECTS = ['none', 'zoom_in', 'zoom_out', 'pan_left', 'pan_right', 'pan_up', 'pan_down', 'zoom_in_pan_right'];

function KenBurnsSection({ segmentId, visualIndex, segment }: {
  segmentId: string; visualIndex: number; segment: any;
}) {
  const visual = segment.visual[visualIndex];
  const currentEffect = visual?.kenBurns || 'none';

  const handleSelect = async (effect: string) => {
    try {
      await api.updateSegment(segmentId, {
        visual_updates: [{ index: visualIndex, ken_burns: effect === 'none' ? null : effect }],
      });
      toast.success(effect === 'none' ? 'Ken Burns cleared' : `Ken Burns: ${effect}`);
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  return (
    <div>
      <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Ken Burns</div>
      <select
        value={currentEffect}
        onChange={e => handleSelect(e.target.value)}
        className="w-full bg-editor-bg border border-editor-border rounded px-2 py-1 text-[10px] text-gray-300"
      >
        {KEN_BURNS_EFFECTS.map(e => <option key={e} value={e}>{e.replace(/_/g, ' ')}</option>)}
      </select>
    </div>
  );
}

function TrimSection({ segmentId, visualIndex, segment }: {
  segmentId: string; visualIndex: number; segment: any;
}) {
  const visual = segment.visual[visualIndex];
  const [trimIn, setTrimIn] = useState<string>(visual?.trim?.[0] != null ? String(visual.trim[0]) : '');
  const [trimOut, setTrimOut] = useState<string>(visual?.trim?.[1] != null ? String(visual.trim[1]) : '');

  // Sync local state when segment data changes
  useEffect(() => {
    setTrimIn(visual?.trim?.[0] != null ? String(visual.trim[0]) : '');
    setTrimOut(visual?.trim?.[1] != null ? String(visual.trim[1]) : '');
  }, [visual?.trim?.[0], visual?.trim?.[1]]);

  const handleBlur = async () => {
    try {
      const inSec = trimIn !== '' ? parseFloat(trimIn) : null;
      const outSec = trimOut !== '' ? parseFloat(trimOut) : null;
      const trim = inSec != null || outSec != null ? [inSec ?? 0, outSec ?? 0] : null;
      await api.updateSegment(segmentId, {
        visual_updates: [{ index: visualIndex, trim }],
      });
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  return (
    <div>
      <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Trim Points (seconds)</div>
      <div className="flex items-center gap-2">
        <label className="text-[9px] text-gray-500">In</label>
        <input
          type="number" value={trimIn} placeholder="0"
          onChange={e => setTrimIn(e.target.value)}
          onBlur={handleBlur}
          className="flex-1 bg-editor-bg border border-editor-border rounded px-1.5 py-0.5 text-[10px] font-mono text-gray-300 focus:border-editor-accent outline-none"
        />
        <label className="text-[9px] text-gray-500">Out</label>
        <input
          type="number" value={trimOut} placeholder="end"
          onChange={e => setTrimOut(e.target.value)}
          onBlur={handleBlur}
          className="flex-1 bg-editor-bg border border-editor-border rounded px-1.5 py-0.5 text-[10px] font-mono text-gray-300 focus:border-editor-accent outline-none"
        />
      </div>
    </div>
  );
}

function VolumeSection({ segmentId, clipType, layerIndex, segment }: {
  segmentId: string; clipType: string; layerIndex: number; segment: any;
}) {
  const isMusic = clipType === 'music';
  const isNar = clipType === 'nar';

  // layerIndex is the original array index (from timeline-adapter)
  let entry: any = null;
  if (isNar || clipType === 'audio') {
    entry = layerIndex >= 0 ? segment.audio[layerIndex] : null;
  } else if (isMusic) {
    entry = layerIndex >= 0 ? segment.music[layerIndex] : null;
  }

  const currentVolume = entry?.volume ?? 1.0;
  const currentFadeIn = (entry as any)?.fade_in ?? 0;
  const currentFadeOut = (entry as any)?.fade_out ?? 0;

  const [volume, setVolume] = useState(currentVolume);
  const [fadeIn, setFadeIn] = useState(currentFadeIn);
  const [fadeOut, setFadeOut] = useState(currentFadeOut);
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync local state when segment changes
  useEffect(() => {
    setVolume(currentVolume);
    setFadeIn(currentFadeIn);
    setFadeOut(currentFadeOut);
  }, [currentVolume, currentFadeIn, currentFadeOut]);

  useEffect(() => {
    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, []);

  const handleVolumeChange = (val: number) => {
    setVolume(val);
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(async () => {
      try {
        await api.updateSegment(segmentId, {
          audio_updates: [{ index: layerIndex, volume: val }],
        });
        const sb = await api.getCurrentProject();
        useProjectStore.setState({ project: sb });
      } catch (e: any) {
        toast.error(e.message);
      }
    }, 500);
  };

  const handleFadeChange = async (field: 'fade_in' | 'fade_out', val: number) => {
    if (field === 'fade_in') setFadeIn(val);
    else setFadeOut(val);
    try {
      await api.updateSegment(segmentId, {
        audio_updates: [{ index: layerIndex, [field]: val }],
      });
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  if (isNar) {
    return (
      <div>
        <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Narration</div>
        <div className="text-[10px] text-gray-400 italic leading-relaxed max-h-16 overflow-y-auto">
          {segment.audio.find((a: any) => a.type === 'NAR')?.text || 'No narration text'}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Volume</div>
      <div className="flex items-center gap-2">
        <input
          type="range" min="0" max="1" step="0.05" value={volume}
          onChange={e => handleVolumeChange(parseFloat(e.target.value))}
          className="flex-1"
        />
        <span className="text-[10px] font-mono text-gray-400 w-8">{volume.toFixed(2)}</span>
      </div>
      {isMusic && (
        <div className="flex items-center gap-2 mt-1">
          <label className="text-[9px] text-gray-500">Fade in</label>
          <input
            type="number" value={fadeIn} step={0.5} min={0}
            onChange={e => handleFadeChange('fade_in', parseFloat(e.target.value) || 0)}
            className="w-12 bg-editor-bg border border-editor-border rounded px-1 py-0.5 text-[10px] text-gray-300 text-center"
          />
          <label className="text-[9px] text-gray-500">out</label>
          <input
            type="number" value={fadeOut} step={0.5} min={0}
            onChange={e => handleFadeChange('fade_out', parseFloat(e.target.value) || 0)}
            className="w-12 bg-editor-bg border border-editor-border rounded px-1 py-0.5 text-[10px] text-gray-300 text-center"
          />
          <span className="text-[9px] text-gray-600">s</span>
        </div>
      )}
    </div>
  );
}

function TransitionSection({ segmentId, segment }: { segmentId: string; segment: any }) {
  const trans = segment.transition;
  const currentType = trans?.type?.toLowerCase() || 'none';
  const currentDuration = trans?.duration ?? 1.0;

  const [type, setType] = useState(currentType);
  const [duration, setDuration] = useState(currentDuration);

  useEffect(() => {
    setType(currentType);
    setDuration(currentDuration);
  }, [currentType, currentDuration]);

  const handleChange = async (newType: string, newDuration: number) => {
    setType(newType);
    setDuration(newDuration);
    try {
      await api.updateSegment(segmentId, {
        transition_in: newType === 'none' ? null : { type: newType, duration: newDuration },
      });
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  return (
    <div>
      <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Transition</div>
      <div className="flex items-center gap-2">
        <select
          value={type}
          onChange={e => handleChange(e.target.value, duration)}
          className="flex-1 bg-editor-bg border border-editor-border rounded px-1.5 py-0.5 text-[10px] text-gray-300"
        >
          {TRANSITIONS.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        {type !== 'none' && (
          <>
            <input
              type="range" min="0.5" max="3" step="0.1" value={duration}
              onChange={e => handleChange(type, parseFloat(e.target.value))}
              className="w-16"
            />
            <span className="text-[10px] text-gray-400 w-8">{duration.toFixed(1)}s</span>
          </>
        )}
      </div>
    </div>
  );
}
