import { describe, test, expect, beforeEach } from 'vitest';
import { useProjectStore } from './project';
import type { TimelineRow } from '@xzdarcy/timeline-engine';

const makeRows = (id: string): TimelineRow[] => [
  { id: 'V1', actions: [{ id, start: 0, end: 5, effectId: 'video' }] },
];

describe('timeline undo/redo', () => {
  beforeEach(() => {
    useProjectStore.setState({
      editorData: [],
      timelineHistory: [],
      timelineHistoryIndex: -1,
    });
  });

  test('pushTimelineHistory adds snapshot', () => {
    useProjectStore.getState().pushTimelineHistory(makeRows('a1'));
    expect(useProjectStore.getState().timelineHistory).toHaveLength(1);
    expect(useProjectStore.getState().timelineHistoryIndex).toBe(0);
  });

  test('undo reverts to previous state', () => {
    const store = useProjectStore.getState();
    store.pushTimelineHistory(makeRows('a1'));
    store.setEditorData(makeRows('a1'));
    store.pushTimelineHistory(makeRows('a2'));
    store.setEditorData(makeRows('a2'));
    useProjectStore.getState().timelineUndo();
    expect(useProjectStore.getState().editorData[0].actions[0].id).toBe('a1');
  });

  test('redo restores undone state', () => {
    const store = useProjectStore.getState();
    store.pushTimelineHistory(makeRows('a1'));
    store.pushTimelineHistory(makeRows('a2'));
    store.setEditorData(makeRows('a2'));
    useProjectStore.getState().timelineUndo();
    useProjectStore.getState().timelineRedo();
    expect(useProjectStore.getState().editorData[0].actions[0].id).toBe('a2');
  });

  test('undo at start of history does nothing', () => {
    useProjectStore.getState().timelineUndo();
    expect(useProjectStore.getState().timelineHistoryIndex).toBe(-1);
  });

  test('new change after undo truncates redo history', () => {
    const store = useProjectStore.getState();
    store.pushTimelineHistory(makeRows('a1'));
    store.pushTimelineHistory(makeRows('a2'));
    store.pushTimelineHistory(makeRows('a3'));
    useProjectStore.getState().timelineUndo();
    useProjectStore.getState().timelineUndo();
    useProjectStore.getState().pushTimelineHistory(makeRows('a4'));
    expect(useProjectStore.getState().timelineHistory).toHaveLength(2);
  });

  test('max 50 history entries', () => {
    const store = useProjectStore.getState();
    for (let i = 0; i < 55; i++) {
      store.pushTimelineHistory(makeRows(`a${i}`));
    }
    expect(useProjectStore.getState().timelineHistory).toHaveLength(50);
  });
});

describe('splitAtPlayhead', () => {
  test('splits action at cursor into two halves', () => {
    const rows: TimelineRow[] = [
      { id: 'V1', actions: [{ id: 'clip1', start: 0, end: 10, effectId: 'video', data: { segmentId: 's1', src: 'a.mp4', title: 'A', contentType: 'FOOTAGE', layerIndex: 0 } } as any] },
    ];
    useProjectStore.setState({
      editorData: rows,
      currentTimeMs: 5000,
      activeClipId: null,
      timelineHistory: [rows],
      timelineHistoryIndex: 0,
    });
    useProjectStore.getState().splitAtPlayhead();
    const result = useProjectStore.getState().editorData;
    const v1 = result.find(r => r.id === 'V1')!;
    expect(v1.actions).toHaveLength(2);
    expect(v1.actions[0].end).toBe(5);
    expect(v1.actions[1].start).toBe(5);
  });
});

