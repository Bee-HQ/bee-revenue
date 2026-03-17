// src/ar/mind-ar.js
export async function createMindARSession({ container, targetSrc, renderer, scene, camera }) {
  const { MindARThree } = await import('mind-ar/dist/mindar-image-three.prod.js');

  const mindar = new MindARThree({
    container,
    imageTargetSrc: targetSrc,
    filterMinCF: 0.001,
    filterBeta: 1000,
    warmupTolerance: 5,
    missTolerance: 5,
    maxTrack: 1,
  });

  const anchor = mindar.addAnchor(0);
  let onFound = null;
  let onLost = null;

  anchor.onTargetFound = () => { if (onFound) onFound(); };
  anchor.onTargetLost = () => { if (onLost) onLost(); };

  return {
    anchor,
    async start() {
      await mindar.start();
    },
    stop() {
      mindar.stop();
    },
    onTargetFound(fn) { onFound = fn; },
    onTargetLost(fn) { onLost = fn; },
    getAnchorGroup() {
      return anchor.group;
    },
  };
}
