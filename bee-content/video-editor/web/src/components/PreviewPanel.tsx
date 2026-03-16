import { useProjectStore } from '../stores/project';
import { api } from '../api/client';
import type { LayerEntry } from '../types';

export function PreviewPanel() {
  const selectedSegmentId = useProjectStore(s => s.selectedSegmentId);
  const storyboard = useProjectStore(s => s.storyboard);

  const segment = storyboard?.segments.find(s => s.id === selectedSegmentId);

  if (!segment) {
    return (
      <div className="flex flex-col h-full">
        <div className="px-3 py-2 border-b border-editor-border">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Preview</h3>
        </div>
        <div className="flex-1 flex items-center justify-center text-xs text-gray-600 px-4 text-center">
          Select a segment to preview its details and assigned media.
        </div>
      </div>
    );
  }

  const assignedFiles = Object.entries(segment.assigned_media);

  return (
    <div className="flex flex-col h-full">
      <div className="px-3 py-2 border-b border-editor-border">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Preview</h3>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Segment info */}
        <div className="px-3 py-3 border-b border-editor-border">
          <div className="text-sm font-medium text-gray-200">{segment.title}</div>
          <div className="text-xs text-gray-500 mt-0.5">
            {segment.start} - {segment.end} ({segment.duration_seconds}s)
          </div>
          {segment.subsection && (
            <div className="text-xs text-gray-600 mt-0.5">{segment.subsection}</div>
          )}
        </div>

        {/* Assigned media preview */}
        {assignedFiles.length > 0 && (
          <div className="px-3 py-3 border-b border-editor-border">
            <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">
              Assigned Media
            </div>
            {assignedFiles.map(([key, path]) => {
              const ext = path.split('.').pop()?.toLowerCase() || '';
              const isVideo = ['mp4', 'mkv', 'webm', 'mov'].includes(ext);
              const isAudio = ['mp3', 'wav', 'm4a'].includes(ext);
              const isImage = ['png', 'jpg', 'jpeg', 'webp'].includes(ext);
              const mediaUrl = api.mediaFileUrl(path);

              return (
                <div key={key} className="mb-2">
                  <div className="text-[10px] text-gray-600 mb-1">{key}</div>
                  {isVideo && (
                    <video
                      src={mediaUrl}
                      controls
                      className="w-full rounded bg-black"
                      style={{ maxHeight: '180px' }}
                    />
                  )}
                  {isAudio && (
                    <audio src={mediaUrl} controls className="w-full" />
                  )}
                  {isImage && (
                    <img src={mediaUrl} alt="" className="w-full rounded" />
                  )}
                  <div className="text-[10px] text-gray-600 truncate mt-0.5">
                    {path.split('/').pop()}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Layer details */}
        <div className="px-3 py-3 space-y-3">
          <LayerSection title="Visual" entries={segment.visual} />
          <LayerSection title="Audio" entries={segment.audio} />
          <LayerSection title="Overlay" entries={segment.overlay} />
          <LayerSection title="Music" entries={segment.music} />
          <LayerSection title="Source" entries={segment.source} />
          <LayerSection title="Transition" entries={segment.transition} />
        </div>
      </div>
    </div>
  );
}

function LayerSection({ title, entries }: { title: string; entries: LayerEntry[] }) {
  if (entries.length === 0) return null;

  return (
    <div>
      <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">{title}</div>
      {entries.map((entry, i) => (
        <div key={i} className="text-xs text-gray-400 mb-1">
          {entry.time_start && (
            <span className="text-gray-600 mr-1">
              [{entry.time_start}-{entry.time_end}]
            </span>
          )}
          <span className="text-gray-500">{entry.content_type}: </span>
          {entry.content || entry.raw}
        </div>
      ))}
    </div>
  );
}
