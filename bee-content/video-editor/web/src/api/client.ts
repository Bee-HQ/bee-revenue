import type { DownloadScriptInfo, DownloadStatus, DownloadTools, MediaListResponse, ProductionStatus, Storyboard } from '../types';

const BASE = import.meta.env.VITE_API_BASE || '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  loadProject(storyboardPath: string, projectDir: string = '.'): Promise<Storyboard> {
    return request('/projects/load', {
      method: 'POST',
      body: JSON.stringify({ storyboard_path: storyboardPath, project_dir: projectDir }),
    });
  },

  getCurrentProject(): Promise<Storyboard> {
    return request('/projects/current');
  },

  assignMedia(segmentId: string, layer: string, mediaPath: string, layerIndex = 0) {
    return request('/projects/assign', {
      method: 'PUT',
      body: JSON.stringify({
        segment_id: segmentId,
        layer,
        media_path: mediaPath,
        layer_index: layerIndex,
      }),
    });
  },

  reorderSegments(order: string[]) {
    return request('/projects/reorder', {
      method: 'PUT',
      body: JSON.stringify({ segment_order: order }),
    });
  },

  listMedia(): Promise<MediaListResponse> {
    return request('/media');
  },

  uploadMedia(file: File, category: string = 'footage') {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE}/media/upload?category=${category}`, {
      method: 'POST',
      body: form,
    }).then(r => r.json());
  },

  mediaFileUrl(path: string): string {
    return `${BASE}/media/file?path=${encodeURIComponent(path)}`;
  },

  getProductionStatus(): Promise<ProductionStatus> {
    return request('/production/status');
  },

  initProject() {
    return request('/production/init', { method: 'POST' });
  },

  generateGraphics() {
    return request('/production/graphics', { method: 'POST' });
  },

  generateNarration(engine = 'edge', voice?: string) {
    return request('/production/narration', {
      method: 'POST',
      body: JSON.stringify({ tts_engine: engine, tts_voice: voice }),
    });
  },

  getNarrationStatus(): Promise<any> {
    return request('/production/narration/status');
  },

  assembleVideo() {
    return request('/production/assemble', { method: 'POST' });
  },

  generatePreview(segmentId: string) {
    return request(`/production/preview/${segmentId}`, { method: 'POST' });
  },

  generateAllPreviews() {
    return request('/production/previews', { method: 'POST' });
  },

  // Download endpoints
  listDownloadScripts(): Promise<DownloadScriptInfo[]> {
    return request('/media/download/scripts');
  },

  checkDownloadTools(): Promise<DownloadTools> {
    return request('/media/download/tools');
  },

  runDownloadScript(scriptPath: string) {
    return request('/media/download/run-script', {
      method: 'POST',
      body: JSON.stringify({ script_path: scriptPath }),
    });
  },

  downloadWithYtDlp(url: string, category = 'footage', filename?: string) {
    const params = new URLSearchParams({ url, category });
    if (filename) params.set('filename', filename);
    return request(`/media/download/yt-dlp?${params}`, { method: 'POST' });
  },

  getDownloadStatus(): Promise<DownloadStatus[]> {
    return request('/media/download/status');
  },

  createMediaDirs() {
    return request('/media/download/create-dirs', { method: 'POST' });
  },

  connectProgress(
    action: string,
    params: Record<string, any>,
    onMessage: (data: any) => void,
    onClose?: () => void,
  ): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}/api/production/ws/progress`);

    ws.onopen = () => {
      ws.send(JSON.stringify({ action, params }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.onclose = () => {
      if (onClose) onClose();
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };

    return ws;
  },
};
