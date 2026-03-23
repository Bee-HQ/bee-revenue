import { describe, test, expect } from 'vitest';
import { parseSourceBadgeData } from './SourceBadge';

describe('parseSourceBadgeData', () => {
  test('parses content string as label', () => {
    const result = parseSourceBadgeData('REENACTMENT');
    expect(result).toEqual({ label: 'REENACTMENT', position: 'bottom-left' });
  });

  test('falls back to metadata.text when content is empty', () => {
    const result = parseSourceBadgeData('', { text: 'ACTUAL PHOTO' });
    expect(result).toEqual({ label: 'ACTUAL PHOTO', position: 'bottom-left' });
  });

  test('reads position from metadata', () => {
    const result = parseSourceBadgeData('ACTUAL', { position: 'top-right' });
    expect(result).toEqual({ label: 'ACTUAL', position: 'top-right' });
  });

  test('defaults position to bottom-left', () => {
    const result = parseSourceBadgeData('TEST', {});
    expect(result.position).toBe('bottom-left');
  });

  test('handles null metadata', () => {
    const result = parseSourceBadgeData('LABEL', null);
    expect(result).toEqual({ label: 'LABEL', position: 'bottom-left' });
  });
});
