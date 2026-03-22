# Timeline Sprint 1 Features — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the essential timeline interactions that make bee-video feel like a real NLE: multi-select, delete, copy/paste/duplicate, right-click context menu, and track lock/mute/hide. (Ordered by dependency, not spec numbering. Ripple delete deferred to Sprint 2.)

**Architecture:** All features are Zustand state + keyboard handlers + one new component (context menu). The `react-timeline-editor` library already provides the callbacks we need (`onContextMenuAction`, `selected` field, `movable`/`flexible` flags). We add state management on top.

**Tech Stack:** React 19, `@xzdarcy/react-timeline-editor`, Zustand, lucide-react, vitest

**Spec:** `docs/superpowers/TIMELINE-FEATURES.md` (Tier 1, items 1-5)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `web/src/stores/project.ts` | Modify | Add selectedActionIds, clipboard, trackState, and actions for multi-select, copy/paste, delete |
| `web/src/stores/project-timeline.test.ts` | Modify | Tests for new store actions |
| `web/src/components/TimelineContextMenu.tsx` | Create | Right-click context menu component |
| `web/src/components/TimelineEditor.tsx` | Modify | Wire context menu, multi-select, track controls |
| `web/src/components/TimelineActionRenderer.tsx` | Modify | Selection highlight styling |
| `web/src/App.tsx` | Modify | Add keyboard shortcuts (Delete, Ctrl+C/V/D) |

---

### Task 1: Multi-select clips

**Files:**
- Modify: `web/src/stores/project.ts`
- Modify: `web/src/stores/project-timeline.test.ts`
- Modify: `web/src/components/TimelineEditor.tsx`

- [ ] **Step 1: Write failing tests**

Add to `web/src/stores/project-timeline.test.ts`:

```ts
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

  test('clearSelection empties selection', () => {
    useProjectStore.getState().selectAction('a1', false);
    useProjectStore.getState().clearActionSelection();
    expect(useProjectStore.getState().selectedActionIds).toEqual([]);
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd bee-content/video-editor/web && npx vitest run src/stores/project-timeline.test.ts
```
Expected: FAIL — `selectAction` not found

- [ ] **Step 3: Add state and actions to store**

In `web/src/stores/project.ts`, add to interface:
```ts
selectedActionIds: string[];
selectAction: (id: string, shiftKey: boolean) => void;
clearActionSelection: () => void;
```

Add initial value: `selectedActionIds: [],`

Implement:
```ts
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
```

Also update `loadProject` reset to include `selectedActionIds: []`.

- [ ] **Step 4: Run tests**

```bash
cd bee-content/video-editor/web && npx vitest run src/stores/project-timeline.test.ts
```
Expected: All pass

- [ ] **Step 5: Wire to TimelineEditor**

In `TimelineEditor.tsx`, replace `handleClickAction`. **Important:** the `<Timeline>` prop is `onClickActionOnly` (not `onClickAction`) — this fires only on true clicks, not drag starts:
```tsx
const handleClickAction = useCallback((e: React.MouseEvent, { action }: { action: TimelineAction }) => {
  useProjectStore.getState().selectAction(action.id, e.shiftKey);
}, []);
```
The existing `<Timeline>` prop `onClickActionOnly={handleClickAction}` stays as-is — do NOT change it to `onClickAction`.

Before passing `editorData` to `<Timeline>`, mark selected actions:
```tsx
const selectedIds = useProjectStore(s => s.selectedActionIds);

// Mark selected actions before passing to Timeline
const markedData = editorData.map(row => ({
  ...row,
  actions: row.actions.map(a => ({
    ...a,
    selected: selectedIds.includes(a.id),
  })),
}));
```

Pass `markedData` instead of `editorData` to `<Timeline editorData={markedData}>`.

Replace `handleClickRow`:
```tsx
const handleClickRow = useCallback(() => {
  useProjectStore.getState().clearActionSelection();
}, []);
```

- [ ] **Step 6: Add selection highlight in renderer**

In `TimelineActionRenderer.tsx`, add a `selected` visual indicator. The library sets `action.selected = true` for selected actions. Add an outline:

```tsx
const isSelected = beeAction.selected;
// In the style object, add:
outline: isSelected ? '2px solid #3b82f6' : 'none',
outlineOffset: -1,
```

- [ ] **Step 7: Build and commit**

```bash
npm run build 2>&1 | tail -5
git add web/src/stores/project.ts web/src/stores/project-timeline.test.ts web/src/components/TimelineEditor.tsx web/src/components/TimelineActionRenderer.tsx
git commit -m "feat: multi-select clips with shift+click and selection highlight"
```

---

### Task 2: Delete clips

