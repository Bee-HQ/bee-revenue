import { useEffect, useRef, useCallback } from 'react';
import { useProjectStore } from '../stores/project';
import { storyboardToDesignCombo } from '../adapters/timeline-adapter';
import { ProductionDropdown } from './ProductionDropdown';
import { api } from '../api/client';
import { toast } from '../stores/toast';
import StateManager from '@designcombo/state';
import Timeline from '@designcombo/timeline';
import { dispatch as dcDispatch } from '@designcombo/events';

const SCALE = { unit: 300, zoom: 1 / 300, segments: 5, index: 7 };

export function TimelineEditor() {
  const storyboard = useProjectStore((s) => s.storyboard);
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const timelineRef = useRef<Timeline | null>(null);
  const stateManagerRef = useRef<StateManager | null>(null);

  useEffect(() => {
    if (!canvasRef.current || !storyboard || !containerRef.current) return;

    // Set canvas dimensions from container
    const rect = containerRef.current.getBoundingClientRect();
    canvasRef.current.width = rect.width;
    canvasRef.current.height = rect.height;

    try {
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
      // Cleanup
      if (timelineRef.current) {
        try {
          // Timeline extends Fabric.js Canvas which has dispose()
          timelineRef.current.dispose();
        } catch {
          // ignore cleanup errors
        }
      }
      if (stateManagerRef.current) {
        try {
          stateManagerRef.current.destroyListeners();
          stateManagerRef.current.purge();
        } catch {
          // ignore cleanup errors
        }
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

      {/* Timeline canvas container */}
      <div ref={containerRef} className="flex-1 overflow-hidden relative">
        <canvas ref={canvasRef} className="absolute inset-0" />
      </div>
    </div>
  );
}
