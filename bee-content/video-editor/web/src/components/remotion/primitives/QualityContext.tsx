import { createContext, useContext } from 'react';

export type QualityTier = 'standard' | 'premium' | 'social';

export interface SpringConfig {
  mass: number;
  damping: number;
  stiffness: number;
  overshootClamping: boolean;
}

const SPRING_CONFIGS: Record<QualityTier, SpringConfig> = {
  standard: { mass: 1, damping: 12, stiffness: 150, overshootClamping: false },
  premium:  { mass: 1, damping: 8,  stiffness: 100, overshootClamping: false },
  social:   { mass: 1, damping: 20, stiffness: 250, overshootClamping: false },
};

const TIMING_MULTIPLIERS: Record<QualityTier, number> = {
  standard: 1.0,
  premium: 1.4,
  social: 0.7,
};

export function getSpringConfig(tier: QualityTier): SpringConfig {
  return SPRING_CONFIGS[tier];
}

export function getTimingMultiplier(tier: QualityTier): number {
  return TIMING_MULTIPLIERS[tier];
}

interface QualityContextValue {
  tier: QualityTier;
  springConfig: SpringConfig;
  timingMultiplier: number;
}

const QualityCtx = createContext<QualityContextValue>({
  tier: 'standard',
  springConfig: SPRING_CONFIGS.standard,
  timingMultiplier: 1.0,
});

export function QualityProvider({ tier = 'standard', children }: { tier?: QualityTier; children: React.ReactNode }) {
  const value: QualityContextValue = {
    tier,
    springConfig: getSpringConfig(tier),
    timingMultiplier: getTimingMultiplier(tier),
  };
  return <QualityCtx.Provider value={value}>{children}</QualityCtx.Provider>;
}

export function useQuality(): QualityContextValue {
  return useContext(QualityCtx);
}
