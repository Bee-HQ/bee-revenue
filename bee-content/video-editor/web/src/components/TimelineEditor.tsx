import { useEffect, useRef, useCallback, useState } from 'react';
import { useProjectStore } from '../stores/project';
import { storyboardToDesignCombo, designComboToStoryboard } from '../adapters/timeline-adapter';
import { ProductionDropdown } from './ProductionDropdown';
import { TimelineRuler } from './TimelineRuler';
import { api } from '../api/client';
import { toast } from '../stores/toast';
import StateManager from '@designcombo/state';
import Timeline, { Trimmable } from '@designcombo/timeline';
import { dispatch as dcDispatch } from '@designcombo/events';

const SCALE = { unit: 300, zoom: 1 / 300, segments: 5, index: 7 };
const FPS = 30;

export function TimelineEditor() {
  const storyboard = useProjectStore((s) => s.storyboard);
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const timelineRef = useRef<Timeline | null>(null);
  const stateManagerRef = useRef<StateManager | null>(null);
  const [zoom, setZoom] = useState(SCALE.index);
  const [snapEnabled, setSnapEnabled] = useState(true);
  const [scrollLeft, setScrollLeft] = useState(0);

  // Ruler zoom: pixels per millisecond, derived from zoom slider index
  const rulerZoom = 1 / (zoom * 75);

  const handleRulerSeek = useCallback((ms: number) => {
    useProjectStore.getState().setCurrentTimeMs(ms);
    const player = useProjectStore.getState().playerRef?.current;
    if (player) {
      const frame = Math.round(ms / (1000 / FPS));
      player.seekTo(frame);
    }
  }, []);

  useEffect(() => {
    if (!canvasRef.current || !storyboard || !containerRef.current) return;

    // Tear down any previous instance first (React strict mode double-mounts)
    if (timelineRef.current) {
      try { timelineRef.current.dispose(); } catch {}
      timelineRef.current = null;
    }
    if (stateManagerRef.current) {
      try { stateManagerRef.current.destroyListeners(); stateManagerRef.current.purge(); } catch {}
      stateManagerRef.current = null;
    }

    // Set canvas dimensions from container
    const rect = containerRef.current.getBoundingClientRect();
    canvasRef.current.width = rect.width;
    canvasRef.current.height = rect.height;

    // Declare outside try so cleanup can always reach them
    let activeIdsSub: { unsubscribe: () => void } | null = null;
    let trackItemSub: { unsubscribe: () => void } | null = null;
    let syncTimeout: ReturnType<typeof setTimeout> | null = null;

    try {
      // Register item classes so Timeline can deserialize track items by type.
      // Trimmable is the base Fabric.js class for all timeline track items.
      try {
        Timeline.registerItems({
          video: Trimmable,
          audio: Trimmable,
          image: Trimmable,
          text: Trimmable,
        });
      } catch {
        // registerItems may throw if classes are already registered — safe to ignore
      }

      // Initialize StateManager
      const sm = new StateManager(
        {
          fps: 30,
          size: { width: 1920, height: 1080 },
        },
        { scale: SCALE },
      );

      const totalMs = Math.max(1000, storyboard.total_duration_seconds * 1000);

      // Initialize Timeline
      const tl = new Timeline(canvasRef.current, {
        scale: SCALE,
        duration: totalMs,
        state: sm,
        itemTypes: ['video', 'audio', 'image', 'text'],
        sizesMap: { video: 36, audio: 28, image: 36, text: 28 },
        acceptsMap: {
          video: ['video', 'image'],
          audio: ['audio'],
          text: ['text'],
        },
        withTransitions: ['video'],
      });

      stateManagerRef.current = sm;
      timelineRef.current = tl;

      // Track viewport scroll for ruler sync
      try {
        if (typeof tl.onViewportChange === 'function') {
          tl.onViewportChange((left: number) => {
            setScrollLeft(left || 0);
          });
        }
      } catch {
        // onViewportChange may not be available in all versions
      }

      // Track clip selection: sync DesignCombo activeIds -> Zustand store
      activeIdsSub = sm.subscribeToActiveIds(({ activeIds }) => {
        const selected = activeIds.length > 0 ? activeIds[0] : null;
        useProjectStore.getState().setActiveClipId(selected);
      });

      // Debounced sync: when clips are dragged/resized, update backend
      trackItemSub = sm.subscribeToUpdateTrackItemTiming(() => {
        if (syncTimeout) clearTimeout(syncTimeout);
        syncTimeout = setTimeout(async () => {
          try {
            const state = sm.getState();
            const currentStoryboard = useProjectStore.getState().storyboard;
            if (!currentStoryboard) return;

            const updated = designComboToStoryboard(state as any, currentStoryboard);

            for (const seg of updated.segments) {
              const original = currentStoryboard.segments.find(s => s.id === seg.id);
              if (!original) continue;

              const changed = JSON.stringify(seg.assigned_media) !== JSON.stringify(original.assigned_media);
              if (changed) {
                for (const [key, path] of Object.entries(seg.assigned_media)) {
                  if (original.assigned_media[key] !== path) {
                    const [layer, indexStr] = key.split(':');
                    await api.assignMedia(seg.id, layer, path, parseInt(indexStr));
                  }
                }
              }
            }

            const sb = await api.getCurrentProject();
            useProjectStore.setState({ storyboard: sb });
          } catch (e) {
            console.error('Timeline sync failed:', e);
          }
        }, 1000);
      });

      // Convert storyboard to DesignCombo state and load
      const dcState = storyboardToDesignCombo(storyboard);
      dcDispatch('design:load', {
        payload: {
          ...dcState,
          size: { width: 1920, height: 1080 },
          fps: 30,
          scale: SCALE,
        },
      });
    } catch (err) {
      console.error('[TimelineEditor] initialization failed:', err);
    }

    return () => {
      // Cleanup subscriptions (declared outside try, so always reachable)
      activeIdsSub?.unsubscribe();
      trackItemSub?.unsubscribe();
      if (syncTimeout) clearTimeout(syncTimeout);
      useProjectStore.getState().setActiveClipId(null);
      // Cleanup timeline and state manager
      if (timelineRef.current) {
        try { timelineRef.current.dispose(); } catch {}
      }
      if (stateManagerRef.current) {
        try {
          stateManagerRef.current.destroyListeners();
          stateManagerRef.current.purge();
        } catch {}
      }
      timelineRef.current = null;
      stateManagerRef.current = null;
    };
  }, [storyboard]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (!containerRef.current || !canvasRef.current || !timelineRef.current)
        return;
      const rect = containerRef.current.getBoundingClientRect();
      canvasRef.current.width = rect.width;
      canvasRef.current.height = rect.height;
      try {
        timelineRef.current.setDimensions({
          width: rect.width,
          height: rect.height,
        });
        timelineRef.current.requestRenderAll();
      } catch {
        // ignore resize errors on unmounted timeline
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleUndo = useCallback(() => {
    stateManagerRef.current?.undo();
  }, []);

  const handleRedo = useCallback(() => {
    stateManagerRef.current?.redo();
  }, []);

  return (
    <div
      className="border-t border-editor-border bg-editor-bg flex flex-col shrink-0"
      style={{ height: 220 }}
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
              useProjectStore.setState({ storyboard: sb });
            } catch (e: unknown) {
              const msg = e instanceof Error ? e.message : String(e);
              toast.error(msg);
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
              const msg = e instanceof Error ? e.message : String(e);
              toast.error(msg);
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
              const msg = e instanceof Error ? e.message : String(e);
              toast.error(msg);
            }
          }}
        >
          Rough Cut
        </button>

        <div className="flex-1" />

        <button
          className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
          onClick={() => {
            const currentMs = useProjectStore.getState().currentTimeMs;
            dcDispatch('active:split', {
              payload: { time: currentMs },
            });
          }}
          title="Split at playhead (S)"
        >
          Split
        </button>
        <button
          className={`text-[10px] px-2 py-1 rounded ${snapEnabled ? 'bg-blue-600/20 text-blue-400' : 'bg-editor-hover text-gray-300'}`}
          onClick={() => {
            const next = !snapEnabled;
            setSnapEnabled(next);
            if (stateManagerRef.current) {
              const state = stateManagerRef.current.getState();
              const updatedTracks = state.tracks.map((t: any) => ({ ...t, magnetic: next }));
              stateManagerRef.current.updateState({ tracks: updatedTracks });
            }
          }}
          title="Toggle snap"
        >
          Snap
        </button>

        <input
          type="range" min="1" max="10" value={zoom}
          onChange={(e) => {
            const val = parseInt(e.target.value);
            setZoom(val);
            const zoomLevel = 1 / (val * 75);
            dcDispatch('scale:changed', {
              payload: {
                scale: { unit: 300, zoom: zoomLevel, segments: 5, index: val },
              },
            });
          }}
          className="w-16" style={{ accentColor: '#3b82f6' }}
          title="Zoom"
        />

        <button
          onClick={handleUndo}
          className="text-[10px] text-gray-400 hover:text-white px-1"
          title="Undo"
        >
          Undo
        </button>
        <button
          onClick={handleRedo}
          className="text-[10px] text-gray-400 hover:text-white px-1"
          title="Redo"
        >
          Redo
        </button>
      </div>

      {/* Time ruler with draggable scrubber */}
      <TimelineRuler
        durationMs={storyboard ? storyboard.total_duration_seconds * 1000 : 1000}
        zoom={rulerZoom}
        scrollLeft={scrollLeft}
        onSeek={handleRulerSeek}
      />

      {/* Timeline canvas container */}
      <div ref={containerRef} className="flex-1 overflow-hidden relative">
        <canvas ref={canvasRef} className="absolute inset-0" />
      </div>
    </div>
  );
}
