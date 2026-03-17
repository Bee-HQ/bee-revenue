// src/viewer/scene.js
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export function createScene(container) {
  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: true,
    powerPreference: 'high-performance',
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();

  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  scene.environment = pmremGenerator.fromScene(new RoomEnvironment()).texture;
  pmremGenerator.dispose();

  const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.01, 100);
  camera.position.set(0, 0.3, 0.6);
  camera.lookAt(0, 0, 0);

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xfff4e6, 1.0);
  keyLight.position.set(0.5, 1.5, 1.0);
  scene.add(keyLight);

  const onResize = () => {
    const w = container.clientWidth;
    const h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  };
  window.addEventListener('resize', onResize);

  let animationId = null;
  const clock = new THREE.Clock();

  function startLoop(onFrame) {
    function loop() {
      animationId = requestAnimationFrame(loop);
      const delta = clock.getDelta();
      if (onFrame) onFrame(delta);
      renderer.render(scene, camera);
    }
    loop();
  }

  function stopLoop() {
    if (animationId) cancelAnimationFrame(animationId);
    animationId = null;
  }

  function dispose() {
    stopLoop();
    window.removeEventListener('resize', onResize);
    renderer.dispose();
  }

  return { renderer, scene, camera, startLoop, stopLoop, dispose };
}
