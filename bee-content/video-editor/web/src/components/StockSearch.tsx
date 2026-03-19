import { useState } from 'react';
import { api } from '../api/client';
import { useProjectStore } from '../stores/project';
import { toast } from '../stores/toast';

interface StockResult {
  id: number;
  url: string;
  duration: number;
  width: number;
  height: number;
  hd_url: string;
  sd_url: string;
}

export function StockSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<StockResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [downloading, setDownloading] = useState<number | null>(null);
  const loadMedia = useProjectStore(s => s.loadMedia);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    try {
      const r = await api.searchStock(query.trim());
      setResults(r.results);
      if (r.results.length === 0) {
        toast.info('No stock footage found');
      }
    } catch (err: any) {
      toast.error(`Stock search failed: ${err.message}`);
    } finally {
      setSearching(false);
    }
  };

  const handleDownload = async (result: StockResult) => {
    setDownloading(result.id);
    try {
      const filename = `pexels-${result.id}-${result.width}x${result.height}.mp4`;
      const r = await api.downloadStock(result.hd_url || result.sd_url, filename);
      toast.success(`Downloaded: ${r.name}`);
      loadMedia();
    } catch (err: any) {
      toast.error(`Download failed: ${err.message}`);
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="p-2 space-y-2">
      <div className="flex gap-1">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
          placeholder="Search Pexels..."
          className="flex-1 bg-editor-bg border border-editor-border rounded px-2 py-1 text-xs
                     focus:outline-none focus:border-editor-accent"
        />
        <button
          onClick={handleSearch}
          disabled={searching || !query.trim()}
          className="bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded text-xs
                     disabled:opacity-50"
        >
          {searching ? '...' : '🔍'}
        </button>
      </div>

      {results.length > 0 && (
        <div className="space-y-1 max-h-64 overflow-y-auto">
          {results.map(r => (
            <div key={r.id} className="flex items-center gap-2 bg-editor-bg rounded p-1.5 border border-editor-border">
              <div className="flex-1 min-w-0">
                <div className="text-[10px] text-gray-300 truncate">
                  Pexels #{r.id}
                </div>
                <div className="text-[10px] text-gray-500">
                  {r.duration}s · {r.width}×{r.height}
                </div>
              </div>
              <a
                href={r.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[10px] text-blue-400 hover:text-blue-300"
                onClick={e => e.stopPropagation()}
              >
                preview
              </a>
              <button
                onClick={() => handleDownload(r)}
                disabled={downloading === r.id}
                className="text-[10px] px-1.5 py-0.5 rounded bg-green-600/20 text-green-400
                           hover:bg-green-600/30 disabled:opacity-50"
              >
                {downloading === r.id ? '...' : '⬇ HD'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
