import { Router } from 'express';
import path from 'node:path';
import { store } from '../services/project-store.js';
import { searchPexels, downloadFile, acquireMedia } from '../services/acquisition.js';
import { sanitizeFilename } from '../lib/media-utils.js';
import type { BeeProject, BeeSegment } from '../../shared/types.js';

export const projectRoutes = Router();

// ---------- Helpers ----------

function exportToMarkdown(project: BeeProject): string {
  const lines: string[] = [];

  lines.push(`# ${project.title}`, '');
  lines.push('```bee-video:project');
  lines.push(JSON.stringify({ title: project.title, fps: project.fps, resolution: project.resolution }));
  lines.push('```');

  let currentSection = '';

  for (const seg of project.segments) {
    if (seg.section !== currentSection) {
      currentSection = seg.section;
      lines.push('', `## ${currentSection}`);
    }

    lines.push('', `### ${seg.id} | ${seg.title}`);
    lines.push('```bee-video:segment');
    lines.push(JSON.stringify(
      {
        duration: seg.duration,
        visual: seg.visual,
        audio: seg.audio,
        overlay: seg.overlay,
        music: seg.music,
        transition: seg.transition,
      },
      null,
      2
    ));
    lines.push('```');
  }

  return lines.join('\n') + '\n';
}

// ---------- Routes ----------

// POST /load
projectRoutes.post('/load', (req, res, next) => {
  try {
    const { storyboard_path, project_dir } = req.body as {
      storyboard_path: string;
      project_dir: string;
    };
    const resolvedDir = path.resolve(project_dir);
    const resolvedPath = path.isAbsolute(storyboard_path)
      ? storyboard_path
      : path.resolve(resolvedDir, storyboard_path);
    const project = store.loadFromMarkdown(resolvedPath, resolvedDir);
    res.json(project);
  } catch (err) {
    next(err);
  }
});

// GET /current
projectRoutes.get('/current', (req, res, next) => {
  try {
    const project = store.get();
    res.json(project);
  } catch (err) {
    next(err);
  }
});

// PUT /assign
projectRoutes.put('/assign', (req, res, next) => {
  try {
    const { segment_id, layer, media_path, layer_index } = req.body as {
      segment_id: string;
      layer: string;
      media_path: string;
      layer_index?: number;
    };
    store.assignMedia(segment_id, layer, layer_index ?? 0, media_path);
    res.json({ status: 'ok' });
  } catch (err) {
    next(err);
  }
});

// PUT /update-segment
projectRoutes.put('/update-segment', (req, res, next) => {
  try {
    const { segment_id, updates } = req.body as {
      segment_id: string;
      updates: Record<string, any>;
    };
    store.updateSegment(segment_id, updates);
    res.json({ status: 'ok' });
  } catch (err) {
    next(err);
  }
});

// PUT /reorder
projectRoutes.put('/reorder', (req, res, next) => {
  try {
    const { segment_order } = req.body as { segment_order: string[] };
    store.reorderSegments(segment_order);
    res.json({ status: 'ok', count: segment_order.length });
  } catch (err) {
    next(err);
  }
});

// GET /export
projectRoutes.get('/export', (req, res, next) => {
  try {
    const format = (req.query.format as string) || 'json';
    const project = store.get();

    if (format === 'md') {
      const content = exportToMarkdown(project);
      res.json({ format: 'md', content });
    } else {
      res.json({ format: 'json', content: JSON.stringify(project, null, 2) });
    }
  } catch (err) {
    next(err);
  }
});

// POST /download-entry — download asset for a segment entry
projectRoutes.post('/download-entry', async (req, res, next) => {
  try {
    const project = store.get();
    const projectDir = store.getProjectDir();
    const { segment_id, layer = 'visual', index = 0 } = req.body || {};

    if (!segment_id) {
      res.status(400).json({ detail: 'Missing segment_id' });
      return;
    }

    const seg = project.segments.find(s => s.id === segment_id);
    if (!seg) {
      res.status(404).json({ detail: `Segment not found: ${segment_id}` });
      return;
    }

    const entries = layer === 'visual' ? seg.visual : layer === 'audio' ? seg.audio : [];
    const entry = entries[index];
    if (!entry) {
      res.status(400).json({ detail: `${layer}[${index}] does not exist` });
      return;
    }

    const query = (entry as any).query;
    if (!query) {
      res.status(400).json({ detail: `No query on ${layer}[${index}]` });
      return;
    }

    // Search and download best match
    const results = await searchPexels(query, { count: 1, minDuration: 5 });
    if (results.length === 0) {
      res.json({ status: 'no_results', path: null, query });
      return;
    }

    const best = results[0];
    const slug = query.toLowerCase().replace(/[^\w\s-]/g, '').replace(/[\s_]+/g, '-').slice(0, 40);
    const filename = `pexels-${best.id}-${slug}.mp4`;
    const stockDir = path.join(projectDir, 'stock');
    const outputPath = path.join(stockDir, filename);
    const relativePath = path.relative(projectDir, outputPath);

    await downloadFile(best.hd_url, outputPath);

    // Assign to segment
    store.assignMedia(segment_id, layer, index, relativePath);

    res.json({ status: 'ok', path: relativePath, query });
  } catch (err) { next(err); }
});

// POST /auto-assign — not yet migrated
projectRoutes.post('/auto-assign', (_req, res) => {
  res.status(501).json({ detail: 'Not yet migrated' });
});

// POST /acquire-media — batch stock acquisition
projectRoutes.post('/acquire-media', async (req, res, next) => {
  try {
    const project = store.get();
    const projectDir = store.getProjectDir();
    const report = await acquireMedia(project.segments, projectDir);
    res.json({ status: 'ok', ...report });
  } catch (err) { next(err); }
});
