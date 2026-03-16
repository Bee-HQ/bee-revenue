import { useState } from 'react';
import { api } from '../api/client';

type Status = 'idle' | 'running' | 'done' | 'error';

export function ProductionBar() {
  const [status, setStatus] = useState<Record<string, Status>>({});
  const [message, setMessage] = useState<string | null>(null);

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
        onClick={() => runAction('narration', () => api.generateNarration())}
      >
        Narration
      </button>

      <button
        className={buttonClass('assemble')}
        disabled={isRunning}
        onClick={() => runAction('assemble', api.assembleVideo)}
      >
        Assemble
      </button>

      {message && (
        <span className="text-xs text-gray-500 ml-auto truncate max-w-md">
          {message}
        </span>
      )}
    </div>
  );
}
