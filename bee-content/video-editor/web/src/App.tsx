import { useEffect } from 'react';
import { useProjectStore } from './stores/project';
import { Layout } from './components/Layout';
import { LoadProject } from './components/LoadProject';
import { ToastContainer } from './components/ToastContainer';
import { ShortcutsPanel } from './components/ShortcutsPanel';
import { dispatch as dcDispatch } from '@designcombo/events';

export default function App() {
  const storyboard = useProjectStore(s => s.storyboard);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        dcDispatch('history:undo', {});
      }
      if (mod && e.key === 'z' && e.shiftKey) {
        e.preventDefault();
        dcDispatch('history:redo', {});
      }
      if (e.key === 's' && !mod) {
        e.preventDefault();
        const currentMs = useProjectStore.getState().currentTimeMs;
        dcDispatch('active:split', { payload: { time: currentMs } });
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
