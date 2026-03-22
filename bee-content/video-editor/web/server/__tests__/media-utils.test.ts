import { describe, test, expect, vi, beforeEach } from 'vitest';
import { probeDuration } from '../lib/media-utils.js';
import * as child_process from 'node:child_process';

// Mock child_process.execFile
vi.mock('node:child_process', () => ({
  execFile: vi.fn(),
}));

const mockExecFile = vi.mocked(child_process.execFile);

describe('probeDuration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('returns duration from ffprobe JSON output', async () => {
    mockExecFile.mockImplementation((_cmd, _args, _opts, callback: any) => {
      callback(null, JSON.stringify({ format: { duration: '12.345' } }), '');
      return {} as any;
    });

    const result = await probeDuration('/path/to/video.mp4');
    expect(result).toBeCloseTo(12.345);
  });

  test('calls ffprobe with correct arguments', async () => {
    mockExecFile.mockImplementation((_cmd, _args, _opts, callback: any) => {
      callback(null, JSON.stringify({ format: { duration: '5.0' } }), '');
      return {} as any;
    });

    await probeDuration('/path/to/clip.mp4');
    expect(mockExecFile).toHaveBeenCalledWith(
      'ffprobe',
      ['-v', 'quiet', '-print_format', 'json', '-show_format', '/path/to/clip.mp4'],
      { timeout: 10000 },
      expect.any(Function),
    );
  });

  test('returns null when ffprobe errors (e.g. not installed)', async () => {
    mockExecFile.mockImplementation((_cmd, _args, _opts, callback: any) => {
      callback(new Error('ENOENT'), '', '');
      return {} as any;
    });

    const result = await probeDuration('/path/to/video.mp4');
    expect(result).toBeNull();
  });

  test('returns null for invalid JSON output', async () => {
    mockExecFile.mockImplementation((_cmd, _args, _opts, callback: any) => {
      callback(null, 'not json', '');
      return {} as any;
    });

    const result = await probeDuration('/path/to/video.mp4');
    expect(result).toBeNull();
  });

  test('returns null when duration is missing from format', async () => {
    mockExecFile.mockImplementation((_cmd, _args, _opts, callback: any) => {
      callback(null, JSON.stringify({ format: {} }), '');
      return {} as any;
    });

    const result = await probeDuration('/path/to/video.mp4');
    expect(result).toBeNull();
  });

  test('returns null when format is missing', async () => {
    mockExecFile.mockImplementation((_cmd, _args, _opts, callback: any) => {
      callback(null, JSON.stringify({}), '');
      return {} as any;
    });

    const result = await probeDuration('/path/to/video.mp4');
    expect(result).toBeNull();
  });

  test('handles integer duration', async () => {
    mockExecFile.mockImplementation((_cmd, _args, _opts, callback: any) => {
      callback(null, JSON.stringify({ format: { duration: '60' } }), '');
      return {} as any;
    });

    const result = await probeDuration('/path/to/video.mp4');
    expect(result).toBe(60);
  });
});
