// @vitest-environment jsdom
import { describe, it, expect, vi } from 'vitest';
import { createMenuCarousel } from '../../src/ui/menu-carousel.js';

describe('createMenuCarousel', () => {
  function setup(total = 5) {
    const container = document.createElement('div');
    const onChange = vi.fn();
    const carousel = createMenuCarousel(container, { total, onChange });
    return { container, onChange, carousel };
  }

  it('navigates forward on ArrowRight key', () => {
    const { onChange } = setup();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }));
    expect(onChange).toHaveBeenCalledWith(1);
  });

  it('navigates backward on ArrowLeft key', () => {
    const { onChange, carousel } = setup();
    carousel.goTo(2);
    onChange.mockClear();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }));
    expect(onChange).toHaveBeenCalledWith(1);
  });

  it('wraps around from last to first on ArrowRight', () => {
    const { onChange, carousel } = setup(3);
    carousel.goTo(2);
    onChange.mockClear();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }));
    expect(onChange).toHaveBeenCalledWith(0);
  });

  it('wraps around from first to last on ArrowLeft', () => {
    const { onChange } = setup(3);
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }));
    expect(onChange).toHaveBeenCalledWith(2);
  });

  it('navigates to item when dot is clicked', () => {
    const { container, onChange } = setup(5);
    const dots = container.querySelectorAll('#carousel-dots div');
    dots[3].click();
    expect(onChange).toHaveBeenCalledWith(3);
  });

  it('updates dot styles on navigation', () => {
    const { container, carousel } = setup(3);
    carousel.goTo(1);
    const dots = container.querySelectorAll('#carousel-dots div');
    // jsdom normalizes hex colors to rgb()
    expect(dots[1].style.background).toBe('rgb(122, 122, 255)');
    expect(dots[0].style.background).toBe('rgb(68, 68, 68)');
  });

  it('renders correct number of dots', () => {
    const { container } = setup(5);
    const dots = container.querySelectorAll('#carousel-dots div');
    expect(dots).toHaveLength(5);
  });

  it('cleans up keyboard listener on destroy', () => {
    const { onChange, carousel } = setup();
    carousel.destroy();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }));
    expect(onChange).not.toHaveBeenCalled();
  });
});
