import { describe, test, expect, beforeEach, afterAll, vi } from 'vitest';
import request from 'supertest';
import { app } from '../index.js';
import { store } from '../services/project-store.js';
import {
  cleanNarrationText,
  generateNarration,
  getNarrationTask,
  resetNarrationTask,
  VALID_ENGINES,
  DEFAULT_VOICES,
} from '../services/tts.js';
import * as fs from 'node:fs/promises';
import * as fsSync from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';
import type { BeeSegment } from '../../shared/types.js';

// ---------- Mock TTS engines ----------

// Mock node-edge-tts so tests don't make real TTS calls
vi.mock('node-edge-tts', () => ({
  EdgeTTS: class {
    constructor(public opts: any) {}
    async ttsPromise(text: string, outputPath: string) {
      await fs.writeFile(outputPath, `mock-edge-audio:${text.slice(0, 20)}`);
    }
  },
}));

// Mock ElevenLabs SDK
vi.mock('@elevenlabs/elevenlabs-js', () => ({
  ElevenLabsClient: class {
    textToSpeech = {
      async *convert(voiceId: string, opts: any) {
        yield Buffer.from(`mock-elevenlabs-audio:${opts.text.slice(0, 20)}`);
      },
    };
  },
}));

// Mock OpenAI SDK
vi.mock('openai', () => ({
  default: class {
    audio = {
      speech: {
        async create(opts: any) {
          const text = `mock-openai-audio:${opts.input.slice(0, 20)}`;
          return {
            arrayBuffer: async () => new TextEncoder().encode(text).buffer,
          };
        },
      },
    };
  },
}));

// ---------- Store reset helper ----------

function resetStore() {
  const s = store as any;
  s.project = null;
  s.projectDir = null;
  s.jsonPath = null;
}

// ---------- Storyboard fixture (with narration text) ----------

const STORYBOARD_MD = `# TTS Test Video

\`\`\`bee-video:project
{"title": "TTS Test", "fps": 30, "resolution": [1920, 1080]}
\`\`\`

## Act 1

### seg-01 | Opening

\`\`\`bee-video:segment
{
  "duration": 15,
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [{"type": "NAR", "text": "This is the opening narration for segment one.", "src": null}],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`

### seg-02 | Middle

\`\`\`bee-video:segment
{
  "duration": 20,
  "visual": [{"type": "STOCK", "src": null}],
  "audio": [{"type": "NAR", "text": "And here is the second segment narration.", "src": null}],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`

### seg-03 | No Narration

