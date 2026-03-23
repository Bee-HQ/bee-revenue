import { describe, it, expect, vi } from 'vitest';
import { isInAppBrowser, detectFeatures } from '../../src/utils/device.js';

describe('isInAppBrowser', () => {
  it('detects Instagram in-app browser', () => {
    expect(isInAppBrowser('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Instagram')).toBe(true);
  });

  it('detects Facebook in-app browser', () => {
    expect(isInAppBrowser('Mozilla/5.0 (Linux; Android 13) FBAN/FB4A')).toBe(true);
  });

  it('detects Twitter in-app browser', () => {
    expect(isInAppBrowser('Mozilla/5.0 (iPhone) Twitter for iPhone')).toBe(true);
  });

  it('detects TikTok in-app browser', () => {
    expect(isInAppBrowser('Mozilla/5.0 (iPhone) BytedanceWebview')).toBe(true);
  });

  it('detects LinkedIn in-app browser', () => {
    expect(isInAppBrowser('Mozilla/5.0 (iPhone) LinkedInApp')).toBe(true);
  });

  it('returns false for Safari', () => {
    expect(isInAppBrowser('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')).toBe(false);
  });

  it('returns false for Chrome', () => {
    expect(isInAppBrowser('Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36')).toBe(false);
  });
});

describe('detectFeatures', () => {
  it('returns object with expected keys', () => {
    const features = detectFeatures({
      userAgent: 'Mozilla/5.0 Chrome',
      mediaDevices: { getUserMedia: () => {} },
      xrSystem: null,
      platform: 'Android',
    });
    expect(features).toHaveProperty('hasCamera');
    expect(features).toHaveProperty('hasWebXR');
    expect(features).toHaveProperty('isIOS');
    expect(features).toHaveProperty('isAndroid');
    expect(features).toHaveProperty('isInAppBrowser');
    expect(features).toHaveProperty('canMindAR');
    expect(features).toHaveProperty('canNativeAR');
  });

  it('detects iOS from user agent', () => {
    const features = detectFeatures({
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)',
      mediaDevices: null,
      xrSystem: null,
      platform: 'iPhone',
    });
    expect(features.isIOS).toBe(true);
    expect(features.isAndroid).toBe(false);
  });

  it('marks canMindAR false when no camera', () => {
    const features = detectFeatures({
      userAgent: 'Chrome Android',
      mediaDevices: null,
      xrSystem: null,
      platform: 'Android',
    });
    expect(features.canMindAR).toBe(false);
  });

  it('marks canMindAR false for in-app browsers', () => {
    const features = detectFeatures({
      userAgent: 'FBAN/FB4A',
      mediaDevices: { getUserMedia: () => {} },
      xrSystem: null,
      platform: 'Android',
    });
    expect(features.canMindAR).toBe(false);
  });

  it('marks canNativeAR true for iOS (Quick Look)', () => {
    const features = detectFeatures({
      userAgent: 'iPhone OS 17',
      mediaDevices: null,
      xrSystem: null,
      platform: 'iPhone',
      canQuickLook: true,
    });
    expect(features.canNativeAR).toBe(true);
  });

  it('marks canNativeAR true for Android with camera', () => {
    const features = detectFeatures({
      userAgent: 'Chrome Android',
      mediaDevices: { getUserMedia: () => {} },
      xrSystem: { isSessionSupported: () => Promise.resolve(true) },
      platform: 'Android',
    });
    expect(features.canNativeAR).toBe(true);
  });

  it('marks canNativeAR false for desktop Chrome with WebXR', () => {
    const features = detectFeatures({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      mediaDevices: { getUserMedia: () => {} },
      xrSystem: { isSessionSupported: () => Promise.resolve(true) },
      platform: 'MacIntel',
    });
    expect(features.canNativeAR).toBe(false);
  });

  it('marks canNativeAR true for Android with camera (no WebXR needed)', () => {
    const features = detectFeatures({
      userAgent: 'Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36',
      mediaDevices: { getUserMedia: () => {} },
      xrSystem: null,
      platform: 'Linux armv8l',
    });
    expect(features.canNativeAR).toBe(true);
  });
});
