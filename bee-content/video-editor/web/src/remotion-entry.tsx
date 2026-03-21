import { registerRoot, Composition } from 'remotion';
import { BeeComposition } from './components/BeeComposition.tsx';
import type { Storyboard } from './types/index.ts';

const Root: React.FC = () => {
  return (
    <Composition
      id="BeeVideo"
      component={BeeComposition}
      durationInFrames={30 * 60}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ storyboard: null as unknown as Storyboard, mediaFiles: [] as string[] }}
      calculateMetadata={({ props }) => {
        const sb = props.storyboard;
        if (!sb) return { durationInFrames: 1 };
        return {
          durationInFrames: Math.max(1, Math.round(sb.total_duration_seconds * 30)),
        };
      }}
    />
  );
};

registerRoot(Root);
