import { useEffect, useRef, useCallback, useState } from 'react';
import { Timeline } from '@xzdarcy/react-timeline-editor';
import type { TimelineState } from '@xzdarcy/react-timeline-editor';
import '@xzdarcy/react-timeline-editor/dist/react-timeline-editor.css';
import type { TimelineRow, TimelineAction } from '@xzdarcy/timeline-engine';
import { useProjectStore } from '../stores/project';
import { storyboardToTimeline, timelineToStoryboard } from '../adapters/timeline-adapter';
import { renderTimelineAction } from './TimelineActionRenderer';
import { ProductionDropdown } from './ProductionDropdown';
import { api } from '../api/client';
import { toast } from '../stores/toast';
import { Wand2, Download, Scissors, Magnet, Undo2, Redo2 } from 'lucide-react';

// Module-level — outside TimelineEditor component
function addActionToTimeline(path: string, type: string, cursorSec: number, duration?: number | null) {
  const { editorData } = useProjectStore.getState();
  const dur = duration ?? 5;
  const effectId = type === 'audio' ? 'audio' : 'video';
  const targetRowId = type === 'audio' ? 'A2' : 'V1';

  const newAction: any = {
    id: `drop-${Date.now()}`,
    start: cursorSec,
    end: cursorSec + dur,
    effectId,
    data: { segmentId: '', contentType: type.toUpperCase(), src: path, title: path.split('/').pop() || '', layerIndex: 0 },
  };

  let newRows: any[];
  const targetRow = editorData.find(r => r.id === targetRowId);
  if (targetRow) {
    newRows = editorData.map(r => r.id === targetRowId ? { ...r, actions: [...r.actions, newAction] } : r);
  } else {
    newRows = [...editorData, { id: targetRowId, actions: [newAction] }];
  }
  useProjectStore.getState().setEditorData(newRows);
  useProjectStore.getState().pushTimelineHistory(newRows);
}

