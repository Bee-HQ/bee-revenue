import { useState } from 'react';
import type { LayerEntry, LayerName, Segment } from '../types';
import { useProjectStore } from '../stores/project';

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

const LAYER_ICONS: Record<LayerName, string> = {
  visual: '🎬',
  audio: '🔊',
  overlay: '🏷️',
  music: '🎵',
  source: '📁',
  transition: '✂️',
};

interface Props {
  segment: Segment;
}

export function SegmentCard({ segment }: Props) {
  const [expanded, setExpanded] = useState(false);
  const selectedSegmentId = useProjectStore(s => s.selectedSegmentId);
  const selectSegment = useProjectStore(s => s.selectSegment);
  const draggedMedia = useProjectStore(s => s.draggedMedia);
  const assignMedia = useProjectStore(s => s.assignMedia);
  const [dropTarget, setDropTarget] = useState<string | null>(null);

  const isSelected = selectedSegmentId === segment.id;
  const hasAssignments = Object.keys(segment.assigned_media).length > 0;

  const handleClick = () => {
    selectSegment(isSelected ? null : segment.id);
  };

  const handleDragOver = (e: React.DragEvent, layer: string) => {
    e.preventDefault();
    setDropTarget(layer);
  };

  const handleDragLeave = () => {
    setDropTarget(null);
  };

  const handleDrop = (e: React.DragEvent, layer: string) => {
    e.preventDefault();
    setDropTarget(null);
    if (draggedMedia) {
      assignMedia(segment.id, layer, draggedMedia.path);
    }
  };

  const renderLayerEntries = (
    entries: LayerEntry[],
    layerName: LayerName,
    colorMap: Record<string, string>,
  ) => {
    if (entries.length === 0) return null;
    const icon = LAYER_ICONS[layerName];
    const assignmentKey = `${layerName}:0`;
    const assigned = segment.assigned_media[assignmentKey];
    const isDropping = dropTarget === layerName;

    return (
      <div
        className={`border-l-2 pl-3 py-1 transition-colors ${
          isDropping ? 'border-editor-accent bg-editor-accent/5' : 'border-editor-border'
        }`}
        onDragOver={e => handleDragOver(e, layerName)}
        onDragLeave={handleDragLeave}
        onDrop={e => handleDrop(e, layerName)}
      >
        <div className="flex items-center gap-1.5 mb-1">
          <span className="text-xs">{icon}</span>
          <span className="text-[10px] uppercase tracking-wider text-gray-500 font-medium">
            {layerName}
          </span>
          {assigned && (
            <span className="text-[10px] bg-editor-accent/20 text-blue-400 px-1.5 rounded ml-auto">
              {assigned.split('/').pop()}
            </span>
          )}
        </div>
        {entries.map((entry, i) => {
          const colors = colorMap[entry.content_type] || colorMap.UNKNOWN;
          return (
            <div key={i} className="flex items-start gap-2 mb-1">
              <span className={`text-[10px] px-1.5 py-0.5 rounded border shrink-0 ${colors}`}>
                {entry.content_type}
              </span>
              {entry.time_start && (
                <span className="text-[10px] text-gray-600 shrink-0">
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
    );
  };

  return (
    <div
      className={`bg-editor-surface rounded-lg border transition-all cursor-pointer ${
        isSelected
          ? 'border-editor-accent ring-1 ring-editor-accent/30'
          : 'border-editor-border hover:border-editor-hover'
      }`}
      onClick={handleClick}
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-3 py-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xs font-mono text-gray-500 shrink-0">
            {segment.start}-{segment.end}
          </span>
          <span className="text-xs font-medium text-gray-200 truncate">
            {segment.title}
          </span>
          {segment.subsection && segment.subsection !== segment.title && (
            <span className="text-[10px] text-gray-600 truncate">
              {segment.subsection}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 ml-auto shrink-0">
          <span className="text-[10px] text-gray-600">{segment.duration_seconds}s</span>
          {hasAssignments && (
            <span className="w-1.5 h-1.5 bg-editor-accent rounded-full" title="Has media assigned" />
          )}
          <button
            className="text-gray-600 hover:text-gray-400 text-xs"
            onClick={e => { e.stopPropagation(); setExpanded(!expanded); }}
          >
            {expanded ? '▼' : '▶'}
          </button>
        </div>
      </div>

      {/* Quick preview of visual types */}
      {!expanded && segment.visual.length > 0 && (
        <div className="px-3 pb-2 flex gap-1 flex-wrap">
          {segment.visual.map((v, i) => {
            const colors = VISUAL_TYPE_COLORS[v.content_type] || VISUAL_TYPE_COLORS.UNKNOWN;
            return (
              <span key={i} className={`text-[10px] px-1.5 py-0.5 rounded border ${colors}`}>
                {v.content_type}
              </span>
            );
          })}
          {segment.audio.map((a, i) => {
            const colors = AUDIO_TYPE_COLORS[a.content_type] || AUDIO_TYPE_COLORS.UNKNOWN;
            return (
              <span key={`a${i}`} className={`text-[10px] px-1.5 py-0.5 rounded border ${colors}`}>
                {a.content_type}
              </span>
            );
          })}
        </div>
      )}

      {/* Expanded layer details */}
      {expanded && (
        <div className="px-3 pb-3 space-y-2">
          {renderLayerEntries(segment.visual, 'visual', VISUAL_TYPE_COLORS)}
          {renderLayerEntries(segment.audio, 'audio', AUDIO_TYPE_COLORS)}
          {renderLayerEntries(segment.overlay, 'overlay', VISUAL_TYPE_COLORS)}
          {renderLayerEntries(segment.music, 'music', AUDIO_TYPE_COLORS)}
          {renderLayerEntries(segment.source, 'source', VISUAL_TYPE_COLORS)}
          {renderLayerEntries(segment.transition, 'transition', VISUAL_TYPE_COLORS)}
        </div>
      )}
    </div>
  );
}
