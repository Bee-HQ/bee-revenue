import { useState } from 'react';
import { useProjectStore } from '../stores/project';
import type { Segment } from '../types';
import { SkeletonList } from './SkeletonCard';
import { parseTimecode, timeToMs } from '../adapters/time-utils';
import { ChevronRight, ChevronDown } from 'lucide-react';

const VISUAL_TYPE_DOT: Record<string, string> = {
  FOOTAGE: 'bg-yellow-400',
  STOCK: 'bg-blue-400',
  PHOTO: 'bg-purple-400',
  MAP: 'bg-green-400',
  GRAPHIC: 'bg-pink-400',
  WAVEFORM: 'bg-emerald-400',
};

interface SegmentRowProps {
  segment: Segment;
  index: number;
  onDragStart: (index: number) => void;
  onDragOver: (e: React.DragEvent, index: number) => void;
  onDrop: (e: React.DragEvent, index: number) => void;
  onDragEnd: () => void;
  isDragging: boolean;
  isDropTarget: boolean;
}

function SegmentRow({
  segment,
  index,
  onDragStart,
  onDragOver,
  onDrop,
  onDragEnd,
  isDragging,
  isDropTarget,
}: SegmentRowProps) {
  const selectedSegmentIds = useProjectStore(s => s.selectedSegmentIds);
  const toggleSegmentSelection = useProjectStore(s => s.toggleSegmentSelection);

  const isSelected = selectedSegmentIds.includes(segment.id);
  const hasAssignments = Object.keys(segment.assigned_media).length > 0;
  const assignmentCount = Object.keys(segment.assigned_media).length;

  const handleClick = (e: React.MouseEvent) => {
    toggleSegmentSelection(segment.id, e.shiftKey);

    // Seek Remotion player to segment start via store — RemotionPreview handles the actual seekTo
    const startSeconds = parseTimecode(segment.start);
    const ms = timeToMs(startSeconds);
    useProjectStore.getState().setCurrentTimeMs(ms);
  };

  return (
    <div
      draggable
      onDragStart={e => {
        e.dataTransfer.effectAllowed = 'move';
        onDragStart(index);
      }}
      onDragOver={e => { e.preventDefault(); onDragOver(e, index); }}
      onDrop={e => onDrop(e, index)}
      onDragEnd={onDragEnd}
      onClick={handleClick}
      className={`px-3 py-2 cursor-pointer border-l-2 transition-colors select-none ${
        isDragging
          ? 'opacity-50'
          : isSelected
          ? 'bg-editor-accent/10 border-editor-accent'
          : 'border-transparent hover:bg-editor-hover'
      } ${isDropTarget ? 'border-t-2 border-t-blue-400' : ''}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-mono text-gray-500">
          {segment.start}-{segment.end}
        </span>
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-gray-600">{segment.duration_seconds}s</span>
          {hasAssignments && (
            <span className="text-[10px] bg-editor-accent/20 text-blue-400 px-1 rounded">
              {assignmentCount}
            </span>
          )}
        </div>
      </div>
      <div className="text-xs text-gray-300 truncate mt-0.5">{segment.title}</div>
      {segment.subsection && segment.subsection !== segment.title && (
        <div className="text-[10px] text-gray-600 truncate">{segment.subsection}</div>
      )}
      {/* Visual type dots + completeness */}
      <div className="flex items-center gap-1 mt-1">
        <div className="flex gap-0.5">
          {segment.visual.map((v, i) => (
            <span
              key={i}
              className={`w-2 h-2 rounded-full ${VISUAL_TYPE_DOT[v.content_type] || 'bg-gray-600'}`}
              title={v.content_type}
            />
          ))}
          {segment.audio.length > 0 && (
            <span className="w-2 h-2 rounded-full bg-green-400 ml-0.5" title="Has audio" />
          )}
        </div>
        {/* Completeness bar */}
        {(() => {
          const totalLayers = segment.visual.length + segment.audio.length + (segment.overlay?.length || 0);
          const assignedLayers = Object.keys(segment.assigned_media).length;
          const pct = totalLayers > 0 ? Math.round((assignedLayers / totalLayers) * 100) : 0;
          return totalLayers > 0 ? (
            <div className="flex-1 h-0.5 bg-editor-border rounded-full overflow-hidden" title={`${assignedLayers}/${totalLayers} layers assigned`}>
              <div className={`h-full rounded-full transition-all ${pct === 100 ? 'bg-green-500' : pct > 0 ? 'bg-blue-500' : ''}`} style={{ width: `${pct}%` }} />
            </div>
          ) : null;
        })()}
      </div>
    </div>
  );
}

export function SegmentList() {
  const storyboard = useProjectStore(s => s.storyboard);
  const loading = useProjectStore(s => s.loading);
  const reorderSegments = useProjectStore(s => s.reorderSegments);
  const selectedSegmentIds = useProjectStore(s => s.selectedSegmentIds);

  const [dragFromIndex, setDragFromIndex] = useState<number | null>(null);
  const [dropTargetIndex, setDropTargetIndex] = useState<number | null>(null);

  if (!storyboard) {
    return (
      <div className="flex flex-col h-full">
        <div className="px-3 py-2 border-b border-editor-border flex items-center justify-between shrink-0">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Segments</h3>
        </div>
        {loading ? <SkeletonList count={5} /> : null}
      </div>
    );
  }

  const segments = storyboard.segments;

  const handleDragStart = (index: number) => {
    setDragFromIndex(index);
    setDropTargetIndex(null);
  };

  const handleDragOver = (_e: React.DragEvent, index: number) => {
    if (dragFromIndex === null) return;
    setDropTargetIndex(index);
  };

  const handleDrop = (_e: React.DragEvent, toIndex: number) => {
    if (dragFromIndex === null) return;
    if (dragFromIndex !== toIndex) {
      reorderSegments(dragFromIndex, toIndex);
    }
    setDragFromIndex(null);
    setDropTargetIndex(null);
  };

  const handleDragEnd = () => {
    setDragFromIndex(null);
    setDropTargetIndex(null);
  };

  // Group by section for display
  const groups: { section: string; segments: { seg: Segment; globalIndex: number }[] }[] = [];
  let currentSection = '';
  segments.forEach((seg, globalIndex) => {
    if (seg.section !== currentSection) {
      currentSection = seg.section;
      groups.push({ section: currentSection, segments: [] });
    }
    groups[groups.length - 1].segments.push({ seg, globalIndex });
  });

  const selectionCount = selectedSegmentIds.length;

  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(
    () => new Set()
  );

  const toggleSection = (section: string) => {
    setCollapsedSections(prev => {
      const next = new Set(prev);
      if (next.has(section)) next.delete(section);
      else next.add(section);
      return next;
    });
  };

  return (
    <div className="flex flex-col h-full">
      <div className="px-3 py-2 border-b border-editor-border flex items-center justify-between shrink-0">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Segments</h3>
        <div className="flex items-center gap-2">
          {selectionCount > 1 && (
            <span className="text-[10px] bg-editor-accent/20 text-blue-400 px-1.5 rounded">
              {selectionCount} selected
            </span>
          )}
          <span className="text-[10px] text-gray-600">{storyboard.total_segments}</span>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        {groups.map(group => {
          const isCollapsed = collapsedSections.has(group.section);
          return (
            <div key={group.section}>
              <div
                className="sticky top-0 z-10 bg-editor-surface/95 backdrop-blur-sm px-3 py-1.5 border-b border-editor-border cursor-pointer hover:bg-editor-hover/50"
                onClick={() => toggleSection(group.section)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-gray-500">
                    {isCollapsed ? <ChevronRight size={12} className="text-gray-600 shrink-0" /> : <ChevronDown size={12} className="text-gray-600 shrink-0" />}
                    <span className="truncate">{group.section}</span>
                  </div>
                  <div className="text-[10px] text-gray-600">{group.segments.length}</div>
                </div>
              </div>
              {!isCollapsed && group.segments.map(({ seg, globalIndex }) => (
                <SegmentRow
                  key={seg.id}
                  segment={seg}
                  index={globalIndex}
                  onDragStart={handleDragStart}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  onDragEnd={handleDragEnd}
                  isDragging={dragFromIndex === globalIndex}
                  isDropTarget={dropTargetIndex === globalIndex && dragFromIndex !== globalIndex}
                />
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}
