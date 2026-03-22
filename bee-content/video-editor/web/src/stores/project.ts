import { create } from 'zustand';
import type { RefObject } from 'react';
import type { PlayerRef } from '@remotion/player';
import type { TimelineAction, TimelineRow } from '@xzdarcy/timeline-engine';
import type { Effects, MediaFile, Segment, Storyboard } from '../types';
import { api } from '../api/client';
import { toast } from './toast';

const MAX_HISTORY = 50;

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
  segmentOrder: string[] | null;
  effects: Effects | null;
  currentTimeMs: number;
  playerRef: RefObject<PlayerRef | null> | null;
  activeClipId: string | null;
  loopIn: number | null;  // frame number
  loopOut: number | null; // frame number
  assetStatus: AssetStatus | null;
  editorData: TimelineRow[];
  timelineHistory: TimelineRow[][];
  timelineHistoryIndex: number;

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
  setEditorData: (data: TimelineRow[]) => void;
  pushTimelineHistory: (data: TimelineRow[]) => void;
  timelineUndo: () => void;
  timelineRedo: () => void;
  splitAtPlayhead: () => void;
  selectedActionIds: string[];
  clipboard: TimelineAction[];
  selectAction: (id: string, shiftKey: boolean) => void;
  clearActionSelection: () => void;
  deleteSelectedActions: () => void;
  copySelectedActions: () => void;
  pasteClipboard: () => void;
  duplicateSelectedActions: () => void;
  assignMedia: (segmentId: string, layer: string, mediaPath: string, layerIndex?: number) => Promise<void>;
  assignMediaBatch: (layer: string, mediaPath: string) => Promise<void>;
  updateSegmentConfig: (segmentId: string, updates: Record<string, unknown>) => Promise<void>;
  reorderSegments: (fromIndex: number, toIndex: number) => void;
  orderedSegments: () => Segment[];

  selectedSegment: () => Segment | null;
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
  segmentOrder: null,
  effects: null,
  currentTimeMs: 0,
  playerRef: null,
  activeClipId: null,
  loopIn: null,
  loopOut: null,
  assetStatus: null,
  editorData: [],
  timelineHistory: [],
  timelineHistoryIndex: -1,
  selectedActionIds: [],
  clipboard: [],

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
        editorData: [],
        timelineHistory: [],
        timelineHistoryIndex: -1,
        segmentOrder: null,
        selectedActionIds: [],
        clipboard: [],
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
    const { storyboard } = get();
    const key = `${layer}:${layerIndex}`;
    try {
      await api.assignMedia(segmentId, layer, mediaPath, layerIndex);
    } catch (e: any) {
      toast.error(`Assignment failed: ${e.message}`);
      throw e;
    }
    if (!storyboard) return;
    const segments = storyboard.segments.map(s => {
      if (s.id !== segmentId) return s;
      return { ...s, assigned_media: { ...s.assigned_media, [key]: mediaPath } };
    });
    set({ storyboard: { ...storyboard, segments } });
    toast.success('Media assigned');
  },

  setEditorData: (data) => set({ editorData: data }),

  pushTimelineHistory: (data) => {
    const { timelineHistory, timelineHistoryIndex } = get();
    const truncated = timelineHistory.slice(0, timelineHistoryIndex + 1);
    const next = [...truncated, structuredClone(data)];
    if (next.length > MAX_HISTORY) next.shift();
    set({ timelineHistory: next, timelineHistoryIndex: next.length - 1 });
  },

  timelineUndo: () => {
    const { timelineHistory, timelineHistoryIndex } = get();
    if (timelineHistoryIndex <= 0) return;
    const newIndex = timelineHistoryIndex - 1;
    set({ editorData: structuredClone(timelineHistory[newIndex]), timelineHistoryIndex: newIndex });
  },

  timelineRedo: () => {
    const { timelineHistory, timelineHistoryIndex } = get();
    if (timelineHistoryIndex >= timelineHistory.length - 1) return;
    const newIndex = timelineHistoryIndex + 1;
    set({ editorData: structuredClone(timelineHistory[newIndex]), timelineHistoryIndex: newIndex });
  },

  splitAtPlayhead: () => {
    const { editorData, currentTimeMs, activeClipId } = get();
    const cursorSec = currentTimeMs / 1000;
    let targetRow = editorData.find(r => r.id === 'V1');
    if (activeClipId) {
      for (const row of editorData) {
        if (row.actions.some(a => a.id === activeClipId)) {
          targetRow = row;
          break;
        }
      }
    }
    if (!targetRow) return;
    const actionIdx = targetRow.actions.findIndex(a => a.start < cursorSec && a.end > cursorSec);
    if (actionIdx === -1) return;
    const action = targetRow.actions[actionIdx] as any;
    const left = { ...action, id: action.id + '-L', end: cursorSec, data: { ...action.data } };
    const right = { ...action, id: action.id + '-R', start: cursorSec, data: { ...action.data } };
    const newActions = [...targetRow.actions];
    newActions.splice(actionIdx, 1, left, right);
    const newRows = editorData.map(r => r.id === targetRow!.id ? { ...r, actions: newActions } : r);
    get().setEditorData(newRows);
    get().pushTimelineHistory(newRows);
  },

  selectAction: (id, shiftKey) => {
    const { selectedActionIds } = get();
    if (shiftKey) {
      if (selectedActionIds.includes(id)) {
        set({ selectedActionIds: selectedActionIds.filter(x => x !== id) });
      } else {
        set({ selectedActionIds: [...selectedActionIds, id] });
      }
    } else {
      set({ selectedActionIds: [id] });
    }
    set({ activeClipId: id });
  },

  clearActionSelection: () => set({ selectedActionIds: [], activeClipId: null }),

  deleteSelectedActions: () => {
    const { editorData, selectedActionIds } = get();
    if (selectedActionIds.length === 0) return;
    const sel = new Set(selectedActionIds);
    const newRows = editorData.map(row => ({
      ...row,
      actions: row.actions.filter(a => !sel.has(a.id)),
    }));
    get().setEditorData(newRows);
    get().pushTimelineHistory(newRows);
    set({ selectedActionIds: [], activeClipId: null });
  },

  copySelectedActions: () => {
    const { editorData, selectedActionIds } = get();
    const sel = new Set(selectedActionIds);
    const copied: TimelineAction[] = [];
    for (const row of editorData) {
      for (const a of row.actions) {
        if (sel.has(a.id)) copied.push(structuredClone(a));
      }
    }
    set({ clipboard: copied });
  },

  pasteClipboard: () => {
    const { clipboard, editorData, currentTimeMs } = get();
    if (clipboard.length === 0) return;
    const cursorSec = currentTimeMs / 1000;
    const earliest = Math.min(...clipboard.map(a => a.start));
    const offset = cursorSec - earliest;

    // Helper to determine a row's effectId from its id
    const rowEffectId = (row: { id: string; actions: TimelineAction[] }): string => {
      if (row.actions.length > 0) return row.actions[0].effectId;
      const map: Record<string, string> = { V1: 'video', A1: 'narration', A2: 'audio', A3: 'music', OV1: 'overlay' };
      return map[row.id] || '';
    };

    const newRows = editorData.map(row => {
      const toAdd = clipboard
        .filter(a => a.effectId === rowEffectId(row))
        .map(a => ({
          ...structuredClone(a),
          id: `paste-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
          start: a.start + offset,
          end: a.end + offset,
          selected: false,
        }));
      if (toAdd.length === 0) return row;
      return { ...row, actions: [...row.actions, ...toAdd] };
    });
    get().setEditorData(newRows);
    get().pushTimelineHistory(newRows);
  },

  duplicateSelectedActions: () => {
    const { editorData, selectedActionIds } = get();
    if (selectedActionIds.length === 0) return;
    const sel = new Set(selectedActionIds);
    const newRows = editorData.map(row => {
      const dupes: TimelineAction[] = [];
      for (const a of row.actions) {
        if (sel.has(a.id)) {
          dupes.push({
            ...structuredClone(a),
            id: `dup-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
            start: a.end,
            end: a.end + (a.end - a.start),
            selected: false,
          });
        }
      }
      return dupes.length > 0 ? { ...row, actions: [...row.actions, ...dupes] } : row;
    });
    get().setEditorData(newRows);
    get().pushTimelineHistory(newRows);
  },

  selectedSegment: () => {
    const { storyboard, selectedSegmentIds } = get();
    if (!storyboard || selectedSegmentIds.length === 0) return null;
    return storyboard.segments.find(s => s.id === selectedSegmentIds[0]) ?? null;
  },
}));
