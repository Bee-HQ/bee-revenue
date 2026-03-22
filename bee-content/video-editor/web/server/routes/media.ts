import { Router } from 'express';
import path from 'node:path';
import fs from 'node:fs/promises';
import multer from 'multer';
import { store } from '../services/project-store.js';
import { listMediaFiles, validatePath, validateUrl, sanitizeFilename, categorizeFile, probeDuration } from '../lib/media-utils.js';
import { searchPexels, downloadFile } from '../services/acquisition.js';

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
mediaRoutes.get('/download/scripts', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.get('/download/tools', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.post('/download/run-script', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.post('/download/yt-dlp', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.get('/download/status', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.post('/download/create-dirs', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.post('/generate-clip', notImplemented('Not yet migrated — Step 5'));
