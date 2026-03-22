import { describe, test, expect, beforeEach, afterAll, vi } from 'vitest';
import request from 'supertest';
import { app } from '../index.js';
import { store } from '../services/project-store.js';
import { searchPexels, acquireMedia } from '../services/acquisition.js';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import * as os from 'node:os';

// ---------- Mock global fetch ----------

const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// ---------- Pexels fixture ----------

const PEXELS_RESPONSE = {
  videos: [
    {
      id: 12345,
      url: 'https://www.pexels.com/video/12345/',
      duration: 15,
      width: 1920,
      height: 1080,
      video_files: [
        { quality: 'hd', file_type: 'video/mp4', link: 'https://videos.pexels.com/12345-hd.mp4' },
        { quality: 'sd', file_type: 'video/mp4', link: 'https://videos.pexels.com/12345-sd.mp4' },
      ],
    },
    {
      id: 67890,
      url: 'https://www.pexels.com/video/67890/',
      duration: 8,
      width: 1280,
      height: 720,
      video_files: [
        { quality: 'sd', file_type: 'video/mp4', link: 'https://videos.pexels.com/67890-sd.mp4' },
      ],
    },
  ],
};

// ---------- Store reset helper ----------

function resetStore() {
  const s = store as any;
  s.project = null;
  s.projectDir = null;
  s.jsonPath = null;
}

// ---------- Storyboard with stock queries ----------

const STORYBOARD_MD = `# Stock Test

\`\`\`bee-video:project
{"title": "Stock Test", "fps": 30, "resolution": [1920, 1080]}
\`\`\`

## Act 1

### seg-01 | Opening

\`\`\`bee-video:segment
{
  "duration": 15,
  "visual": [{"type": "STOCK", "src": null, "query": "aerial farm dusk"}],
  "audio": [{"type": "NAR", "text": "Opening", "src": null}],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`

### seg-02 | Has Media

