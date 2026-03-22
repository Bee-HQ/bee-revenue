import { useEffect, useRef } from 'react';
import { useProjectStore } from './stores/project';
import { api } from './api/client';
import { Layout } from './components/Layout';
import { LoadProject } from './components/LoadProject';
import { ToastContainer } from './components/ToastContainer';
import { ShortcutsPanel } from './components/ShortcutsPanel';

const FPS = 30;

export default function App() {
  const storyboard = useProjectStore(s => s.project);
  const loading = useProjectStore(s => s.loading);
  const restoreAttempted = useRef(false);

  // Try to restore session from backend on mount
  useEffect(() => {
    if (!storyboard && !loading && !restoreAttempted.current) {
      restoreAttempted.current = true;
      api.getCurrentProject()
        .then((sb) => {
          if (sb && sb.segments?.length > 0) {
            useProjectStore.setState({ project: sb });
            useProjectStore.getState().loadMedia();
            useProjectStore.getState().loadAssetStatus();
          }
        })
        .catch(() => {
          // No session to restore — show LoadProject
        });
    }
  }, []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLSelectElement) return;
      const mod = e.metaKey || e.ctrlKey;

      // Undo / Redo
      if (mod && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        useProjectStore.getState().timelineUndo();
      }
      if (mod && e.key === 'z' && e.shiftKey) {
        e.preventDefault();
        useProjectStore.getState().timelineRedo();
      }

      // Copy (Ctrl+C)
      if (mod && e.key === 'c') {
        const { selectedActionIds } = useProjectStore.getState();
        if (selectedActionIds.length > 0) {
          e.preventDefault();
          useProjectStore.getState().copySelectedActions();
        }
      }

      // Paste (Ctrl+V) — only if clipboard has content
      if (mod && e.key === 'v') {
        const { clipboard } = useProjectStore.getState();
        if (clipboard.length > 0) {
          e.preventDefault();
          useProjectStore.getState().pasteClipboard();
        }
      }

      // Duplicate (Ctrl+D)
      if (mod && e.key === 'd') {
        e.preventDefault();
        useProjectStore.getState().duplicateSelectedActions();
      }

      // Split at playhead
      if (e.key === 's' && !mod) {
        e.preventDefault();
        useProjectStore.getState().splitAtPlayhead();
      }

      // Delete / Backspace — delete selected clips
      if ((e.key === 'Delete' || e.key === 'Backspace') && !mod) {
        e.preventDefault();
        useProjectStore.getState().deleteSelectedActions();
      }

      // Space — play/pause
      if (e.key === ' ' && !mod) {
        e.preventDefault();
        const player = useProjectStore.getState().playerRef?.current;
        if (player) {
          if (player.isPlaying()) player.pause();
          else player.play();
        }
      }

      // J — step back 5 frames
      if (e.key === 'j' && !mod) {
        e.preventDefault();
        const player = useProjectStore.getState().playerRef?.current;
        if (player) {
          player.pause();
          const frame = player.getCurrentFrame();
          player.seekTo(Math.max(0, frame - 5));
        }
      }

      // K — pause
      if (e.key === 'k' && !mod) {
        e.preventDefault();
        const player = useProjectStore.getState().playerRef?.current;
        player?.pause();
      }

      // L — play forward
      if (e.key === 'l' && !mod) {
        e.preventDefault();
        const player = useProjectStore.getState().playerRef?.current;
        if (player && !player.isPlaying()) {
          player.play();
        }
      }

      // Arrow left — skip back 1 second
      if (e.key === 'ArrowLeft' && !mod) {
        e.preventDefault();
        const player = useProjectStore.getState().playerRef?.current;
        if (player) {
          const frame = player.getCurrentFrame();
          player.seekTo(Math.max(0, frame - FPS));
        }
      }

      // Arrow right — skip forward 1 second
      if (e.key === 'ArrowRight' && !mod) {
        e.preventDefault();
        const player = useProjectStore.getState().playerRef?.current;
        if (player) {
          const frame = player.getCurrentFrame();
          const sb = useProjectStore.getState().project;
          const totalDuration = sb ? sb.segments.reduce((sum, s) => sum + s.duration, 0) : 0;
          const maxFrame = sb ? Math.round(totalDuration * FPS) : Infinity;
          player.seekTo(Math.min(maxFrame - 1, frame + FPS));
        }
      }

      // I — set loop in
      if (e.key === 'i' && !mod) {
        e.preventDefault();
        const player = useProjectStore.getState().playerRef?.current;
        if (player) {
          useProjectStore.getState().setLoopIn(player.getCurrentFrame());
        }
      }

      // O — set loop out
      if (e.key === 'o' && !mod) {
        e.preventDefault();
        const player = useProjectStore.getState().playerRef?.current;
        if (player) {
          useProjectStore.getState().setLoopOut(player.getCurrentFrame());
        }
      }

      // Home — go to start
      if (e.key === 'Home' && !mod) {
        e.preventDefault();
        useProjectStore.getState().playerRef?.current?.seekTo(0);
      }

      // End — go to end
      if (e.key === 'End' && !mod) {
        e.preventDefault();
        const sb = useProjectStore.getState().project;
        if (sb) {
          const totalDuration = sb.segments.reduce((sum, s) => sum + s.duration, 0);
          const maxFrame = Math.round(totalDuration * FPS);
          useProjectStore.getState().playerRef?.current?.seekTo(Math.max(0, maxFrame - 1));
        }
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  if (!storyboard) {
    return (
      <>
        <LoadProject />
        <ToastContainer />
        <ShortcutsPanel />
      </>
    );
  }

  return (
    <>
      <Layout />
      <ToastContainer />
      <ShortcutsPanel />
    </>
  );
}
