import { useProjectStore } from '../stores/project';
import type { Segment } from '../types';

const VISUAL_TYPE_DOT: Record<string, string> = {
  FOOTAGE: 'bg-yellow-400',
  STOCK: 'bg-blue-400',
  PHOTO: 'bg-purple-400',
  MAP: 'bg-green-400',
  GRAPHIC: 'bg-pink-400',
  WAVEFORM: 'bg-emerald-400',
};

function SegmentRow({ segment }: { segment: Segment }) {
  const selectedSegmentId = useProjectStore(s => s.selectedSegmentId);
  const selectSegment = useProjectStore(s => s.selectSegment);
  const draggedMedia = useProjectStore(s => s.draggedMedia);
  const assignMedia = useProjectStore(s => s.assignMedia);

  const isSelected = selectedSegmentId === segment.id;
  const hasAssignments = Object.keys(segment.assigned_media).length > 0;
  const assignmentCount = Object.keys(segment.assigned_media).length;

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (draggedMedia) {
      // Auto-assign to first visual layer
      assignMedia(segment.id, 'visual', draggedMedia.path);
    }
  };

  return (
    <div
      onClick={() => selectSegment(isSelected ? null : segment.id)}
      onDragOver={e => e.preventDefault()}
      onDrop={handleDrop}
      className={`px-3 py-2 cursor-pointer border-l-2 transition-colors ${
        isSelected
          ? 'bg-editor-accent/10 border-editor-accent'
          : 'border-transparent hover:bg-editor-hover'
      }`}
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
      {/* Visual type dots */}
      <div className="flex gap-0.5 mt-1">
        {segment.visual.map((v, i) => (
          <span
            key={i}
            className={`w-1.5 h-1.5 rounded-full ${VISUAL_TYPE_DOT[v.content_type] || 'bg-gray-600'}`}
            title={v.content_type}
          />
        ))}
        {segment.audio.length > 0 && (
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 ml-0.5" title="Has audio" />
        )}
      </div>
    </div>
  );
}

export function SegmentList() {
  const storyboard = useProjectStore(s => s.storyboard);
  if (!storyboard) return null;

  // Group by section
  const groups: { section: string; segments: Segment[] }[] = [];
  let currentSection = '';
  for (const seg of storyboard.segments) {
    if (seg.section !== currentSection) {
      currentSection = seg.section;
      groups.push({ section: currentSection, segments: [] });
    }
    groups[groups.length - 1].segments.push(seg);
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-3 py-2 border-b border-editor-border flex items-center justify-between shrink-0">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Segments</h3>
        <span className="text-[10px] text-gray-600">{storyboard.total_segments}</span>
      </div>
      <div className="flex-1 overflow-y-auto">
        {groups.map(group => (
          <div key={group.section}>
            <div className="sticky top-0 z-10 bg-editor-surface/95 backdrop-blur-sm px-3 py-1.5 border-b border-editor-border">
              <div className="text-[10px] font-bold uppercase tracking-wider text-gray-500">
                {group.section}
              </div>
              <div className="text-[10px] text-gray-600">{group.segments.length} segments</div>
            </div>
            {group.segments.map(seg => (
              <SegmentRow key={seg.id} segment={seg} />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
