/**
 * Consistency tests — ensures component registries, DEFAULT_DURATIONS,
 * and the storyboard parser stay in sync. If you add a new Remotion
 * component, these tests will tell you what else needs updating.
 */
import { describe, test, expect } from 'vitest';
import { DEFAULT_DURATIONS } from './overlays';
import { VISUAL_TYPE_MAP } from '../../../shared/storyboard-parser';

// These are the component type keys registered in BeeComposition.tsx.
// Maintained here as the single test-side source of truth.
// If you add a component to OVERLAY_COMPONENTS or VISUAL_COMPONENTS,
// add it here too — the test will then verify the rest of the chain.

const OVERLAY_REGISTRY_KEYS = [
  'QUOTE_CARD', 'FINANCIAL_CARD', 'TEXT_OVERLAY', 'TIMELINE_MARKER',
  'TEXT_CHAT', 'EVIDENCE_BOARD', 'MAP', 'SOCIAL_POST', 'PIP',
  'AUDIO_VIS', 'WAVEFORM', 'CALLOUT', 'KINETIC_TEXT',
  'SOURCE_BADGE', 'BULLET_LIST', 'PHOTO_VIEWER', 'INFO_CARD',
  'NOTEPAD', 'MAP_ANNOTATION', 'DRAMATIC_QUOTE',
];

const VISUAL_REGISTRY_KEYS = [
  'KINETIC_TEXT', 'CALLOUT',
  'BULLET_LIST', 'PHOTO_VIEWER', 'INFO_CARD', 'NOTEPAD',
];

// Components handled specially in BeeComposition (not via registry)
const SPECIAL_CASES = ['LOWER_THIRD', 'TEXT_CHAT', 'SOCIAL_POST', 'EVIDENCE_BOARD', 'WAVEFORM'];

describe('Component registry consistency', () => {

  test('every OVERLAY_COMPONENTS key has a DEFAULT_DURATIONS entry', () => {
    const missing = OVERLAY_REGISTRY_KEYS.filter(key => !(key in DEFAULT_DURATIONS));
    expect(missing, `Missing DEFAULT_DURATIONS entries: ${missing.join(', ')}`).toEqual([]);
  });

  test('every VISUAL_COMPONENTS key has a DEFAULT_DURATIONS entry', () => {
    const missing = VISUAL_REGISTRY_KEYS.filter(key => !(key in DEFAULT_DURATIONS));
    expect(missing, `Missing DEFAULT_DURATIONS entries: ${missing.join(', ')}`).toEqual([]);
  });

  test('every VISUAL_COMPONENTS key is also in OVERLAY_COMPONENTS (dual registration)', () => {
    const missing = VISUAL_REGISTRY_KEYS.filter(key => !OVERLAY_REGISTRY_KEYS.includes(key));
    expect(missing, `Visual-only keys not in overlay registry: ${missing.join(', ')}`).toEqual([]);
  });

});

describe('Storyboard parser consistency', () => {

  test('every OVERLAY_COMPONENTS key has a parser pass-through (underscore form)', () => {
    const missing = OVERLAY_REGISTRY_KEYS.filter(key => {
      // The key itself should be in the map as a pass-through
      return VISUAL_TYPE_MAP[key] !== key;
    });
    // Filter out types that are only used as overlays and don't need visual pass-through
    // (e.g., SOURCE_BADGE, MAP_ANNOTATION, DRAMATIC_QUOTE are overlay-only)
    const overlayOnly = ['SOURCE_BADGE', 'MAP_ANNOTATION', 'DRAMATIC_QUOTE',
      'AUDIO_VIS', 'WAVEFORM', 'MAP', 'PIP',
      'QUOTE_CARD', 'FINANCIAL_CARD', 'TEXT_OVERLAY', 'TIMELINE_MARKER'];
    const actualMissing = missing.filter(k => !overlayOnly.includes(k));
    expect(actualMissing, `Missing parser pass-throughs: ${actualMissing.join(', ')}`).toEqual([]);
  });

  test('every VISUAL_COMPONENTS key has a parser pass-through', () => {
    const missing = VISUAL_REGISTRY_KEYS.filter(key => VISUAL_TYPE_MAP[key] !== key);
    expect(missing, `Missing parser pass-throughs for visual types: ${missing.join(', ')}`).toEqual([]);
  });

  test('every VISUAL_COMPONENTS key has a hyphenated alias in the parser', () => {
    const missing = VISUAL_REGISTRY_KEYS.filter(key => {
      const hyphenated = key.replace(/_/g, '-');
      if (hyphenated === key) return false; // no underscore = no alias needed (e.g., NOTEPAD)
      return VISUAL_TYPE_MAP[hyphenated] !== key;
    });
    expect(missing, `Missing hyphenated parser aliases: ${missing.join(', ')}`).toEqual([]);
  });

  test('legacy codes map to correct new types', () => {
    expect(VISUAL_TYPE_MAP['PIP-SINGLE']).toBe('PHOTO_VIEWER');
    expect(VISUAL_TYPE_MAP['PIP-DUAL']).toBe('PHOTO_VIEWER');
    expect(VISUAL_TYPE_MAP['MUGSHOT-CARD']).toBe('INFO_CARD');
    expect(VISUAL_TYPE_MAP['SPLIT-INFO']).toBe('INFO_CARD');
    expect(VISUAL_TYPE_MAP['POLICE-DB']).toBe('NOTEPAD');
    expect(VISUAL_TYPE_MAP['DOCUMENT-MOCKUP']).toBe('NOTEPAD');
    expect(VISUAL_TYPE_MAP['EVIDENCE-CLOSEUP']).toBe('MAP_ANNOTATION');
  });

  test('standard visual types pass through unchanged', () => {
    const standardTypes = ['FOOTAGE', 'STOCK', 'PHOTO', 'MAP', 'GRAPHIC', 'WAVEFORM', 'BLACK', 'GENERATED'];
    for (const type of standardTypes) {
      expect(VISUAL_TYPE_MAP[type], `${type} should pass through`).toBe(type);
    }
  });

});
