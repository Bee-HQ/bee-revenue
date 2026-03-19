import { useState } from 'react';
import { api } from '../api/client';
import { useProjectStore } from '../stores/project';
import { toast } from '../stores/toast';

interface Props {
  segmentId: string;
  layer: 'visual' | 'audio';
  index: number;
  downloadUrl?: string;
  pexelsUrl?: string;
  query?: string;
  hasSrc: boolean;
}

export function DownloadButton({ segmentId, layer, index, downloadUrl, pexelsUrl, query, hasSrc }: Props) {
  const [status, setStatus] = useState<'idle' | 'downloading' | 'done' | 'error'>('idle');
  const [message, setMessage] = useState('');

  // Nothing to download
  if (!downloadUrl && !pexelsUrl && !query) return null;
  // Already has a local file and no explicit download URL
  if (hasSrc && !downloadUrl && !pexelsUrl) return null;

  const handleDownload = async () => {
    setStatus('downloading');
    setMessage('');
    try {
      const result = await api.downloadEntry(segmentId, layer, index);
      if (result.status === 'search_needed') {
        setStatus('idle');
        setMessage(`Search: "${result.query}"`);
      } else if (result.path) {
        const filename = result.path.split('/').pop() || 'Downloaded';
        setStatus('done');
        setMessage(filename);
        toast.success(`Downloaded: ${filename}`);
        // Refresh project to pick up the new src
        const storyboard = await api.getCurrentProject();
        useProjectStore.setState({ storyboard });
      }
    } catch (err: unknown) {
      setStatus('error');
      const msg = err instanceof Error ? err.message : 'Download failed';
      setMessage(msg);
      toast.error(`Download failed: ${msg}`);
    }
    setTimeout(() => {
      setStatus((prev) => (prev !== 'downloading' ? 'idle' : prev));
      setMessage('');
    }, 5000);
  };

  const icon = status === 'downloading' ? '...' : status === 'done' ? '\u2713' : status === 'error' ? '!' : '\u2B07';
  const colors: Record<typeof status, string> = {
    idle: 'text-gray-500 hover:text-blue-400 hover:bg-blue-500/10',
    downloading: 'text-yellow-400 bg-yellow-500/10',
    done: 'text-green-400 bg-green-500/10',
    error: 'text-red-400 bg-red-500/10',
  };

  return (
    <span className="inline-flex items-center gap-1">
      <button
        onClick={(e) => { e.stopPropagation(); handleDownload(); }}
        disabled={status === 'downloading'}
        className={`text-[10px] px-1 py-0.5 rounded transition-colors ${colors[status]}`}
        title={downloadUrl || pexelsUrl || `Search: ${query}`}
      >
        {icon}
      </button>
      {message && <span className="text-[9px] text-gray-500">{message}</span>}
    </span>
  );
}
