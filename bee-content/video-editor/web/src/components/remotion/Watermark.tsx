import React from 'react';
import { AbsoluteFill, Img } from 'remotion';
import { mediaUrl } from './SafeMedia';
import type { WatermarkConfig } from '../../types';

export interface WatermarkProps {
  config: WatermarkConfig;
}

const POSITION_STYLES: Record<WatermarkConfig['position'], React.CSSProperties> = {
  'bottom-right': { bottom: 30, right: 30 },
  'bottom-left': { bottom: 30, left: 30 },
  'top-right': { top: 30, right: 30 },
  'top-left': { top: 30, left: 30 },
};

export const Watermark: React.FC<WatermarkProps> = ({ config }) => {
  const posStyle = POSITION_STYLES[config.position] || POSITION_STYLES['bottom-right'];

  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      <div style={{
        position: 'absolute',
        ...posStyle,
        opacity: config.opacity ?? 0.3,
      }}>
        {config.src ? (
          <Img src={mediaUrl(config.src)} style={{ maxHeight: 40, width: 'auto' }} />
        ) : config.text ? (
          <span style={{
            color: '#fff',
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: 2,
            fontFamily: 'Arial, Helvetica, sans-serif',
          }}>
            {config.text}
          </span>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
