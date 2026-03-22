import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { execFile } from 'node:child_process';
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

  async function scanDir(absDir: string, category: string): Promise<void> {
    let entries: string[];
    try {
      entries = await fs.readdir(absDir);
    } catch {
      return;
    }

    for (const entry of entries) {
      if (entry.startsWith('.')) continue;
      const absPath = path.join(absDir, entry);
      let stat: Awaited<ReturnType<typeof fs.stat>>;
      try {
        stat = await fs.stat(absPath);
      } catch {
        continue;
      }

      if (stat.isDirectory()) {
        await scanDir(absPath, category);
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

  for (const { relDir, category } of dirsToScan) {
    await scanDir(path.join(projectDir, relDir), category);
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

export function probeDuration(filePath: string): Promise<number | null> {
  return new Promise((resolve) => {
    execFile(
      'ffprobe',
      ['-v', 'quiet', '-print_format', 'json', '-show_format', filePath],
      { timeout: 10000 },
      (error, stdout) => {
        if (error) {
          resolve(null);
          return;
        }
        try {
          const data = JSON.parse(stdout);
          const duration = parseFloat(data?.format?.duration);
          resolve(isNaN(duration) ? null : duration);
        } catch {
          resolve(null);
        }
      },
    );
  });
}

const PRIVATE_IP_RANGES = [
  /^127\./, /^10\./, /^172\.(1[6-9]|2\d|3[01])\./, /^192\.168\./,
  /^0\./, /^169\.254\./, /^fc00:/i, /^fe80:/i, /^::1$/, /^localhost$/i,
];

export function validateUrl(url: string): boolean {
  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    return false;
  }
  if (parsed.protocol !== 'https:') return false;
  const hostname = parsed.hostname;
  for (const pattern of PRIVATE_IP_RANGES) {
    if (pattern.test(hostname)) return false;
  }
  return true;
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
