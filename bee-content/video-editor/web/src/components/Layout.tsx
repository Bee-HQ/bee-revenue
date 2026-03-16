import { useProjectStore } from '../stores/project';
import { StoryboardTimeline } from './StoryboardTimeline';
import { MediaLibrary } from './MediaLibrary';
import { VideoPlayer } from './VideoPlayer';
import { SegmentList } from './SegmentList';
import { ProductionBar } from './ProductionBar';

export function Layout() {
  const storyboard = useProjectStore(s => s.storyboard);
  if (!storyboard) return null;

  const totalMins = Math.floor(storyboard.total_duration_seconds / 60);
  const totalSecs = storyboard.total_duration_seconds % 60;

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
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
        </div>
      </header>

      {/* Main area: three columns */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Segment list */}
        <aside className="w-72 border-r border-editor-border flex flex-col shrink-0">
          <SegmentList />
        </aside>

        {/* Center: Player + Timeline */}
        <main className="flex-1 flex flex-col overflow-hidden min-w-0">
          {/* Video player */}
          <div className="flex-shrink-0">
            <VideoPlayer />
          </div>

          {/* Timeline */}
          <div className="flex-1 overflow-y-auto border-t border-editor-border">
            <StoryboardTimeline />
          </div>
        </main>

        {/* Right: Media library */}
        <aside className="w-72 border-l border-editor-border flex flex-col shrink-0">
          <MediaLibrary />
        </aside>
      </div>

      {/* Bottom: Production controls */}
      <footer className="border-t border-editor-border shrink-0">
        <ProductionBar />
      </footer>
    </div>
  );
}
