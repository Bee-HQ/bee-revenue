# Spike Notes: DesignCombo + Remotion Integration

## Package Versions (working)

```json
"@designcombo/state": "5.5.8",
"@designcombo/timeline": "5.5.8",
"@designcombo/types": "5.5.8",
"@designcombo/events": "1.0.2",
"@types/lodash-es": "^4.17.12",
"remotion": "^4.0.283",
"@remotion/player": "^4.0.283",
"@remotion/cli": "^4.0.283"
```

**Note:** `@designcombo/events` is at v1.0.2, NOT 5.5.8. The state/timeline packages peer-depend on `^1.0.2`.

## React 19 Compatibility

Both DesignCombo and Remotion compile and import fine with React 19. No downgrade needed.

## DesignCombo API Surface

### StateManager

```typescript
import { default as StateManager } from '@designcombo/state';
// OR: import StateManager from '@designcombo/state';

const sm = new StateManager(initialState?: Partial<State>, config?: StateManagerConfig);

// Key methods:
sm.getState(): State
sm.subscribe(callback: (state: State) => void): Subscription  // RxJS
sm.updateState(partialState: Partial<State>, options?: IUpdateStateOptions): void
sm.undo(): void
sm.redo(): void
sm.toJSON(): serialized state
sm.purge(): void  // cleanup
sm.initListeners(): void
sm.destroyListeners(): void

// Targeted subscriptions:
sm.subscribeToUpdateTrackItem(cb)
sm.subscribeToActiveIds(cb)
sm.subscribeToTracks(cb)
sm.subscribeToHistory(cb)
sm.subscribeToState(cb)  // full state (tracks + items + transitions)
```

### State Shape

```typescript
interface State {
  fps: number;
  size: { width: number; height: number };
  tracks: ITrack[];
  trackItemIds: string[];
  trackItemsMap: Record<string, ITrackItem>;
  transitionIds: string[];
  transitionsMap: Record<string, ITransition>;
  duration: number;
  activeIds: string[];
  scale: ITimelineScaleState;
  background: any;
  structure: ItemStructure[];
}
```

### ITrack

```typescript
interface ITrack {
  id: string;
  type: ITrackType;  // "main" | "video" | "audio" | "text" | "image" | ...
  items: string[];   // array of trackItem IDs
  muted: boolean;
  accepts?: string[];
  magnetic?: boolean;
  static?: boolean;
}
```

### ITrackItem (base)

```typescript
interface ITrackItemBase {
  id: string;
  name: string;
  type: ItemType;  // "video" | "audio" | "image" | "text" | "caption" | ...
  display: IDisplay;  // { from: number, to: number } — in milliseconds
  trim?: ITrim;       // { from: number, to: number } — trim offset in ms
  duration?: number;
  playbackRate?: number;
  metadata: Record<string, any>;  // custom data (we'll use this for segment info)
  details?: any;  // type-specific (IVideoDetails, IAudioDetails, etc.)
}

// Type-specific:
interface IVideoDetails { src: string; width: number; height: number; volume?: number; }
interface IAudioDetails { src: string; volume?: number; }
interface IImageDetails { src: string; }
interface ITextDetails { text: string; fontSize: number; fontFamily: string; color: string; }
```

### Events

```typescript
import { dispatch, subject, filter } from '@designcombo/events';

// Dispatch an event:
dispatch('design:load', { payload: stateData });
dispatch('add:video', { payload: { ... } });
dispatch('edit:object', { payload: { ... } });
dispatch('history:undo', {});
dispatch('history:redo', {});
dispatch('layer:select', { payload: { activeIds: ['item-1'] } });

// Subscribe to events:
subject.pipe(filter(e => e.key === 'some:event')).subscribe(e => { ... });
```

### Timeline (Canvas)

```typescript
import { default as Timeline } from '@designcombo/timeline';
// OR: import Timeline from '@designcombo/timeline';

const tl = new Timeline(canvasElement, {
  scale: { unit: 300, zoom: 1/300, segments: 5, index: 7 },
  duration: totalDurationMs,
  state: stateManager,           // required — IStateManager
  itemTypes: ['video', 'audio', 'image', 'text'],  // which types to render
  sizesMap: { video: 40, audio: 30, image: 40, text: 30 },  // track heights
  acceptsMap: { video: ['video', 'image'], audio: ['audio'] },  // drag-drop rules
  withTransitions: ['video'],    // which tracks show transitions
});

// Timeline is a Fabric.js Canvas subclass — has all Fabric.js methods
// Key additions:
tl.tracks: ITrack[]
tl.trackItemsMap: Record<string, ITrackItem>
tl.onViewportChange(callback: (left: number) => void)
tl.initScrollbars(config)
tl.disposeScrollbars()
```

## Key Findings

1. **StateManager is default export**, not named: `import StateManager from '@designcombo/state'`
2. **Timeline is default export**: `import Timeline from '@designcombo/timeline'`
3. **Events use RxJS Subject**: `dispatch(key, { payload })` to send, `subject.pipe(filter(...)).subscribe(...)` to listen
4. **Display times are in milliseconds**: `display: { from: 0, to: 15000 }` = 0s to 15s
5. **Timeline extends Fabric.js Canvas**: needs a real `<canvas>` element, not a div
6. **Timeline constructor requires `itemTypes`, `sizesMap`, `acceptsMap`** — more config needed than the spec assumed
7. **No explicit seek event** — scrubber position may need to be managed via Timeline's Fabric.js viewport or a custom mechanism
8. **Undo/redo is on StateManager**: `sm.undo()`, `sm.redo()` — not via events (though events trigger them)
