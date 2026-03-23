// @vitest-environment jsdom
import { describe, it, expect } from 'vitest';
import { createLoadingScreen } from '../../src/ui/loading.js';

describe('createLoadingScreen', () => {
  it('does not execute HTML in restaurant name', () => {
    const container = document.createElement('div');
    createLoadingScreen(container, { name: '<img src=x onerror=alert(1)>' });
    const title = container.querySelector('.loading-title');
    expect(title.textContent).toBe('<img src=x onerror=alert(1)>');
    expect(title.innerHTML).not.toContain('<img');
  });

  it('displays plain text restaurant name correctly', () => {
    const container = document.createElement('div');
    createLoadingScreen(container, { name: 'Demo Pizza Co' });
    const title = container.querySelector('.loading-title');
    expect(title.textContent).toBe('Demo Pizza Co');
  });
});
