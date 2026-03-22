import { useState } from 'react';
import { useProjectStore } from '../stores/project';

export function LoadProject() {
  const [storyboardPath, setStoryboardPath] = useState('sample-3min.md');
  const [projectDir, setProjectDir] = useState('../../discovery/true-crime/cases/alex-murdaugh');
  const { loadProject, loading, error } = useProjectStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (storyboardPath.trim()) {
      loadProject(storyboardPath.trim(), projectDir.trim() || '.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="bg-editor-surface border border-editor-border rounded-xl p-8 w-full max-w-lg">
        <h1 className="text-2xl font-bold mb-1">Bee Video Editor</h1>
        <p className="text-gray-500 text-sm mb-6">Storyboard-first AI video production</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Project File</label>
            <input
              type="text"
              value={storyboardPath}
              onChange={e => setStoryboardPath(e.target.value)}
              placeholder="/path/to/project.md or .otio"
              className="w-full bg-editor-bg border border-editor-border rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:border-editor-accent"
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Project Directory</label>
            <input
              type="text"
              value={projectDir}
              onChange={e => setProjectDir(e.target.value)}
              placeholder="."
              className="w-full bg-editor-bg border border-editor-border rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:border-editor-accent"
            />
          </div>

          {error && (
            <div className="bg-red-900/30 border border-red-800 rounded-lg px-3 py-2 text-sm text-red-300">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !storyboardPath.trim()}
            className="w-full bg-editor-accent hover:bg-blue-600 disabled:opacity-50
                       rounded-lg px-4 py-2 text-sm font-medium transition-colors"
          >
            {loading ? 'Loading...' : 'Load Project'}
          </button>
        </form>
      </div>
    </div>
  );
}
