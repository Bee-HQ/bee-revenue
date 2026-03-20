import { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';
import { toast } from '../stores/toast';

const ACTIONS: [string, () => Promise<unknown>][] = [
  ['Init Dirs', () => api.initProject()],
  ['Graphics', () => api.generateGraphics()],
  ['Narration', () => api.generateNarration()],
  ['Captions', () => api.generateCaptions()],
  ['Preflight', () => api.getPreflight()],
  ['Composite', () => api.compositeSegments()],
  ['Assemble', () => api.assembleVideo()],
];

export function ProductionDropdown() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node))
        setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const run = async (name: string, action: () => Promise<unknown>) => {
    setOpen(false);
    toast.info(`${name}: starting...`);
    try {
      await action();
      toast.success(`${name}: done`);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      toast.error(`${name} failed: ${msg}`);
    }
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="text-[10px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded"
      >
        Pipeline
      </button>
      {open && (
        <div className="absolute left-0 bottom-full mb-1 bg-editor-surface border border-editor-border rounded-lg shadow-lg py-1 w-40 z-50">
          {ACTIONS.map(([name, action]) => (
            <button
              key={name}
              onClick={() => run(name, action)}
              className="w-full text-left px-3 py-1.5 text-[10px] text-gray-300 hover:bg-editor-hover"
            >
              {name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
