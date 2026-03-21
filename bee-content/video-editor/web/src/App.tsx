import { useEffect, useRef } from 'react';
import { useProjectStore } from './stores/project';
import { api } from './api/client';
import { Layout } from './components/Layout';
import { LoadProject } from './components/LoadProject';
import { ToastContainer } from './components/ToastContainer';
import { ShortcutsPanel } from './components/ShortcutsPanel';
import { dispatch as dcDispatch } from '@designcombo/events';

const FPS = 30;

export default function App() {
  const storyboard = useProjectStore(s => s.storyboard);
  const loading = useProjectStore(s => s.loading);
  const restoreAttempted = useRef(false);

  // Try to restore session from backend on mount
  useEffect(() => {
    if (!storyboard && !loading && !restoreAttempted.current) {
      restoreAttempted.current = true;
      api.getCurrentProject()
        .then((sb) => {
          if (sb && sb.total_segments > 0) {
            useProjectStore.setState({ storyboard: sb });
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
        dcDispatch('history:undo', { payload: {} });
      }
      if (mod && e.key === 'z' && e.shiftKey) {
        e.preventDefault();
        dcDispatch('history:redo', { payload: {} });
      }

      // Split at playhead
      if (e.key === 's' && !mod) {
        e.preventDefault();
        const currentMs = useProjectStore.getState().currentTimeMs;
        dcDispatch('active:split', { payload: { time: currentMs } });
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
          const sb = useProjectStore.getState().storyboard;
          const maxFrame = sb ? Math.round(sb.total_duration_seconds * FPS) : Infinity;
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
        const sb = useProjectStore.getState().storyboard;
        if (sb) {
          const maxFrame = Math.round(sb.total_duration_seconds * FPS);
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
