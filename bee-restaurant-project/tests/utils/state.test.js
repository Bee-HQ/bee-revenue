import { describe, it, expect, vi } from 'vitest';
import { createStateMachine } from '../../src/utils/state.js';

describe('createStateMachine', () => {
  const config = {
    initial: 'LOADING',
    states: {
      LOADING:   { LOADED: 'VIEWING' },
      VIEWING:   { START_AR: 'SCANNING', START_NATIVE: 'NATIVE_AR' },
      NATIVE_AR: { BACK: 'VIEWING' },
      SCANNING:  { TARGET_FOUND: 'TRACKING', BACK: 'VIEWING' },
      TRACKING:  { TARGET_LOST: 'STICKY', BACK: 'VIEWING' },
      STICKY:    { TARGET_FOUND: 'TRACKING', TIMEOUT: 'VIEWING', BACK: 'VIEWING' },
    },
  };

  it('starts in initial state', () => {
    const sm = createStateMachine(config);
    expect(sm.current()).toBe('LOADING');
  });

  it('transitions on valid event', () => {
    const sm = createStateMachine(config);
    sm.send('LOADED');
    expect(sm.current()).toBe('VIEWING');
  });

  it('ignores invalid event for current state', () => {
    const sm = createStateMachine(config);
    sm.send('TARGET_FOUND');
    expect(sm.current()).toBe('LOADING');
  });

  it('calls listeners on transition', () => {
    const sm = createStateMachine(config);
    const listener = vi.fn();
    sm.on(listener);
    sm.send('LOADED');
    expect(listener).toHaveBeenCalledWith('VIEWING', 'LOADING');
  });

  it('removes listener with off', () => {
    const sm = createStateMachine(config);
    const listener = vi.fn();
    sm.on(listener);
    sm.off(listener);
    sm.send('LOADED');
    expect(listener).not.toHaveBeenCalled();
  });

  it('supports full Layer 3 flow', () => {
    const sm = createStateMachine(config);
    sm.send('LOADED');
    sm.send('START_AR');
    expect(sm.current()).toBe('SCANNING');
    sm.send('TARGET_FOUND');
    expect(sm.current()).toBe('TRACKING');
    sm.send('TARGET_LOST');
    expect(sm.current()).toBe('STICKY');
    sm.send('TIMEOUT');
    expect(sm.current()).toBe('VIEWING');
  });
});
