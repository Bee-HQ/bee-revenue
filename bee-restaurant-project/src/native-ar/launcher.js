export function getNativeARUrl({ glb, usdz, title, isIOS }) {
  if (isIOS) {
    if (!usdz) return null;
    return usdz;
  }

  // Android Scene Viewer intent
  const modelUrl = new URL(glb, window.location.href).href;
  return `intent://arvr.google.com/scene-viewer/1.0?file=${encodeURIComponent(modelUrl)}&mode=ar_preferred&title=${encodeURIComponent(title)}#Intent;scheme=https;package=com.google.android.googlequicksearchbox;action=android.intent.action.VIEW;end;`;
}

export function launchNativeAR({ glb, usdz, title, isIOS }) {
  const url = getNativeARUrl({ glb, usdz, title, isIOS });
  if (!url) return false;

  if (isIOS && usdz) {
    const a = document.createElement('a');
    a.rel = 'ar';
    a.href = new URL(usdz, window.location.href).href;
    const img = document.createElement('img');
    a.appendChild(img);
    document.body.appendChild(a);
    a.click();
    setTimeout(() => a.remove(), 100);
    return true;
  }

  window.location.href = url;
  return true;
}
