import { useEffect, useRef, useCallback, useState } from 'react';
import { Timeline } from '@xzdarcy/react-timeline-editor';
import type { TimelineState, TimelineRow, TimelineAction } from '@xzdarcy/react-timeline-editor';
import { useProjectStore } from '../stores/project';
import { storyboardToTimeline, timelineToStoryboard } from '../adapters/timeline-adapter';
import { renderTimelineAction } from './TimelineActionRenderer';
import { ProductionDropdown } from './ProductionDropdown';
import { api } from '../api/client';
import { toast } from '../stores/toast';

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

  // Convert storyboard → timeline rows on storyboard change
  useEffect(() => {
    if (!storyboard) return;
    const { rows, effects: eff } = storyboardToTimeline(storyboard);
    setEditorData(rows);
    setEffects(eff);
    pushTimelineHistory(rows);
  }, [storyboard]);

  // Sync Remotion playback → timeline cursor
  useEffect(() => {
    if (timelineRef.current) {
      timelineRef.current.setTime(currentTimeMs / 1000);
    }
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

  if (!storyboard) return null;

  return (
    <div
      className="border-t border-editor-border bg-editor-bg flex flex-col shrink-0"
      style={{ height: 180 }}
      tabIndex={0}
    >
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-3 py-1 border-b border-editor-border bg-editor-surface shrink-0">
        <ProductionDropdown />
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
      {/* Track labels + Timeline */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        <div className="w-12 shrink-0 border-r border-editor-border bg-editor-surface flex flex-col">
          {editorData.map(row => (
            <div key={row.id} className="text-[9px] text-gray-500 font-mono px-1 flex items-center" style={{ height: 28 }}>
              {row.id}
            </div>
          ))}
        </div>
        <div className="flex-1 overflow-hidden">
          <Timeline
            ref={timelineRef}
            editorData={editorData}
            effects={effects}
            onChange={handleChange}
            scale={1}
            scaleWidth={zoomLevel * 40}
            rowHeight={28}
            gridSnap={snapEnabled}
            dragLine={true}
            autoScroll={true}
            getActionRender={renderTimelineAction}
            onClickAction={handleClickAction}
            onClickActionOnly={handleClickAction}
            onClickRow={handleClickRow}
            onCursorDrag={handleCursorDrag}
            onCursorDragEnd={handleCursorDragEnd}
          />
        </div>
      </div>
    </div>
  );
}
