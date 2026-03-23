import React from 'react';
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { useQuality } from '../primitives/QualityContext';
import { mediaUrl } from '../SafeMedia';
import type { OverlayProps } from '../overlays';

export interface InfoCardSection {
  header: string;
  body: string;
  color?: string;
}

export interface InfoCardData {
  sections: InfoCardSection[];
  src?: string;
  photoSide: 'left' | 'right' | 'none';
}

export function parseInfoCardData(
  content: string,
  metadata?: Record<string, any> | null,
): InfoCardData {
  let sections: InfoCardSection[];

  try {
    const parsed = JSON.parse(content);
    if (parsed && Array.isArray(parsed.sections)) {
      sections = parsed.sections.map((s: any) => ({
        header: s.header || '',
        body: s.body || '',
        color: s.color || undefined,
      }));
    } else {
      throw new Error('not a sections object');
    }
  } catch {
    sections = [{
      header: metadata?.header || '',
      body: content,
      color: undefined,
    }];
  }

  return {
    sections,
    src: metadata?.src || undefined,
    photoSide: (metadata?.photoSide as InfoCardData['photoSide']) || 'right',
  };
}

const DEFAULT_HEADER_COLOR = '#dc2626';

function InfoCardVisual({
  data, durationInFrames, background,
}: { data: InfoCardData; durationInFrames: number; background?: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { springConfig, timingMultiplier } = useQuality();
  const sectionInterval = Math.round(10 * timingMultiplier);

  // Container fade in
  const containerOpacity = interpolate(frame, [0, Math.round(20 * timingMultiplier)], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Exit fade
  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Photo slide in
  const photoProgress = spring({
    frame: Math.max(0, frame - Math.round(10 * timingMultiplier)), fps, config: springConfig,
  });
  const photoTranslateX = data.photoSide === 'left'
    ? interpolate(photoProgress, [0, 1], [-200, 0])
    : interpolate(photoProgress, [0, 1], [200, 0]);

  const showPhoto = data.src && data.photoSide !== 'none';
  const isPhotoLeft = data.photoSide === 'left';

  const sectionsEl = (
    <div style={{
      flex: 1, padding: 40, display: 'flex', flexDirection: 'column',
      justifyContent: 'center', gap: 24,
    }}>
      {data.sections.map((section, i) => {
        const delay = Math.round(5 * timingMultiplier) + i * sectionInterval;
        const progress = spring({
          frame: Math.max(0, frame - delay), fps, config: springConfig,
        });
        const sectionOpacity = interpolate(progress, [0, 1], [0, 1]);
        const translateY = interpolate(progress, [0, 1], [30, 0]);

        return (
          <div key={i} style={{ opacity: sectionOpacity, transform: `translateY(${translateY}px)` }}>
            {section.header && (
              <div style={{
                color: section.color || DEFAULT_HEADER_COLOR,
                fontSize: 24, fontWeight: 800,
                fontFamily: 'Arial, Helvetica, sans-serif',
                marginBottom: 8,
              }}>{section.header}</div>
            )}
            <div style={{
              color: '#e5e5e5', fontSize: 16, lineHeight: 1.5,
              fontFamily: 'Arial, Helvetica, sans-serif',
            }}>{section.body}</div>
          </div>
        );
      })}
    </div>
  );

  const photoEl = showPhoto ? (
    <div style={{
      flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
      transform: `translateX(${photoTranslateX}px)`,
      opacity: interpolate(photoProgress, [0, 1], [0, 1]),
    }}>
      <Img src={mediaUrl(data.src!)} style={{
        maxWidth: '90%', maxHeight: '90%', objectFit: 'cover', borderRadius: 4,
      }} />
    </div>
  ) : null;

  return (
    <AbsoluteFill style={{
      backgroundColor: background, justifyContent: 'center', alignItems: 'center',
    }}>
      <div style={{
        width: '85%', height: '75%', display: 'flex',
        opacity: containerOpacity * exitOpacity,
      }}>
        {isPhotoLeft ? <>{photoEl}{sectionsEl}</> : <>{sectionsEl}{photoEl}</>}
      </div>
    </AbsoluteFill>
  );
}

export const InfoCardOverlay: React.FC<OverlayProps> = (props) => {
  const data = parseInfoCardData(props.content, props.metadata);
  return <InfoCardVisual data={data} durationInFrames={props.durationInFrames} />;
};

export const InfoCard: React.FC<OverlayProps> = (props) => {
  const data = parseInfoCardData(props.content, props.metadata);
  return <InfoCardVisual data={data} durationInFrames={props.durationInFrames} background="#0a0a0a" />;
};
