import { Router } from 'express';
import path from 'node:path';
import fs from 'node:fs/promises';
import multer from 'multer';
import { store } from '../services/project-store.js';
import { execFileSync } from 'node:child_process';
import { readdir } from 'node:fs/promises';
import { listMediaFiles, validatePath, validateUrl, sanitizeFilename, categorizeFile, probeDuration } from '../lib/media-utils.js';
import { searchPexels, downloadFile } from '../services/acquisition.js';
import { runSubprocess, getAllTasks } from '../services/download-tasks.js';

export const mediaRoutes = Router();

const upload = multer({ dest: '/tmp/bee-uploads/' });

// ---------- Helper ----------

function notImplemented(detail: string) {
  return (_req: any, res: any) => res.status(501).json({ detail });
}

// ---------- GET / — list media ----------

mediaRoutes.get('/', async (_req, res, next) => {
  try {
    const projectDir = store.getProjectDir();
    const result = await listMediaFiles(projectDir);
    res.json(result);
  } catch (err) {
    next(err);
  }
});

// ---------- POST /upload ----------

mediaRoutes.post('/upload', upload.single('file'), async (req, res, next) => {
  try {
    const projectDir = store.getProjectDir();
    const category = (req.query.category as string) || 'footage';

    const validCategories = ['footage', 'stock', 'photos', 'graphics', 'narration', 'maps', 'music', 'generated'];
    if (!validCategories.includes(category)) {
      res.status(400).json({ detail: `Invalid category: ${category}` });
      return;
    }

    if (!req.file) {
      res.status(400).json({ detail: 'No file uploaded' });
      return;
    }

    const filename = sanitizeFilename(req.file.originalname);
    const targetDir = path.join(projectDir, category);
    await fs.mkdir(targetDir, { recursive: true });
    const targetPath = path.join(targetDir, filename);
    await fs.rename(req.file.path, targetPath);

    const ext = path.extname(filename).slice(1).toLowerCase();
    const type = categorizeFile(ext);
    const relativePath = path.relative(projectDir, targetPath);

    const duration = type !== 'image' ? await probeDuration(targetPath) : null;
    res.json({ status: 'ok', path: relativePath, type, name: filename, duration });
  } catch (err) {
    next(err);
  }
});

// ---------- GET /file — serve file ----------

mediaRoutes.get('/file', (req, res, next) => {
  try {
    const projectDir = store.getProjectDir();
    const filePath = req.query.path as string;
    if (!filePath) {
      res.status(400).json({ detail: 'Missing path parameter' });
      return;
    }
    if (!validatePath(filePath, projectDir)) {
      res.status(403).json({ detail: 'Access denied — path outside project directory' });
      return;
    }
    const absPath = path.resolve(projectDir, filePath);
    res.sendFile(absPath);
  } catch (err) {
    next(err);
  }
});

// ---------- Stock search ----------

mediaRoutes.post('/stock/search', async (req, res, next) => {
  try {
    const { query, count, min_duration, orientation } = req.body || {};
    if (!query) {
      res.status(400).json({ detail: 'Missing query parameter' });
      return;
    }
    const results = await searchPexels(query, {
      count: count ?? 5,
      minDuration: min_duration ?? 5,
      orientation,
    });
    res.json({ results, count: results.length });
  } catch (err: any) {
    if (err.message?.includes('PEXELS_API_KEY')) {
      res.status(400).json({ detail: err.message });
      return;
    }
    next(err);
  }
});

// ---------- Stock download ----------

mediaRoutes.post('/stock/download', async (req, res, next) => {
  try {
    const projectDir = store.getProjectDir();
    const { url, filename } = req.body || {};

    if (!url || !filename) {
      res.status(400).json({ detail: 'Missing url or filename' });
      return;
    }
    if (!validateUrl(url)) {
      res.status(400).json({ detail: 'URL blocked — must be HTTPS and not a private address' });
      return;
    }

    const cleanName = sanitizeFilename(filename);
    const stockDir = path.join(projectDir, 'stock');
    const outputPath = path.join(stockDir, cleanName);

    await downloadFile(url, outputPath);

    const relativePath = path.relative(projectDir, outputPath);
    res.json({ status: 'ok', path: relativePath, name: cleanName });
  } catch (err) { next(err); }
});
// ---------- Download panel ----------

mediaRoutes.get('/download/scripts', async (req, res, next) => {
  try {
    const projectDir = store.getProjectDir();
    const scripts: Array<{ name: string; path: string; relative_to_project: string }> = [];

    // Search project dir and up to 3 parent levels
    const searchDirs = [projectDir];
    let dir = projectDir;
    for (let i = 0; i < 3; i++) {
      dir = path.dirname(dir);
      searchDirs.push(dir);
    }

    for (const searchDir of searchDirs) {
      let entries: string[];
      try { entries = await readdir(searchDir); } catch { continue; }
      for (const entry of entries) {
        if (!entry.endsWith('.sh')) continue;
        if (!/download|fetch/i.test(entry)) continue;
        const absPath = path.join(searchDir, entry);
        scripts.push({
          name: entry,
          path: absPath,
          relative_to_project: path.relative(projectDir, absPath),
        });
      }
    }

    res.json(scripts);
  } catch (err) { next(err); }
});

mediaRoutes.get('/download/tools', (_req, res) => {
  function hasCommand(cmd: string): boolean {
    try { execFileSync('which', [cmd], { stdio: 'pipe' }); return true; } catch { return false; }
  }
  res.json({
    yt_dlp: hasCommand('yt-dlp'),
    curl: hasCommand('curl'),
    wget: hasCommand('wget'),
    ffmpeg: hasCommand('ffmpeg'),
  });
});

mediaRoutes.post('/download/run-script', (req, res, next) => {
  try {
    const projectDir = store.getProjectDir();
    const { script_path } = req.body || {};
    if (!script_path) {
      res.status(400).json({ detail: 'Missing script_path' });
      return;
    }

    const absScript = path.isAbsolute(script_path)
      ? script_path
      : path.resolve(projectDir, script_path);

    if (!validatePath(absScript, projectDir) && !validatePath(absScript, path.resolve(projectDir, '..'))) {
      res.status(403).json({ detail: 'Script path outside allowed directories' });
      return;
    }

    const task = runSubprocess('script-download', 'bash', [absScript], projectDir);
    res.json({ status: 'started', task_id: task.task_id });
  } catch (err) { next(err); }
});

mediaRoutes.post('/download/yt-dlp', (req, res, next) => {
  try {
    const projectDir = store.getProjectDir();
    const { url, category = 'footage', filename } = req.body || {};

    if (!url) {
      res.status(400).json({ detail: 'Missing url' });
      return;
    }

    const outputDir = path.join(projectDir, category);
    const outputTemplate = filename
      ? path.join(outputDir, filename)
      : path.join(outputDir, '%(title)s.%(ext)s');

    const taskId = `ytdlp-${Date.now()}`;
    const args = [
      '-f', 'bestvideo[height<=720]+bestaudio/best[height<=720]',
      '--no-playlist',
      '-o', outputTemplate,
      url,
    ];

    const task = runSubprocess(taskId, 'yt-dlp', args, projectDir);
    res.json({ status: 'started', task_id: task.task_id });
  } catch (err) { next(err); }
});

mediaRoutes.get('/download/status', (_req, res) => {
  res.json(getAllTasks());
});

// ---------- Stubs (not needed for web editor) ----------

mediaRoutes.post('/download/create-dirs', (_req, res) => {
  res.json({ status: 'ok', created: [] });
});

mediaRoutes.post('/generate-clip', notImplemented('AI video generation not yet available'));
