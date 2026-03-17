import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const gltfLoader = new GLTFLoader();
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/');
gltfLoader.setDRACOLoader(dracoLoader);

const cache = new Map();

export function loadModel(url, onProgress) {
  if (cache.has(url)) {
    return Promise.resolve(cache.get(url).clone());
  }

  return new Promise((resolve, reject) => {
    gltfLoader.load(
      url,
      (gltf) => {
        cache.set(url, gltf.scene);
        resolve(gltf.scene.clone());
      },
      (event) => {
        if (onProgress && event.total > 0) {
          onProgress(event.loaded / event.total);
        }
      },
      (error) => reject(new Error(`Failed to load model ${url}: ${error.message}`)),
    );
  });
}

export async function preloadModels(urls) {
  await Promise.allSettled(urls.map((url) => loadModel(url)));
}

export function applyTransform(model, transform) {
  if (transform.scale) model.scale.set(...transform.scale);
  if (transform.position) model.position.set(...transform.position);
  if (transform.rotation) model.rotation.set(...transform.rotation);
}
