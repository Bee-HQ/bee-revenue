import { create } from 'zustand';
import type { RefObject } from 'react';
import type { PlayerRef } from '@remotion/player';
import type { Effects, MediaFile, Segment, Storyboard } from '../types';
import { api } from '../api/client';
import { toast } from './toast';

const MAX_HISTORY = 50;

interface HistoryEntry {
  segmentId: string;
  key: string;        // e.g. "visual:0"
  oldValue: string | null;
  newValue: string;
}

export interface SegmentAssetInfo {
  hasVideo: boolean;
  videoStatus: 'found' | 'missing' | 'needs_download' | 'needs_generation' | 'no_source';
  videoType: string;
  videoAction: string;
}

export interface AssetStatus {
  total: number;
  found: number;
  missing: number;
  needsDownload: number;
  needsGeneration: number;
  needsFile: number;
  segments: Record<string, SegmentAssetInfo>;
}

interface ProjectState {
  storyboard: Storyboard | null;
  loading: boolean;
  error: string | null;
  selectedSegmentIds: string[];
  mediaFiles: MediaFile[];
  mediaCategories: Record<string, number>;
  draggedMedia: MediaFile | null;
  previewMedia: MediaFile | null;
  undoStack: HistoryEntry[];
  redoStack: HistoryEntry[];
  segmentOrder: string[] | null;
  effects: Effects | null;
  currentTimeMs: number;
  playerRef: RefObject<PlayerRef | null> | null;
  activeClipId: string | null;
  loopIn: number | null;  // frame number
  loopOut: number | null; // frame number
  assetStatus: AssetStatus | null;

  setCurrentTimeMs: (ms: number) => void;
  setPlayerRef: (ref: RefObject<PlayerRef | null>) => void;
  setActiveClipId: (id: string | null) => void;
  setLoopIn: (frame: number | null) => void;
  setLoopOut: (frame: number | null) => void;
  loadProject: (storyboardPath: string, projectDir: string) => Promise<void>;
  selectSegment: (id: string | null) => void;
  toggleSegmentSelection: (id: string, shiftKey: boolean) => void;
  loadMedia: () => Promise<void>;
  loadEffects: () => Promise<void>;
  loadAssetStatus: () => void;
  setDraggedMedia: (file: MediaFile | null) => void;
  setPreviewMedia: (file: MediaFile | null) => void;
  assignMedia: (segmentId: string, layer: string, mediaPath: string, layerIndex?: number) => Promise<void>;
  assignMediaBatch: (layer: string, mediaPath: string) => Promise<void>;
  updateSegmentConfig: (segmentId: string, updates: Record<string, unknown>) => Promise<void>;
  reorderSegments: (fromIndex: number, toIndex: number) => void;
  orderedSegments: () => Segment[];
  undo: () => Promise<void>;
  redo: () => Promise<void>;

  selectedSegment: () => Segment | null;
}

