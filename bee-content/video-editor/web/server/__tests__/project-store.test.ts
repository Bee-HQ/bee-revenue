import { describe, test, expect, beforeEach } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

// Import the class directly (not the singleton) by re-importing the module.
// ProjectStore is not exported — we access it via a fresh import each test by
// instantiating it ourselves through a thin wrapper we expose via a factory.
// Since the class is not exported we use a workaround: import the module file
// as text isn't possible cleanly, so instead we duplicate minimal logic and
// test the exported `store` singleton reset pattern.
//
// Actually: the task says "Create a fresh ProjectStore instance per test".
// The class itself is not exported from project-store.ts — only the singleton
// `store` is. We'll work around this by importing the singleton and resetting
// its internal state between tests using a cast to `any`.

import { store as _store } from '../services/project-store.js';

// Helper: cast to any so we can reset private state between tests
function freshStore() {
  // Reset the singleton's private fields so each test starts clean
  const s = _store as any;
  s.project = null;
  s.projectDir = null;
  s.jsonPath = null;
  return _store;
}

// ---------- Fixture ----------

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
  "overlay": [{"type": "LOWER_THIRD", "content": "Location Name"}],
  "music": [{"type": "MUSIC", "src": null, "volume": 0.2}],
  "transition": {"type": "FADE_FROM_BLACK", "duration": 1.5}
}
\`\`\`

### seg-02 | Scene Two

\`\`\`bee-video:segment
{
  "duration": 20,
  "visual": [{"type": "STOCK", "src": null, "query": "crime scene"}],
  "audio": [{"type": "NAR", "text": "More narration", "src": null}],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`