\`\`\`bee-video:segment
{
  "duration": 10,
  "visual": [{"type": "FOOTAGE", "src": "footage/clip.mp4"}],
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
let storyboardPath: string;

async function makeTempProject() {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'bee-stock-test-'));
  const mdPath = path.join(dir, 'storyboard.md');
  await fs.writeFile(mdPath, STORYBOARD_MD, 'utf-8');
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
// Unit: searchPexels
// ============================================================

describe('searchPexels', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env.PEXELS_API_KEY = 'test-key';
  });

  test('parses Pexels API response into StockResult[]', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => PEXELS_RESPONSE,
    });

    const results = await searchPexels('farm');
    expect(results).toHaveLength(2);
    expect(results[0].id).toBe(12345);
    expect(results[0].hd_url).toBe('https://videos.pexels.com/12345-hd.mp4');
    expect(results[0].duration).toBe(15);
    expect(results[1].id).toBe(67890);
    expect(results[1].hd_url).toBe('https://videos.pexels.com/67890-sd.mp4');
  });

  test('prefers HD MP4 over SD', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => PEXELS_RESPONSE,
    });

    const results = await searchPexels('test');
    // First video: HD selected as primary, SD available as fallback
    expect(results[0].hd_url).toContain('hd');
    expect(results[0].sd_url).toContain('sd');
    // Second video: only SD available, used as primary hd_url
    expect(results[1].hd_url).toContain('sd');
  });

  test('filters by minDuration', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => PEXELS_RESPONSE,
    });

    const results = await searchPexels('test', { minDuration: 10 });
    expect(results).toHaveLength(1); // only 12345 (15s), not 67890 (8s)
    expect(results[0].id).toBe(12345);
  });

  test('throws without PEXELS_API_KEY', async () => {
    delete process.env.PEXELS_API_KEY;
    await expect(searchPexels('test')).rejects.toThrow('PEXELS_API_KEY');
  });

  test('throws on API error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 429,
      statusText: 'Too Many Requests',
    });

    await expect(searchPexels('test')).rejects.toThrow('Pexels API error: 429');
  });

  test('sends Authorization header', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ videos: [] }),
    });

    await searchPexels('query');
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('api.pexels.com/videos/search'),
      expect.objectContaining({ headers: { Authorization: 'test-key' } }),
    );
  });
});

// ============================================================
// Route integration: stock search + download
// ============================================================

describe('Stock routes', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    resetStore();
    process.env.PEXELS_API_KEY = 'test-key';
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    storyboardPath = proj.storyboardPath;
    await loadProject(tmpDir, storyboardPath);
  });

  test('POST /api/media/stock/search — returns results', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => PEXELS_RESPONSE,
    });

    const res = await request(app)
      .post('/api/media/stock/search')
      .send({ query: 'farm', count: 5 });

    expect(res.status).toBe(200);
    expect(res.body.results).toHaveLength(2);
    expect(res.body.count).toBe(2);
    expect(res.body.results[0].id).toBe(12345);
  });

  test('POST /api/media/stock/search — 400 without query', async () => {
    const res = await request(app)
      .post('/api/media/stock/search')
      .send({});

    expect(res.status).toBe(400);
    expect(res.body.detail).toContain('query');
  });

  test('POST /api/media/stock/download — downloads file', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      body: new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode('fake video data'));
          controller.close();
        },
      }),
    });

    const res = await request(app)
      .post('/api/media/stock/download')
      .send({
        url: 'https://videos.pexels.com/12345.mp4',
        filename: 'test-clip.mp4',
      });

    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.path).toBe(path.join('stock', 'test-clip.mp4'));
    expect(res.body.name).toBe('test-clip.mp4');
  });

  test('POST /api/media/stock/download — blocks non-HTTPS', async () => {
    const res = await request(app)
      .post('/api/media/stock/download')
      .send({
        url: 'http://evil.com/malware.exe',
        filename: 'bad.mp4',
      });

    expect(res.status).toBe(400);
    expect(res.body.detail).toContain('HTTPS');
  });

  test('POST /api/media/stock/download — 400 without params', async () => {
    const res = await request(app)
      .post('/api/media/stock/download')
      .send({});

    expect(res.status).toBe(400);
    expect(res.body.detail).toContain('url or filename');
  });
});

describe('Acquire media route', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    resetStore();
    process.env.PEXELS_API_KEY = 'test-key';
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    storyboardPath = proj.storyboardPath;
    await loadProject(tmpDir, storyboardPath);
  });

  test('POST /api/projects/acquire-media — processes segments with queries', async () => {
    // Mock Pexels search
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => PEXELS_RESPONSE,
    });
    // Mock download
    mockFetch.mockResolvedValueOnce({
      ok: true,
      body: new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode('video'));
          controller.close();
        },
      }),
    });

    const res = await request(app)
      .post('/api/projects/acquire-media');

    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.queries).toBe(1); // only seg-01 has query + no src
    expect(res.body.downloaded).toBe(1);
  });

  test('POST /api/projects/acquire-media — skips segments with src', async () => {
    // seg-02 already has src, so only seg-01 should be queried
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ videos: [] }), // no results
    });

    const res = await request(app)
      .post('/api/projects/acquire-media');

    expect(res.status).toBe(200);
    expect(res.body.queries).toBe(1);
    expect(res.body.matched).toBe(0);
    expect(res.body.errors).toHaveLength(1);
  });
});

describe('Download entry route', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    resetStore();
    process.env.PEXELS_API_KEY = 'test-key';
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    storyboardPath = proj.storyboardPath;
    await loadProject(tmpDir, storyboardPath);
  });

  test('POST /api/projects/download-entry — downloads and assigns', async () => {
    // Search
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => PEXELS_RESPONSE,
    });
    // Download
    mockFetch.mockResolvedValueOnce({
      ok: true,
      body: new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode('video'));
          controller.close();
        },
      }),
    });

    const res = await request(app)
      .post('/api/projects/download-entry')
      .send({ segment_id: 'seg-01' });

    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.path).toContain('stock/');
    expect(res.body.query).toBe('aerial farm dusk');

    // Verify assignment persisted
    const project = store.get();
    const seg = project.segments.find(s => s.id === 'seg-01');
    expect(seg?.visual[0].src).toContain('stock/');
  });

  test('POST /api/projects/download-entry — 400 without segment_id', async () => {
    const res = await request(app)
      .post('/api/projects/download-entry')
      .send({});

    expect(res.status).toBe(400);
    expect(res.body.detail).toContain('segment_id');
  });

  test('POST /api/projects/download-entry — 404 for unknown segment', async () => {
    const res = await request(app)
      .post('/api/projects/download-entry')
      .send({ segment_id: 'nonexistent' });

    expect(res.status).toBe(404);
  });

  test('POST /api/projects/download-entry — returns no_results when Pexels has none', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ videos: [] }),
    });

    const res = await request(app)
      .post('/api/projects/download-entry')
      .send({ segment_id: 'seg-01' });

    expect(res.status).toBe(200);
    expect(res.body.status).toBe('no_results');
    expect(res.body.path).toBeNull();
  });
});
