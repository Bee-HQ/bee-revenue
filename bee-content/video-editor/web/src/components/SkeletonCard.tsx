export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div className="bg-editor-surface rounded-lg border border-editor-border p-3 animate-pulse">
      <div className="h-3 bg-editor-hover rounded w-1/3 mb-2" />
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="h-2 bg-editor-hover rounded mb-1.5" style={{ width: `${70 + Math.random() * 30}%` }} />
      ))}
    </div>
  );
}

export function SkeletonList({ count = 5 }: { count?: number }) {
  return (
    <div className="p-2 space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} lines={2} />
      ))}
    </div>
  );
}
