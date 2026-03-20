import { describe, test, expect } from 'vitest';
import {
  parseTimecode,
  formatTimecode,
  timeToFrames,
  framesToTime,
  timeToMs,
  msToTime,
} from './time-utils';

describe('parseTimecode', () => {
  test('M:SS', () => expect(parseTimecode('2:30')).toBe(150));
  test('H:MM:SS', () => expect(parseTimecode('1:05:30')).toBe(3930));
  test('0:00', () => expect(parseTimecode('0:00')).toBe(0));
});

describe('formatTimecode', () => {
  test('minutes', () => expect(formatTimecode(150)).toBe('2:30'));
  test('hours', () => expect(formatTimecode(3930)).toBe('1:05:30'));
  test('zero', () => expect(formatTimecode(0)).toBe('0:00'));
});

describe('timeToFrames', () => {
  test('30fps', () => expect(timeToFrames(1, 30)).toBe(30));
  test('fractional', () => expect(timeToFrames(0.5, 30)).toBe(15));
});

describe('framesToTime', () => {
  test('30fps', () => expect(framesToTime(30, 30)).toBe(1));
  test('roundtrip', () =>
    expect(framesToTime(timeToFrames(42.5, 30), 30)).toBeCloseTo(42.5, 1));
});

describe('timeToMs', () => {
  test('basic', () => expect(timeToMs(1.5)).toBe(1500));
});

describe('msToTime', () => {
  test('basic', () => expect(msToTime(1500)).toBe(1.5));
});
