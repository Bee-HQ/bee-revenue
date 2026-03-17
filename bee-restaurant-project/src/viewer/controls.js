import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export function createControls(camera, domElement) {
  const controls = new OrbitControls(camera, domElement);

  controls.enableDamping = true;
  controls.dampingFactor = 0.1;

  controls.minPolarAngle = 0.2;
  controls.maxPolarAngle = Math.PI / 2;

  controls.minDistance = 0.2;
  controls.maxDistance = 1.5;

  controls.enablePan = false;

  controls.touches = {
    ONE: 0,
    TWO: 2,
  };

  return controls;
}
