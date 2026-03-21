import { defineConfig } from '@playwright/test';

const BACKEND_PORT = 8420;
const FRONTEND_PORT = 5173;

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }]],

  use: {
    baseURL: `http://localhost:${FRONTEND_PORT}`,
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    viewport: { width: 1440, height: 900 },
  },

  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],

  webServer: [
    {
      command: `uv run bee-video serve --port ${BACKEND_PORT}`,
      port: BACKEND_PORT,
      cwd: '..',
      reuseExistingServer: true,
      timeout: 30_000,
    },
    {
      command: `VITE_API_PORT=${BACKEND_PORT} npx vite --port ${FRONTEND_PORT}`,
      port: FRONTEND_PORT,
      reuseExistingServer: true,
      timeout: 15_000,
    },
  ],
});
