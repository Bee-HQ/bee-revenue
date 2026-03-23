import { describe, test, expect } from 'vitest';
import { parseInfoCardData } from './InfoCard';

describe('parseInfoCardData', () => {
  test('parses JSON content with sections array', () => {
    const content = JSON.stringify({
      sections: [
        { header: 'Charges', body: 'First degree murder' },
        { header: 'Sentence', body: 'Life in prison' },
      ],
    });
    const result = parseInfoCardData(content);
    expect(result.sections).toHaveLength(2);
    expect(result.sections[0]).toEqual({ header: 'Charges', body: 'First degree murder', color: undefined });
    expect(result.sections[1]).toEqual({ header: 'Sentence', body: 'Life in prison', color: undefined });
  });

  test('plain text falls back to single section', () => {
    const result = parseInfoCardData('Some plain text', { header: 'Details' });
    expect(result.sections).toEqual([{ header: 'Details', body: 'Some plain text', color: undefined }]);
  });

  test('malformed JSON falls back to plain text', () => {
    const result = parseInfoCardData('{invalid json}', { header: 'Info' });
    expect(result.sections).toEqual([{ header: 'Info', body: '{invalid json}', color: undefined }]);
  });

  test('defaults photoSide to right', () => {
    const result = parseInfoCardData('text');
    expect(result.photoSide).toBe('right');
  });

  test('reads src and photoSide from metadata', () => {
    const result = parseInfoCardData('text', { src: 'photo.jpg', photoSide: 'left' });
    expect(result.src).toBe('photo.jpg');
    expect(result.photoSide).toBe('left');
  });

  test('section color override', () => {
    const content = JSON.stringify({
      sections: [{ header: 'H', body: 'B', color: '#00ff00' }],
    });
    const result = parseInfoCardData(content);
    expect(result.sections[0].color).toBe('#00ff00');
  });

  test('empty sections array', () => {
    const content = JSON.stringify({ sections: [] });
    const result = parseInfoCardData(content);
    expect(result.sections).toEqual([]);
  });

  test('empty content with no header metadata creates section with empty header', () => {
    const result = parseInfoCardData('');
    expect(result.sections).toEqual([{ header: '', body: '', color: undefined }]);
  });
});
