import type { DownloadScriptInfo, DownloadStatus, DownloadTools, MediaListResponse, ProductionStatus, Storyboard } from '../types';

const BASE = import.meta.env.VITE_API_BASE || '/api';

interface StatusResponse {
  status: string;
  count?: number;
  output?: string;
}

interface NarrationStatus {
  running: boolean;
  done: number;
  total: number;
  status?: string;
  succeeded?: string[];
  failed?: Array<{ file: string; error: string }>;
  count?: number;
}

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
    return request<StatusResponse>('/projects/assign', {
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
    return request<StatusResponse>('/projects/reorder', {
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
    }).then(r => r.json()) as Promise<StatusResponse>;
  },

  mediaFileUrl(path: string): string {
    return `${BASE}/media/file?path=${encodeURIComponent(path)}`;
  },

  getProductionStatus(): Promise<ProductionStatus> {
    return request('/production/status');
  },

  initProject() {
    return request<StatusResponse>('/production/init', { method: 'POST' });
  },

  generateGraphics() {
    return request<StatusResponse>('/production/graphics', { method: 'POST' });
  },

  generateNarration(engine = 'edge', voice?: string) {
    return request<StatusResponse>('/production/narration', {
      method: 'POST',
      body: JSON.stringify({ tts_engine: engine, tts_voice: voice }),
    });
  },

  getNarrationStatus(): Promise<NarrationStatus> {
    return request('/production/narration/status');
  },

  assembleVideo() {
    return request<StatusResponse>('/production/assemble', { method: 'POST' });
  },

  generatePreview(segmentId: string) {
    return request<{ preview?: string }>(`/production/preview/${segmentId}`, { method: 'POST' });
  },

  generateAllPreviews() {
    return request<StatusResponse>('/production/previews', { method: 'POST' });
  },

  // Download endpoints
  listDownloadScripts(): Promise<DownloadScriptInfo[]> {
    return request('/media/download/scripts');
  },

  checkDownloadTools(): Promise<DownloadTools> {
    return request('/media/download/tools');
  },

  runDownloadScript(scriptPath: string) {
    return request<StatusResponse>('/media/download/run-script', {
      method: 'POST',
      body: JSON.stringify({ script_path: scriptPath }),
    });
  },

  downloadWithYtDlp(url: string, category = 'footage', filename?: string) {
    const params = new URLSearchParams({ url, category });
    if (filename) params.set('filename', filename);
    return request<StatusResponse>(`/media/download/yt-dlp?${params}`, { method: 'POST' });
  },

  getDownloadStatus(): Promise<DownloadStatus[]> {
    return request('/media/download/status');
  },

  createMediaDirs() {
    return request<StatusResponse>('/media/download/create-dirs', { method: 'POST' });
  },

  exportMarkdown(): Promise<{ format: string; content: string }> {
    return request('/projects/export?format=md');
  },

  exportOtio(): Promise<{ format: string; path: string }> {
    return request('/projects/export?format=otio');
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
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch {
        console.error('WebSocket: failed to parse message', event.data);
      }
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
