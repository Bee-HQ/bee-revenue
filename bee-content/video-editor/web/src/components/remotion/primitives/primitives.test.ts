import { describe, test, expect } from 'vitest';
import { getSpringConfig, getTimingMultiplier } from './QualityContext';

describe('QualityContext helpers', () => {
  test('standard spring config', () => {
    const cfg = getSpringConfig('standard');
    expect(cfg.damping).toBe(12);
    expect(cfg.stiffness).toBe(150);
  });

  test('premium has lower stiffness for elegance', () => {
    const cfg = getSpringConfig('premium');
    expect(cfg.stiffness).toBeLessThan(getSpringConfig('standard').stiffness);
  });

  test('social has higher stiffness for snappiness', () => {
    const cfg = getSpringConfig('social');
    expect(cfg.stiffness).toBeGreaterThan(getSpringConfig('standard').stiffness);
  });

  test('timing multiplier scales duration', () => {
    expect(getTimingMultiplier('standard')).toBe(1);
    expect(getTimingMultiplier('premium')).toBeGreaterThan(1);
    expect(getTimingMultiplier('social')).toBeLessThan(1);
  });
});