**Files:**
- Modify: `web/src/stores/project.ts`
- Modify: `web/src/stores/project-timeline.test.ts`
- Modify: `web/src/App.tsx`

- [ ] **Step 1: Write failing tests**

```ts
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
```

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement deleteSelectedActions**

Add to interface: `deleteSelectedActions: () => void;`

```ts
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
```

- [ ] **Step 4: Run tests**

- [ ] **Step 5: Wire Delete/Backspace key in App.tsx**

In the keyboard handler, add before the Space handler:
```ts
// Delete / Backspace — delete selected clips
if ((e.key === 'Delete' || e.key === 'Backspace') && !mod) {
  e.preventDefault();
  useProjectStore.getState().deleteSelectedActions();
}
```

- [ ] **Step 6: Build and commit**

```bash
npm run build 2>&1 | tail -5
git add web/src/stores/project.ts web/src/stores/project-timeline.test.ts web/src/App.tsx
git commit -m "feat: delete selected clips with Delete/Backspace key"
```

---

### Task 3: Copy/paste/duplicate clips

**Files:**
- Modify: `web/src/stores/project.ts`
- Modify: `web/src/stores/project-timeline.test.ts`
- Modify: `web/src/App.tsx`

- [ ] **Step 1: Write failing tests**

```ts
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

  test('duplicateSelectedActions copies in-place offset by 0.5s', () => {
    useProjectStore.getState().duplicateSelectedActions();
    const v1 = useProjectStore.getState().editorData.find(r => r.id === 'V1')!;
    expect(v1.actions).toHaveLength(2);
    expect(v1.actions[1].start).toBe(5); // right after original end
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement store actions**

Add to interface:
```ts
clipboard: TimelineAction[];
copySelectedActions: () => void;
pasteClipboard: () => void;
duplicateSelectedActions: () => void;
```

Add initial value: `clipboard: [],`

```ts
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
  // Find earliest start in clipboard to compute offset
  const earliest = Math.min(...clipboard.map(a => a.start));
  const offset = cursorSec - earliest;

  // Match clipboard items to rows by effectId
  const rowEffectId = (row: TimelineRow): string => {
    if (row.actions.length > 0) return row.actions[0].effectId;
    if (row.id === 'V1') return 'video';
    if (row.id === 'A1') return 'narration';
    if (row.id === 'A2') return 'audio';
    if (row.id === 'A3') return 'music';
    if (row.id === 'OV1') return 'overlay';
    return '';
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
```

Also update `loadProject` reset: `clipboard: [],`

- [ ] **Step 4: Run tests**

- [ ] **Step 5: Wire keyboard shortcuts in App.tsx**

```ts
// Copy (Ctrl+C)
if (mod && e.key === 'c') {
  const { selectedActionIds } = useProjectStore.getState();
  if (selectedActionIds.length > 0) {
    e.preventDefault();
    useProjectStore.getState().copySelectedActions();
  }
}

// Paste (Ctrl+V) — only if clipboard has content, otherwise let paste handler in TimelineEditor handle it
if (mod && e.key === 'v') {
  const { clipboard } = useProjectStore.getState();
  if (clipboard.length > 0) {
    e.preventDefault();
    useProjectStore.getState().pasteClipboard();
  }
}

// Duplicate (Ctrl+D)
if (mod && e.key === 'd') {
  e.preventDefault();
  useProjectStore.getState().duplicateSelectedActions();
}
```

- [ ] **Step 6: Build and commit**

```bash
npm run build 2>&1 | tail -5
git add web/src/stores/project.ts web/src/stores/project-timeline.test.ts web/src/App.tsx
git commit -m "feat: copy/paste/duplicate clips with keyboard shortcuts"
```

---

### Task 4: Right-click context menu

**Files:**
- Create: `web/src/components/TimelineContextMenu.tsx`
- Modify: `web/src/components/TimelineEditor.tsx`

- [ ] **Step 1: Create TimelineContextMenu.tsx**

```tsx
import { useEffect, useRef } from 'react';
import { Trash2, Copy, ClipboardPaste, CopyPlus, Scissors, SlidersHorizontal } from 'lucide-react';
import { useProjectStore } from '../stores/project';

interface Props {
  x: number;
  y: number;
  actionId: string;
  onClose: () => void;
}

export function TimelineContextMenu({ x, y, actionId, onClose }: Props) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) onClose();
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [onClose]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  const items = [
    { label: 'Split', icon: Scissors, action: () => { useProjectStore.getState().splitAtPlayhead(); onClose(); } },
    { label: 'Duplicate', icon: CopyPlus, action: () => { useProjectStore.getState().duplicateSelectedActions(); onClose(); } },
    { label: 'Copy', icon: Copy, action: () => { useProjectStore.getState().copySelectedActions(); onClose(); } },
    { label: 'Paste', icon: ClipboardPaste, action: () => { useProjectStore.getState().pasteClipboard(); onClose(); } },
    null, // separator
    { label: 'Delete', icon: Trash2, action: () => { useProjectStore.getState().deleteSelectedActions(); onClose(); }, danger: true },
  ];

  return (
    <div
      ref={menuRef}
      className="fixed z-50 bg-editor-surface border border-editor-border rounded-md shadow-xl py-1 min-w-[160px]"
      style={{ left: x, top: y }}
    >
      {items.map((item, i) =>
        item === null ? (
          <div key={i} className="border-t border-editor-border my-1" />
        ) : (
          <button
            key={item.label}
            onClick={item.action}
            className={`w-full flex items-center gap-2 px-3 py-1.5 text-[11px] text-left hover:bg-editor-hover transition-colors ${
              (item as any).danger ? 'text-red-400 hover:text-red-300' : 'text-gray-300'
            }`}
          >
            <item.icon size={12} />
            {item.label}
          </button>
        )
      )}
    </div>
  );
}
```

- [ ] **Step 2: Wire to TimelineEditor**

Add state for context menu:
```tsx
const [contextMenu, setContextMenu] = useState<{ x: number; y: number; actionId: string } | null>(null);
```

Add handler:
```tsx
const handleContextMenuAction = useCallback((e: React.MouseEvent, { action }: { action: TimelineAction }) => {
  e.preventDefault();
  // Select the action if not already selected
  const { selectedActionIds } = useProjectStore.getState();
  if (!selectedActionIds.includes(action.id)) {
    useProjectStore.getState().selectAction(action.id, false);
  }
  setContextMenu({ x: e.clientX, y: e.clientY, actionId: action.id });
}, []);
```

Add prop to `<Timeline>`:
```tsx
onContextMenuAction={handleContextMenuAction}
```

Render context menu in JSX (inside the return, before closing `</div>`):
```tsx
{contextMenu && (
  <TimelineContextMenu
    x={contextMenu.x}
    y={contextMenu.y}
    actionId={contextMenu.actionId}
    onClose={() => setContextMenu(null)}
  />
)}
```

- [ ] **Step 3: Build and commit**

```bash
npm run build 2>&1 | tail -5
git add web/src/components/TimelineContextMenu.tsx web/src/components/TimelineEditor.tsx
git commit -m "feat: right-click context menu on timeline clips"
```

---

### Task 5: Track lock/mute/hide

**Files:**
- Modify: `web/src/stores/project.ts`
- Modify: `web/src/stores/project-timeline.test.ts`
- Modify: `web/src/components/TimelineEditor.tsx`

- [ ] **Step 1: Write failing tests**

```ts
describe('track state', () => {
  beforeEach(() => {
    const rows: TimelineRow[] = [
      { id: 'V1', actions: [{ id: 'a1', start: 0, end: 5, effectId: 'video' }] },
      { id: 'A1', actions: [{ id: 'a2', start: 0, end: 5, effectId: 'narration' }] },
    ];
    useProjectStore.setState({ editorData: rows, trackState: {}, timelineHistory: [rows], timelineHistoryIndex: 0 });
  });

  test('toggleTrackLock sets locked state', () => {
    useProjectStore.getState().toggleTrackLock('V1');
    expect(useProjectStore.getState().trackState.V1?.locked).toBe(true);
  });

  test('toggleTrackLock toggles off', () => {
    useProjectStore.getState().toggleTrackLock('V1');
    useProjectStore.getState().toggleTrackLock('V1');
    expect(useProjectStore.getState().trackState.V1?.locked).toBe(false);
  });

  test('toggleTrackMute sets muted state', () => {
    useProjectStore.getState().toggleTrackMute('A1');
    expect(useProjectStore.getState().trackState.A1?.muted).toBe(true);
  });

  test('toggleTrackHide sets hidden state', () => {
    useProjectStore.getState().toggleTrackHide('A1');
    expect(useProjectStore.getState().trackState.A1?.hidden).toBe(true);
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement track state**

Add to interface:
```ts
trackState: Record<string, { locked?: boolean; muted?: boolean; hidden?: boolean }>;
toggleTrackLock: (rowId: string) => void;
toggleTrackMute: (rowId: string) => void;
toggleTrackHide: (rowId: string) => void;
```

Add initial value: `trackState: {},`

```ts
toggleTrackLock: (rowId) => {
  const { trackState } = get();
  const current = trackState[rowId] || {};
  set({ trackState: { ...trackState, [rowId]: { ...current, locked: !current.locked } } });
},
toggleTrackMute: (rowId) => {
  const { trackState } = get();
  const current = trackState[rowId] || {};
  set({ trackState: { ...trackState, [rowId]: { ...current, muted: !current.muted } } });
},
toggleTrackHide: (rowId) => {
  const { trackState } = get();
  const current = trackState[rowId] || {};
  set({ trackState: { ...trackState, [rowId]: { ...current, hidden: !current.hidden } } });
},
```

Also update `loadProject` reset: `trackState: {},`

- [ ] **Step 4: Run tests**

- [ ] **Step 5: Apply track state to editorData in TimelineEditor**

In `TimelineEditor.tsx`, when building `markedData`, also apply lock/hide:

```tsx
const trackState = useProjectStore(s => s.trackState);

const markedData = editorData
  .filter(row => !trackState[row.id]?.hidden) // hide hidden tracks
  .map(row => {
    const state = trackState[row.id];
    return {
      ...row,
      actions: row.actions.map(a => ({
        ...a,
        selected: selectedIds.includes(a.id),
        movable: state?.locked ? false : a.movable,
        flexible: state?.locked ? false : a.flexible,
      })),
    };
  });
```

- [ ] **Step 6: Add track control buttons**

In the track label area (rendered inside `getActionRender` for the first action in each row — already showing `row.id`), add small lock/mute/hide icons. Alternatively, render a small panel to the left of the Timeline.

Since the library doesn't support a control column natively, add a thin column before the `<Timeline>`:

```tsx
<div className="w-16 shrink-0 border-r border-editor-border bg-editor-surface flex flex-col overflow-hidden" style={{ marginTop: 32 }}>
  {markedData.map(row => {
    const state = trackState[row.id] || {};
    return (
      <div key={row.id} className="flex items-center gap-0.5 px-0.5" style={{ height: 28 }}>
        <span className="text-[8px] text-gray-500 font-mono w-6">{row.id}</span>
        <button
          onClick={() => useProjectStore.getState().toggleTrackLock(row.id)}
          className={`p-0.5 rounded ${state.locked ? 'text-red-400' : 'text-gray-600 hover:text-gray-400'}`}
          title={state.locked ? 'Unlock' : 'Lock'}
        >
          <Lock size={9} />
        </button>
        <button
          onClick={() => useProjectStore.getState().toggleTrackMute(row.id)}
          className={`p-0.5 rounded ${state.muted ? 'text-yellow-400' : 'text-gray-600 hover:text-gray-400'}`}
          title={state.muted ? 'Unmute' : 'Mute'}
        >
          <VolumeX size={9} />
        </button>
        <button
          onClick={() => useProjectStore.getState().toggleTrackHide(row.id)}
          className={`p-0.5 rounded ${state.hidden ? 'text-blue-400' : 'text-gray-600 hover:text-gray-400'}`}
          title={state.hidden ? 'Show' : 'Hide'}
        >
          <EyeOff size={9} />
        </button>
      </div>
    );
  })}
</div>
```

Add imports: `import { Lock, VolumeX, EyeOff } from 'lucide-react';`

Note: The `marginTop: 32` matches the Timeline's `.timeline-editor-time-area { height: 32px }` CSS rule. If misaligned, inspect with DevTools: the track control rows must align with `.timeline-editor-edit-row` elements. The edit area also has `margin-top: 10px` — if the library version includes that, use `marginTop: 42`.

- [ ] **Step 7: Build and commit**

```bash
npm run build 2>&1 | tail -5
git add web/src/stores/project.ts web/src/stores/project-timeline.test.ts web/src/components/TimelineEditor.tsx
git commit -m "feat: track lock/mute/hide with visual controls"
```

---

### Task 6: Final verification

- [ ] **Step 1: Run all tests**

```bash
cd bee-content/video-editor/web && npx vitest run
```
Expected: All pass

- [ ] **Step 2: Full build**

```bash
npm run build 2>&1 | tail -5
```
Expected: Clean

- [ ] **Step 3: Manual smoke test**

```bash
cd bee-content/video-editor && ./dev.sh
```

Verify:
1. Click clip → blue outline selection
2. Shift+click → multi-select (multiple blue outlines)
3. Delete key → selected clips removed
4. Ctrl+C then Ctrl+V → clips pasted at cursor
5. Ctrl+D → duplicate clip right after original
6. Right-click clip → context menu with Split, Duplicate, Copy, Paste, Delete
7. Lock icon on track → clips can't be moved/resized
8. Mute icon on track → visual indicator (no audio effect yet)
9. Eye icon on track → track hidden from timeline
10. Undo/redo still works for all operations

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "chore: sprint 1 timeline features complete"
```
