import { useState, useCallback } from 'react';
import { useProjectStore } from '../stores/project';
import { api } from '../api/client';
import { toast } from '../stores/toast';
import type { Segment } from '../types';
import { Search, Captions, Palette } from 'lucide-react';

const COLOR_SUGGESTIONS: Record<string, string> = {
  'night': 'surveillance',
  'dark': 'dark_crime',
  'court': 'cold_blue',
  'police': 'bodycam',
  'victim': 'warm_victim',
  'old': 'vintage',
  'photo': 'sepia',
  'farm': 'golden_hour',
  'vhs': 'vhs',
  'tape': 'vhs',
  'evidence': 'bleach_bypass',
};

export function AIPanel() {
  const project = useProjectStore(s => s.project);
  const activeClipId = useProjectStore(s => s.activeClipId);

  // Find the selected segment from the active clip id
  const segmentId = activeClipId?.match(/^(.+)-(v|nar|audio|music|ov)-/)?.[1];
  const segment = project?.segments.find(s => s.id === segmentId) ?? null;

  return (
    <div className="flex flex-col h-full">
      <div className="px-3 py-2 bg-editor-surface border-b border-editor-border">
        <div className="text-[10px] font-bold text-gray-300">AI Tools</div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        <BRollSection segment={segment} />
        <CaptionSection />
        <ColorSuggestSection segment={segment} />
      </div>
    </div>
  );
}

// --- B-Roll Section ---

