import { describe, test, expect, beforeEach, afterAll } from 'vitest';
import request from 'supertest';
import { app } from '../index.js';
import { store } from '../services/project-store.js';
import * as fs from 'node:fs/promises';
import * as fsSync from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';

// ---------- Store reset helper ----------

function resetStore() {
  const s = store as any;
  s.project = null;
  s.projectDir = null;
  s.jsonPath = null;
}

// ---------- Storyboard fixture ----------

const STORYBOARD_MD = `# Test Video

\`\`\`bee-video:project
{"title": "Test Video", "fps": 30, "resolution": [1920, 1080]}
\`\`\`

## Act 1

### seg-01 | Cold Open

\`\`\`bee-video:segment
{
  "duration": 15,
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [{"type": "NAR", "text": "Opening narration", "src": null}],
  "overlay": [{"type": "LOWER_THIRD", "content": "Location"}],
  "music": [],
  "transition": null
}
\`\`\`

### seg-02 | Scene Two

\`\`\`bee-video:segment
{
  "duration": 20,
  "visual": [{"type": "STOCK", "src": null}],
  "audio": [{"type": "NAR", "text": "More narration", "src": null}],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`
`;

// ---------- Temp project setup ----------

let tmpDir: string;
let storyboardPath: string;

async function makeTempProject(): Promise<{ tmpDir: string; storyboardPath: string }> {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'bee-routes-test-'));
  const mdPath = path.join(dir, 'storyboard.md');
  await fs.writeFile(mdPath, STORYBOARD_MD, 'utf-8');
  return { tmpDir: dir, storyboardPath: mdPath };
}

async function loadProject(dir: string, mdPath: string) {
  const res = await request(app)
    .post('/api/projects/load')
    .send({ storyboard_path: mdPath, project_dir: dir });
  expect(res.status).toBe(200);
  return res.body;
}

// ---------- Cleanup ----------

const tempDirs: string[] = [];

afterAll(async () => {
  for (const dir of tempDirs) {
    try {
      await fs.rm(dir, { recursive: true, force: true });
    } catch {
      // ignore
    }
  }
});

// ============================================================
// Project routes
// ============================================================

describe('Project routes', () => {
  beforeEach(async () => {
    resetStore();
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    storyboardPath = proj.storyboardPath;
    tempDirs.push(tmpDir);
  });

  // 1. POST /api/projects/load
  test('POST /api/projects/load — returns BeeProject with 2 segments', async () => {
    const res = await request(app)
      .post('/api/projects/load')
      .send({ storyboard_path: storyboardPath, project_dir: tmpDir });

    expect(res.status).toBe(200);
    expect(res.body.title).toBe('Test Video');
    expect(res.body.fps).toBe(30);
    expect(res.body.resolution).toEqual([1920, 1080]);
    expect(res.body.segments).toHaveLength(2);
    expect(res.body.segments[0].id).toBe('seg-01');
    expect(res.body.segments[1].id).toBe('seg-02');
  });

  // 1b. POST /api/projects/load — 404 for non-existent file
  test('POST /api/projects/load — returns 404 for non-existent storyboard', async () => {
    const res = await request(app)
      .post('/api/projects/load')
      .send({ storyboard_path: '/no/such/file.md', project_dir: tmpDir });

    expect(res.status).toBe(404);
    expect(res.body.detail).toContain('not found');
  });

  // 1c. POST /api/projects/load — works with relative storyboard_path
  test('POST /api/projects/load — resolves relative storyboard_path against project_dir', async () => {
    const res = await request(app)
      .post('/api/projects/load')
      .send({ storyboard_path: 'storyboard.md', project_dir: tmpDir });

    expect(res.status).toBe(200);
    expect(res.body.segments).toHaveLength(2);
  });

  // 1d. POST /api/projects/load — 404 for non-existent project_dir
  test('POST /api/projects/load — returns 404 for non-existent project_dir', async () => {
    const res = await request(app)
      .post('/api/projects/load')
      .send({ storyboard_path: 'storyboard.md', project_dir: '/no/such/dir' });

    expect(res.status).toBe(404);
    expect(res.body.detail).toContain('not found');
  });

  // 2. GET /api/projects/current — after load
  test('GET /api/projects/current — returns loaded project', async () => {
    await loadProject(tmpDir, storyboardPath);

    const res = await request(app).get('/api/projects/current');
    expect(res.status).toBe(200);
    expect(res.body.title).toBe('Test Video');
    expect(res.body.segments).toHaveLength(2);
  });

  // 3. GET /api/projects/current — before load
  test('GET /api/projects/current — 404 when no project loaded', async () => {
    resetStore();
    const res = await request(app).get('/api/projects/current');
    expect(res.status).toBe(404);
    expect(res.body).toHaveProperty('detail');
  });

  // 4. PUT /api/projects/assign
  test('PUT /api/projects/assign — assigns visual src and persists', async () => {
    await loadProject(tmpDir, storyboardPath);

    const assignRes = await request(app)
      .put('/api/projects/assign')
      .send({ segment_id: 'seg-01', layer: 'visual', layer_index: 0, media_path: 'footage/clip.mp4' });
    expect(assignRes.status).toBe(200);
    expect(assignRes.body.status).toBe('ok');

    const current = await request(app).get('/api/projects/current');
    const seg = current.body.segments.find((s: any) => s.id === 'seg-01');
    expect(seg.visual[0].src).toBe('footage/clip.mp4');
  });

  // 5. PUT /api/projects/update-segment — visual_updates with color
  test('PUT /api/projects/update-segment — sets color via visual_updates', async () => {
    await loadProject(tmpDir, storyboardPath);

    const updateRes = await request(app)
      .put('/api/projects/update-segment')
      .send({ segment_id: 'seg-01', updates: { visual_updates: [{ index: 0, color: 'noir' }] } });
    expect(updateRes.status).toBe(200);
    expect(updateRes.body.status).toBe('ok');

    const current = await request(app).get('/api/projects/current');
    const seg = current.body.segments.find((s: any) => s.id === 'seg-01');
    expect(seg.visual[0].color).toBe('noir');
  });

  // overlay_updates
  test('PUT /api/projects/update-segment — overlay_updates sets transform', async () => {
    await loadProject(tmpDir, storyboardPath);

    // First verify the fixture has overlays — if not, use a segment that does
    const before = await request(app).get('/api/projects/current');
    const segWithOverlay = before.body.segments.find((s: any) => s.overlay.length > 0);
    expect(segWithOverlay).toBeDefined();

    const res = await request(app)
      .put('/api/projects/update-segment')
      .send({
        segment_id: segWithOverlay.id,
        updates: {
          overlay_updates: [{ index: 0, transform: { position: 'top-left', x: 10, y: 5 } }],
        },
      });
    expect(res.status).toBe(200);

    const after = await request(app).get('/api/projects/current');
    const seg = after.body.segments.find((s: any) => s.id === segWithOverlay.id);
    expect(seg.overlay[0].transform).toEqual({ position: 'top-left', x: 10, y: 5 });
  });

  test('PUT /api/projects/update-segment — overlay transform deep-merges', async () => {
    await loadProject(tmpDir, storyboardPath);

    const before = await request(app).get('/api/projects/current');
    const segWithOverlay = before.body.segments.find((s: any) => s.overlay.length > 0);
    expect(segWithOverlay).toBeDefined();

    // Set initial transform
    await request(app)
      .put('/api/projects/update-segment')
      .send({
        segment_id: segWithOverlay.id,
        updates: { overlay_updates: [{ index: 0, transform: { position: 'top-left', scale: 1.5 } }] },
      });

    // Deep-merge: change position, keep scale
    await request(app)
      .put('/api/projects/update-segment')
      .send({
        segment_id: segWithOverlay.id,
        updates: { overlay_updates: [{ index: 0, transform: { position: 'bottom-right' } }] },
      });

    const after = await request(app).get('/api/projects/current');
    const seg = after.body.segments.find((s: any) => s.id === segWithOverlay.id);
    expect(seg.overlay[0].transform.position).toBe('bottom-right');
    expect(seg.overlay[0].transform.scale).toBe(1.5); // preserved from first update
  });

  test('PUT /api/projects/update-segment — overlay transform null resets', async () => {
    await loadProject(tmpDir, storyboardPath);

    const before = await request(app).get('/api/projects/current');
    const segWithOverlay = before.body.segments.find((s: any) => s.overlay.length > 0);
    expect(segWithOverlay).toBeDefined();

    // Set then reset
    await request(app)
      .put('/api/projects/update-segment')
      .send({
        segment_id: segWithOverlay.id,
        updates: { overlay_updates: [{ index: 0, transform: { position: 'top-left' } }] },
      });

    await request(app)
      .put('/api/projects/update-segment')
      .send({
        segment_id: segWithOverlay.id,
        updates: { overlay_updates: [{ index: 0, transform: null }] },
      });

    const after = await request(app).get('/api/projects/current');
    const seg = after.body.segments.find((s: any) => s.id === segWithOverlay.id);
    expect(seg.overlay[0].transform).toBeUndefined();
  });

  // visual_updates transform
  test('PUT /api/projects/update-segment — visual_updates accepts transform', async () => {
    await loadProject(tmpDir, storyboardPath);

    const res = await request(app)
      .put('/api/projects/update-segment')
      .send({
        segment_id: 'seg-01',
        updates: { visual_updates: [{ index: 0, transform: { scale: 0.8, rotation: -5 } }] },
      });
    expect(res.status).toBe(200);

    const after = await request(app).get('/api/projects/current');
    const seg = after.body.segments.find((s: any) => s.id === 'seg-01');
    expect(seg.visual[0].transform).toEqual({ scale: 0.8, rotation: -5 });
  });

  test('PUT /api/projects/update-segment — visual_updates transform deep-merges', async () => {
    await loadProject(tmpDir, storyboardPath);

    // Set initial transform with scale + rotation
    await request(app)
      .put('/api/projects/update-segment')
      .send({
        segment_id: 'seg-01',
        updates: { visual_updates: [{ index: 0, transform: { scale: 1.5, rotation: 10 } }] },
      });

    // Update only scale — rotation should be preserved
    await request(app)
      .put('/api/projects/update-segment')
      .send({
        segment_id: 'seg-01',
        updates: { visual_updates: [{ index: 0, transform: { scale: 0.8 } }] },
      });

    const after = await request(app).get('/api/projects/current');
    const seg = after.body.segments.find((s: any) => s.id === 'seg-01');
    expect(seg.visual[0].transform.scale).toBe(0.8);
    expect(seg.visual[0].transform.rotation).toBe(10); // preserved from first update
  });

  test('PUT /api/projects/update-segment — visual_updates transform null resets', async () => {
    await loadProject(tmpDir, storyboardPath);

    // Set transform then reset with null
    await request(app)
      .put('/api/projects/update-segment')
      .send({
        segment_id: 'seg-01',
        updates: { visual_updates: [{ index: 0, transform: { scale: 1.5 } }] },
      });

    await request(app)
      .put('/api/projects/update-segment')
      .send({
        segment_id: 'seg-01',
        updates: { visual_updates: [{ index: 0, transform: null }] },
      });

    const after = await request(app).get('/api/projects/current');
    const seg = after.body.segments.find((s: any) => s.id === 'seg-01');
    expect(seg.visual[0].transform).toBeUndefined();
  });

  // 6. PUT /api/projects/reorder
  test('PUT /api/projects/reorder — reorders segments', async () => {
    await loadProject(tmpDir, storyboardPath);

    const reorderRes = await request(app)
      .put('/api/projects/reorder')
      .send({ segment_order: ['seg-02', 'seg-01'] });
    expect(reorderRes.status).toBe(200);
    expect(reorderRes.body.status).toBe('ok');
    expect(reorderRes.body.count).toBe(2);

    const current = await request(app).get('/api/projects/current');
    expect(current.body.segments[0].id).toBe('seg-02');
    expect(current.body.segments[1].id).toBe('seg-01');
  });

  // 7. GET /api/projects/export?format=md
  test('GET /api/projects/export?format=md — returns markdown content', async () => {
    await loadProject(tmpDir, storyboardPath);

    const res = await request(app).get('/api/projects/export?format=md');
    expect(res.status).toBe(200);
    expect(res.body.format).toBe('md');
    expect(res.body.content).toContain('bee-video:project');
    expect(res.body.content).toContain('Test Video');
  });

  // 8. GET /api/projects/export?format=json
  test('GET /api/projects/export?format=json — returns valid JSON string', async () => {
    await loadProject(tmpDir, storyboardPath);

    const res = await request(app).get('/api/projects/export?format=json');
    expect(res.status).toBe(200);
    expect(res.body.format).toBe('json');
    const parsed = JSON.parse(res.body.content);
    expect(parsed.title).toBe('Test Video');
    expect(parsed.segments).toHaveLength(2);
  });

  // 9. POST /api/projects/auto-assign — now implemented (see matcher-download.test.ts)
  test('POST /api/projects/auto-assign — returns 200', async () => {
    await loadProject(tmpDir, storyboardPath);
    const res = await request(app).post('/api/projects/auto-assign');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });

  // 10. POST /api/projects/acquire-media — now implemented (see acquisition.test.ts)
  test('POST /api/projects/acquire-media — returns 200', async () => {
    // Re-load in case parallel test files reset the shared store
    await loadProject(tmpDir, storyboardPath);
    const res = await request(app).post('/api/projects/acquire-media');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });
});

// ============================================================
// Media routes
// ============================================================

describe('Media routes', () => {
  beforeEach(async () => {
    resetStore();
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    storyboardPath = proj.storyboardPath;
    tempDirs.push(tmpDir);
    await loadProject(tmpDir, storyboardPath);
  });

  // 11. GET /api/media — file list after creating footage dir
  test('GET /api/media — returns file list for loaded project', async () => {
    // Create a footage dir with a file so the response is non-empty
    const footageDir = path.join(tmpDir, 'footage');
    await fs.mkdir(footageDir, { recursive: true });
    await fs.writeFile(path.join(footageDir, 'test-clip.mp4'), 'fake video data');

    const res = await request(app).get('/api/media');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('files');
    expect(res.body).toHaveProperty('categories');
    expect(Array.isArray(res.body.files)).toBe(true);
    const names = res.body.files.map((f: any) => f.name);
    expect(names).toContain('test-clip.mp4');
  });

  // 12. POST /api/media/upload — upload a small file
  test('POST /api/media/upload — uploads file to category directory', async () => {
    const res = await request(app)
      .post('/api/media/upload?category=footage')
      .attach('file', Buffer.from('fake video content'), 'test-upload.mp4');

    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.name).toBe('test-upload.mp4');
    expect(res.body.path).toContain('footage');

    // Verify the file exists on disk
    const targetPath = path.join(tmpDir, 'footage', 'test-upload.mp4');
    const exists = fsSync.existsSync(targetPath);
    expect(exists).toBe(true);
  });

  // 13. GET /api/media/file?path=... — serve uploaded file
  test('GET /api/media/file — serves a file from the project directory', async () => {
    // Create a file in footage dir
    const footageDir = path.join(tmpDir, 'footage');
    await fs.mkdir(footageDir, { recursive: true });
    await fs.writeFile(path.join(footageDir, 'serve-me.txt'), 'hello world');

    const res = await request(app).get('/api/media/file?path=footage/serve-me.txt');
    expect(res.status).toBe(200);
    expect(res.text).toBe('hello world');
  });

  // 14. GET /api/media/file?path=../../etc/passwd — 403 path traversal
  test('GET /api/media/file — rejects path traversal with 403', async () => {
    const res = await request(app).get('/api/media/file?path=../../etc/passwd');
    expect(res.status).toBe(403);
    expect(res.body).toHaveProperty('detail');
  });

  // 15. POST /api/media/stock/search — now implemented (see acquisition.test.ts)
  test('POST /api/media/stock/search — returns 400 without query', async () => {
    const res = await request(app).post('/api/media/stock/search').send({});
    expect(res.status).toBe(400);
    expect(res.body).toHaveProperty('detail');
  });
});

// ============================================================
// Production routes
// ============================================================

describe('Production routes', () => {
  beforeEach(async () => {
    resetStore();
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    storyboardPath = proj.storyboardPath;
    tempDirs.push(tmpDir);
    await loadProject(tmpDir, storyboardPath);
  });

  // 16. GET /api/production/effects
  test('GET /api/production/effects — returns color_presets, transitions, ken_burns', async () => {
    const res = await request(app).get('/api/production/effects');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body.color_presets)).toBe(true);
    expect(Array.isArray(res.body.transitions)).toBe(true);
    expect(Array.isArray(res.body.ken_burns)).toBe(true);
    expect(res.body.color_presets).toContain('noir');
    expect(res.body.color_presets).toContain('dark_crime');
    expect(res.body.transitions).toContain('dissolve');
    expect(res.body.ken_burns).toContain('zoom_in');
  });

  // 17. GET /api/production/status
  test('GET /api/production/status — returns segments_total matching loaded project', async () => {
    const res = await request(app).get('/api/production/status');
    expect(res.status).toBe(200);
    expect(res.body.segments_total).toBe(2);
    expect(res.body).toHaveProperty('phase');
    expect(res.body).toHaveProperty('segments_done');
    expect(res.body).toHaveProperty('narration_files');
    expect(res.body).toHaveProperty('graphics_files');
    expect(res.body).toHaveProperty('trimmed_files');
  });

  // 18. GET /api/production/preflight
  test('GET /api/production/preflight — returns total, found, missing counts', async () => {
    const res = await request(app).get('/api/production/preflight');
    expect(res.status).toBe(200);
    expect(res.body.total).toBe(2);
    expect(typeof res.body.found).toBe('number');
    expect(typeof res.body.missing).toBe('number');
    // Both segments have null src, so all should be missing
    expect(res.body.missing).toBe(2);
    expect(res.body.found).toBe(0);
    expect(res.body.found + res.body.missing).toBe(res.body.total);
  });

  // 19. POST /api/production/init
  test('POST /api/production/init — returns { status: "ok" }', async () => {
    const res = await request(app).post('/api/production/init');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });

  // 20. POST /api/production/narration — now implemented (see tts.test.ts for full coverage)
  test('POST /api/production/narration — returns 200 with started status', async () => {
    const res = await request(app)
      .post('/api/production/narration')
      .send({ tts_engine: 'edge' });
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('started');
    // Wait for background task to complete
    await new Promise(r => setTimeout(r, 200));
  });
});

// ============================================================
// Error handling
// ============================================================

describe('Error handling', () => {
  beforeEach(() => {
    resetStore();
  });

  // 21. GET /api/projects/current with no project — { detail: "..." } format
  test('GET /api/projects/current — error response uses { detail } format', async () => {
    const res = await request(app).get('/api/projects/current');
    expect(res.status).toBe(404);
    expect(res.body).toHaveProperty('detail');
    expect(typeof res.body.detail).toBe('string');
    expect(res.body.detail.length).toBeGreaterThan(0);
  });
});
