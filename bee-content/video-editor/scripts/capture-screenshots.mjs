#!/usr/bin/env node
/**
 * Capture UI screenshots for docs using Playwright.
 *
 * Usage:
 *   node scripts/capture-screenshots.mjs [version]
 *
 * Starts the backend + frontend, loads the default storyboard,
 * captures all 7 required screenshots, and saves them to
 * docs/screenshots/<version>/ and docs/screenshots/latest/.
 *
 * Requires: playwright (npx playwright install chromium)
 */

import { chromium } from 'playwright';
import { execSync, spawn } from 'child_process';
import { mkdirSync, cpSync, existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const DOCS_DIR = join(ROOT, 'docs', 'screenshots');

// Read version from pyproject.toml
function getVersion() {
  const arg = process.argv[2];
  if (arg) return arg;
  const toml = execSync('cat pyproject.toml', { cwd: ROOT, encoding: 'utf-8' });
  const match = toml.match(/version\s*=\s*"([^"]+)"/);
  return match ? `v${match[1]}` : 'latest';
}

// Wait for a URL to respond
async function waitForServer(url, timeoutMs = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url);
      if (res.ok || res.status < 500) return true;
    } catch {}
    await new Promise(r => setTimeout(r, 500));
  }
  throw new Error(`Server at ${url} did not start within ${timeoutMs}ms`);
}

// Find an open port
function findOpenPort(start) {
  for (let port = start; port < start + 100; port++) {
    try {
      execSync(`ss -tlnp 2>/dev/null | grep -q ":${port} "`, { stdio: 'ignore' });
    } catch {
      return port; // port is free (grep found nothing)
    }
  }
  return start + 100;
}

async function main() {
  const version = getVersion();
  const versionDir = join(DOCS_DIR, version);
  const latestDir = join(DOCS_DIR, 'latest');

  mkdirSync(versionDir, { recursive: true });
  mkdirSync(latestDir, { recursive: true });

  console.log(`Capturing screenshots for ${version}`);

  // Find open ports
  const backendPort = findOpenPort(18420);
  const frontendPort = findOpenPort(15173);

  // Start backend
  console.log(`Starting backend on :${backendPort}`);
  const backend = spawn('uv', ['run', 'bee-video', 'serve', '--dev', '--port', String(backendPort)], {
    cwd: ROOT,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  // Start frontend
  console.log(`Starting frontend on :${frontendPort}`);
  const frontend = spawn('npx', ['vite', '--port', String(frontendPort), '--strictPort'], {
    cwd: join(ROOT, 'web'),
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, VITE_API_PORT: String(backendPort) },
  });

  const cleanup = () => {
    backend.kill();
    frontend.kill();
  };
  process.on('SIGINT', cleanup);
  process.on('SIGTERM', cleanup);

  try {
    console.log('Waiting for servers...');
    await waitForServer(`http://127.0.0.1:${backendPort}/docs`);
    await waitForServer(`http://127.0.0.1:${frontendPort}`);
    console.log('Servers ready');

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 1,
      colorScheme: 'dark',
    });
    const page = await context.newPage();
    const baseUrl = `http://127.0.0.1:${frontendPort}`;

    // --- 01: Load Project screen ---
    console.log('01 - Load project screen');
    await page.goto(baseUrl);
    await page.waitForSelector('form', { timeout: 10000 });
    await page.screenshot({ path: join(versionDir, '01-load-project.png') });

    // --- Load the storyboard ---
    console.log('Loading storyboard...');
    const storyboardInput = page.locator('input[type="text"]').first();
    const projectInput = page.locator('input[type="text"]').nth(1);

    // Clear and fill (defaults may be pre-filled)
    await storyboardInput.fill('../discovery/true-crime/cases/alex-murdaugh/storyboard.md');
    await projectInput.fill('../discovery/true-crime/cases/alex-murdaugh');

    await page.locator('button[type="submit"]').click();

    // Wait for editor to load (segment list appears)
    await page.waitForSelector('header', { timeout: 15000 });
    // Give the UI time to render all segments
    await page.waitForTimeout(2000);

    // --- 02: Editor main view ---
    console.log('02 - Editor main view');
    await page.screenshot({ path: join(versionDir, '02-editor-main.png') });

    // --- Click first segment ---
    const firstSegment = page.locator('aside').first().locator('[class*="cursor-pointer"], [class*="rounded"]').first();
    await firstSegment.click();
    await page.waitForTimeout(500);

    // --- 03: Segment list with selection ---
    console.log('03 - Segment list');
    const leftSidebar = page.locator('aside').first();
    await leftSidebar.screenshot({ path: join(versionDir, '03-segment-list.png') });

    // --- 04: Video player ---
    console.log('04 - Video player');
    const mainArea = page.locator('main');
    const playerArea = mainArea.locator('div').first();
    await playerArea.screenshot({ path: join(versionDir, '04-video-player.png') });

    // --- 05: Media library ---
    console.log('05 - Media library');
    const rightSidebar = page.locator('aside').nth(1);
    await rightSidebar.screenshot({ path: join(versionDir, '05-media-library.png') });

    // --- 06: Production bar ---
    console.log('06 - Production bar');
    const footer = page.locator('footer');
    await footer.screenshot({ path: join(versionDir, '06-production-bar.png') });

    // --- 07: Storyboard timeline (full center column with segment selected) ---
    console.log('07 - Storyboard timeline');
    await mainArea.screenshot({ path: join(versionDir, '07-storyboard-timeline.png') });

    await browser.close();
    console.log(`\nScreenshots saved to ${versionDir}`);

    // Copy to latest/
    const files = readdirSync(versionDir).filter(f => f.endsWith('.png'));
    // Clean latest
    if (existsSync(latestDir)) {
      for (const f of readdirSync(latestDir).filter(f => f.endsWith('.png'))) {
        const { unlinkSync } = await import('fs');
        unlinkSync(join(latestDir, f));
      }
    }
    for (const f of files) {
      cpSync(join(versionDir, f), join(latestDir, f));
    }
    console.log(`Copied ${files.length} screenshots to ${latestDir}`);

  } finally {
    cleanup();
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