export function TimelineEditor({ style }: { style?: React.CSSProperties }) {
  const storyboard = useProjectStore(s => s.storyboard);
  const editorData = useProjectStore(s => s.editorData);
  const setEditorData = useProjectStore(s => s.setEditorData);
  const pushTimelineHistory = useProjectStore(s => s.pushTimelineHistory);
  const setCurrentTimeMs = useProjectStore(s => s.setCurrentTimeMs);
  const currentTimeMs = useProjectStore(s => s.currentTimeMs);
  const timelineRef = useRef<TimelineState>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [snapEnabled, setSnapEnabled] = useState(true);
  const [effects, setEffects] = useState<Record<string, any>>({});
  const syncTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const syncingRef = useRef(false);

  // Compute scaleWidth so zoom=1 fits the full duration to the container width.
  // Higher zoom levels expand proportionally.
  const SCALE = 10; // seconds per major grid division
  const totalDuration = editorData.reduce((max, row) => {
    for (const a of row.actions) {
      if (a.end > max) max = a.end;
    }
    return max;
  }, 30); // minimum 30s so empty timelines don't look weird
  const [containerWidth, setContainerWidth] = useState(800);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const measure = () => setContainerWidth(el.clientWidth);
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // At zoom=1, the full duration fits the container.
  // scaleWidth = pixels per `scale` seconds.
  // Total pixels = (totalDuration / SCALE) * scaleWidth => should equal containerWidth at zoom=1
  // So base scaleWidth = containerWidth / (totalDuration / SCALE) = containerWidth * SCALE / totalDuration
  const baseScaleWidth = Math.max(20, (containerWidth * SCALE) / totalDuration);
  const scaleWidth = baseScaleWidth * zoomLevel;

  // Convert storyboard → timeline rows on storyboard change
  // Skip re-conversion when storyboard was updated by the debounced sync callback
  useEffect(() => {
    if (!storyboard) return;
    if (syncingRef.current) {
      syncingRef.current = false;
      return;
    }
    const { rows, effects: eff } = storyboardToTimeline(storyboard);
    setEditorData(rows);
    setEffects(eff);
    pushTimelineHistory(rows);
  }, [storyboard]);

  // Sync Remotion playback → timeline cursor.
  // RemotionPreview polls at 100ms (~10fps), so updates are already throttled at the source.
  useEffect(() => {
    if (!timelineRef.current) return;
    timelineRef.current.setTime(currentTimeMs / 1000);
    (timelineRef.current as any).reRender?.();
  }, [currentTimeMs]);

  const handleChange = useCallback((newData: TimelineRow[]) => {
    setEditorData(newData);
    pushTimelineHistory(newData);
    // Debounced backend sync
    if (syncTimeoutRef.current) clearTimeout(syncTimeoutRef.current);
    syncTimeoutRef.current = setTimeout(async () => {
      try {
        const sb = useProjectStore.getState().storyboard;
        if (!sb) return;
        const updated = timelineToStoryboard(newData, sb);
        for (const seg of updated.segments) {
          const original = sb.segments.find(s => s.id === seg.id);
          if (!original) continue;
          for (const [key, path] of Object.entries(seg.assigned_media)) {
            if (original.assigned_media[key] !== path) {
              const [layer, indexStr] = key.split(':');
              await api.assignMedia(seg.id, layer, path, parseInt(indexStr));
            }
          }
        }
        syncingRef.current = true;
        const freshSb = await api.getCurrentProject();
        useProjectStore.setState({ storyboard: freshSb });
      } catch (e) {
        console.error('Timeline sync failed:', e);
      }
    }, 1000);
  }, []);

  const handleCursorDrag = useCallback((time: number) => {
    setCurrentTimeMs(time * 1000);
  }, []);

  const handleCursorDragEnd = useCallback((time: number) => {
    setCurrentTimeMs(time * 1000);
  }, []);

  const handleClickAction = useCallback((e: React.MouseEvent, { action }: { action: TimelineAction }) => {
    useProjectStore.getState().selectAction(action.id, e.shiftKey);
  }, []);

  const handleClickRow = useCallback(() => {
    useProjectStore.getState().clearActionSelection();
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    const cursorSec = timelineRef.current?.getTime() ?? 0;

    // 1. Internal drag (from Media Library)
    const beeMedia = e.dataTransfer.getData('bee/media');
    if (beeMedia) {
      try {
        const { path, type } = JSON.parse(beeMedia);
        addActionToTimeline(path, type, cursorSec);
      } catch {}
      return;
    }

    // 2. External file drop
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      for (const file of Array.from(files)) {
        try {
          const formData = new FormData();
          formData.append('file', file);
          const res = await fetch('/api/media/upload', { method: 'POST', body: formData });
          if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
          const data = await res.json();
          addActionToTimeline(data.path, data.type, cursorSec, data.duration);
          toast.success(`Uploaded: ${file.name}`);
        } catch {
          toast.error(`Upload failed: ${file.name}`);
        }
      }
    }
  }, []);

  const handlePaste = useCallback(async (e: React.ClipboardEvent) => {
    const cursorSec = timelineRef.current?.getTime() ?? 0;

    if (e.clipboardData.files.length > 0) {
      for (const file of Array.from(e.clipboardData.files)) {
        const formData = new FormData();
        formData.append('file', file);
        try {
          const res = await fetch('/api/media/upload', { method: 'POST', body: formData });
          if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
          const data = await res.json();
          addActionToTimeline(data.path, data.type, cursorSec, data.duration);
        } catch {
          toast.error(`Paste upload failed: ${file.name}`);
        }
      }
      return;
    }

    const text = e.clipboardData.getData('text').trim();
    if (text && (text.includes('/') || text.includes('\\'))) {
      const ext = text.split('.').pop()?.toLowerCase() || '';
      const type = ['mp4','mov','webm','avi'].includes(ext) ? 'video'
        : ['mp3','wav','aac','m4a'].includes(ext) ? 'audio'
        : ['png','jpg','jpeg','webp'].includes(ext) ? 'image' : 'video';
      addActionToTimeline(text, type, cursorSec);
    }
  }, []);

  if (!storyboard) return null;

  const selectedIds = useProjectStore.getState().selectedActionIds;
  const markedData = editorData.map(row => ({
    ...row,
    actions: row.actions.map(a => ({
      ...a,
      selected: selectedIds.includes(a.id),
    })),
  }));

  return (
    <div
      className="border-t border-editor-border bg-editor-bg flex flex-col shrink-0"
      style={{ height: 250, ...style }}
      tabIndex={0}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onPaste={handlePaste}
    >
      {/* Toolbar */}
      <div className="flex items-center gap-1.5 px-3 py-1.5 border-b border-editor-border bg-editor-surface shrink-0">
        {/* Pipeline group */}
        <button
          className="flex items-center gap-1.5 text-[11px] bg-blue-600/10 text-blue-400 hover:bg-blue-600/20 px-2.5 py-1 rounded transition-colors"
          onClick={async () => {
            try {
              const r = await api.autoAssign();
              toast.success(`Auto-assigned ${r.assigned} segments`);
              const sb = await api.getCurrentProject();
              syncingRef.current = true;
              useProjectStore.setState({ storyboard: sb });
            } catch (e: unknown) {
              toast.error(e instanceof Error ? e.message : String(e));
            }
          }}
        >
          <Wand2 size={12} />
          Auto-Assign
        </button>
        <button
          className="flex items-center gap-1.5 text-[11px] bg-blue-600/10 text-blue-400 hover:bg-blue-600/20 px-2.5 py-1 rounded transition-colors"
          onClick={async () => {
            try {
              const r = await api.acquireMedia();
              toast.success(`Acquired: ${r.downloaded} downloaded`);
              useProjectStore.getState().loadMedia();
            } catch (e: unknown) {
              toast.error(e instanceof Error ? e.message : String(e));
            }
          }}
        >
          <Download size={12} />
          Acquire
        </button>
        <ProductionDropdown />
        <button
          className="flex items-center gap-1.5 text-[11px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2.5 py-1 rounded transition-colors"
          onClick={async () => {
            try {
              await api.roughCut();
              toast.success('Rough cut exported');
            } catch (e: unknown) {
              toast.error(e instanceof Error ? e.message : String(e));
            }
          }}
        >
          <Scissors size={12} />
          Rough Cut
        </button>

        <div className="flex-1" />

        {/* Editing group */}
        <div className="w-px h-4 bg-editor-border" />
        <button
          className="flex items-center gap-1.5 text-[11px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2.5 py-1 rounded transition-colors"
          onClick={() => useProjectStore.getState().splitAtPlayhead()}
          title="Split at playhead (S)"
        >
          <Scissors size={12} />
          Split
        </button>
        <button
          className={`flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded transition-colors ${snapEnabled ? 'bg-blue-600/20 text-blue-400' : 'bg-editor-hover text-gray-300'}`}
          onClick={() => setSnapEnabled(!snapEnabled)}
          title="Toggle snap"
        >
          <Magnet size={12} />
          Snap
        </button>

        {/* View group */}
        <div className="w-px h-4 bg-editor-border" />
        <input
          type="range" min="1" max="20" value={zoomLevel}
          onChange={(e) => setZoomLevel(parseInt(e.target.value))}
          className="w-20"
          title="Zoom (1 = fit to screen)"
        />
        <button
          onClick={() => useProjectStore.getState().timelineUndo()}
          className="p-1 text-gray-400 hover:text-white hover:bg-editor-hover rounded transition-colors"
          aria-label="Undo"
          title="Undo (Ctrl+Z)"
        >
          <Undo2 size={14} />
        </button>
        <button
          onClick={() => useProjectStore.getState().timelineRedo()}
          className="p-1 text-gray-400 hover:text-white hover:bg-editor-hover rounded transition-colors"
          aria-label="Redo"
          title="Redo (Ctrl+Shift+Z)"
        >
          <Redo2 size={14} />
        </button>
      </div>
      {/* Timeline */}
      <div ref={containerRef} className="flex-1 min-h-0 overflow-hidden">
          <Timeline
            style={{ width: '100%', height: '100%' }}
            ref={timelineRef}
            editorData={markedData}
            effects={effects}
            onChange={handleChange}
            scale={SCALE}
            scaleWidth={scaleWidth}
            rowHeight={28}
            gridSnap={snapEnabled}
            dragLine={true}
            autoScroll={true}
            getActionRender={renderTimelineAction}
            onClickActionOnly={handleClickAction}
            onClickRow={handleClickRow}
            onCursorDrag={handleCursorDrag}
            onCursorDragEnd={handleCursorDragEnd}
          />
      </div>
    </div>
  );
}
