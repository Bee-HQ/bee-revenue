// --- New BeeProject format ---

import type { TransformConfig } from './transform';

export interface VisualEntry {
  type: string;
  src: string | null;
  trim?: [number, number];
  color?: string;
  kenBurns?: string;
  transform?: TransformConfig;
  query?: string;
  lat?: number;
  lng?: number;
  [key: string]: any;
}

export interface AudioEntry {
  type: string;
  src: string | null;
  text?: string;
  volume?: number;
}

export interface OverlayEntry {
  type: string;
  content: string;
  startOffset?: number;
  duration?: number;
  platform?: string;
  animation?: string;
  transform?: TransformConfig;
  [key: string]: any;
}

export interface MusicEntry {
  type: string;
  src: string | null;
  volume?: number;
}

export interface TransitionEntry {
  type: string;
  duration: number;
}

export interface BeeSegment {
  id: string;
  title: string;
  section: string;
  start: number;
  duration: number;
  visual: VisualEntry[];
  audio: AudioEntry[];
  overlay: OverlayEntry[];
  music: MusicEntry[];
  transition: TransitionEntry | null;
}

export interface ProductionState {
  narrationEngine: string;
  narrationVoice: string;
  transitionMode: 'overlap' | 'fade';
  status: {
    narration: { completed: number; total: number } | null;
    stock: { completed: number; total: number } | null;
    render: { status: string; progress: number } | null;
  };
  renders: RenderRecord[];
}

export interface RenderRecord {
  id: string;
  timestamp: string;
  format: string;
  resolution: [number, number];
  output: string;
  duration: number;
}

export interface WatermarkConfig {
  text?: string;
  src?: string;
  position: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  opacity: number;
  enabled: boolean;
}

export interface BeeProject {
  version: number;
  title: string;
  fps: number;
  resolution: [number, number];
  createdAt: string;
  updatedAt: string;
  segments: BeeSegment[];
  production: ProductionState;
  quality?: 'standard' | 'premium' | 'social';
  watermark?: WatermarkConfig;
}
export interface MediaFile {
  name: string;
  path: string;
  relative_path: string;
  size_bytes: number;
  category: string;
  extension: string;
}

export interface MediaListResponse {
  files: MediaFile[];
  categories: Record<string, number>;
}

export interface ProductionStatus {
  phase: string;
  segments_total: number;
  segments_done: number;
  narration_files: number;
  graphics_files: number;
  trimmed_files: number;
}

export interface DownloadScriptInfo {
  name: string;
  path: string;
  relative_to_project: string;
}

export interface DownloadTools {
  yt_dlp: boolean;
  curl: boolean;
  wget: boolean;
  ffmpeg: boolean;
}

export interface DownloadStatus {
  task_id: string;
  running: boolean;
  output_lines: string[];
  return_code: number | null;
}

export interface Effects {
  color_presets: string[];
  transitions: string[];
  ken_burns: string[];
}