`;

// ---------- Helper: write storyboard to a temp dir ----------

function makeTempProject(): { tmpDir: string; mdPath: string } {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'bee-project-test-'));
  const mdPath = path.join(tmpDir, 'storyboard.md');
  fs.writeFileSync(mdPath, STORYBOARD_MD, 'utf-8');
  return { tmpDir, mdPath };
}

// ---------- Tests ----------

describe('ProjectStore', () => {
  let store: typeof _store;

  beforeEach(() => {
    store = freshStore();
  });

  // 1. loadFromMarkdown
  describe('loadFromMarkdown', () => {
    test('returns BeeProject with correct metadata', () => {
      const { tmpDir, mdPath } = makeTempProject();
      const project = store.loadFromMarkdown(mdPath, tmpDir);

      expect(project.version).toBe(1);
      expect(project.title).toBe('Test Video');
      expect(project.fps).toBe(30);
      expect(project.resolution).toEqual([1920, 1080]);
    });

    test('returns 2 segments with correct ids, titles, sections', () => {
      const { tmpDir, mdPath } = makeTempProject();
      const project = store.loadFromMarkdown(mdPath, tmpDir);

      expect(project.segments).toHaveLength(2);

      expect(project.segments[0].id).toBe('seg-01');
      expect(project.segments[0].title).toBe('Cold Open');
      expect(project.segments[0].section).toBe('Act 1');

      expect(project.segments[1].id).toBe('seg-02');
      expect(project.segments[1].title).toBe('Scene Two');
      expect(project.segments[1].section).toBe('Act 1');
    });

    test('writes .bee-project.json to disk', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      const jsonPath = path.join(tmpDir, '.bee-project.json');
      expect(fs.existsSync(jsonPath)).toBe(true);

      const parsed = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
      expect(parsed.title).toBe('Test Video');
    });

    test('writes session.json to {projectDir}/.bee-video/', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      const sessionPath = path.join(tmpDir, '.bee-video', 'session.json');
      expect(fs.existsSync(sessionPath)).toBe(true);
    });
  });

  // 2. get() throws when no project loaded
  describe('get()', () => {
    test('throws with status 404 when no project loaded', () => {
      expect(() => store.get()).toThrow('No project loaded');
      try {
        store.get();
      } catch (err: any) {
        expect(err.status).toBe(404);
      }
    });
  });

  // 3. getProjectDir() throws when no project loaded
  describe('getProjectDir()', () => {
    test('throws with status 404 when no project loaded', () => {
      expect(() => store.getProjectDir()).toThrow('No project loaded');
      try {
        store.getProjectDir();
      } catch (err: any) {
        expect(err.status).toBe(404);
      }
    });

    test('returns correct dir after load', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);
      expect(store.getProjectDir()).toBe(tmpDir);
    });
  });

  // 4. assignMedia
  describe('assignMedia', () => {
    test('assigns visual src', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.assignMedia('seg-01', 'visual', 0, 'footage/clip.mp4');

      const seg = store.get().segments.find(s => s.id === 'seg-01')!;
      expect(seg.visual[0].src).toBe('footage/clip.mp4');
    });

    test('assigns audio src', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.assignMedia('seg-01', 'audio', 0, 'narration/seg-01.mp3');

      const seg = store.get().segments.find(s => s.id === 'seg-01')!;
      expect(seg.audio[0].src).toBe('narration/seg-01.mp3');
    });

    test('assigns music src', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.assignMedia('seg-01', 'music', 0, 'music/bg.mp3');

      const seg = store.get().segments.find(s => s.id === 'seg-01')!;
      expect(seg.music[0].src).toBe('music/bg.mp3');
    });

    test('throws 400 for unknown layer', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      expect(() => store.assignMedia('seg-01', 'unknown', 0, 'file.mp4')).toThrow();
      try {
        store.assignMedia('seg-01', 'unknown', 0, 'file.mp4');
      } catch (err: any) {
        expect(err.status).toBe(400);
      }
    });
  });

  // 5. updateSegment — visual_updates
  describe('updateSegment — visual_updates', () => {
    test('sets color and kenBurns on visual entry', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.updateSegment('seg-01', {
        visual_updates: [{ index: 0, color: 'noir', kenBurns: 'zoom_in' }],
      });

      const seg = store.get().segments.find(s => s.id === 'seg-01')!;
      expect(seg.visual[0].color).toBe('noir');
      expect(seg.visual[0].kenBurns).toBe('zoom_in');
    });
  });

  // 6. updateSegment — audio_updates
  describe('updateSegment — audio_updates', () => {
    test('sets volume on audio entry', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.updateSegment('seg-01', {
        audio_updates: [{ index: 0, volume: 0.5 }],
      });

      const seg = store.get().segments.find(s => s.id === 'seg-01')!;
      expect(seg.audio[0].volume).toBe(0.5);
    });
  });

  // 7. updateSegment — transition_in
  describe('updateSegment — transition_in', () => {
    test('sets transition on segment', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.updateSegment('seg-02', {
        transition_in: { type: 'dissolve', duration: 1.0 },
      });

      const seg = store.get().segments.find(s => s.id === 'seg-02')!;
      expect(seg.transition).not.toBeNull();
      expect(seg.transition!.type).toBe('dissolve');
      expect(seg.transition!.duration).toBe(1.0);
    });

    test('clears transition when null is passed', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      // First set a transition
      store.updateSegment('seg-02', {
        transition_in: { type: 'dissolve', duration: 1.0 },
      });

      // Then clear it
      store.updateSegment('seg-02', { transition_in: null });

      const seg = store.get().segments.find(s => s.id === 'seg-02')!;
      expect(seg.transition).toBeNull();
    });
  });

  // 8. reorderSegments
  describe('reorderSegments', () => {
    test('reorders segments array', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.reorderSegments(['seg-02', 'seg-01']);

      const segments = store.get().segments;
      expect(segments[0].id).toBe('seg-02');
      expect(segments[1].id).toBe('seg-01');
    });

    test('recalculates start times after reorder', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.reorderSegments(['seg-02', 'seg-01']);

      const segments = store.get().segments;
      // seg-02 duration = 20, seg-01 duration = 15
      expect(segments[0].start).toBe(0);
      expect(segments[1].start).toBe(20);
    });
  });

  // 9. save updates timestamp
  describe('save()', () => {
    test('updates updatedAt timestamp', async () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      const before = store.get().updatedAt;

      // Wait a tick to ensure timestamp differs
      await new Promise(r => setTimeout(r, 5));

      store.save();

      const after = store.get().updatedAt;
      expect(after).not.toBe(before);
      expect(new Date(after).getTime()).toBeGreaterThan(new Date(before).getTime());
    });
  });

  // 10. loadFromJson
  describe('loadFromJson', () => {
    test('loads existing .bee-project.json and returns same project', () => {
      const { tmpDir, mdPath } = makeTempProject();
      const original = store.loadFromMarkdown(mdPath, tmpDir);
      const jsonPath = path.join(tmpDir, '.bee-project.json');

      // Fresh store state
      store = freshStore();
      const loaded = store.loadFromJson(jsonPath);

      expect(loaded.title).toBe(original.title);
      expect(loaded.fps).toBe(original.fps);
      expect(loaded.resolution).toEqual(original.resolution);
      expect(loaded.segments).toHaveLength(original.segments.length);
      expect(loaded.segments[0].id).toBe(original.segments[0].id);
      expect(loaded.segments[1].id).toBe(original.segments[1].id);
    });

    test('sets projectDir from json path dirname', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);
      const jsonPath = path.join(tmpDir, '.bee-project.json');

      store = freshStore();
      store.loadFromJson(jsonPath);

      expect(store.getProjectDir()).toBe(tmpDir);
    });
  });

  // 11. updateProduction
  describe('updateProduction', () => {
    test('merges narrationEngine and narrationVoice into production', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.updateProduction({ narrationEngine: 'elevenlabs', narrationVoice: 'Daniel' });

      const production = store.get().production;
      expect(production.narrationEngine).toBe('elevenlabs');
      expect(production.narrationVoice).toBe('Daniel');
    });

    test('preserves existing production fields not in update', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);
      const originalMode = store.get().production.transitionMode;

      store.updateProduction({ narrationEngine: 'openai' });

      expect(store.get().production.transitionMode).toBe(originalMode);
    });
  });

  // 12. persistence
  describe('persistence', () => {
    test('assignMedia writes src to .bee-project.json on disk', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.assignMedia('seg-01', 'visual', 0, 'footage/clip.mp4');

      const jsonPath = path.join(tmpDir, '.bee-project.json');
      const persisted = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
      const seg = persisted.segments.find((s: any) => s.id === 'seg-01');
      expect(seg.visual[0].src).toBe('footage/clip.mp4');
    });

    test('save() writes updated project state to disk', () => {
      const { tmpDir, mdPath } = makeTempProject();
      store.loadFromMarkdown(mdPath, tmpDir);

      store.updateSegment('seg-01', {
        visual_updates: [{ index: 0, color: 'noir' }],
      });

      const jsonPath = path.join(tmpDir, '.bee-project.json');
      const persisted = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
      const seg = persisted.segments.find((s: any) => s.id === 'seg-01');
      expect(seg.visual[0].color).toBe('noir');
    });
  });
});
