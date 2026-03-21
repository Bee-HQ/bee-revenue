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

export function TimelineEditor() {
  const storyboard = useProjectStore(s => s.storyboard);
  const editorData = useProjectStore(s => s.editorData);
  const setEditorData = useProjectStore(s => s.setEditorData);
  const pushTimelineHistory = useProjectStore(s => s.pushTimelineHistory);
  const setActiveClipId = useProjectStore(s => s.setActiveClipId);
  const setCurrentTimeMs = useProjectStore(s => s.setCurrentTimeMs);
  const currentTimeMs = useProjectStore(s => s.currentTimeMs);
  const timelineRef = useRef<TimelineState>(null);
  const [zoomLevel, setZoomLevel] = useState(5);
  const [snapEnabled, setSnapEnabled] = useState(true);
  const [effects, setEffects] = useState<Record<string, any>>({});
  const syncTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const syncingRef = useRef(false);
  const isPlayingRef = useRef(false);
  const lastSyncRef = useRef(0);

  // Track Remotion play/pause state for cursor sync throttling
  useEffect(() => {
    const player = useProjectStore.getState().playerRef?.current;
    if (!player || typeof player.addEventListener !== 'function') return;
    const onPlay = () => { isPlayingRef.current = true; };
    const onPause = () => { isPlayingRef.current = false; };
    player.addEventListener('play', onPlay as never);
    player.addEventListener('pause', onPause as never);
    return () => {
      try {
        player.removeEventListener('play', onPlay as never);
        player.removeEventListener('pause', onPause as never);
      } catch {}
    };
  }, [storyboard]);

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

  // Sync Remotion playback → timeline cursor (throttled during playback)
  useEffect(() => {
    if (!timelineRef.current) return;
    const now = Date.now();
    // During playback: throttle to ~5fps to avoid 30fps churn
    if (isPlayingRef.current && now - lastSyncRef.current < 200) return;
    lastSyncRef.current = now;
    timelineRef.current.setTime(currentTimeMs / 1000);
    // reRender() needed for the library to visually update cursor position
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

  const handleClickAction = useCallback((_e: any, { action }: { action: TimelineAction }) => {
    setActiveClipId(action.id);
  }, []);

  const handleClickRow = useCallback(() => {
    setActiveClipId(null);
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

  return (
    <div
      className="border-t border-editor-border bg-editor-bg flex flex-col shrink-0"
      style={{ height: 250 }}
      tabIndex={0}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onPaste={handlePaste}
    >
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-3 py-1 border-b border-editor-border bg-editor-surface shrink-0">
        <button
          className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
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
          Auto-Assign
        </button>
        <button
          className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
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
          Acquire
        </button>
        <ProductionDropdown />
        <button
          className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
          onClick={async () => {
            try {
              await api.roughCut();
              toast.success('Rough cut exported');
            } catch (e: unknown) {
              toast.error(e instanceof Error ? e.message : String(e));
            }
          }}
        >
          Rough Cut
        </button>
        <div className="flex-1" />
        <button
          className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
          onClick={() => useProjectStore.getState().splitAtPlayhead()}
          title="Split at playhead (S)"
        >
          Split
        </button>
        <button
          className={`text-[10px] px-2 py-1 rounded ${snapEnabled ? 'bg-blue-600/20 text-blue-400' : 'bg-editor-hover text-gray-300'}`}
          onClick={() => setSnapEnabled(!snapEnabled)}
          title="Toggle snap"
        >
          Snap
        </button>
        <input
          type="range" min="1" max="10" value={zoomLevel}
          onChange={(e) => setZoomLevel(parseInt(e.target.value))}
          className="w-16" style={{ accentColor: '#3b82f6' }}
          title="Zoom"
        />
        <button
          onClick={() => useProjectStore.getState().timelineUndo()}
          className="text-[10px] text-gray-400 hover:text-white px-1"
          title="Undo"
        >
          Undo
        </button>
        <button
          onClick={() => useProjectStore.getState().timelineRedo()}
          className="text-[10px] text-gray-400 hover:text-white px-1"
          title="Redo"
        >
          Redo
        </button>
      </div>
      {/* Timeline */}
      <div className="flex-1 min-h-0 overflow-hidden">
          <Timeline
            style={{ width: '100%', height: '100%' }}
            ref={timelineRef}
            editorData={editorData}
            effects={effects}
            onChange={handleChange}
            scale={10}
            scaleWidth={zoomLevel * 60}
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
