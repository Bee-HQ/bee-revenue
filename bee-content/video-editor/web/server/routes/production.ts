import { Router } from 'express';
import { execFile } from 'node:child_process';
import { readdir, writeFile, mkdir, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { store } from '../services/project-store.js';
import { VALID_ENGINES, getNarrationTask, startNarrationTask } from '../services/tts.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const productionRoutes = Router();

// --- Helpers ---

function stub(response: object) {
  return (_req: any, res: any) => res.json(response);
}

function notImplemented(detail: string) {
  return (_req: any, res: any) => res.status(501).json({ detail });
}

// --- Real Routes ---

productionRoutes.get('/effects', (_req, res) => {
  res.json({
    color_presets: [
      'dark_crime', 'warm_victim', 'bodycam', 'noir', 'sepia', 'cold_blue',
      'vintage', 'bleach_bypass', 'night_vision', 'golden_hour', 'surveillance', 'vhs',
    ],
    transitions: [
      'fade', 'dissolve', 'wipeleft', 'wiperight', 'wipeup', 'wipedown',
      'slideleft', 'slideright', 'slideup', 'slidedown', 'smoothleft', 'smoothright',
      'circlecrop', 'rectcrop', 'pixelize', 'radial', 'diagtl', 'diagtr', 'diagbl', 'diagbr',
      'hlslice', 'hrslice', 'vuslice', 'vdslice', 'distance', 'zoomin',
      'fadeblack', 'fadewhite', 'hblur',
    ],
    ken_burns: ['zoom_in', 'zoom_out', 'pan_left', 'pan_right', 'pan_up', 'pan_down', 'zoom_in_pan_right'],
  });
});

productionRoutes.get('/status', async (req, res, next) => {
  try {
    const projectDir = store.getProjectDir();
    const project = store.get();

    const countFiles = async (dir: string): Promise<number> => {
      try {
        const files = await readdir(path.join(projectDir, dir));
        return files.length;
      } catch { return 0; }
    };

    res.json({
      phase: 'ready',
      segments_total: project.segments.length,
      segments_done: project.segments.filter(s => s.visual[0]?.src).length,
      narration_files: await countFiles('output/narration'),
      graphics_files: await countFiles('output/graphics'),
      trimmed_files: await countFiles('output/segments'),
    });
  } catch (err) { next(err); }
});

productionRoutes.get('/preflight', (req, res, next) => {
  try {
    const project = store.get();
    let found = 0, missing = 0;
    for (const seg of project.segments) {
      if (seg.visual[0]?.src) found++;
      else missing++;
    }
    res.json({ total: project.segments.length, found, missing, needs_check: 0 });
  } catch (err) { next(err); }
});

productionRoutes.post('/render-remotion', async (req, res, next) => {
  try {
    const project = store.get();
    const projectDir = store.getProjectDir();

    // Write project JSON to temp file
    const jsonPath = path.join(tmpdir(), `bee-render-${Date.now()}.json`);
    await writeFile(jsonPath, JSON.stringify(project));

    // Output path
    const outputDir = path.join(projectDir, 'output', 'final');
    await mkdir(outputDir, { recursive: true });
    const outputPath = path.join(outputDir, 'render.mp4');

    // Resolve render script path
    const renderScript = path.resolve(__dirname, '../../render.mjs');

    await new Promise<void>((resolve, reject) => {
      execFile('node', [renderScript, jsonPath, outputPath], { timeout: 600000 }, (error) => {
        if (error) reject(error);
        else resolve();
      });
    });

    const stats = await stat(outputPath);
    res.json({ status: 'ok', output: outputPath, size_bytes: stats.size });
  } catch (err) { next(err); }
});

// --- Stub Routes (Remotion handles these) ---

productionRoutes.post('/init', stub({ status: 'ok' }));
productionRoutes.post('/graphics', stub({ status: 'ok', count: 0 }));
productionRoutes.post('/composite', stub({ status: 'ok', succeeded: 0, failed: 0, skipped: 0, errors: [] }));
productionRoutes.post('/assemble', stub({ status: 'ok' }));
productionRoutes.post('/captions', stub({ status: 'ok' }));
productionRoutes.post('/rough-cut', stub({ status: 'ok' }));

// --- Narration Routes ---

productionRoutes.post('/narration', (req, res, next) => {
  try {
    const project = store.get();
    const projectDir = store.getProjectDir();

    const engine = req.body?.tts_engine || project.production.narrationEngine || 'edge';
    const voice = req.body?.tts_voice || project.production.narrationVoice || undefined;

    if (!VALID_ENGINES.includes(engine)) {
      res.status(400).json({
        detail: `Invalid TTS engine: ${engine}. Available: ${VALID_ENGINES.join(', ')}`,
      });
      return;
    }

    const outputDir = path.join(projectDir, 'output', 'narration');
    const { total } = startNarrationTask(project.segments, engine, voice, outputDir, projectDir);

    // Persist engine/voice choice
    store.updateProduction({
      narrationEngine: engine,
      narrationVoice: voice || project.production.narrationVoice,
    });

    res.json({ status: 'started', total });
  } catch (err: any) {
    if (err.message === 'Narration is already running') {
      res.status(409).json({ detail: err.message });
      return;
    }
    next(err);
  }
});

productionRoutes.get('/narration/status', async (req, res, next) => {
  try {
    const projectDir = store.getProjectDir();
    const task = getNarrationTask();

    // Ignore stale task from a different project
    const isCurrentProject = task && task.projectDir === projectDir;

    // Count files on disk for accurate done count
    let done = 0;
    const narrationDir = path.join(projectDir, 'output', 'narration');
    try {
      const files = await readdir(narrationDir);
      done = files.filter(f => f.endsWith('.mp3')).length;
    } catch { /* dir doesn't exist yet */ }

    const result: Record<string, any> = {
      running: isCurrentProject ? task!.running : false,
      done,
      total: isCurrentProject ? task!.total : 0,
    };

    // Include final results when task is done
    if (isCurrentProject && !task!.running && task!.status) {
      result.status = task!.status;
      result.succeeded = task!.succeeded;
      result.failed = task!.failed;
      result.count = task!.succeeded.length;
    }

    res.json(result);
  } catch (err) { next(err); }
});

// --- Voice Lock Routes ---

productionRoutes.get('/voice-lock', (req, res, next) => {
  try {
    const project = store.get();
    res.json({
      engine: project.production.narrationEngine || 'edge',
      voice: project.production.narrationVoice || '',
    });
  } catch (err) { next(err); }
});

productionRoutes.put('/voice-lock', (req, res, next) => {
  try {
    const { engine, voice } = req.body || {};
    if (engine && !VALID_ENGINES.includes(engine)) {
      res.status(400).json({
        detail: `Invalid TTS engine: ${engine}. Available: ${VALID_ENGINES.join(', ')}`,
      });
      return;
    }
    store.updateProduction({
      ...(engine && { narrationEngine: engine }),
      ...(voice !== undefined && { narrationVoice: voice }),
    });
    const project = store.get();
    res.json({
      engine: project.production.narrationEngine,
      voice: project.production.narrationVoice,
    });
  } catch (err) { next(err); }
});

// --- 501 Stubs (not yet migrated) ---

productionRoutes.post('/produce', notImplemented('Not yet migrated'));
productionRoutes.post('/preview/:segmentId', notImplemented('Not yet migrated'));
productionRoutes.post('/previews', notImplemented('Not yet migrated'));
productionRoutes.post('/export/otio', notImplemented('OTIO export removed — use JSON export'));
productionRoutes.post('/graphics-batch', notImplemented('Not yet migrated'));
