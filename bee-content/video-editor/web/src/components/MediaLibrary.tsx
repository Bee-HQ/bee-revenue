import { useState, useRef } from 'react';
import type { MediaFile } from '../types';
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

export function MediaLibrary() {
  const { mediaFiles, mediaCategories, loadMedia, setDraggedMedia } = useProjectStore();
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  const categories = Object.keys(mediaCategories);
  const filteredFiles = activeCategory
    ? mediaFiles.filter(f => f.category === activeCategory)
    : mediaFiles;

  const handleDragStart = (file: MediaFile) => {
    setDraggedMedia(file);
  };

  const handleDragEnd = () => {
    setDraggedMedia(null);
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

      {/* Category tabs */}
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

      {/* File list */}
      <div className="flex-1 overflow-y-auto px-1 py-1">
        {uploading && (
          <div className="px-2 py-1 text-xs text-gray-500">Uploading...</div>
        )}
        {filteredFiles.length === 0 && !uploading && (
          <div className="px-2 py-4 text-xs text-gray-600 text-center">
            No media files found.
            <br />
            Add files to your project directory.
          </div>
        )}
        {filteredFiles.map(file => (
          <div
            key={file.path}
            draggable
            onDragStart={() => handleDragStart(file)}
            onDragEnd={handleDragEnd}
            className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-editor-hover
                       cursor-grab active:cursor-grabbing group transition-colors"
          >
            <span className="text-xs shrink-0">
              {MEDIA_TYPE_ICON[file.extension] || '📄'}
            </span>
            <div className="min-w-0 flex-1">
              <div className="text-xs text-gray-300 truncate group-hover:text-gray-100">
                {file.name}
              </div>
              <div className="text-[10px] text-gray-600">
                {formatSize(file.size_bytes)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
