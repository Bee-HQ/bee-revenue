import { create } from 'zustand';
import type { MediaFile, Segment, Storyboard } from '../types';
import { api } from '../api/client';

const MAX_HISTORY = 50;

interface HistoryEntry {
  segmentId: string;
  key: string;        // e.g. "visual:0"
  oldValue: string | null;
  newValue: string;
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

  loadProject: (storyboardPath: string, projectDir: string) => Promise<void>;
  selectSegment: (id: string | null) => void;
  toggleSegmentSelection: (id: string, shiftKey: boolean) => void;
  loadMedia: () => Promise<void>;
  setDraggedMedia: (file: MediaFile | null) => void;
  setPreviewMedia: (file: MediaFile | null) => void;
  assignMedia: (segmentId: string, layer: string, mediaPath: string, layerIndex?: number) => Promise<void>;
  assignMediaBatch: (layer: string, mediaPath: string) => Promise<void>;
  reorderSegments: (fromIndex: number, toIndex: number) => void;
  orderedSegments: () => Segment[];
  undo: () => Promise<void>;
  redo: () => Promise<void>;

  selectedSegment: () => Segment | null;
  /** @deprecated use selectedSegmentIds[0] */
  selectedSegmentId: string | null;
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
  selectedSegmentId: null,  // kept in sync for backwards compat
  mediaFiles: [],
  mediaCategories: {},
  draggedMedia: null,
  previewMedia: null,
  undoStack: [],
  redoStack: [],
  segmentOrder: null,

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
        selectedSegmentId: null,
        undoStack: [],
        redoStack: [],
        segmentOrder: null,
      });
      get().loadMedia();
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  selectSegment: (id) => {
    const ids = id ? [id] : [];
    set({ selectedSegmentIds: ids, selectedSegmentId: id, previewMedia: null });
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
    set({ selectedSegmentIds: next, selectedSegmentId: next[0] ?? null, previewMedia: null });
  },

  reorderSegments: (fromIndex, toIndex) => {
    const { storyboard } = get();
    if (!storyboard) return;
    const segments = [...storyboard.segments];
    const [moved] = segments.splice(fromIndex, 1);
    segments.splice(toIndex, 0, moved);
    const newOrder = segments.map(s => s.id);
    set({ storyboard: { ...storyboard, segments }, segmentOrder: newOrder });
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

  setDraggedMedia: (file) => set({ draggedMedia: file }),

  setPreviewMedia: (file) => set({ previewMedia: file, selectedSegmentId: null }),

  assignMedia: async (segmentId, layer, mediaPath, layerIndex = 0) => {
    const { storyboard, undoStack } = get();
    const key = `${layer}:${layerIndex}`;

    // Capture old value before the API call
    const segment = storyboard?.segments.find(s => s.id === segmentId);
    const oldValue = segment?.assigned_media[key] ?? null;

    await api.assignMedia(segmentId, layer, mediaPath, layerIndex);

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
  },

  undo: async () => {
    const { storyboard, undoStack, redoStack } = get();
    if (undoStack.length === 0 || !storyboard) return;

    const entry = undoStack[undoStack.length - 1];
    const newUndoStack = undoStack.slice(0, -1);

    // If oldValue is null, this was a fresh assignment — just remove from local state
    // (no API call since the backend has no delete endpoint)
    if (entry.oldValue !== null) {
      const [layer, layerIndexStr] = entry.key.split(':');
      await api.assignMedia(entry.segmentId, layer, entry.oldValue, parseInt(layerIndexStr ?? '0', 10));
    }

    const inverseEntry: HistoryEntry = {
      segmentId: entry.segmentId,
      key: entry.key,
      oldValue: entry.newValue,
      newValue: entry.oldValue ?? '',
    };

    set({
      storyboard: applyAssignment(storyboard, entry.segmentId, entry.key, entry.oldValue),
      undoStack: newUndoStack,
      redoStack: [...redoStack, inverseEntry],
    });
  },

  redo: async () => {
    const { storyboard, undoStack, redoStack } = get();
    if (redoStack.length === 0 || !storyboard) return;

    const entry = redoStack[redoStack.length - 1];
    const newRedoStack = redoStack.slice(0, -1);

    const [layer, layerIndexStr] = entry.key.split(':');
    await api.assignMedia(entry.segmentId, layer, entry.newValue, parseInt(layerIndexStr ?? '0', 10));

    const inverseEntry: HistoryEntry = {
      segmentId: entry.segmentId,
      key: entry.key,
      oldValue: entry.newValue,
      newValue: entry.oldValue ?? '',
    };

    set({
      storyboard: applyAssignment(storyboard, entry.segmentId, entry.key, entry.newValue),
      undoStack: [...undoStack, inverseEntry],
      redoStack: newRedoStack,
    });
  },

  selectedSegment: () => {
    const { storyboard, selectedSegmentIds } = get();
    if (!storyboard || selectedSegmentIds.length === 0) return null;
    return storyboard.segments.find(s => s.id === selectedSegmentIds[0]) ?? null;
  },
}));
