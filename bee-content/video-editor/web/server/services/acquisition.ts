import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import { Writable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { Readable } from 'node:stream';
import type { BeeSegment } from '../../shared/types.js';
import { validateUrl, sanitizeFilename } from '../lib/media-utils.js';

// --- Pexels search result ---

export interface StockResult {
  id: number;
  url: string;
  duration: number;
  width: number;
  height: number;
  hd_url: string;
  sd_url: string | null;
}

// --- Pexels video search ---

export async function searchPexels(
  query: string,
  options: { count?: number; minDuration?: number; orientation?: string } = {},
): Promise<StockResult[]> {
  const apiKey = process.env.PEXELS_API_KEY;
  if (!apiKey) throw new Error('PEXELS_API_KEY environment variable is not set');

  const params = new URLSearchParams({
    query,
    per_page: String(Math.min(options.count ?? 5, 80)),
  });
  if (options.orientation) params.set('orientation', options.orientation);

  const response = await fetch(`https://api.pexels.com/videos/search?${params}`, {
    headers: { Authorization: apiKey },
  });

  if (!response.ok) {
    throw new Error(`Pexels API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  const videos: any[] = data.videos ?? [];
  const minDur = options.minDuration ?? 0;

  const results: StockResult[] = [];
  for (const video of videos) {
    if (minDur > 0 && (video.duration ?? 0) < minDur) continue;

    const files: any[] = video.video_files ?? [];
    // Prefer HD MP4, fallback to any MP4
    const hdMp4 = files.find((f: any) => f.quality === 'hd' && f.file_type === 'video/mp4');
    const sdMp4 = files.find((f: any) => f.quality !== 'hd' && f.file_type === 'video/mp4');
    const best = hdMp4 ?? sdMp4;
    if (!best?.link) continue;

    results.push({
      id: video.id,
      url: video.url ?? '',
      duration: video.duration ?? 0,
      width: video.width ?? 0,
      height: video.height ?? 0,
      hd_url: best.link,
      sd_url: sdMp4?.link ?? null,
    });
  }

  return results;
}

// --- Download ---

export async function downloadFile(
  url: string,
  outputPath: string,
): Promise<void> {
  if (!validateUrl(url)) {
    throw new Error(`URL blocked by SSRF validation: ${url}`);
  }

  await fsp.mkdir(path.dirname(outputPath), { recursive: true });

  const response = await fetch(url);
  if (!response.ok || !response.body) {
    throw new Error(`Download failed: ${response.status} ${response.statusText}`);
  }

  const fileStream = fs.createWriteStream(outputPath);
  try {
    await pipeline(Readable.fromWeb(response.body as any), fileStream);
  } catch (err) {
    // Clean up partial file
    try { await fsp.unlink(outputPath); } catch {}
    throw err;
  }
}

// --- Filename generation ---

function makeFilename(id: number, query: string, ext: string = '.mp4'): string {
  const slug = query
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 40);
  return `pexels-${id}-${slug}${ext}`;
}

// --- Batch acquisition ---

export interface AcquisitionReport {
  queries: number;
  matched: number;
  downloaded: number;
  failed: number;
  errors: string[];
}

export async function acquireMedia(
  segments: BeeSegment[],
  projectDir: string,
  options: { perQuery?: number } = {},
): Promise<AcquisitionReport> {
  const report: AcquisitionReport = {
    queries: 0,
    matched: 0,
    downloaded: 0,
    failed: 0,
    errors: [],
  };

  // Collect queries from segments with visual[0].query and no src
  const tasks: Array<{ segId: string; query: string; index: number }> = [];
  for (const seg of segments) {
    for (let i = 0; i < seg.visual.length; i++) {
      const v = seg.visual[i];
      if (v.query && !v.src) {
        tasks.push({ segId: seg.id, query: v.query, index: i });
      }
    }
  }

  report.queries = tasks.length;
  if (tasks.length === 0) return report;

  const stockDir = path.join(projectDir, 'stock');

  for (const task of tasks) {
    try {
      const results = await searchPexels(task.query, {
        count: options.perQuery ?? 3,
        minDuration: 5,
      });

      if (results.length === 0) {
        report.errors.push(`No results for: ${task.query}`);
        continue;
      }
      report.matched++;

      const best = results[0];
      const filename = makeFilename(best.id, task.query);
      const outputPath = path.join(stockDir, filename);

      // Skip if already downloaded
      if (fs.existsSync(outputPath)) {
        report.downloaded++;
        continue;
      }

      await downloadFile(best.hd_url, outputPath);
      report.downloaded++;
    } catch (err) {
      report.failed++;
      report.errors.push(`${task.query}: ${err}`);
    }
  }

  return report;
}
