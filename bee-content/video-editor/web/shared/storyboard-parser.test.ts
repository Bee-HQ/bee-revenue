import { describe, test, expect } from 'vitest';
import { parseStoryboardMarkdown } from './storyboard-parser';

describe('quality field parsing', () => {
  test('parses quality from project block', () => {
    const md = '```bee-video:project\n{"title":"Test","quality":"premium"}\n```\n';
    const project = parseStoryboardMarkdown(md);
    expect(project.quality).toBe('premium');
  });

  test('defaults quality to undefined when not set', () => {
    const md = '```bee-video:project\n{"title":"Test"}\n```\n';
    const project = parseStoryboardMarkdown(md);
    expect(project.quality).toBeUndefined();
  });
});

describe('new visual type mapping', () => {
  test('KINETIC_TEXT passes through visual type map', () => {
    const md = `### seg-01 | Test\n\`\`\`bee-video:segment\n{"visual":[{"type":"KINETIC_TEXT","src":null}],"audio":[],"overlay":[],"music":[]}\n\`\`\``;
    const project = parseStoryboardMarkdown(md);
    expect(project.segments[0].visual[0].type).toBe('KINETIC_TEXT');
  });

  test('lowercase visual type maps via toUpperCase', () => {
    const md = `### seg-01 | Test\n\`\`\`bee-video:segment\n{"visual":[{"type":"kinetic_text","src":null}],"audio":[],"overlay":[],"music":[]}\n\`\`\``;
    const project = parseStoryboardMarkdown(md);
    expect(project.segments[0].visual[0].type).toBe('KINETIC_TEXT');
  });
});
