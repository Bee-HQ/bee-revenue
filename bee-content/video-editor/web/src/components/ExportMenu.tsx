import { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';
import { toast } from '../stores/toast';
import { FileText, FileVideo, Film, Package, ChevronDown } from 'lucide-react';

export function ExportMenu() {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState('');
  const [rendering, setRendering] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleExportMd = async () => {
    setOpen(false);
    setStatus('Exporting...');
    try {
      const result = await api.exportMarkdown();
      // Trigger browser download
      const blob = new Blob([result.content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'storyboard.md';
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setStatus('Markdown exported');
      toast.success('Markdown exported');
    } catch (err: any) {
      setStatus(`Error: ${err.message}`);
      toast.error(`Export failed: ${err.message}`);
    }
    setTimeout(() => setStatus(''), 3000);
  };

  const handleExportOtio = async () => {
    setOpen(false);
    setStatus('Exporting...');
    try {
      const result = await api.exportOtio();
      const msg = `OTIO saved to ${result.path}`;
      setStatus(msg);
      toast.success(msg);
    } catch (err: any) {
      setStatus(`Error: ${err.message}`);
      toast.error(`Export failed: ${err.message}`);
    }
    setTimeout(() => setStatus(''), 5000);
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white px-2.5 py-1 rounded
                   border border-editor-border hover:border-gray-500 transition-colors"
      >
        Export
        <ChevronDown size={11} />
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1 bg-editor-surface border border-editor-border
                        rounded-lg shadow-lg py-1 w-48 z-50">
          <button
            onClick={handleExportMd}
            className="w-full text-left px-3 py-1.5 text-xs text-gray-300 hover:bg-editor-hover flex items-start gap-2"
          >
            <FileText size={14} className="text-gray-500 shrink-0 mt-0.5" />
            <div>
              Export Markdown
              <span className="block text-gray-500 text-[10px]">For review & version control</span>
            </div>
          </button>
          <button
            onClick={handleExportOtio}
            className="w-full text-left px-3 py-1.5 text-xs text-gray-300 hover:bg-editor-hover flex items-start gap-2"
          >
            <FileVideo size={14} className="text-gray-500 shrink-0 mt-0.5" />
            <div>
              Export for NLE
              <span className="block text-gray-500 text-[10px]">Clean OTIO for DaVinci/Premiere</span>
            </div>
          </button>
          <div className="border-t border-editor-border my-1" />
          <button
            onClick={async () => {
              setOpen(false);
              setRendering(true);
              setStatus('Rendering with Remotion...');
              toast.info('Rendering with Remotion — this may take a few minutes...');
              try {
                const r = await api.renderRemotion();
                const msg = `Rendered: ${(r.size_bytes / 1024 / 1024).toFixed(1)} MB`;
                setStatus(msg);
                toast.success(msg);
              } catch (err: any) {
                setStatus(`Error: ${err.message}`);
                toast.error(`Render failed: ${err.message}`);
              } finally {
                setRendering(false);
              }
              setTimeout(() => setStatus(''), 5000);
            }}
            disabled={rendering}
            className={`w-full text-left px-3 py-1.5 text-xs hover:bg-editor-hover flex items-start gap-2 ${rendering ? 'text-gray-500 cursor-wait' : 'text-gray-300'}`}
          >
            <Film size={14} className="text-gray-500 shrink-0 mt-0.5" />
            <div>
              {rendering ? 'Rendering...' : 'Render with Remotion'}
              <span className="block text-gray-500 text-[10px]">
                {rendering ? 'This may take a few minutes' : 'Full quality MP4 with overlays'}
              </span>
            </div>
          </button>
          <button
            onClick={() => { setOpen(false); setStatus('Use Assemble in the production bar'); setTimeout(() => setStatus(''), 3000); }}
            className="w-full text-left px-3 py-1.5 text-xs text-gray-300 hover:bg-editor-hover flex items-start gap-2"
          >
            <Package size={14} className="text-gray-500 shrink-0 mt-0.5" />
            <div>
              Export Final Video
              <span className="block text-gray-500 text-[10px]">Assemble via production pipeline</span>
            </div>
          </button>
        </div>
      )}

      {status && (
        <span className="absolute right-0 top-full mt-8 text-[10px] text-gray-400 whitespace-nowrap">
          {status}
        </span>
      )}
    </div>
  );
}