\`\`\`bee-video:segment
{
  "duration": 10,
  "visual": [{"type": "FOOTAGE", "src": null}],
  "audio": [{"type": "SFX", "src": "sfx/boom.mp3"}],
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

async function makeTempProject(): Promise<{ tmpDir: string; storyboardPath: string }> {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'bee-tts-test-'));
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

afterAll(async () => {
  for (const dir of tempDirs) {
    try { await fs.rm(dir, { recursive: true, force: true }); } catch {}
  }
});

// ============================================================
// Unit: cleanNarrationText
// ============================================================

describe('cleanNarrationText', () => {
  test('strips trailing + notes', () => {
    expect(cleanNarrationText('Hello world + some note')).toBe('Hello world');
  });

  test('strips surrounding quotes', () => {
    expect(cleanNarrationText('"Hello world"')).toBe('Hello world');
  });

  test('strips smart quotes', () => {
    expect(cleanNarrationText('\u201cHello world\u201d')).toBe('Hello world');
  });

  test('handles both notes and quotes', () => {
    expect(cleanNarrationText('"Some text" + note')).toBe('Some text');
  });

  test('trims whitespace', () => {
    expect(cleanNarrationText('  spaced out  ')).toBe('spaced out');
  });

  test('returns empty for empty input', () => {
    expect(cleanNarrationText('')).toBe('');
    expect(cleanNarrationText('   ')).toBe('');
  });
});

// ============================================================
// Unit: generateNarration (with mocked engines)
// ============================================================

describe('generateNarration', () => {
  let outputDir: string;
  let segments: BeeSegment[];

  beforeEach(async () => {
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    tempDirs.push(tmpDir);
    outputDir = path.join(tmpDir, 'output', 'narration');

    segments = [
      {
        id: 'seg-01', title: 'Opening', section: 'Act 1',
        start: 0, duration: 15,
        visual: [{ type: 'FOOTAGE', src: null }],
        audio: [{ type: 'NAR', text: 'First segment narration', src: null }],
        overlay: [], music: [], transition: null,
      },
      {
        id: 'seg-02', title: 'Middle', section: 'Act 1',
        start: 15, duration: 20,
        visual: [{ type: 'STOCK', src: null }],
        audio: [{ type: 'NAR', text: 'Second segment narration', src: null }],
        overlay: [], music: [], transition: null,
      },
      {
        id: 'seg-03', title: 'No Nar', section: 'Act 1',
        start: 35, duration: 10,
        visual: [{ type: 'FOOTAGE', src: null }],
        audio: [{ type: 'SFX', src: 'sfx/boom.mp3' }],
        overlay: [], music: [], transition: null,
      },
    ];
  });

  test('generates audio for segments with NAR text (edge)', async () => {
    const result = await generateNarration(segments, 'edge', undefined, outputDir);
    expect(result.succeeded).toHaveLength(2);
    expect(result.failed).toHaveLength(0);

    // Verify files were created
    expect(fsSync.existsSync(path.join(outputDir, 'seg-01.mp3'))).toBe(true);
    expect(fsSync.existsSync(path.join(outputDir, 'seg-02.mp3'))).toBe(true);
    // seg-03 has no NAR, should not be created
    expect(fsSync.existsSync(path.join(outputDir, 'seg-03.mp3'))).toBe(false);
  });

  test('skips segments without NAR audio entry', async () => {
    const result = await generateNarration(segments, 'edge', undefined, outputDir);
    // seg-03 has SFX, not NAR
    expect(result.succeeded).toHaveLength(2);
  });

  test('skips already-generated files', async () => {
    // Pre-create one file
    await fs.mkdir(outputDir, { recursive: true });
    await fs.writeFile(path.join(outputDir, 'seg-01.mp3'), 'existing');

    const result = await generateNarration(segments, 'edge', undefined, outputDir);
    expect(result.succeeded).toHaveLength(1); // only seg-02
    expect(result.succeeded[0]).toContain('seg-02.mp3');
  });

  test('works with elevenlabs engine', async () => {
    const result = await generateNarration(segments, 'elevenlabs', undefined, outputDir);
    expect(result.succeeded).toHaveLength(2);
    expect(result.failed).toHaveLength(0);
  });

  test('works with openai engine', async () => {
    const result = await generateNarration(segments, 'openai', undefined, outputDir);
    expect(result.succeeded).toHaveLength(2);
    expect(result.failed).toHaveLength(0);
  });

  test('throws for invalid engine', async () => {
    await expect(
      generateNarration(segments, 'invalid', undefined, outputDir)
    ).rejects.toThrow('Unknown TTS engine: invalid');
  });

  test('calls onProgress callback', async () => {
    const progress: Array<[number, number]> = [];
    await generateNarration(segments, 'edge', undefined, outputDir, (done, total) => {
      progress.push([done, total]);
    });
    expect(progress).toEqual([[1, 2], [2, 2]]);
  });

  test('uses custom voice when provided', async () => {
    const result = await generateNarration(segments, 'edge', 'en-US-AriaNeural', outputDir);
    expect(result.succeeded).toHaveLength(2);
  });
});

// ============================================================
// Route integration: narration + voice-lock
// ============================================================

describe('Narration routes', () => {
  beforeEach(async () => {
    resetStore();
    resetNarrationTask();
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    storyboardPath = proj.storyboardPath;
    tempDirs.push(tmpDir);
    await loadProject(tmpDir, storyboardPath);
  });

  test('POST /api/production/narration — starts narration', async () => {
    const res = await request(app)
      .post('/api/production/narration')
      .send({ tts_engine: 'edge' });

    expect(res.status).toBe(200);
    expect(res.body.status).toBe('started');
    expect(res.body.total).toBe(2); // seg-01 and seg-02 have NAR text

    // Wait for background task to complete
    await new Promise(r => setTimeout(r, 200));

    const task = getNarrationTask();
    expect(task?.running).toBe(false);
    expect(task?.succeeded.length).toBe(2);
  });

  test('POST /api/production/narration — rejects invalid engine', async () => {
    const res = await request(app)
      .post('/api/production/narration')
      .send({ tts_engine: 'fake' });

    expect(res.status).toBe(400);
    expect(res.body.detail).toContain('Invalid TTS engine');
  });

  test('POST /api/production/narration — 409 if already running', async () => {
    // Start first
    await request(app)
      .post('/api/production/narration')
      .send({ tts_engine: 'edge' });

    // Try again immediately
    const res = await request(app)
      .post('/api/production/narration')
      .send({ tts_engine: 'edge' });

    expect(res.status).toBe(409);
    expect(res.body.detail).toContain('already running');

    // Wait for completion
    await new Promise(r => setTimeout(r, 200));
  });

  test('POST /api/production/narration — persists engine choice', async () => {
    await request(app)
      .post('/api/production/narration')
      .send({ tts_engine: 'openai', tts_voice: 'nova' });

    const project = store.get();
    expect(project.production.narrationEngine).toBe('openai');
    expect(project.production.narrationVoice).toBe('nova');

    // Wait for completion
    await new Promise(r => setTimeout(r, 200));
  });

  test('GET /api/production/narration/status — returns progress', async () => {
    await request(app)
      .post('/api/production/narration')
      .send({ tts_engine: 'edge' });

    // Wait for completion
    await new Promise(r => setTimeout(r, 200));

    const res = await request(app).get('/api/production/narration/status');
    expect(res.status).toBe(200);
    expect(res.body.running).toBe(false);
    expect(res.body.done).toBe(2);
    expect(res.body.status).toBe('ok');
    expect(res.body.succeeded).toHaveLength(2);
  });

  test('GET /api/production/narration/status — no prior task', async () => {
    const res = await request(app).get('/api/production/narration/status');
    expect(res.status).toBe(200);
    expect(res.body.running).toBe(false);
    expect(res.body.done).toBe(0);
  });
});

describe('Voice-lock routes', () => {
  beforeEach(async () => {
    resetStore();
    resetNarrationTask();
    const proj = await makeTempProject();
    tmpDir = proj.tmpDir;
    storyboardPath = proj.storyboardPath;
    tempDirs.push(tmpDir);
    await loadProject(tmpDir, storyboardPath);
  });

  test('GET /api/production/voice-lock — returns defaults', async () => {
    const res = await request(app).get('/api/production/voice-lock');
    expect(res.status).toBe(200);
    expect(res.body.engine).toBe('edge');
  });

  test('PUT /api/production/voice-lock — updates engine and voice', async () => {
    const res = await request(app)
      .put('/api/production/voice-lock')
      .send({ engine: 'elevenlabs', voice: 'custom-voice-id' });

    expect(res.status).toBe(200);
    expect(res.body.engine).toBe('elevenlabs');
    expect(res.body.voice).toBe('custom-voice-id');

    // Verify persistence
    const project = store.get();
    expect(project.production.narrationEngine).toBe('elevenlabs');
    expect(project.production.narrationVoice).toBe('custom-voice-id');
  });

  test('PUT /api/production/voice-lock — rejects invalid engine', async () => {
    const res = await request(app)
      .put('/api/production/voice-lock')
      .send({ engine: 'invalid' });

    expect(res.status).toBe(400);
    expect(res.body.detail).toContain('Invalid TTS engine');
  });

  test('PUT /api/production/voice-lock — partial update (voice only)', async () => {
    // Set initial
    await request(app)
      .put('/api/production/voice-lock')
      .send({ engine: 'openai', voice: 'onyx' });

    // Update only voice
    const res = await request(app)
      .put('/api/production/voice-lock')
      .send({ voice: 'nova' });

    expect(res.status).toBe(200);
    expect(res.body.engine).toBe('openai'); // unchanged
    expect(res.body.voice).toBe('nova');    // updated
  });
});

// ============================================================
// Constants
// ============================================================

describe('TTS constants', () => {
  test('VALID_ENGINES has 3 entries', () => {
    expect(VALID_ENGINES).toEqual(['edge', 'elevenlabs', 'openai']);
  });

  test('DEFAULT_VOICES maps all engines', () => {
    for (const engine of VALID_ENGINES) {
      expect(DEFAULT_VOICES[engine]).toBeTruthy();
    }
  });
});