function applyAssignment(
  storyboard: Storyboard,
  segmentId: string,
  key: string,
  value: string | null,
): Storyboard {
  const segments = storyboard.segments.map(s => {
    if (s.id !== segmentId) return s;
    const assigned_media = { ...s.assigned_media };
    if (value === null) {
      delete assigned_media[key];
    } else {
      assigned_media[key] = value;
    }
    return { ...s, assigned_media };
  });
  return { ...storyboard, segments };
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  storyboard: null,
  loading: false,
  error: null,
  selectedSegmentIds: [],
  mediaFiles: [],
  mediaCategories: {},
  draggedMedia: null,
  previewMedia: null,
  undoStack: [],
  redoStack: [],
  segmentOrder: null,
  effects: null,
  currentTimeMs: 0,
  playerRef: null,
  activeClipId: null,
  loopIn: null,
  loopOut: null,
  assetStatus: null,

  setCurrentTimeMs: (ms) => set({ currentTimeMs: ms }),
  setPlayerRef: (ref) => set({ playerRef: ref }),
  setActiveClipId: (id) => set({ activeClipId: id }),
  setLoopIn: (frame) => set({ loopIn: frame }),
  setLoopOut: (frame) => set({ loopOut: frame }),

  loadProject: async (storyboardPath, projectDir) => {
    set({ loading: true, error: null });
    try {
      const storyboard = await api.loadProject(storyboardPath, projectDir);
      // Backend restores segment order in its list — we don't need to track clientside order separately
      // after load; reset to null so orderedSegments() uses the server-returned order.
      set({
        storyboard,
        loading: false,
        selectedSegmentIds: [],
        undoStack: [],
        redoStack: [],
        segmentOrder: null,
      });
      get().loadMedia();
      get().loadAssetStatus();
    } catch (e: any) {
      set({ error: e.message, loading: false });
      toast.error(`Failed to load: ${e.message}`);
    }
  },

  selectSegment: (id) => {
    const ids = id ? [id] : [];
    set({ selectedSegmentIds: ids, previewMedia: null });
  },

  toggleSegmentSelection: (id, shiftKey) => {
    const { selectedSegmentIds } = get();
    let next: string[];
    if (shiftKey) {
      // Toggle this id in/out of the set
      if (selectedSegmentIds.includes(id)) {
        next = selectedSegmentIds.filter(s => s !== id);
      } else {
        next = [...selectedSegmentIds, id];
      }
    } else {
      // Single-select: replace selection (deselect if already sole selection)
      next = selectedSegmentIds.length === 1 && selectedSegmentIds[0] === id ? [] : [id];
    }
    set({ selectedSegmentIds: next, previewMedia: null });
  },

  reorderSegments: (fromIndex, toIndex) => {
    const { storyboard } = get();
    if (!storyboard) return;
    const segments = [...storyboard.segments];
    const [moved] = segments.splice(fromIndex, 1);
    segments.splice(toIndex, 0, moved);
    const newOrder = segments.map(s => s.id);
    set({ storyboard: { ...storyboard, segments }, segmentOrder: newOrder });
    toast.info('Segments reordered');
    // Persist to backend (fire-and-forget, non-critical)
    api.reorderSegments(newOrder).catch(() => {});
  },

  orderedSegments: () => {
    const { storyboard } = get();
    if (!storyboard) return [];
    return storyboard.segments;
  },

  assignMediaBatch: async (layer, mediaPath) => {
    const { selectedSegmentIds } = get();
    for (const segmentId of selectedSegmentIds) {
      await get().assignMedia(segmentId, layer, mediaPath);
    }
  },

  loadMedia: async () => {
    try {
      const res = await api.listMedia();
      set({ mediaFiles: res.files, mediaCategories: res.categories });
    } catch {
      // Media loading is non-critical
    }
  },

  loadEffects: async () => {
    if (get().effects) return; // already loaded
    try {
      const effects = await api.getEffects();
      set({ effects });
    } catch {
      // Effects loading is non-critical
    }
  },

  loadAssetStatus: () => {
    const sb = get().storyboard;
    if (!sb) return;

    const segments: Record<string, SegmentAssetInfo> = {};
    let found = 0, missing = 0, needsDownload = 0, needsGeneration = 0, needsFile = 0;

    for (const seg of sb.segments) {
      const visual = seg.visual[0];
      const assigned = seg.assigned_media['visual:0'];

      if (!visual) {
        segments[seg.id] = { hasVideo: false, videoStatus: 'no_source', videoType: 'NONE', videoAction: 'No visual defined' };
        missing++;
        continue;
      }

      const type = visual.content_type;
      const src = assigned || visual.content;
      const query = visual.metadata?.query;
      const isRealPath = src && (src.includes('/') || src.endsWith('.mp4') || src.endsWith('.jpg') || src.endsWith('.png') || src.endsWith('.wav'));

      if (type === 'BLACK') {
        segments[seg.id] = { hasVideo: true, videoStatus: 'found', videoType: 'BLACK', videoAction: 'Black frame — no file needed' };
        found++;
      } else if (isRealPath) {
        segments[seg.id] = { hasVideo: true, videoStatus: 'found', videoType: type, videoAction: `File: ${src}` };
        found++;
      } else if (query || type === 'STOCK') {
        segments[seg.id] = { hasVideo: false, videoStatus: 'needs_download', videoType: type, videoAction: `Download stock: "${query || 'search needed'}"` };
        needsDownload++;
      } else if (['MAP', 'MAP-FLAT', 'MAP-3D', 'MAP-TACTICAL', 'MAP-PULSE', 'MAP-ROUTE'].includes(type)) {
        segments[seg.id] = { hasVideo: false, videoStatus: 'needs_generation', videoType: type, videoAction: `Generate ${type} map` };
        needsGeneration++;
      } else if (['GRAPHIC', 'GENERATED', 'DOCUMENT-MOCKUP', 'PIP-SINGLE', 'PIP-DUAL'].includes(type)) {
        segments[seg.id] = { hasVideo: false, videoStatus: 'needs_generation', videoType: type, videoAction: `Generate ${type}` };
        needsGeneration++;
      } else {
        segments[seg.id] = { hasVideo: false, videoStatus: 'missing', videoType: type, videoAction: `Need: ${type} — ${src || 'no source'}` };
        needsFile++;
      }
    }

    set({
      assetStatus: {
        total: sb.segments.length,
        found, missing, needsDownload, needsGeneration, needsFile,
        segments,
      },
    });
  },

  updateSegmentConfig: async (segmentId, updates) => {
    await api.updateSegment(segmentId, updates);
    // Refresh storyboard from server to get updated state
    const storyboard = await api.getCurrentProject();
    set({ storyboard });
  },

  setDraggedMedia: (file) => set({ draggedMedia: file }),

  setPreviewMedia: (file) => set({ previewMedia: file, selectedSegmentIds: [] }),

  assignMedia: async (segmentId, layer, mediaPath, layerIndex = 0) => {
    const { storyboard, undoStack } = get();
    const key = `${layer}:${layerIndex}`;

    // Capture old value before the API call
    const segment = storyboard?.segments.find(s => s.id === segmentId);
    const oldValue = segment?.assigned_media[key] ?? null;

    try {
      await api.assignMedia(segmentId, layer, mediaPath, layerIndex);
    } catch (e: any) {
      toast.error(`Assignment failed: ${e.message}`);
      throw e;
    }

    // Push history entry, cap at MAX_HISTORY
    const entry: HistoryEntry = { segmentId, key, oldValue, newValue: mediaPath };
    const newStack = [...undoStack, entry];
    if (newStack.length > MAX_HISTORY) newStack.shift();

    // Update local state
    if (!storyboard) return;
    set({
      storyboard: applyAssignment(storyboard, segmentId, key, mediaPath),
      undoStack: newStack,
      redoStack: [],
    });
    toast.success('Media assigned');
  },

  undo: async () => {
    const { storyboard, undoStack, redoStack } = get();
    if (undoStack.length === 0 || !storyboard) return;

    const entry = undoStack[undoStack.length - 1];

    // Sync with backend first — only modify stacks on success
    const [layer, layerIndexStr] = entry.key.split(':');
    try {
      await api.assignMedia(entry.segmentId, layer, entry.oldValue ?? '', parseInt(layerIndexStr ?? '0', 10));
    } catch (e) {
      console.error('Undo failed:', e);
      return;
    }

    const inverseEntry: HistoryEntry = {
      segmentId: entry.segmentId,
      key: entry.key,
      oldValue: entry.newValue,
      newValue: entry.oldValue ?? '',
    };

    set({
      storyboard: applyAssignment(storyboard, entry.segmentId, entry.key, entry.oldValue),
      undoStack: undoStack.slice(0, -1),
      redoStack: [...redoStack, inverseEntry],
    });
  },

  redo: async () => {
    const { storyboard, undoStack, redoStack } = get();
    if (redoStack.length === 0 || !storyboard) return;

    const entry = redoStack[redoStack.length - 1];

    const [layer, layerIndexStr] = entry.key.split(':');
    try {
      await api.assignMedia(entry.segmentId, layer, entry.newValue, parseInt(layerIndexStr ?? '0', 10));
    } catch (e) {
      console.error('Redo failed:', e);
      return;
    }

    const inverseEntry: HistoryEntry = {
      segmentId: entry.segmentId,
      key: entry.key,
      oldValue: entry.newValue,
      newValue: entry.oldValue ?? '',
    };

    set({
      storyboard: applyAssignment(storyboard, entry.segmentId, entry.key, entry.newValue),
      undoStack: [...undoStack, inverseEntry],
      redoStack: redoStack.slice(0, -1),
    });
  },

  selectedSegment: () => {
    const { storyboard, selectedSegmentIds } = get();
    if (!storyboard || selectedSegmentIds.length === 0) return null;
    return storyboard.segments.find(s => s.id === selectedSegmentIds[0]) ?? null;
  },
}));
