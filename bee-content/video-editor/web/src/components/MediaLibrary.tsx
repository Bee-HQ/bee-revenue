import { useState, useRef, useEffect, useCallback } from 'react';
import type { DownloadScriptInfo, DownloadStatus, DownloadTools, MediaFile } from '../types';
import { useProjectStore } from '../stores/project';
import { api } from '../api/client';

const CATEGORY_ICONS: Record<string, string> = {
  footage: '🎥',
  stock: '📦',
  photos: '📷',
  graphics: '🎨',
  narration: '🎙️',
  maps: '🗺️',
  music: '🎵',
  segments: '🔗',
};

const MEDIA_TYPE_ICON: Record<string, string> = {
  '.mp4': '🎬',
  '.mkv': '🎬',
  '.webm': '🎬',
  '.mov': '🎬',
  '.mp3': '🔊',
  '.wav': '🔊',
  '.m4a': '🔊',
  '.png': '🖼️',
  '.jpg': '🖼️',
  '.jpeg': '🖼️',
  '.webp': '🖼️',
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

function DownloadPanel({ onDone }: { onDone: () => void }) {
  const [scripts, setScripts] = useState<DownloadScriptInfo[]>([]);
  const [tools, setTools] = useState<DownloadTools | null>(null);
  const [statuses, setStatuses] = useState<DownloadStatus[]>([]);
  const [ytUrl, setYtUrl] = useState('');
  const [ytCategory, setYtCategory] = useState('footage');
  const [loading, setLoading] = useState(true);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    Promise.all([api.listDownloadScripts(), api.checkDownloadTools()])
      .then(([s, t]) => {
        setScripts(s);
        setTools(t);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const pollStatus = useCallback(() => {
    if (pollRef.current) return;
    pollRef.current = setInterval(async () => {
      try {
        const s = await api.getDownloadStatus();
        setStatuses(s);
        const anyRunning = s.some(d => d.running);
        if (!anyRunning && pollRef.current) {
          clearInterval(pollRef.current);
          pollRef.current = null;
          onDone();
        }
      } catch { /* ignore */ }
    }, 2000);
  }, [onDone]);

  useEffect(() => () => {
    if (pollRef.current) clearInterval(pollRef.current);
  }, []);

  const runScript = async (script: DownloadScriptInfo) => {
    try {
      await api.runDownloadScript(script.path);
      pollStatus();
      const s = await api.getDownloadStatus();
      setStatuses(s);
    } catch (e: any) {
      alert(e.message);
    }
  };

  const downloadYt = async () => {
    if (!ytUrl.trim()) return;
    try {
      await api.downloadWithYtDlp(ytUrl.trim(), ytCategory);
      setYtUrl('');
      pollStatus();
      const s = await api.getDownloadStatus();
      setStatuses(s);
    } catch (e: any) {
      alert(e.message);
    }
  };

  const createDirs = async () => {
    try {
      await api.createMediaDirs();
      onDone();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const anyRunning = statuses.some(d => d.running);

  if (loading) {
    return <div className="px-3 py-4 text-xs text-gray-500">Checking download tools...</div>;
  }

  return (
    <div className="px-3 py-2 space-y-3">
      {/* Download scripts */}
      {scripts.length > 0 && (
        <div>
          <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1.5">
            Download Scripts
          </div>
          {scripts.map(script => (
            <button
              key={script.path}
              onClick={() => runScript(script)}
              disabled={anyRunning}
              className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs
                         bg-editor-hover hover:bg-editor-accent/20 text-gray-300
                         hover:text-white transition-colors disabled:opacity-50
                         disabled:cursor-not-allowed mb-1"
            >
              <span className="text-green-400">▶</span>
              <span className="truncate">{script.name}</span>
            </button>
          ))}
        </div>
      )}

      {/* yt-dlp download */}
      {tools?.yt_dlp && (
        <div>
          <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1.5">
            Download from URL
          </div>
          <div className="flex gap-1 mb-1">
            <input
              type="text"
              value={ytUrl}
              onChange={e => setYtUrl(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && downloadYt()}
              placeholder="Paste video URL..."
              className="flex-1 bg-editor-surface border border-editor-border rounded px-2 py-1
                         text-xs text-gray-200 placeholder-gray-600 outline-none
                         focus:border-editor-accent/50"
            />
            <select
              value={ytCategory}
              onChange={e => setYtCategory(e.target.value)}
              className="bg-editor-surface border border-editor-border rounded px-1 py-1
                         text-[10px] text-gray-400 outline-none"
            >
              <option value="footage">footage</option>
              <option value="stock">stock</option>
              <option value="music">music</option>
            </select>
          </div>
          <button
            onClick={downloadYt}
            disabled={!ytUrl.trim() || anyRunning}
            className="w-full px-2 py-1 rounded text-xs bg-blue-600/20 text-blue-400
                       hover:bg-blue-600/30 transition-colors disabled:opacity-50
                       disabled:cursor-not-allowed"
          >
            Download with yt-dlp
          </button>
        </div>
      )}

      {/* Create dirs button */}
      <button
        onClick={createDirs}
        className="w-full px-2 py-1 rounded text-xs bg-editor-hover text-gray-400
                   hover:text-gray-200 transition-colors"
      >
        Create media folders
      </button>

      {/* Status */}
      {statuses.length > 0 && (
        <div>
          <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">
            Downloads
          </div>
          {statuses.map(s => (
            <div key={s.task_id} className="mb-2">
              <div className="flex items-center gap-1.5 text-xs">
                {s.running ? (
                  <span className="text-yellow-400 animate-pulse">●</span>
                ) : s.return_code === 0 ? (
                  <span className="text-green-400">✓</span>
                ) : (
                  <span className="text-red-400">✗</span>
                )}
                <span className="text-gray-400 truncate">{s.task_id}</span>
              </div>
              {s.output_lines.length > 0 && (
                <pre className="mt-0.5 px-1.5 py-1 rounded bg-black/30 text-[9px] text-gray-500
                               max-h-16 overflow-y-auto leading-tight font-mono">
                  {s.output_lines.slice(-8).join('\n')}
                </pre>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Tool status */}
      {tools && !tools.yt_dlp && (
        <div className="text-[10px] text-gray-600">
          yt-dlp not found — install with <code className="text-gray-500">pip install yt-dlp</code>
        </div>
      )}
    </div>
  );
}

function MediaThumbnail({ file }: { file: MediaFile }) {
  const isImage = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'].includes(file.extension);
  const isVideo = ['.mp4', '.mkv', '.webm', '.mov', '.avi'].includes(file.extension);

  if (isImage) {
    return (
      <img
        src={api.mediaFileUrl(file.path)}
        alt=""
        className="w-8 h-8 rounded object-cover bg-editor-border shrink-0"
        loading="lazy"
      />
    );
  }

  if (isVideo) {
    return (
      <div className="w-8 h-8 rounded bg-editor-border shrink-0 flex items-center justify-center text-[10px]">
        ▶
      </div>
    );
  }

  return (
    <span className="text-xs shrink-0 w-8 text-center">
      {MEDIA_TYPE_ICON[file.extension] || '📄'}
    </span>
  );
}

export function MediaLibrary() {
  const { mediaFiles, mediaCategories, loadMedia, setDraggedMedia, setPreviewMedia, previewMedia } = useProjectStore();
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [showDownloads, setShowDownloads] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  const categories = Object.keys(mediaCategories);
  const filteredFiles = activeCategory
    ? mediaFiles.filter(f => f.category === activeCategory)
    : mediaFiles;
  const isEmpty = mediaFiles.length === 0;

  const handleDragStart = (file: MediaFile) => {
    setDraggedMedia(file);
  };

  const handleDragEnd = () => {
    setDraggedMedia(null);
  };

  const handleClick = (file: MediaFile) => {
    setPreviewMedia(previewMedia?.path === file.path ? null : file);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;
    setUploading(true);
    for (const file of files) {
      await api.uploadMedia(file, activeCategory || 'footage');
    }
    setUploading(false);
    loadMedia();
    if (fileInput.current) fileInput.current.value = '';
  };

  return (
    <div className="flex flex-col h-full">
      <div className="px-3 py-2 border-b border-editor-border flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Media</h3>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setShowDownloads(!showDownloads)}
            className={`text-xs px-1 transition-colors ${
              showDownloads ? 'text-blue-400' : 'text-gray-500 hover:text-gray-300'
            }`}
            title="Downloads"
          >
            ⬇
          </button>
          <button
            onClick={() => loadMedia()}
            className="text-gray-500 hover:text-gray-300 text-xs px-1"
            title="Refresh"
          >
            ↻
          </button>
          <button
            onClick={() => fileInput.current?.click()}
            className="text-gray-500 hover:text-gray-300 text-xs px-1"
            title="Upload"
          >
            +
          </button>
          <input
            ref={fileInput}
            type="file"
            multiple
            onChange={handleUpload}
            className="hidden"
          />
        </div>
      </div>

      {/* Download panel */}
      {showDownloads && (
        <div className="border-b border-editor-border max-h-64 overflow-y-auto">
          <DownloadPanel onDone={() => loadMedia()} />
        </div>
      )}

      {/* Category tabs */}
      {!isEmpty && (
        <div className="px-2 py-1.5 border-b border-editor-border flex gap-1 flex-wrap">
          <button
            onClick={() => setActiveCategory(null)}
            className={`text-[10px] px-2 py-0.5 rounded-full transition-colors ${
              !activeCategory
                ? 'bg-editor-accent/20 text-blue-400'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            All ({mediaFiles.length})
          </button>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(activeCategory === cat ? null : cat)}
              className={`text-[10px] px-2 py-0.5 rounded-full transition-colors ${
                activeCategory === cat
                  ? 'bg-editor-accent/20 text-blue-400'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {CATEGORY_ICONS[cat] || '📂'} {cat} ({mediaCategories[cat]})
            </button>
          ))}
        </div>
      )}

      {/* File list */}
      <div className="flex-1 overflow-y-auto px-1 py-1">
        {uploading && (
          <div className="px-2 py-1 text-xs text-gray-500">Uploading...</div>
        )}

        {/* Empty state with download prompt */}
        {isEmpty && !uploading && !showDownloads && (
          <div className="px-3 py-6 text-center">
            <div className="text-2xl mb-2">📂</div>
            <div className="text-xs text-gray-400 mb-3">
              No media files found
            </div>
            <button
              onClick={() => setShowDownloads(true)}
              className="px-3 py-1.5 rounded text-xs bg-blue-600/20 text-blue-400
                         hover:bg-blue-600/30 transition-colors mb-2 w-full"
            >
              ⬇ Download media
            </button>
            <button
              onClick={() => fileInput.current?.click()}
              className="px-3 py-1.5 rounded text-xs bg-editor-hover text-gray-400
                         hover:text-gray-200 transition-colors w-full"
            >
              + Upload files
            </button>
          </div>
        )}

        {filteredFiles.length === 0 && !isEmpty && !uploading && (
          <div className="px-2 py-4 text-xs text-gray-600 text-center">
            No files in this category.
          </div>
        )}

        {filteredFiles.map(file => {
          const isActive = previewMedia?.path === file.path;
          return (
            <div
              key={file.path}
              draggable
              onDragStart={() => handleDragStart(file)}
              onDragEnd={handleDragEnd}
              onClick={() => handleClick(file)}
              className={`flex items-center gap-2 px-2 py-1.5 rounded
                         cursor-grab active:cursor-grabbing group transition-colors ${
                           isActive
                             ? 'bg-editor-accent/15 ring-1 ring-editor-accent/30'
                             : 'hover:bg-editor-hover'
                         }`}
            >
              <MediaThumbnail file={file} />
              <div className="min-w-0 flex-1">
                <div className="text-xs text-gray-300 truncate group-hover:text-gray-100">
                  {file.name}
                </div>
                <div className="text-[10px] text-gray-600">
                  {formatSize(file.size_bytes)} · {file.category}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
