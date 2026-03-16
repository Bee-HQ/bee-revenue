export interface LayerEntry {
  content: string;
  content_type: string;
  time_start: string | null;
  time_end: string | null;
  raw: string;
}

export interface Segment {
  id: string;
  start: string;
  end: string;
  title: string;
  section: string;
  section_time: string;
  subsection: string;
  duration_seconds: number;
  visual: LayerEntry[];
  audio: LayerEntry[];
  overlay: LayerEntry[];
  music: LayerEntry[];
  source: LayerEntry[];
  transition: LayerEntry[];
  assigned_media: Record<string, string>;
}

export interface Storyboard {
  title: string;
  total_segments: number;
  total_duration_seconds: number;
  sections: string[];
  segments: Segment[];
  stock_footage_needed: number;
  photos_needed: number;
  maps_needed: number;
  production_rules: string[];
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

export type LayerName = 'visual' | 'audio' | 'overlay' | 'music' | 'source' | 'transition';
