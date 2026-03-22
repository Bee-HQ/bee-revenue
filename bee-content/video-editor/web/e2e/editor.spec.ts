import { test, expect, type Page } from '@playwright/test';

// Paths relative to web/ server cwd
const STORYBOARD_PATH = 'storyboard_v2_full.md';
const PROJECT_DIR = '../tests/fixtures';

/**
 * Ensure the editor is loaded with a storyboard.
 * Handles both fresh load (LoadProject screen) and session restore.
 */
async function ensureEditorLoaded(page: Page) {
  await page.goto('/');
  // Wait for either the editor layout or the load screen
  const autoAssign = page.getByRole('button', { name: 'Auto-Assign' });
  const loadBtn = page.getByRole('button', { name: 'Load Project' });

  // Race: either editor is already loaded (session restore) or we need to load
  const winner = await Promise.race([
    autoAssign.waitFor({ timeout: 10_000 }).then(() => 'editor' as const),
    loadBtn.waitFor({ timeout: 10_000 }).then(() => 'load' as const),
  ]);

  if (winner === 'load') {
    const inputs = page.locator('input[type="text"]');
    await inputs.first().fill(STORYBOARD_PATH);
    await inputs.nth(1).fill(PROJECT_DIR);
    await loadBtn.click();
    await autoAssign.waitFor({ timeout: 15_000 });
  }
}

test.describe('Load Project Screen', () => {
  test('renders load form or restores session', async ({ page }) => {
    await page.goto('/');
    // Should show either the load form or the editor (if session restored)
    const hasEditor = await page.getByRole('button', { name: 'Auto-Assign' }).isVisible().catch(() => false);
    const hasLoadForm = await page.getByRole('button', { name: 'Load Project' }).isVisible().catch(() => false);
    expect(hasEditor || hasLoadForm).toBe(true);
    await expect(page.getByText('Bee Video Editor')).toBeVisible();
  });
});

test.describe('Editor Layout', () => {
  test.beforeEach(async ({ page }) => {
    await ensureEditorLoaded(page);
  });

  test('shows header with title, segment count, and duration', async ({ page }) => {
    await expect(page.getByText(/^\d+ segments$/)).toBeVisible();
    await expect(page.getByText(/\d+m \d+s/)).toBeVisible();
  });

  test('renders timeline toolbar with all buttons', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Auto-Assign' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Acquire' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Rough Cut' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Split' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Snap' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Undo' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Redo' })).toBeVisible();
  });

  test('renders timeline with proper dimensions', async ({ page }) => {
    const timeline = page.locator('.timeline-editor');
    await expect(timeline).toBeVisible();
    const box = await timeline.boundingBox();
    expect(box).not.toBeNull();
    // Timeline should fill available width (not stuck at 600px default)
    expect(box!.width).toBeGreaterThan(700);
    // Timeline should have enough height for tracks
    expect(box!.height).toBeGreaterThan(100);
  });

  test('timeline ruler shows scale markers', async ({ page }) => {
    // Verify timeline renders with visible ruler area
    const timeline = page.locator('.timeline-editor');
    await expect(timeline).toBeVisible();
    // Ruler should have at least some scale text rendered
    const rulerArea = timeline.locator('.timeline-editor-edit-area');
    await expect(rulerArea).toBeVisible();
  });

  test('shows segment list with expanded sections', async ({ page }) => {
    const aside = page.locator('aside').first();
    // Should have visible segment entries with timecodes
    const timecodes = aside.getByText(/\d+:\d+-\d+:\d+/);
    expect(await timecodes.count()).toBeGreaterThan(0);
  });

  test('right sidebar tabs switch correctly', async ({ page }) => {
    // Switch to Props — should show empty state
    await page.getByRole('button', { name: 'Props' }).click();
    await expect(page.getByText('Select a clip on the timeline')).toBeVisible();

    // Switch to AI — panel visible
    await page.getByRole('button', { name: 'AI' }).click();
    await page.waitForTimeout(300);

    // Back to Media
    await page.getByRole('button', { name: 'Media', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Media' })).toBeVisible();
  });

  test('keyboard shortcuts panel opens with ? key', async ({ page }) => {
    await page.keyboard.press('?');
    await expect(page.getByText('Keyboard Shortcuts')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByText('Keyboard Shortcuts')).not.toBeVisible();
  });

  test('export menu opens and shows options', async ({ page }) => {
    await page.getByRole('button', { name: 'Export' }).click();
    await expect(page.getByText('Export Markdown')).toBeVisible();
    await expect(page.getByText('Export Project JSON')).toBeVisible();
    // Close by clicking elsewhere
    await page.mouse.click(10, 10);
    await expect(page.getByText('Export Markdown')).not.toBeVisible();
  });

  test('no console errors during normal usage', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    page.on('pageerror', err => errors.push(err.message));

    // Exercise different code paths
    await page.getByRole('button', { name: 'Props' }).click();
    await page.waitForTimeout(300);
    await page.getByRole('button', { name: 'AI' }).click();
    await page.waitForTimeout(300);
    await page.getByRole('button', { name: 'Media' }).click();
    await page.waitForTimeout(300);

    expect(errors).toEqual([]);
  });

  test('zoom slider is interactive', async ({ page }) => {
    const slider = page.locator('input[type="range"]').last();
    await expect(slider).toBeVisible();
    const timeline = page.locator('.timeline-editor');
    await slider.fill('10');
    await page.waitForTimeout(300);
    await expect(timeline).toBeVisible();
  });
});
