import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createStickyMode } from '../../src/ar/sticky-mode.js';

describe('createStickyMode', () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  it('calls onTimeout after specified delay', () => {
    const onTimeout = vi.fn();
    const sticky = createStickyMode({ timeoutMs: 10000, onTimeout });
    sticky.start();
    vi.advanceTimersByTime(10000);
    expect(onTimeout).toHaveBeenCalledOnce();
  });

  it('cancels timeout on stop', () => {
    const onTimeout = vi.fn();
    const sticky = createStickyMode({ timeoutMs: 10000, onTimeout });
    sticky.start();
    vi.advanceTimersByTime(5000);
    sticky.stop();
    vi.advanceTimersByTime(10000);
    expect(onTimeout).not.toHaveBeenCalled();
  });

  it('resets timeout on restart', () => {
    const onTimeout = vi.fn();
    const sticky = createStickyMode({ timeoutMs: 10000, onTimeout });
    sticky.start();
    vi.advanceTimersByTime(8000);
    sticky.stop();
    sticky.start();
    vi.advanceTimersByTime(8000);
    expect(onTimeout).not.toHaveBeenCalled();
    vi.advanceTimersByTime(2000);
    expect(onTimeout).toHaveBeenCalledOnce();
  });

  it('reports active state', () => {
    const sticky = createStickyMode({ timeoutMs: 10000, onTimeout: () => {} });
    expect(sticky.isActive()).toBe(false);
    sticky.start();
    expect(sticky.isActive()).toBe(true);
    sticky.stop();
    expect(sticky.isActive()).toBe(false);
  });
});
