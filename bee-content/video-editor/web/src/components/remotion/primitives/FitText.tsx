import { useState, useEffect } from 'react';
import { continueRender, delayRender } from 'remotion';

interface Props {
  text: string;
  maxWidth: number;
  maxLines?: number;
  fontFamily?: string;
  fontWeight?: number | string;
  style?: React.CSSProperties;
}

export const FitText: React.FC<Props> = ({
  text,
  maxWidth,
  maxLines = 1,
  fontFamily = 'Arial, Helvetica, sans-serif',
  fontWeight = 700,
  style,
}) => {
  const [fontSize, setFontSize] = useState(48);
  const [handle] = useState(() => delayRender('FitText measuring'));

  useEffect(() => {
    let lo = 8;
    let hi = 200;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;

    while (lo < hi - 1) {
      const mid = Math.floor((lo + hi) / 2);
      ctx.font = `${fontWeight} ${mid}px ${fontFamily}`;
      const measured = ctx.measureText(text);
      const textWidth = measured.width;

      if (maxLines === 1) {
        if (textWidth <= maxWidth) lo = mid;
        else hi = mid;
      } else {
        const totalSpace = maxWidth * maxLines;
        if (textWidth <= totalSpace) lo = mid;
        else hi = mid;
      }
    }

    setFontSize(lo);
    continueRender(handle);
  }, [text, maxWidth, maxLines, fontFamily, fontWeight, handle]);

  return (
    <span style={{ fontSize, fontFamily, fontWeight, lineHeight: 1.2, ...style }}>
      {text}
    </span>
  );
};
