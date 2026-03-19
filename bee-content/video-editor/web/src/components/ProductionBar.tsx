import { useState, useCallback } from 'react';
import { api } from '../api/client';
import { useProjectStore } from '../stores/project';

type Status = 'idle' | 'running' | 'done' | 'error';

export function ProductionBar() {
  const [status, setStatus] = useState<Record<string, Status>>({});
  const [message, setMessage] = useState<string | null>(null);
  const undoStack = useProjectStore(s => s.undoStack);
  const redoStack = useProjectStore(s => s.redoStack);

  const runAction = async (key: string, action: () => Promise<any>) => {
    setStatus(s => ({ ...s, [key]: 'running' }));
    setMessage(null);
    try {
      const result = await action();
      setStatus(s => ({ ...s, [key]: 'done' }));
      if (result.count !== undefined) {
        setMessage(`${key}: generated ${result.count} files`);
      } else if (result.output) {
        setMessage(`${key}: ${result.output}`);
      } else {
        setMessage(`${key}: done`);
      }
    } catch (e: any) {
      setStatus(s => ({ ...s, [key]: 'error' }));
      setMessage(`${key} failed: ${e.message}`);
    }
  };

  const runNarrationWs = useCallback(() => {
    setStatus(s => ({ ...s, narration: 'running' }));
    setMessage('Narration: connecting...');

    api.connectProgress('narration', { tts_engine: 'edge' }, (data) => {
      if (data.step === 'narration') {
        setMessage(`Narration: ${data.done}/${data.total}`);
      } else if (data.step === 'complete') {
        const finalStatus = data.status === 'ok' ? 'done' : 'error';
        setStatus(s => ({ ...s, narration: finalStatus as Status }));
        setMessage(`Narration: ${data.succeeded} generated${data.failed ? ` (${data.failed} failed)` : ''}`);
      } else if (data.error) {
        setStatus(s => ({ ...s, narration: 'error' }));
        setMessage(`Narration failed: ${data.error}`);
      }
    }, () => {
      setStatus(s => {
        if (s.narration === 'running') return { ...s, narration: 'done' };
        return s;
      });
    });
  }, []);

  const runProduceWs = useCallback(() => {
    setStatus(s => ({ ...s, produce: 'running' }));
    setMessage('Produce: starting...');

    api.connectProgress('produce', {}, (data) => {
      if (data.step === 'complete') {
        setStatus(s => ({ ...s, produce: data.status === 'ok' ? 'done' : 'error' }));
        setMessage(data.output ? `Done: ${data.output}` : 'Produce complete');
      } else if (data.error) {
        setStatus(s => ({ ...s, produce: 'error' }));
        setMessage(`Produce failed: ${data.error}`);
      } else {
        setMessage(`${data.step}: ${data.status}${data.message ? ' — ' + data.message : ''}`);
      }
    });
  }, []);

  const buttonClass = (key: string) => {
    const s = status[key] || 'idle';
    const base = 'px-3 py-1.5 rounded text-xs font-medium transition-colors disabled:opacity-50';
    switch (s) {
      case 'running': return `${base} bg-yellow-600/20 text-yellow-400`;
      case 'done': return `${base} bg-green-600/20 text-green-400`;
      case 'error': return `${base} bg-red-600/20 text-red-400`;
      default: return `${base} bg-editor-hover text-gray-300 hover:bg-editor-border`;
    }
  };

  const isRunning = Object.values(status).some(s => s === 'running');

  return (
    <div className="px-4 py-2 flex items-center gap-3">
      <span className="text-[10px] uppercase tracking-wider text-gray-500 mr-1">Production</span>

      <button
        className="px-3 py-1.5 rounded text-xs font-medium transition-colors disabled:opacity-50 bg-editor-hover text-gray-300 hover:bg-editor-border"
        disabled={undoStack.length === 0}
        onClick={() => useProjectStore.getState().undo()}
        title="Undo (Ctrl+Z / Cmd+Z)"
      >
        Undo ({undoStack.length})
      </button>

      <button
        className="px-3 py-1.5 rounded text-xs font-medium transition-colors disabled:opacity-50 bg-editor-hover text-gray-300 hover:bg-editor-border"
        disabled={redoStack.length === 0}
        onClick={() => useProjectStore.getState().redo()}
        title="Redo (Ctrl+Shift+Z / Cmd+Shift+Z)"
      >
        Redo ({redoStack.length})
      </button>

      <button
        className={buttonClass('init')}
        disabled={isRunning}
        onClick={() => runAction('init', api.initProject)}
      >
        Init Dirs
      </button>

      <button
        className={buttonClass('graphics')}
        disabled={isRunning}
        onClick={() => runAction('graphics', api.generateGraphics)}
      >
        Graphics
      </button>

      <button
        className={buttonClass('narration')}
        disabled={isRunning}
        onClick={runNarrationWs}
      >
        Narration
      </button>

      <button
        className={buttonClass('produce')}
        disabled={isRunning}
        onClick={runProduceWs}
      >
        Produce
      </button>

      <button
        className={buttonClass('assemble')}
        disabled={isRunning}
        onClick={() => runAction('assemble', api.assembleVideo)}
      >
        Assemble
      </button>

      <button
        className={buttonClass('previews')}
        disabled={isRunning}
        onClick={() => runAction('previews', api.generateAllPreviews)}
      >
        Previews
      </button>

      <span className="text-gray-700">|</span>

      <button
        className={buttonClass('captions')}
        disabled={isRunning}
        onClick={() => runAction('captions', () => api.generateCaptions('karaoke'))}
      >
        Captions
      </button>

      <button
        className={buttonClass('roughcut')}
        disabled={isRunning}
        onClick={() => runAction('roughcut', api.roughCut)}
      >
        Rough Cut
      </button>

      <button
        className={buttonClass('preflight')}
        disabled={isRunning}
        onClick={async () => {
          setStatus(s => ({ ...s, preflight: 'running' }));
          try {
            const r = await api.getPreflight();
            const ok = r.missing === 0;
            setStatus(s => ({ ...s, preflight: ok ? 'done' : 'error' }));
            setMessage(`Preflight: ${r.found} found, ${r.missing} missing, ${r.needs_check} to check`);
          } catch (e: any) {
            setStatus(s => ({ ...s, preflight: 'error' }));
            setMessage(`Preflight failed: ${e.message}`);
          }
        }}
      >
        Preflight
      </button>

      {message && (
        <span className="text-xs text-gray-500 ml-auto truncate max-w-md">
          {message}
        </span>
      )}
    </div>
  );
}
