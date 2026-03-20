import { useProjectStore } from '../stores/project';
import { RemotionPreview } from './RemotionPreview';
import { TimelineEditor } from './TimelineEditor';
import { MediaLibrary } from './MediaLibrary';
import { ClipProperties } from './ClipProperties';
import { SegmentList } from './SegmentList';
import { ExportMenu } from './ExportMenu';

export function Layout() {
  const storyboard = useProjectStore(s => s.storyboard);
  if (!storyboard) return null;

  const totalMins = Math.floor(storyboard.total_duration_seconds / 60);
  const totalSecs = storyboard.total_duration_seconds % 60;

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <header className="bg-editor-surface border-b border-editor-border px-4 py-1.5 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-bold">Bee Video Editor</h1>
          <span className="text-xs text-gray-500">|</span>
          <span className="text-xs text-gray-400 truncate max-w-md">{storyboard.title}</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span>{storyboard.total_segments} segments</span>
          <span>{totalMins}m {totalSecs}s</span>
          <span>{storyboard.sections.length} sections</span>
          <ExportMenu />
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-56 border-r border-editor-border flex flex-col shrink-0">
          <SegmentList />
        </aside>

        <main className="flex-1 flex flex-col overflow-hidden min-w-0">
          <RemotionPreview />
          <TimelineEditor />
        </main>

        <aside className="w-56 border-l border-editor-border flex flex-col shrink-0">
          <div className="flex-1 overflow-hidden">
            <MediaLibrary />
          </div>
          <ClipProperties />
        </aside>
      </div>
    </div>
  );
}
