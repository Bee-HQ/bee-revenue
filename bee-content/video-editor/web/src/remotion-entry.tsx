import { registerRoot, Composition } from 'remotion';
import { BeeComposition } from './components/BeeComposition.tsx';
import type { Storyboard } from './types/index.ts';
import { calculateSegmentPositions } from './components/remotion/overlays.ts';

const Root: React.FC = () => {
  return (
    <Composition
      id="BeeVideo"
      component={BeeComposition}
      durationInFrames={30 * 60}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ storyboard: null as unknown as Storyboard, mediaFiles: [] as string[], showCaptions: true, transitionMode: 'overlap' as const }}
      calculateMetadata={({ props }) => {
        const sb = props.storyboard;
        if (!sb) return { durationInFrames: 1 };
        const mode = props.transitionMode || 'overlap';
        const { totalFrames } = calculateSegmentPositions(sb.segments, 30, mode);
        return { durationInFrames: Math.max(1, totalFrames) };
      }}
    />
  );
};

registerRoot(Root);
