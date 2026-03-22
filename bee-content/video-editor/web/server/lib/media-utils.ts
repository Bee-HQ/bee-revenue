import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import type { MediaFile } from '../../shared/types.js';

const MEDIA_DIRS = [
  'footage',
  'stock',
  'photos',
  'graphics',
  'narration',
  'maps',
  'music',
  'generated',
];

const SEGMENTS_DIR = 'output/segments';

export async function listMediaFiles(
  projectDir: string,
): Promise<{ files: MediaFile[]; categories: Record<string, number> }> {
  const files: MediaFile[] = [];
  const categories: Record<string, number> = {};

  const dirsToScan: Array<{ relDir: string; category: string }> = [
    ...MEDIA_DIRS.map((d) => ({ relDir: d, category: d })),
    { relDir: SEGMENTS_DIR, category: 'segments' },
  ];

  for (const { relDir, category } of dirsToScan) {
    const absDir = path.join(projectDir, relDir);

    let entries: string[];
    try {
      entries = await fs.readdir(absDir);
    } catch {
      // Directory doesn't exist — skip silently
      continue;
    }

    for (const entry of entries) {
      const absPath = path.join(absDir, entry);
      let stat: Awaited<ReturnType<typeof fs.stat>>;
      try {
        stat = await fs.stat(absPath);
      } catch {
        continue;
      }

      if (!stat.isFile()) continue;

      const ext = path.extname(entry).replace(/^\./, '').toLowerCase();
      const relativePath = path.relative(projectDir, absPath);

      files.push({
        name: entry,
        path: absPath,
        relative_path: relativePath,
        size_bytes: stat.size,
        category,
        extension: ext,
      });

      categories[category] = (categories[category] ?? 0) + 1;
    }
  }

  return { files, categories };
}

export function validatePath(filePath: string, projectDir: string): boolean {
  const resolved = path.resolve(projectDir, filePath);
  const resolvedDir = path.resolve(projectDir);
  return resolved.startsWith(resolvedDir + path.sep) || resolved === resolvedDir;
}

export function sanitizeFilename(name: string): string {
  if (name === '.' || name === '..') {
    throw new Error(`Invalid filename: "${name}"`);
  }
  if (name.startsWith('.')) {
    throw new Error(`Hidden filenames are not allowed: "${name}"`);
  }

  const cleaned = name.replace(/[/\\]/g, '-');

  if (cleaned.length === 0) {
    throw new Error('Filename is empty after sanitization');
  }

  return cleaned;
}

export function categorizeFile(ext: string): 'video' | 'audio' | 'image' {
  const normalized = ext.toLowerCase();

  const VIDEO_EXTS = new Set(['mp4', 'mov', 'webm', 'avi', 'mkv']);
  const AUDIO_EXTS = new Set(['mp3', 'wav', 'aac', 'm4a', 'ogg', 'flac']);
  const IMAGE_EXTS = new Set(['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg']);

  if (VIDEO_EXTS.has(normalized)) return 'video';
  if (AUDIO_EXTS.has(normalized)) return 'audio';
  if (IMAGE_EXTS.has(normalized)) return 'image';

  return 'video';
}