describe('multi-select', () => {
  beforeEach(() => {
    const rows: TimelineRow[] = [
      { id: 'V1', actions: [
        { id: 'a1', start: 0, end: 5, effectId: 'video' },
        { id: 'a2', start: 5, end: 10, effectId: 'video' },
        { id: 'a3', start: 10, end: 15, effectId: 'video' },
      ]},
    ];
    useProjectStore.setState({ editorData: rows, selectedActionIds: [], timelineHistory: [rows], timelineHistoryIndex: 0 });
  });

  test('selectAction sets single selection', () => {
    useProjectStore.getState().selectAction('a1', false);
    expect(useProjectStore.getState().selectedActionIds).toEqual(['a1']);
  });

  test('selectAction with shift adds to selection', () => {
    useProjectStore.getState().selectAction('a1', false);
    useProjectStore.getState().selectAction('a2', true);
    expect(useProjectStore.getState().selectedActionIds).toEqual(['a1', 'a2']);
  });

  test('selectAction with shift toggles off', () => {
    useProjectStore.getState().selectAction('a1', false);
    useProjectStore.getState().selectAction('a2', true);
    useProjectStore.getState().selectAction('a1', true);
    expect(useProjectStore.getState().selectedActionIds).toEqual(['a2']);
  });

  test('clearActionSelection empties selection', () => {
    useProjectStore.getState().selectAction('a1', false);
    useProjectStore.getState().clearActionSelection();
    expect(useProjectStore.getState().selectedActionIds).toEqual([]);
  });
});

describe('deleteSelectedActions', () => {
  beforeEach(() => {
    const rows: TimelineRow[] = [
      { id: 'V1', actions: [
        { id: 'a1', start: 0, end: 5, effectId: 'video' },
        { id: 'a2', start: 5, end: 10, effectId: 'video' },
      ]},
    ];
    useProjectStore.setState({ editorData: rows, selectedActionIds: ['a1'], timelineHistory: [rows], timelineHistoryIndex: 0 });
  });

  test('removes selected action', () => {
    useProjectStore.getState().deleteSelectedActions();
    const v1 = useProjectStore.getState().editorData.find(r => r.id === 'V1')!;
    expect(v1.actions).toHaveLength(1);
    expect(v1.actions[0].id).toBe('a2');
  });

  test('clears selection after delete', () => {
    useProjectStore.getState().deleteSelectedActions();
    expect(useProjectStore.getState().selectedActionIds).toEqual([]);
  });

  test('pushes to history', () => {
    const prevIndex = useProjectStore.getState().timelineHistoryIndex;
    useProjectStore.getState().deleteSelectedActions();
    expect(useProjectStore.getState().timelineHistoryIndex).toBe(prevIndex + 1);
  });
});

describe('copy/paste/duplicate', () => {
  beforeEach(() => {
    const rows: TimelineRow[] = [
      { id: 'V1', actions: [
        { id: 'a1', start: 0, end: 5, effectId: 'video', data: { segmentId: 's1', src: 'a.mp4', title: 'A', contentType: 'FOOTAGE', layerIndex: 0 } } as any,
      ]},
    ];
    useProjectStore.setState({
      editorData: rows, selectedActionIds: ['a1'], clipboard: [],
      currentTimeMs: 10000, timelineHistory: [rows], timelineHistoryIndex: 0,
    });
  });

  test('copySelectedActions stores in clipboard', () => {
    useProjectStore.getState().copySelectedActions();
    expect(useProjectStore.getState().clipboard).toHaveLength(1);
    expect(useProjectStore.getState().clipboard[0].id).toBe('a1');
  });

  test('pasteClipboard inserts at cursor with new IDs', () => {
    useProjectStore.getState().copySelectedActions();
    useProjectStore.getState().pasteClipboard();
    const v1 = useProjectStore.getState().editorData.find(r => r.id === 'V1')!;
    expect(v1.actions).toHaveLength(2);
    expect(v1.actions[1].start).toBe(10); // cursor at 10s (10000ms / 1000)
    expect(v1.actions[1].id).not.toBe('a1'); // new ID
  });

  test('duplicateSelectedActions copies in-place after original', () => {
    useProjectStore.getState().duplicateSelectedActions();
    const v1 = useProjectStore.getState().editorData.find(r => r.id === 'V1')!;
    expect(v1.actions).toHaveLength(2);
    expect(v1.actions[1].start).toBe(5); // right after original end
  });
});
