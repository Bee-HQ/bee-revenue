import React from 'react';
import { AbsoluteFill } from 'remotion';
import { POSITION_PRESETS, TRANSFORM_DEFAULTS } from '../../../shared/transform';
import type { TransformConfig, PositionPreset } from '../../../shared/transform';

export function resolveTransformStyle(transform: TransformConfig | null | undefined) {
  const t = { ...TRANSFORM_DEFAULTS, ...transform };
  const preset = POSITION_PRESETS[t.position as PositionPreset] || POSITION_PRESETS.center;

  const hasTransform = t.x !== 0 || t.y !== 0 || t.scale !== 1 || t.rotation !== 0;

  return {
    outer: {
      display: 'flex' as const,
      flexDirection: 'column' as const,
      justifyContent: preset.justifyContent,
      alignItems: preset.alignItems,
      padding: preset.padding,
      opacity: t.opacity,
    },
    inner: {
      position: 'relative' as const,
      transform: hasTransform
        ? `translate(${t.x}%, ${t.y}%) scale(${t.scale}) rotate(${t.rotation}deg)`
        : undefined,
    },
  };
}

export const TransformWrapper: React.FC<{
  transform?: TransformConfig | null;
  children: React.ReactNode;
}> = ({ transform, children }) => {
  const styles = resolveTransformStyle(transform);

  return (
    <AbsoluteFill style={styles.outer}>
      <div style={styles.inner}>
        {children}
      </div>
    </AbsoluteFill>
  );
};
