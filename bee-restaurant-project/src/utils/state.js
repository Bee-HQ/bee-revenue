export function createStateMachine({ initial, states }) {
  let state = initial;
  const listeners = new Set();

  return {
    current() {
      return state;
    },
    send(event) {
      const transitions = states[state];
      if (!transitions || !(event in transitions)) return;
      const prev = state;
      state = transitions[event];
      for (const fn of listeners) fn(state, prev);
    },
    on(fn) {
      listeners.add(fn);
    },
    off(fn) {
      listeners.delete(fn);
    },
  };
}
