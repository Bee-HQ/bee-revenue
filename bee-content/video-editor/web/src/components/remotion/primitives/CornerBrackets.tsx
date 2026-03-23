import React from 'react';

interface CornerBracketsProps {
  children: React.ReactNode;
  color?: string;
  size?: number;
  thickness?: number;
  offset?: number;
  style?: React.CSSProperties;
}

export const CornerBrackets: React.FC<CornerBracketsProps> = ({
  children,
  color = 'rgba(255,255,255,0.6)',
  size = 8,
  thickness = 2,
  offset = 4,
  style,
}) => {
  const cornerBase: React.CSSProperties = {
    position: 'absolute',
    width: size,
    height: size,
    pointerEvents: 'none',
  };

  return (
    <div style={{ position: 'relative', display: 'inline-block', ...style }}>
      {children}
      {/* Top-left */}
      <div style={{
        ...cornerBase,
        top: -offset,
        left: -offset,
        borderTop: `${thickness}px solid ${color}`,
        borderLeft: `${thickness}px solid ${color}`,
      }} />
      {/* Top-right */}
      <div style={{
        ...cornerBase,
        top: -offset,
        right: -offset,
        borderTop: `${thickness}px solid ${color}`,
        borderRight: `${thickness}px solid ${color}`,
      }} />
      {/* Bottom-left */}
      <div style={{
        ...cornerBase,
        bottom: -offset,
        left: -offset,
        borderBottom: `${thickness}px solid ${color}`,
        borderLeft: `${thickness}px solid ${color}`,
      }} />
      {/* Bottom-right */}
      <div style={{
        ...cornerBase,
        bottom: -offset,
        right: -offset,
        borderBottom: `${thickness}px solid ${color}`,
        borderRight: `${thickness}px solid ${color}`,
      }} />
    </div>
  );
};
