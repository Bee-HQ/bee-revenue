import { useState, useEffect } from 'react';

const SHORTCUTS = [
  { keys: ['Ctrl', 'Z'], desc: 'Undo' },
  { keys: ['Ctrl', 'Shift', 'Z'], desc: 'Redo' },
  { keys: ['Space'], desc: 'Play / Pause' },
  { keys: ['J'], desc: 'Step back 5 frames' },
  { keys: ['K'], desc: 'Pause' },
  { keys: ['L'], desc: 'Play forward' },
  { keys: ['←'], desc: 'Skip back 1s' },
  { keys: ['→'], desc: 'Skip forward 1s' },
  { keys: ['Home'], desc: 'Go to start' },
  { keys: ['End'], desc: 'Go to end' },
  { keys: ['S'], desc: 'Split at playhead' },
  { keys: ['I'], desc: 'Set loop in' },
  { keys: ['O'], desc: 'Set loop out' },
  { keys: ['Esc'], desc: 'Close panel' },
  { keys: ['?'], desc: 'Toggle this panel' },
];

export function ShortcutsPanel() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Don't trigger when typing in inputs
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLSelectElement) return;
      if (e.key === '?') {
        e.preventDefault();
        setOpen(o => !o);
      }
      if (e.key === 'Escape' && open) {
        setOpen(false);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={() => setOpen(false)}>
      <div className="bg-editor-surface border border-editor-border rounded-xl p-6 w-80 shadow-2xl" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-bold text-gray-200">Keyboard Shortcuts</h2>
          <button onClick={() => setOpen(false)} className="text-gray-500 hover:text-gray-300 text-lg">×</button>
        </div>
        <div className="space-y-2">
          {SHORTCUTS.map((s, i) => (
            <div key={i} className="flex items-center justify-between">
              <span className="text-xs text-gray-400">{s.desc}</span>
              <div className="flex gap-1">
                {s.keys.map((k, j) => (
                  <kbd key={j} className="px-1.5 py-0.5 text-[10px] bg-editor-bg border border-editor-border rounded text-gray-300 font-mono">
                    {k}
                  </kbd>
                ))}
              </div>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-gray-600 mt-4 text-center">Press ? or Esc to close</p>
      </div>
    </div>
  );
}
