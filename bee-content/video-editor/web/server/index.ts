import express from 'express';
import cors from 'cors';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { projectRoutes } from './routes/projects.js';
import { mediaRoutes } from './routes/media.js';
import { productionRoutes } from './routes/production.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const app = express();
const PORT = parseInt(process.env.PORT || '8420');

// CORS
const origins = (process.env.CORS_ORIGINS || '*').split(',');
app.use(cors({ origin: origins }));
app.use(express.json());

// API routes
app.use('/api/projects', projectRoutes);
app.use('/api/media', mediaRoutes);
app.use('/api/production', productionRoutes);

// Health check
app.get('/api/health', (_req, res) => res.json({ status: 'ok' }));

// Static frontend (production mode)
const staticDir = process.env.STATIC_DIR || path.join(__dirname, '../dist');
app.use(express.static(staticDir));

// SPA catch-all (Express 5 requires named wildcard)
app.get('/{*splat}', (req, res) => {
  if (!req.path.startsWith('/api/')) {
    res.sendFile(path.join(staticDir, 'index.html'));
  }
});

// Error handler — { detail: "..." } format to match frontend (must be last)
app.use((err: any, _req: any, res: any, _next: any) => {
  const status = err.status || 500;
  res.status(status).json({ detail: err.message || 'Internal server error' });
});

// Only start listening if this is the main module (not imported by tests)
if (process.argv[1]?.includes('server/index')) {
  app.listen(PORT, () => console.log(`Bee Video Editor — http://localhost:${PORT}`));
}
