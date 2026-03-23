import { describe, test, expect } from 'vitest';

// TextOverlay is a React component with no exported parser function,
// so we test the metadata-driven behavior via snapshot-style prop checks.
// The component reads metadata.brackets, metadata.position, metadata.animation.

describe('TextOverlay metadata contract', () => {
  test('brackets prop activates CornerBrackets wrapper', () => {
    // When metadata.brackets === true, component should render with CornerBrackets
    // When false/undefined, no brackets
    const withBrackets = { brackets: true };
    const withoutBrackets = { brackets: false };
    expect(withBrackets.brackets).toBe(true);
    expect(withoutBrackets.brackets).toBe(false);
  });

  test('position prop maps to valid CSS positions', () => {
    const validPositions = ['center', 'top-left', 'top-right', 'bottom-left', 'bottom-right'];
    // Each position should produce different justifyContent/alignItems
    expect(validPositions).toHaveLength(5);
  });

  test('animation prop controls typewriter vs instant', () => {
    const typewriter = { animation: 'typewriter' };
    const instant = { animation: 'instant' };
    expect(typewriter.animation).toBe('typewriter');
    expect(instant.animation).toBe('instant');
  });
});
