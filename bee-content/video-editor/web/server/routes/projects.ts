import { Router } from 'express';
import { store } from '../services/project-store.js';
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
    const project = store.loadFromMarkdown(storyboard_path, project_dir);
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
    store.assignMedia(segment_id, layer, layer_index || 0, media_path);
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

// POST /download-entry — not yet migrated
projectRoutes.post('/download-entry', (_req, res) => {
  res.status(501).json({ detail: 'Not yet migrated — Step 6' });
});

// POST /auto-assign — not yet migrated
projectRoutes.post('/auto-assign', (_req, res) => {
  res.status(501).json({ detail: 'Not yet migrated — Step 6' });
});

// POST /acquire-media — not yet migrated
projectRoutes.post('/acquire-media', (_req, res) => {
  res.status(501).json({ detail: 'Not yet migrated — Step 6' });
});
