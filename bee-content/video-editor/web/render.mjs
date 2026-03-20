#!/usr/bin/env node
/**
 * Remotion render script — called by the Python backend as a subprocess.
 *
 * Usage: node render.mjs <storyboard-json-path> <output-path> [--codec h264] [--crf 18]
 *
 * Reads storyboard JSON from a file, bundles the BeeComposition,
 * and renders to the specified output path.
 */

import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: node render.mjs <storyboard-json-path> <output-path> [--codec h264] [--crf 18]');
  process.exit(1);
}

const storyboardPath = args[0];
const outputPath = args[1];

// Parse optional flags
let codec = 'h264';
let crf = 18;
for (let i = 2; i < args.length; i++) {
  if (args[i] === '--codec' && args[i + 1]) codec = args[++i];
  if (args[i] === '--crf' && args[i + 1]) crf = parseInt(args[++i]);
}

async function main() {
  console.log(`Rendering: codec=${codec}, crf=${crf}`);
  console.log(`Storyboard: ${storyboardPath}`);
  console.log(`Output: ${outputPath}`);

  // Read storyboard JSON
  const storyboard = JSON.parse(readFileSync(storyboardPath, 'utf-8'));

  // Bundle the web app (contains BeeComposition)
  console.log('Bundling...');
  const bundleLocation = await bundle({
    entryPoint: resolve('./src/remotion-entry.tsx'),
    webpackOverride: (config) => config,
  });

  // Select the composition
  console.log('Selecting composition...');
  const composition = await selectComposition({
    serveUrl: bundleLocation,
    id: 'BeeVideo',
    inputProps: { storyboard },
  });

  // Render
  console.log(`Rendering ${composition.durationInFrames} frames at ${composition.fps}fps...`);
  await renderMedia({
    composition,
    serveUrl: bundleLocation,
    codec,
    crf,
    outputLocation: outputPath,
    inputProps: { storyboard },
    onProgress: ({ progress }) => {
      const pct = Math.round(progress * 100);
      process.stdout.write(`\rProgress: ${pct}%`);
    },
  });

  console.log(`\nDone: ${outputPath}`);
}

main().catch((err) => {
  console.error('Render failed:', err.message);
  process.exit(1);
});
