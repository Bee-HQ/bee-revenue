import React from 'react';
import { SpringReveal } from './SpringReveal';
import { useQuality } from './QualityContext';

type Direction = 'left' | 'right' | 'up' | 'down' | 'scale';

interface Props {
  interval?: number;
  direction?: Direction;
  children: React.ReactNode;
}

export const StaggerChildren: React.FC<Props> = ({
  interval = 8,
  direction = 'up',
  children,
}) => {
  const { timingMultiplier } = useQuality();
  const adjustedInterval = Math.round(interval * timingMultiplier);
  const childArray = React.Children.toArray(children);

  return (
    <>
      {childArray.map((child, i) => (
        <SpringReveal key={i} direction={direction} delay={i * adjustedInterval}>
          {child}
        </SpringReveal>
      ))}
    </>
  );
};
