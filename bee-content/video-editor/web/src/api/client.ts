import type { MediaListResponse, ProductionStatus, Storyboard } from '../types';

const BASE = '/api';

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

  assembleVideo() {
    return request('/production/assemble', { method: 'POST' });
  },
};
