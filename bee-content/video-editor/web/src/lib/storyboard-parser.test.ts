import { describe, test, expect } from 'vitest';
import { parseStoryboardMarkdown } from './storyboard-parser';

const MINIMAL_MD = `
# My Video

\`\`\`bee-video:project
{"title": "My Video", "fps": 30, "resolution": [1920, 1080]}
\`\`\`

## Act 1

### seg-01 | Cold Open

\`\`\`bee-video:segment
{
  "duration": 15,
  "visual": [{"type": "FOOTAGE", "src": "footage/clip.mp4", "trim": [0, 10]}],
  "audio":  [{"type": "NAR", "text": "Narration text here.", "src": "narration/seg-01.mp3"}],
  "overlay": [{"type": "LOWER_THIRD", "content": "Alex Murdaugh — Defendant"}],
  "music":  [{"type": "MUSIC", "src": "music/bg.mp3", "volume": 0.2}],
  "transition": {"type": "DISSOLVE", "duration": 1.5}
}
\`\`\`

### seg-02 | Second Scene

\`\`\`bee-video:segment
{
  "duration": 20,
  "visual": [{"type": "BROLL-DARK", "src": null, "query": "courtroom aerial"}],
  "audio":  [{"type": "NAR", "text": "More narration.", "src": null}],
  "overlay": [],
  "music":  [],
  "transition": null
}
\`\`\`
`;

describe('parseStoryboardMarkdown', () => {
  test('parses project-level fields', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.title).toBe('My Video');
    expect(project.fps).toBe(30);
    expect(project.resolution).toEqual([1920, 1080]);
    expect(project.version).toBe(1);
  });

  test('produces correct segment count', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments.length).toBe(2);
  });

  test('segment IDs come from ### header', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments[0].id).toBe('seg-01');
    expect(project.segments[1].id).toBe('seg-02');
  });

  test('segment titles come from ### header', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments[0].title).toBe('Cold Open');
    expect(project.segments[1].title).toBe('Second Scene');
  });

  test('segment section comes from ## header', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments[0].section).toBe('Act 1');
    expect(project.segments[1].section).toBe('Act 1');
  });

  test('duration parsed from segment JSON', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments[0].duration).toBe(15);
    expect(project.segments[1].duration).toBe(20);
  });

  test('start times computed cumulatively', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments[0].start).toBe(0);
    expect(project.segments[1].start).toBe(15);
  });

  test('visual entries have src, type, trim as top-level fields', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    const visual = project.segments[0].visual[0];
    expect(visual.src).toBe('footage/clip.mp4');
    expect(visual.type).toBe('FOOTAGE');
    expect(visual.trim).toEqual([0, 10]);
  });

  test('visual src can be null', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments[1].visual[0].src).toBeNull();
  });

  test('visual query preserved', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments[1].visual[0].query).toBe('courtroom aerial');
  });

  test('audio entries have type, text, src', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    const audio = project.segments[0].audio[0];
    expect(audio.type).toBe('NAR');
    expect(audio.text).toBe('Narration text here.');
    expect(audio.src).toBe('narration/seg-01.mp3');
  });

  test('overlay entries have type, content', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    const overlay = project.segments[0].overlay[0];
    expect(overlay.type).toBe('LOWER_THIRD');
    expect(overlay.content).toBe('Alex Murdaugh — Defendant');
  });

  test('music entries have type, src, volume', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    const music = project.segments[0].music[0];
    expect(music.type).toBe('MUSIC');
    expect(music.src).toBe('music/bg.mp3');
    expect(music.volume).toBe(0.2);
  });

  test('transition parsed as object', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    const t = project.segments[0].transition;
    expect(t).not.toBeNull();
    expect(t!.type).toBe('DISSOLVE');
    expect(t!.duration).toBe(1.5);
  });

  test('null transition is stored as null', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments[1].transition).toBeNull();
  });

  test('visual type normalization: BROLL-DARK → STOCK', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments[1].visual[0].type).toBe('STOCK');
  });

  test('empty segments array produces valid BeeProject', () => {
    const md = `
# Empty

\`\`\`bee-video:project
{"title": "Empty", "fps": 24, "resolution": [1920, 1080]}
\`\`\`
`;
    const project = parseStoryboardMarkdown(md);
    expect(project.segments).toEqual([]);
    expect(project.title).toBe('Empty');
    expect(project.fps).toBe(24);
  });

  test('production block has required defaults', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.production.narrationEngine).toBeDefined();
    expect(project.production.narrationVoice).toBeDefined();
    expect(project.production.transitionMode).toMatch(/^(overlap|fade)$/);
    expect(project.production.status.narration).toBeNull();
    expect(project.production.status.stock).toBeNull();
    expect(project.production.status.render).toBeNull();
    expect(project.production.renders).toEqual([]);
  });

  test('createdAt and updatedAt are ISO date strings', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(() => new Date(project.createdAt)).not.toThrow();
    expect(() => new Date(project.updatedAt)).not.toThrow();
  });

  test('segment with no overlay/music gets empty arrays', () => {
    const project = parseStoryboardMarkdown(MINIMAL_MD);
    expect(project.segments[1].overlay).toEqual([]);
    expect(project.segments[1].music).toEqual([]);
  });
});

describe('parseStoryboardMarkdown — timecode durations', () => {
  test('timecode string duration is converted to seconds', () => {
    const md = `
# TC Test

\`\`\`bee-video:project
{"title": "TC Test", "fps": 30, "resolution": [1920, 1080]}
\`\`\`

## Section

### seg-01 | Scene One

\`\`\`bee-video:segment
{
  "duration": "1:30",
  "visual": [{"type": "FOOTAGE", "src": "footage/a.mp4"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`

### seg-02 | Scene Two

\`\`\`bee-video:segment
{
  "duration": "0:45",
  "visual": [{"type": "STOCK", "src": null}],
  "audio": [],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`
`;
    const project = parseStoryboardMarkdown(md);
    expect(project.segments[0].duration).toBe(90);
    expect(project.segments[1].duration).toBe(45);
    expect(project.segments[0].start).toBe(0);
    expect(project.segments[1].start).toBe(90);
  });
});

describe('parseStoryboardMarkdown — ID slugification', () => {
  test('titles without explicit ID get slugified IDs', () => {
    const md = `
# Slug Test

\`\`\`bee-video:project
{"title": "Slug Test", "fps": 30, "resolution": [1920, 1080]}
\`\`\`

## Section

### My Cool Scene

\`\`\`bee-video:segment
{
  "duration": 10,
  "visual": [{"type": "FOOTAGE", "src": "footage/a.mp4"}],
  "audio": [],
  "overlay": [],
  "music": [],
  "transition": null
}
\`\`\`
`;
    const project = parseStoryboardMarkdown(md);
    // ID should be a slugified version of the title
    expect(project.segments[0].id).toMatch(/^[a-z0-9-]+$/);
    expect(project.segments[0].title).toBe('My Cool Scene');
  });
});
