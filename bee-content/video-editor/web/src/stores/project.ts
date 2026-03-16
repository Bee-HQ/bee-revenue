import { create } from 'zustand';
import type { MediaFile, Segment, Storyboard } from '../types';
import { api } from '../api/client';

interface ProjectState {
  storyboard: Storyboard | null;
  loading: boolean;
  error: string | null;
  selectedSegmentId: string | null;
  mediaFiles: MediaFile[];
  mediaCategories: Record<string, number>;
  draggedMedia: MediaFile | null;

  loadProject: (storyboardPath: string, projectDir: string) => Promise<void>;
  selectSegment: (id: string | null) => void;
  loadMedia: () => Promise<void>;
  setDraggedMedia: (file: MediaFile | null) => void;
  assignMedia: (segmentId: string, layer: string, mediaPath: string, layerIndex?: number) => Promise<void>;

  selectedSegment: () => Segment | null;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  storyboard: null,
  loading: false,
  error: null,
  selectedSegmentId: null,
  mediaFiles: [],
  mediaCategories: {},
  draggedMedia: null,

  loadProject: async (storyboardPath, projectDir) => {
    set({ loading: true, error: null });
    try {
      const storyboard = await api.loadProject(storyboardPath, projectDir);
      set({ storyboard, loading: false, selectedSegmentId: null });
      // Also load media
      get().loadMedia();
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  selectSegment: (id) => set({ selectedSegmentId: id }),

  loadMedia: async () => {
    try {
      const res = await api.listMedia();
      set({ mediaFiles: res.files, mediaCategories: res.categories });
    } catch {
      // Media loading is non-critical
    }
  },

  setDraggedMedia: (file) => set({ draggedMedia: file }),

  assignMedia: async (segmentId, layer, mediaPath, layerIndex = 0) => {
    await api.assignMedia(segmentId, layer, mediaPath, layerIndex);
    // Update local state
    const { storyboard } = get();
    if (!storyboard) return;
    const segments = storyboard.segments.map(s => {
      if (s.id !== segmentId) return s;
      return {
        ...s,
        assigned_media: { ...s.assigned_media, [`${layer}:${layerIndex}`]: mediaPath },
      };
    });
    set({ storyboard: { ...storyboard, segments } });
  },

  selectedSegment: () => {
    const { storyboard, selectedSegmentId } = get();
    if (!storyboard || !selectedSegmentId) return null;
    return storyboard.segments.find(s => s.id === selectedSegmentId) ?? null;
  },
}));
