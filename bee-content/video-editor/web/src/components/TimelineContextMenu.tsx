import { useEffect, useRef } from 'react';
import { Trash2, Copy, ClipboardPaste, CopyPlus, Scissors } from 'lucide-react';
import { useProjectStore } from '../stores/project';

interface Props {
  x: number;
  y: number;
  actionId: string;
  onClose: () => void;
}

export function TimelineContextMenu({ x, y, actionId: _actionId, onClose }: Props) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) onClose();
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [onClose]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  const items = [
    { label: 'Split', icon: Scissors, action: () => { useProjectStore.getState().splitAtPlayhead(); onClose(); } },
    { label: 'Duplicate', icon: CopyPlus, action: () => { useProjectStore.getState().duplicateSelectedActions(); onClose(); } },
    { label: 'Copy', icon: Copy, action: () => { useProjectStore.getState().copySelectedActions(); onClose(); } },
    { label: 'Paste', icon: ClipboardPaste, action: () => { useProjectStore.getState().pasteClipboard(); onClose(); } },
    null, // separator
    { label: 'Delete', icon: Trash2, action: () => { useProjectStore.getState().deleteSelectedActions(); onClose(); }, danger: true },
  ];

  return (
    <div
      ref={menuRef}
      className="fixed z-50 bg-editor-surface border border-editor-border rounded-md shadow-xl py-1 min-w-[160px]"
      style={{ left: x, top: y }}
    >
      {items.map((item, i) =>
        item === null ? (
          <div key={i} className="border-t border-editor-border my-1" />
        ) : (
          <button
            key={item.label}
            onClick={item.action}
            className={`w-full flex items-center gap-2 px-3 py-1.5 text-[11px] text-left hover:bg-editor-hover transition-colors ${
              (item as any).danger ? 'text-red-400 hover:text-red-300' : 'text-gray-300'
            }`}
          >
            <item.icon size={12} />
            {item.label}
          </button>
        )
      )}
    </div>
  );
}
