import { Router } from 'express';
import path from 'node:path';
import fs from 'node:fs/promises';
import multer from 'multer';
import { store } from '../services/project-store.js';
import { listMediaFiles, validatePath, sanitizeFilename, categorizeFile, probeDuration } from '../lib/media-utils.js';

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

// ---------- 501 stubs ----------

mediaRoutes.post('/stock/search', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.post('/stock/download', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.get('/download/scripts', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.get('/download/tools', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.post('/download/run-script', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.post('/download/yt-dlp', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.get('/download/status', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.post('/download/create-dirs', notImplemented('Not yet migrated — Step 5'));
mediaRoutes.post('/generate-clip', notImplemented('Not yet migrated — Step 5'));
