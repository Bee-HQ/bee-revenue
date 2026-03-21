import { useState, useEffect, useCallback, useRef } from 'react';
import { useProjectStore } from '../stores/project';
import { RemotionPreview } from './RemotionPreview';
import { TimelineEditor } from './TimelineEditor';
import { MediaLibrary } from './MediaLibrary';
import { ClipProperties } from './ClipProperties';
import { AIPanel } from './AIPanel';
import { SegmentList } from './SegmentList';
import { ExportMenu } from './ExportMenu';
import { AssetStatusBanner } from './AssetStatusBanner';
import { Hexagon, Film, SlidersHorizontal, Sparkles, Sun, Moon } from 'lucide-react';

function useTheme() {
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    try {
      return (localStorage.getItem('bee-editor-theme') as 'dark' | 'light') || 'dark';
    } catch { return 'dark'; }
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'light') {
      root.classList.add('light');
    } else {
      root.classList.remove('light');
    }
    try { localStorage.setItem('bee-editor-theme', theme); } catch {}
  }, [theme]);

  const toggle = useCallback(() => setTheme(t => t === 'dark' ? 'light' : 'dark'), []);
  return { theme, toggle };
}

function useResizable(defaultHeight: number, storageKey: string) {
  const [height, setHeight] = useState(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      return stored ? parseInt(stored, 10) : defaultHeight;
    } catch { return defaultHeight; }
  });
  const dragging = useRef(false);
  const startY = useRef(0);
  const startH = useRef(0);

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;
    startY.current = e.clientY;
    startH.current = height;

    const onMouseMove = (ev: MouseEvent) => {
      if (!dragging.current) return;
      const delta = startY.current - ev.clientY;
      const maxH = Math.floor(window.innerHeight * 0.6);
      const newH = Math.max(120, Math.min(maxH, startH.current + delta));
      setHeight(newH);
    };

    const onMouseUp = () => {
      dragging.current = false;
      try { localStorage.setItem(storageKey, String(height)); } catch {}
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  }, [height, storageKey]);

  return { height, onMouseDown };
}

export function Layout() {
  const storyboard = useProjectStore(s => s.storyboard);
  const activeClipId = useProjectStore(s => s.activeClipId);
  const [rightTab, setRightTab] = useState<'media' | 'properties' | 'ai'>('media');
  const { theme, toggle: toggleTheme } = useTheme();
  const { height: timelineHeight, onMouseDown: onResizeMouseDown } = useResizable(250, 'bee-editor-timeline-h');

  // Auto-switch to Properties tab when a clip is selected
  useEffect(() => {
    if (activeClipId) setRightTab('properties');
  }, [activeClipId]);
  if (!storyboard) return null;

  const totalMins = Math.floor(storyboard.total_duration_seconds / 60);
  const totalSecs = Math.round(storyboard.total_duration_seconds % 60);

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <header className="bg-editor-surface border-b border-editor-border px-4 py-1.5 flex items-center justify-between shrink-0" style={{ borderImage: `linear-gradient(to right, var(--editor-accent), transparent) 1`, borderBottomWidth: '1px' }}>
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
          <button
            onClick={toggleTheme}
            className="p-1 rounded text-gray-400 hover:text-white hover:bg-editor-hover transition-colors"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
          </button>
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
          {/* Resize handle */}
          <div
            className="h-1.5 bg-editor-border hover:bg-editor-accent/40 cursor-row-resize shrink-0 flex items-center justify-center transition-colors group"
            onMouseDown={onResizeMouseDown}
          >
            <div className="flex gap-0.5">
              <div className="w-0.5 h-0.5 rounded-full bg-gray-600 group-hover:bg-gray-400" />
              <div className="w-0.5 h-0.5 rounded-full bg-gray-600 group-hover:bg-gray-400" />
              <div className="w-0.5 h-0.5 rounded-full bg-gray-600 group-hover:bg-gray-400" />
            </div>
          </div>
          <TimelineEditor style={{ height: timelineHeight }} />
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
