import fs from 'node:fs';
import path from 'node:path';
import type { BeeProject } from '../../shared/types.js';

// --- Tokenization ---

const STOPWORDS = new Set([
  'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'is', 'it',
  'and', 'or', 'but', 'not', 'no', 'by', 'with', 'from', 'as', 'be',
  'was', 'were', 'are', 'been', 'has', 'had', 'have', 'do', 'does',
  'did', 'will', 'can', 'may', 'this', 'that', 'into', 'over', 'then',
  'than', 'its', 'his', 'her', 'our', 'all', 'also', 'just', 'about',
]);

const MEDIA_EXTS = new Set([
  'mp4', 'mkv', 'avi', 'mov', 'webm', 'jpg', 'jpeg', 'png', 'webp',
  'mp3', 'wav', 'aac', 'm4a', 'ogg', 'flac',
]);

export function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter(w => w.length >= 3 && !STOPWORDS.has(w));
}

// --- File scanning ---

function scanMediaFiles(dirs: string[]): Array<{ absPath: string; relPath: string; tokens: string[] }> {
  const files: Array<{ absPath: string; relPath: string; tokens: string[] }> = [];

  function walk(dir: string, baseDir: string) {
    let entries: string[];
    try {
      entries = fs.readdirSync(dir);
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.startsWith('.')) continue;
      const absPath = path.join(dir, entry);
      try {
        const stat = fs.statSync(absPath);
        if (stat.isDirectory()) {
          walk(absPath, baseDir);
        } else if (stat.isFile()) {
          const ext = path.extname(entry).slice(1).toLowerCase();
          if (!MEDIA_EXTS.has(ext)) continue;
          const relPath = path.relative(baseDir, absPath);
          const nameNoExt = path.basename(entry, path.extname(entry));
          files.push({ absPath, relPath, tokens: tokenize(nameNoExt) });
        }
      } catch {
        continue;
      }
    }
  }

  for (const dir of dirs) {
    walk(dir, path.dirname(dir));
  }

  return files;
}

// --- Scoring ---

function scoreMatch(descTokens: string[], fileTokens: string[]): number {
  if (descTokens.length === 0 || fileTokens.length === 0) return 0;
  const fileSet = new Set(fileTokens);
  let overlap = 0;
  for (const t of descTokens) {
    if (fileSet.has(t)) overlap++;
  }
  return overlap / Math.min(descTokens.length, fileTokens.length);
}

// --- Auto-assign ---

export interface AssignmentResult {
  assigned: number;
  unmatched: number;
  conflicts: string[];
}

export function autoAssignMedia(
  project: BeeProject,
  projectDir: string,
  minConfidence: number = 0.1,
): AssignmentResult {
  // Scan media directories
  const mediaDirs = [
    'footage', 'stock', 'photos', 'graphics', 'narration',
    'maps', 'music', 'generated',
  ].map(d => path.join(projectDir, d));

  const inventory = scanMediaFiles(mediaDirs);
  const useCounts = new Map<string, number>();
  let assigned = 0;
  let unmatched = 0;
  const conflicts: string[] = [];

  for (const seg of project.segments) {
    for (let i = 0; i < seg.visual.length; i++) {
      const entry = seg.visual[i];
      if (entry.src) continue; // already assigned

      // Build description from segment title, section, query, type
      const descText = [seg.title, seg.section, entry.query || '', entry.type || ''].join(' ');
      const descTokens = tokenize(descText);

      let bestFile: (typeof inventory)[0] | null = null;
      let bestScore = 0;

      for (const file of inventory) {
        let score = scoreMatch(descTokens, file.tokens);
        if (score < minConfidence) continue;

        // Reuse penalty
        const uses = useCounts.get(file.relPath) ?? 0;
        score *= Math.max(0.3, 1.0 - uses * 0.2);

        if (score > bestScore) {
          bestScore = score;
          bestFile = file;
        }
      }

      if (bestFile) {
        entry.src = bestFile.relPath;
        const uses = (useCounts.get(bestFile.relPath) ?? 0) + 1;
        useCounts.set(bestFile.relPath, uses);
        if (uses > 3 && !conflicts.includes(bestFile.relPath)) {
          conflicts.push(bestFile.relPath);
        }
        assigned++;
      } else {
        unmatched++;
      }
    }
  }

  return { assigned, unmatched, conflicts };
}