function BRollSection({ segment }: { segment: Segment | null }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Array<{ id: number; duration: number; width: number; height: number; hd_url: string; sd_url: string }>>([]);
  const [searching, setSearching] = useState(false);
  const [downloading, setDownloading] = useState<number | null>(null);

  // Auto-populate query from narration text
  const narText = segment?.audio?.find(a => a.type === 'NAR')?.text || '';

  const handleSearch = async () => {
    const q = query || narText.substring(0, 50);
    if (!q.trim()) {
      toast.info('No search query -- select a segment with narration');
      return;
    }
    setSearching(true);
    try {
      const r = await api.searchStock(q.trim(), 5);
      setResults(r.results);
      if (r.results.length === 0) toast.info('No stock footage found');
    } catch (e: unknown) {
      toast.error(`Search failed: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setSearching(false);
    }
  };

  const handleDownloadAndAssign = async (result: { id: number; hd_url: string; sd_url: string }) => {
    if (!segment) return;
    setDownloading(result.id);
    try {
      const filename = `broll-${result.id}-${segment.id}.mp4`;
      const r = await api.downloadStock(result.hd_url || result.sd_url, filename);
      await api.assignMedia(segment.id, 'visual', r.path, 0);
      toast.success(`B-Roll assigned: ${r.name}`);
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
    } catch (e: unknown) {
      toast.error(`Download failed: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div>
      <div className="flex items-center gap-1.5 text-[9px] text-gray-500 uppercase tracking-wider mb-2">
        <Search size={10} />
        AI B-Roll
      </div>
      {segment ? (
        <>
          <div className="flex gap-1 mb-2">
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              placeholder={narText ? narText.substring(0, 30) + '...' : 'Search query...'}
              className="flex-1 bg-editor-bg border border-editor-border rounded px-2 py-1 text-[10px] focus:border-editor-accent outline-none"
            />
            <button
              onClick={handleSearch}
              disabled={searching}
              className="bg-editor-hover text-gray-300 hover:bg-editor-border px-2 py-1 rounded text-[10px] disabled:opacity-50"
            >
              {searching ? '...' : 'Go'}
            </button>
          </div>

          {narText && !query && (
            <button
              onClick={() => { setQuery(narText.substring(0, 50)); handleSearch(); }}
              className="text-[9px] text-blue-400 hover:text-blue-300 mb-2 block"
            >
              Auto-search from narration
            </button>
          )}

          {results.length > 0 && (
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {results.map(r => (
                <div key={r.id} className="flex items-center gap-2 bg-editor-bg rounded p-1.5 border border-editor-border">
                  <div className="flex-1 min-w-0">
                    <div className="text-[9px] text-gray-400">{r.duration}s · {r.width}x{r.height}</div>
                  </div>
                  <button
                    onClick={() => handleDownloadAndAssign(r)}
                    disabled={downloading === r.id}
                    className="text-[9px] px-1.5 py-0.5 rounded bg-green-600/20 text-green-400 hover:bg-green-600/30 disabled:opacity-50"
                  >
                    {downloading === r.id ? '...' : '+ Assign'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <div className="text-[10px] text-gray-600 italic">Select a clip to search B-Roll</div>
      )}
    </div>
  );
}

// --- Caption Section ---

function CaptionSection() {
  const [style, setStyle] = useState<'karaoke' | 'phrase'>('karaoke');
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await api.generateCaptions(style);
      toast.success(`Captions generated (${style} style)`);
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
    } catch (e: unknown) {
      toast.error(`Caption generation failed: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div>
      <div className="flex items-center gap-1.5 text-[9px] text-gray-500 uppercase tracking-wider mb-2">
        <Captions size={10} />
        AI Captions
      </div>
      <div className="flex items-center gap-2 mb-2">
        <select
          value={style}
          onChange={e => setStyle(e.target.value as 'karaoke' | 'phrase')}
          className="flex-1 bg-editor-bg border border-editor-border rounded px-2 py-1 text-[10px] text-gray-300"
        >
          <option value="karaoke">Karaoke (word-by-word)</option>
          <option value="phrase">Phrase (3-5 words)</option>
        </select>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 px-3 py-1 rounded text-[10px] disabled:opacity-50"
        >
          {generating ? 'Generating...' : 'Generate'}
        </button>
      </div>
      <div className="text-[9px] text-gray-600">
        Captions render live in the Remotion preview. Generated captions also export with the final video.
      </div>
    </div>
  );
}

// --- Auto Color Grade Section ---

function ColorSuggestSection({ segment }: { segment: Segment | null }) {
  const suggestColor = useCallback((seg: Segment | null): string | null => {
    if (!seg) return null;
    const text = [
      seg.title,
      ...seg.visual.map(v => v.src || ''),
      ...seg.audio.map(a => a.text || a.src || ''),
    ].join(' ').toLowerCase();

    for (const [keyword, preset] of Object.entries(COLOR_SUGGESTIONS)) {
      if (text.includes(keyword)) return preset;
    }
    return 'dark_crime'; // default for true crime
  }, []);

  const suggested = suggestColor(segment);

  const handleApply = async () => {
    if (!segment || !suggested) return;
    try {
      await api.updateSegment(segment.id, {
        visual_updates: [{ index: 0, color: suggested }],
      });
      toast.success(`Applied color: ${suggested}`);
      const sb = await api.getCurrentProject();
      useProjectStore.setState({ project: sb });
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : String(e));
    }
  };

  const handleApplyAll = async () => {
    const storyboard = useProjectStore.getState().project;
    if (!storyboard) return;
    let applied = 0;
    for (const seg of storyboard.segments) {
      const color = suggestColor(seg);
      if (color && seg.visual.length > 0) {
        try {
          await api.updateSegment(seg.id, { visual_updates: [{ index: 0, color }] });
          applied++;
        } catch { /* skip */ }
      }
    }
    toast.success(`Applied color grades to ${applied} segments`);
    const sb = await api.getCurrentProject();
    useProjectStore.setState({ project: sb });
  };

  return (
    <div>
      <div className="flex items-center gap-1.5 text-[9px] text-gray-500 uppercase tracking-wider mb-2">
        <Palette size={10} />
        Auto Color Grade
      </div>
      {segment ? (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-gray-400">Suggested:</span>
            <span className="text-[10px] text-yellow-400 font-mono">{suggested || 'none'}</span>
            <button
              onClick={handleApply}
              className="text-[9px] bg-yellow-600/20 text-yellow-400 hover:bg-yellow-600/30 px-2 py-0.5 rounded"
            >
              Apply
            </button>
          </div>
          <button
            onClick={handleApplyAll}
            className="text-[9px] text-gray-500 hover:text-gray-300 underline"
          >
            Apply smart colors to all segments
          </button>
        </div>
      ) : (
        <div className="text-[10px] text-gray-600 italic">Select a clip for color suggestions</div>
      )}
    </div>
  );
}
