import { useState, useEffect } from 'react';
import { useProjectStore } from '../stores/project';
import { RemotionPreview } from './RemotionPreview';
import { TimelineEditor } from './TimelineEditor';
import { MediaLibrary } from './MediaLibrary';
import { ClipProperties } from './ClipProperties';
import { AIPanel } from './AIPanel';
import { SegmentList } from './SegmentList';
import { ExportMenu } from './ExportMenu';
import { AssetStatusBanner } from './AssetStatusBanner';
import { Hexagon, Film, SlidersHorizontal, Sparkles } from 'lucide-react';

export function Layout() {
  const storyboard = useProjectStore(s => s.storyboard);
  const activeClipId = useProjectStore(s => s.activeClipId);
  const [rightTab, setRightTab] = useState<'media' | 'properties' | 'ai'>('media');

  // Auto-switch to Properties tab when a clip is selected
  useEffect(() => {
    if (activeClipId) setRightTab('properties');
  }, [activeClipId]);
  if (!storyboard) return null;

  const totalMins = Math.floor(storyboard.total_duration_seconds / 60);
  const totalSecs = Math.round(storyboard.total_duration_seconds % 60);

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <header className="bg-editor-surface border-b border-editor-border px-4 py-1.5 flex items-center justify-between shrink-0" style={{ borderImage: 'linear-gradient(to right, #3b82f6, transparent) 1', borderBottomWidth: '1px' }}>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <Hexagon size={16} className="text-blue-400" fill="currentColor" fillOpacity={0.15} />
            <h1 className="text-sm font-bold"><span className="text-blue-400">Bee</span> <span className="text-gray-300">Video Editor</span></h1>
          </div>
          <span className="text-xs text-gray-600">|</span>
          <span className="text-xs text-gray-400 truncate max-w-md">{storyboard.title}</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span>{storyboard.total_segments} segments</span>
          <span>{totalMins}m {totalSecs}s</span>
          <span>{storyboard.sections.length} sections</span>
          <ExportMenu />
        </div>
      </header>

      <AssetStatusBanner />

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-56 border-r border-editor-border flex flex-col shrink-0">
          <SegmentList />
        </aside>

        <main className="flex-1 flex flex-col overflow-hidden min-w-0">
          <RemotionPreview />
          <TimelineEditor />
        </main>

        <aside className="w-56 border-l border-editor-border flex flex-col shrink-0">
          {/* Tab bar */}
          <div className="flex border-b border-editor-border shrink-0">
            {([
              { key: 'media' as const, label: 'Media', icon: Film },
              { key: 'properties' as const, label: 'Props', icon: SlidersHorizontal },
              { key: 'ai' as const, label: 'AI', icon: Sparkles },
            ]).map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setRightTab(key)}
                className={`flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-[10px] uppercase tracking-wider transition-colors ${
                  rightTab === key
                    ? 'text-blue-400 border-b-2 border-blue-400 bg-editor-surface'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                <Icon size={11} />
                {label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-hidden">
            {rightTab === 'media' && <MediaLibrary />}
            {rightTab === 'properties' && <ClipProperties />}
            {rightTab === 'ai' && <AIPanel />}
          </div>
        </aside>
      </div>
    </div>
  );
}
