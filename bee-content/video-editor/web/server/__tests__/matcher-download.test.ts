import { describe, test, expect, beforeEach, afterAll, vi } from 'vitest';
import request from 'supertest';
import { app } from '../index.js';
import { store } from '../services/project-store.js';
import { tokenize, autoAssignMedia } from '../services/matcher.js';
import { resetTasks } from '../services/download-tasks.js';
import * as fs from 'node:fs/promises';
import * as fsSync from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';

// ---------- Store reset ----------

function resetStore() {
  const s = store as any;
  s.project = null;
  s.projectDir = null;
  s.jsonPath = null;
}

// ---------- Storyboard with stock queries ----------

const STORYBOARD_MD = `# Matcher Test

\`\`\`bee-video:project
{"title": "Matcher Test", "fps": 30, "resolution": [1920, 1080]}
\`\`\`

## Act 1

### seg-01 | Bodycam Arrival

\`\`\`bee-video:segment
{
  "duration": 15,
  "visual": [{"type": "FOOTAGE", "src": null, "query": "bodycam arrival night"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`

### seg-02 | Crime Scene

\`\`\`bee-video:segment
{
  "duration": 10,
  "visual": [{"type": "STOCK", "src": null, "query": "crime scene tape"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`

### seg-03 | Already Assigned

\`\`\`bee-video:segment
{
  "duration": 10,
  "visual": [{"type": "FOOTAGE", "src": "footage/existing.mp4"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`
