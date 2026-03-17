const IN_APP_PATTERNS = /FBAN|FBAV|Instagram|Twitter|BytedanceWebview|Snapchat|LinkedInApp|Line\//i;

export function isInAppBrowser(ua) {
  return IN_APP_PATTERNS.test(ua);
}

export function detectFeatures({ userAgent, mediaDevices, xrSystem, platform, canQuickLook = false }) {
  const isIOS = /iPhone|iPad|iPod/i.test(userAgent) || /iPhone|iPad/i.test(platform);
  const isAndroid = /Android/i.test(userAgent) || /Android/i.test(platform);
  const hasCamera = !!(mediaDevices && mediaDevices.getUserMedia);
  const hasWebXR = !!xrSystem;
  const inApp = isInAppBrowser(userAgent);

  return {
    isIOS,
    isAndroid,
    hasCamera,
    hasWebXR,
    isInAppBrowser: inApp,
    canMindAR: hasCamera && !inApp,
    canNativeAR: canQuickLook || hasWebXR || (isAndroid && hasCamera),
  };
}

export async function detectLiveFeatures() {
  const ua = navigator.userAgent || '';
  const mediaDevices = navigator.mediaDevices || null;
  const xrSystem = navigator.xr || null;
  const platform = navigator.platform || '';
  const canQuickLook = (() => {
    const a = document.createElement('a');
    return a.relList && a.relList.supports && a.relList.supports('ar');
  })();
  return detectFeatures({ userAgent: ua, mediaDevices, xrSystem, platform, canQuickLook });
}
