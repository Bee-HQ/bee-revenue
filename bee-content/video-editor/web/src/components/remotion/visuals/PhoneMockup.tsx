import React from 'react';
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../primitives/QualityContext';
import { mediaUrl } from '../SafeMedia';
import type { OverlayProps } from '../overlays';
import { AnimatedBG } from '../cards/AnimatedBG';

export interface PhoneMockupData {
  title: string;
  src?: string;
  phoneColor: 'black' | 'red' | 'white';
  tilt: number;
  background: string;
}

const PHONE_COLORS: Record<string, string> = {
  black: '#1a1a1a',
  red: '#991b1b',
  white: '#e5e5e5',
};

export function parsePhoneMockupData(
  content: string,
  metadata?: Record<string, any> | null,
): PhoneMockupData {
  return {
    title: content || metadata?.title || metadata?.text || '',
    src: metadata?.src || undefined,
    phoneColor: (metadata?.phoneColor as PhoneMockupData['phoneColor']) || 'black',
    tilt: typeof metadata?.tilt === 'number' ? metadata.tilt : 0,
    background: (metadata?.background as string) || '#000',
  };
}

function PhoneMockupVisual({
  data, durationInFrames, background,
}: { data: PhoneMockupData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig } = useQuality();

  const exitOpacity = interpolate(
    frame, [durationInFrames - 15, durationInFrames], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  const enterProgress = spring({ frame, fps, config: springConfig });
  const enterScale = interpolate(enterProgress, [0, 1], [0.8, 1]);
  const enterOpacity = interpolate(enterProgress, [0, 1], [0, 1]);

  const bezelColor = PHONE_COLORS[data.phoneColor] || PHONE_COLORS.black;
  const bgStyle = background?.startsWith('animated-') ? undefined : { backgroundColor: background };

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', ...bgStyle }}>
      {background?.startsWith('animated-') && (
        <AbsoluteFill><AnimatedBG preset={background} /></AbsoluteFill>
      )}
      <div style={{
        opacity: exitOpacity * enterOpacity,
        transform: `scale(${enterScale}) rotate(${data.tilt}deg)`,
      }}>
        {/* Phone frame */}
        <div style={{
          width: 240, borderRadius: 28, background: bezelColor,
          padding: '40px 8px 40px 8px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.6)',
          position: 'relative',
        }}>
          {/* Notch */}
          <div style={{
            position: 'absolute', top: 12, left: '50%', transform: 'translateX(-50%)',
            width: 80, height: 20, background: bezelColor, borderRadius: 10,
            zIndex: 2,
          }} />
          {/* Screen */}
          <div style={{
            width: '100%', height: 460, borderRadius: 20, overflow: 'hidden',
            background: '#fff',
          }}>
            {data.src ? (
              <Img src={mediaUrl(data.src)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            ) : (
              <div style={{
                width: '100%', height: '100%', display: 'flex',
                alignItems: 'center', justifyContent: 'center',
                background: '#f0f0f0', color: '#999', fontSize: 14,
                fontFamily: 'system-ui', padding: 20, textAlign: 'center',
              }}>
                {data.title}
              </div>
            )}
          </div>
          {/* Home indicator */}
          <div style={{
            position: 'absolute', bottom: 16, left: '50%', transform: 'translateX(-50%)',
            width: 60, height: 4, background: 'rgba(255,255,255,0.3)', borderRadius: 2,
          }} />
        </div>
      </div>
    </AbsoluteFill>
  );
}

export const PhoneMockupOverlay: React.FC<OverlayProps> = (props) => {
  const data = parsePhoneMockupData(props.content, props.metadata);
  return <PhoneMockupVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const PhoneMockup: React.FC<OverlayProps> = (props) => {
  const data = parsePhoneMockupData(props.content, props.metadata);
  return <PhoneMockupVisual data={data} durationInFrames={props.durationInFrames} background={data.background} />;
};
