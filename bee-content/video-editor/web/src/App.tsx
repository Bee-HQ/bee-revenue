import { useEffect } from 'react';
import { useProjectStore } from './stores/project';
import { Layout } from './components/Layout';
import { LoadProject } from './components/LoadProject';
import { ToastContainer } from './components/ToastContainer';
import { ShortcutsPanel } from './components/ShortcutsPanel';

export default function App() {
  const storyboard = useProjectStore(s => s.storyboard);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        useProjectStore.getState().undo();
      }
      if (mod && e.key === 'z' && e.shiftKey) {
        e.preventDefault();
        useProjectStore.getState().redo();
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
