import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

const PRESET_COLORS: Record<string, string> = {
  'animated-teal': '13, 148, 136',
  'animated-red': '220, 38, 38',
  'animated-blue': '59, 130, 246',
};

interface AnimatedBGProps {
  preset: string;
}

export const AnimatedBG: React.FC<AnimatedBGProps> = ({ preset }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const rgb = PRESET_COLORS[preset] || PRESET_COLORS['animated-teal'];

  const orb1X = interpolate(frame, [0, durationInFrames], [-10, 10], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const orb2X = interpolate(frame, [0, durationInFrames], [10, -5], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const streakY = interpolate(frame, [0, durationInFrames], [0, 50], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill>
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(135deg, #0a1628 0%, #0d2847 30%, #0a1628 50%, #0f3060 70%, #0a1628 100%)',
      }} />
      <div style={{
        position: 'absolute', top: '-20%', left: '-10%', width: '60%', height: '140%',
        background: `radial-gradient(ellipse, rgba(${rgb}, 0.15) 0%, transparent 70%)`,
        transform: `translateX(${orb1X}%)`,
      }} />
      <div style={{
        position: 'absolute', top: '10%', right: '-20%', width: '50%', height: '100%',
        background: `radial-gradient(ellipse, rgba(${rgb}, 0.1) 0%, transparent 60%)`,
        transform: `translateX(${orb2X}%)`,
      }} />
      <div style={{
        position: 'absolute', top: 0, left: '20%', width: 2, height: '200%',
        background: `linear-gradient(180deg, transparent, rgba(${rgb}, 0.3), transparent)`,
        transform: `rotate(-25deg) translateY(${streakY}px)`,
      }} />
      <div style={{
        position: 'absolute', top: 0, left: '60%', width: 1, height: '200%',
        background: `linear-gradient(180deg, transparent, rgba(${rgb}, 0.2), transparent)`,
        transform: `rotate(-20deg) translateY(${streakY * 0.7}px)`,
      }} />
    </AbsoluteFill>
  );
};
