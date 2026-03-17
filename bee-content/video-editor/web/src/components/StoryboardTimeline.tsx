import { useState } from 'react';
import { useProjectStore } from '../stores/project';
import type { LayerEntry, LayerName, Segment } from '../types';

const VISUAL_TYPE_COLORS: Record<string, string> = {
  FOOTAGE: 'bg-yellow-600/20 text-yellow-400 border-yellow-600/40',
  STOCK: 'bg-blue-600/20 text-blue-400 border-blue-600/40',
  PHOTO: 'bg-purple-600/20 text-purple-400 border-purple-600/40',
  MAP: 'bg-green-600/20 text-green-400 border-green-600/40',
  GRAPHIC: 'bg-pink-600/20 text-pink-400 border-pink-600/40',
  WAVEFORM: 'bg-emerald-600/20 text-emerald-400 border-emerald-600/40',
  UNKNOWN: 'bg-gray-600/20 text-gray-400 border-gray-600/40',
};

const AUDIO_TYPE_COLORS: Record<string, string> = {
  NAR: 'bg-green-600/20 text-green-400 border-green-600/40',
  'REAL AUDIO': 'bg-yellow-600/20 text-yellow-400 border-yellow-600/40',
  MUSIC: 'bg-indigo-600/20 text-indigo-400 border-indigo-600/40',
  UNKNOWN: 'bg-gray-600/20 text-gray-400 border-gray-600/40',
};

const LAYER_COLORS: Record<string, string> = {
  visual: 'border-yellow-600/50 bg-yellow-600/5',
  audio: 'border-green-600/50 bg-green-600/5',
  overlay: 'border-purple-600/50 bg-purple-600/5',
  music: 'border-indigo-600/50 bg-indigo-600/5',
  source: 'border-gray-600/50 bg-gray-600/5',
  transition: 'border-orange-600/50 bg-orange-600/5',
};

const LAYER_ICONS: Record<string, string> = {
  visual: '🎬',
  audio: '🔊',
  overlay: '🏷️',
  music: '🎵',
  source: '📁',
  transition: '✂️',
};

function LayerTrack({
  layerName,
  entries,
  segment,
  colorMap,
}: {
  layerName: LayerName;
  entries: LayerEntry[];
  segment: Segment;
  colorMap: Record<string, string>;
}) {
  const draggedMedia = useProjectStore(s => s.draggedMedia);
  const assignMedia = useProjectStore(s => s.assignMedia);
  const [dropping, setDropping] = useState(false);

  if (entries.length === 0) return null;

  const assignmentKey = `${layerName}:0`;
  const assigned = segment.assigned_media[assignmentKey];
  const trackColor = LAYER_COLORS[layerName] || LAYER_COLORS.source;

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDropping(false);
    if (draggedMedia) {
      assignMedia(segment.id, layerName, draggedMedia.path);
    }
  };

  return (
    <div
      className={`border rounded px-3 py-2 transition-colors ${trackColor} ${
        dropping ? 'ring-1 ring-editor-accent' : ''
      }`}
      onDragOver={e => { e.preventDefault(); setDropping(true); }}
      onDragLeave={() => setDropping(false)}
      onDrop={handleDrop}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-xs">{LAYER_ICONS[layerName]}</span>
        <span className="text-[10px] uppercase tracking-wider text-gray-500 font-bold">
          {layerName}
        </span>
        {assigned && (
          <span className="text-[10px] bg-editor-accent/20 text-blue-400 px-1.5 rounded ml-auto truncate max-w-[200px]">
            {assigned.split('/').pop()}
          </span>
        )}
      </div>
      <div className="space-y-1">
        {entries.map((entry, i) => {
          const colors = colorMap[entry.content_type] || colorMap.UNKNOWN || 'bg-gray-600/20 text-gray-400 border-gray-600/40';
          return (
            <div key={i} className="flex items-start gap-2">
              <span className={`text-[10px] px-1.5 py-0.5 rounded border shrink-0 ${colors}`}>
                {entry.content_type}
              </span>
              {entry.time_start && (
                <span className="text-[10px] text-gray-600 shrink-0 font-mono">
                  {entry.time_start}-{entry.time_end}
                </span>
              )}
              <span className="text-xs text-gray-400 leading-relaxed">
                {entry.content || entry.raw}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function StoryboardTimeline() {
  const storyboard = useProjectStore(s => s.storyboard);
  const selectedSegmentIds = useProjectStore(s => s.selectedSegmentIds);

  if (!storyboard) return null;

  const segment = storyboard.segments.find(s => s.id === selectedSegmentIds[0]);

  if (!segment) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-2xl mb-2 opacity-30">🎬</div>
          <div className="text-xs text-gray-600">
            Select a segment from the left panel to see its layers and assign media.
          </div>
        </div>
      </div>
    );
  }

  const layers: { name: LayerName; entries: LayerEntry[]; colorMap: Record<string, string> }[] = [
    { name: 'visual', entries: segment.visual, colorMap: VISUAL_TYPE_COLORS },
    { name: 'audio', entries: segment.audio, colorMap: AUDIO_TYPE_COLORS },
    { name: 'overlay', entries: segment.overlay, colorMap: VISUAL_TYPE_COLORS },
    { name: 'music', entries: segment.music, colorMap: AUDIO_TYPE_COLORS },
    { name: 'source', entries: segment.source, colorMap: VISUAL_TYPE_COLORS },
    { name: 'transition', entries: segment.transition, colorMap: VISUAL_TYPE_COLORS },
  ];

  const activeLayers = layers.filter(l => l.entries.length > 0);

  return (
    <div className="p-4">
      {/* Segment header */}
      <div className="flex items-center gap-3 mb-4">
        <span className="text-xs font-mono text-gray-500">{segment.start} - {segment.end}</span>
        <span className="text-sm font-medium text-gray-200">{segment.title}</span>
        {segment.subsection && segment.subsection !== segment.title && (
          <span className="text-xs text-gray-600">{segment.subsection}</span>
        )}
        <span className="text-[10px] text-gray-600 ml-auto">{segment.duration_seconds}s</span>
      </div>

      {/* Layer tracks */}
      <div className="space-y-2">
        {activeLayers.map(layer => (
          <LayerTrack
            key={layer.name}
            layerName={layer.name}
            entries={layer.entries}
            segment={segment}
            colorMap={layer.colorMap}
          />
        ))}
      </div>

      {activeLayers.length === 0 && (
        <div className="text-xs text-gray-600 text-center py-4">
          No layer data for this segment.
        </div>
      )}
    </div>
  );
}
