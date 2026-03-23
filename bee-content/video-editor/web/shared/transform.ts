export interface TransformConfig {
  position?: 'top-left' | 'top' | 'top-right' | 'left' | 'center' | 'right' | 'bottom-left' | 'bottom' | 'bottom-right';
  x?: number;
  y?: number;
  scale?: number;
  rotation?: number;
  opacity?: number;
}

export type PositionPreset = NonNullable<TransformConfig['position']>;

export const POSITION_PRESETS: Record<PositionPreset, {
  justifyContent: string;
  alignItems: string;
  padding: string;
}> = {
  'top-left':     { justifyContent: 'flex-start', alignItems: 'flex-start', padding: '80px 60px 0' },
  'top':          { justifyContent: 'flex-start', alignItems: 'center',     padding: '80px 60px 0' },
  'top-right':    { justifyContent: 'flex-start', alignItems: 'flex-end',   padding: '80px 60px 0' },
  'left':         { justifyContent: 'center',     alignItems: 'flex-start', padding: '0 60px' },
  'center':       { justifyContent: 'center',     alignItems: 'center',     padding: '0' },
  'right':        { justifyContent: 'center',     alignItems: 'flex-end',   padding: '0 60px' },
  'bottom-left':  { justifyContent: 'flex-end',   alignItems: 'flex-start', padding: '0 60px 80px' },
  'bottom':       { justifyContent: 'flex-end',   alignItems: 'center',     padding: '0 60px 80px' },
  'bottom-right': { justifyContent: 'flex-end',   alignItems: 'flex-end',   padding: '0 60px 80px' },
};

export const TRANSFORM_DEFAULTS: Required<TransformConfig> = {
  position: 'center',
  x: 0,
  y: 0,
  scale: 1,
  rotation: 0,
  opacity: 1,
};
