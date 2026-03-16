import { useProjectStore } from '../stores/project';
import { StoryboardTimeline } from './StoryboardTimeline';
import { MediaLibrary } from './MediaLibrary';
import { PreviewPanel } from './PreviewPanel';
import { ProductionBar } from './ProductionBar';

export function Layout() {
  const storyboard = useProjectStore(s => s.storyboard);
  if (!storyboard) return null;

  const totalMins = Math.floor(storyboard.total_duration_seconds / 60);
  const totalSecs = storyboard.total_duration_seconds % 60;

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <header className="bg-editor-surface border-b border-editor-border px-4 py-2 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-bold">Bee Video Editor</h1>
          <span className="text-xs text-gray-500">|</span>
          <span className="text-xs text-gray-400 truncate max-w-md">{storyboard.title}</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span>{storyboard.total_segments} segments</span>
          <span>{totalMins}m {totalSecs}s</span>
          <span>{storyboard.sections.length} sections</span>
        </div>
      </header>

      {/* Main area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Media Library */}
        <aside className="w-64 border-r border-editor-border flex flex-col shrink-0">
          <MediaLibrary />
        </aside>

        {/* Center: Storyboard Timeline */}
        <main className="flex-1 overflow-y-auto">
          <StoryboardTimeline />
        </main>

        {/* Right: Preview */}
        <aside className="w-80 border-l border-editor-border flex flex-col shrink-0">
          <PreviewPanel />
        </aside>
      </div>

      {/* Bottom: Production controls */}
      <footer className="border-t border-editor-border shrink-0">
        <ProductionBar />
      </footer>
    </div>
  );
}
