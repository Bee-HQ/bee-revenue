import { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';
import { toast } from '../stores/toast';
import { FolderOpen, ImageIcon, Mic, Captions, ClipboardCheck, Layers, Film, ChevronUp } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

const ACTIONS: [string, () => Promise<unknown>, LucideIcon][] = [
  ['Init Dirs', () => api.initProject(), FolderOpen],
  ['Graphics', () => api.generateGraphics(), ImageIcon],
  ['Narration', () => api.generateNarration(), Mic],
  ['Captions', () => api.generateCaptions(), Captions],
  ['Preflight', () => api.getPreflight(), ClipboardCheck],
  ['Composite', () => api.compositeSegments(), Layers],
  ['Assemble', () => api.assembleVideo(), Film],
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
        className="flex items-center gap-1.5 text-[11px] bg-editor-hover text-gray-300 hover:bg-editor-border px-2.5 py-1 rounded transition-colors"
      >
        Pipeline
        <ChevronUp size={11} className={`transition-transform ${open ? '' : 'rotate-180'}`} />
      </button>
      {open && (
        <div className="absolute left-0 bottom-full mb-1 bg-editor-surface border border-editor-border rounded-lg shadow-lg py-1 w-44 z-50">
          {ACTIONS.map(([name, action, Icon]) => (
            <button
              key={name}
              onClick={() => run(name, action)}
              className="w-full text-left px-3 py-1.5 text-[11px] text-gray-300 hover:bg-editor-hover flex items-center gap-2"
            >
              <Icon size={12} className="text-gray-500" />
              {name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