`;

// ---------- Temp project ----------

const tempDirs: string[] = [];
let tmpDir: string;

async function makeTempProject() {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'bee-matcher-test-'));
  const mdPath = path.join(dir, 'storyboard.md');
  await fs.writeFile(mdPath, STORYBOARD_MD, 'utf-8');
  // Create media files for matching
  await fs.mkdir(path.join(dir, 'footage'), { recursive: true });
  await fs.writeFile(path.join(dir, 'footage', 'bodycam-arrival-night.mp4'), 'fake');
  await fs.mkdir(path.join(dir, 'stock'), { recursive: true });
  await fs.writeFile(path.join(dir, 'stock', 'crime-scene-tape-dark.mp4'), 'fake');
  tempDirs.push(dir);
  return { tmpDir: dir, storyboardPath: mdPath };
}

async function loadProject(dir: string, mdPath: string) {
  const res = await request(app)
    .post('/api/projects/load')
    .send({ storyboard_path: mdPath, project_dir: dir });
  expect(res.status).toBe(200);
  return res.body;
}

afterAll(async () => {
  for (const dir of tempDirs) {
    try { await fs.rm(dir, { recursive: true, force: true }); } catch {}
  }
});

// ============================================================
// Unit: tokenize
// ============================================================

describe('tokenize', () => {
  test('splits on non-alphanumeric, lowercases, filters short words', () => {
    expect(tokenize('Bodycam Arrival at Night')).toEqual(['bodycam', 'arrival', 'night']);
  });

  test('filters stopwords', () => {
    expect(tokenize('the crime of the century')).toEqual(['crime', 'century']);
  });

  test('returns empty for short/stop-only input', () => {
    expect(tokenize('a is')).toEqual([]);
  });
});

// ============================================================
// Unit: autoAssignMedia
// ============================================================

describe('autoAssignMedia', () => {
  test('matches media files to segments by keywords', async () => {
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    await loadProject(tmpDir, proj.storyboardPath);
    const loaded = store.get();

    const result = autoAssignMedia(loaded, tmpDir);

    expect(result.assigned).toBe(2); // seg-01 and seg-02
    expect(result.unmatched).toBe(0);
    expect(loaded.segments[0].visual[0].src).toContain('bodycam');
    expect(loaded.segments[1].visual[0].src).toContain('crime');
    // seg-03 already had src, should be unchanged
    expect(loaded.segments[2].visual[0].src).toBe('footage/existing.mp4');
  });

  test('skips segments with existing src', async () => {
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    await loadProject(tmpDir, proj.storyboardPath);
    const loaded = store.get();

    const result = autoAssignMedia(loaded, tmpDir);
    // seg-03 has src already, should not be touched
    expect(loaded.segments[2].visual[0].src).toBe('footage/existing.mp4');
  });

  test('returns unmatched count when no files match', async () => {
    const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'bee-matcher-empty-'));
    tempDirs.push(dir);
    const mdPath = path.join(dir, 'storyboard.md');
    await fs.writeFile(mdPath, STORYBOARD_MD, 'utf-8');
    // No media files at all

    await loadProject(dir, mdPath);
    const loaded = store.get();
    const result = autoAssignMedia(loaded, dir);

    expect(result.assigned).toBe(0);
    expect(result.unmatched).toBe(2); // seg-01 and seg-02
  });
});

// ============================================================
// Route: auto-assign
// ============================================================

describe('Auto-assign route', () => {
  beforeEach(async () => {
    resetStore();
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    await loadProject(tmpDir, proj.storyboardPath);
  });

  test('POST /api/projects/auto-assign — assigns media and persists', async () => {
    const res = await request(app).post('/api/projects/auto-assign');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.assigned).toBe(2);

    // Verify persisted
    const current = await request(app).get('/api/projects/current');
    expect(current.body.segments[0].visual[0].src).toContain('bodycam');
  });
});

// ============================================================
// Download panel routes
// ============================================================

describe('Download tools route', () => {
  beforeEach(async () => {
    resetStore();
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    await loadProject(tmpDir, proj.storyboardPath);
  });

  test('GET /api/media/download/tools — returns tool availability', async () => {
    const res = await request(app).get('/api/media/download/tools');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('yt_dlp');
    expect(res.body).toHaveProperty('ffmpeg');
    expect(typeof res.body.yt_dlp).toBe('boolean');
  });
});

describe('Download scripts route', () => {
  beforeEach(async () => {
    resetStore();
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    await loadProject(tmpDir, proj.storyboardPath);
  });

  test('GET /api/media/download/scripts — lists download scripts', async () => {
    // Create a download script in project dir
    await fs.writeFile(path.join(tmpDir, 'download-footage.sh'), '#!/bin/bash\necho ok');

    const res = await request(app).get('/api/media/download/scripts');
    expect(res.status).toBe(200);
    expect(res.body.length).toBeGreaterThanOrEqual(1);
    expect(res.body[0].name).toBe('download-footage.sh');
  });

  test('GET /api/media/download/scripts — returns empty when no scripts', async () => {
    const res = await request(app).get('/api/media/download/scripts');
    expect(res.status).toBe(200);
    expect(res.body).toEqual([]);
  });
});

describe('Download status route', () => {
  beforeEach(() => {
    resetTasks();
  });

  test('GET /api/media/download/status — returns empty when no tasks', async () => {
    const res = await request(app).get('/api/media/download/status');
    expect(res.status).toBe(200);
    expect(res.body).toEqual([]);
  });
});

describe('Download yt-dlp route', () => {
  beforeEach(async () => {
    resetStore();
    resetTasks();
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    await loadProject(tmpDir, proj.storyboardPath);
  });

  test('POST /api/media/download/yt-dlp — 400 without url', async () => {
    const res = await request(app)
      .post('/api/media/download/yt-dlp')
      .send({});
    expect(res.status).toBe(400);
    expect(res.body.detail).toContain('url');
  });
});

describe('Download run-script route', () => {
  beforeEach(async () => {
    resetStore();
    resetTasks();
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    await loadProject(tmpDir, proj.storyboardPath);
  });

  test('POST /api/media/download/run-script — 400 without script_path', async () => {
    const res = await request(app)
      .post('/api/media/download/run-script')
      .send({});
    expect(res.status).toBe(400);
    expect(res.body.detail).toContain('script_path');
  });
});
