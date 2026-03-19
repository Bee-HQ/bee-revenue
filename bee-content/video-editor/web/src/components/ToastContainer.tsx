import { useToastStore } from '../stores/toast';

const TYPE_STYLES = {
  success: 'bg-green-900/90 border-green-700 text-green-200',
  error: 'bg-red-900/90 border-red-700 text-red-200',
  info: 'bg-blue-900/90 border-blue-700 text-blue-200',
  warning: 'bg-yellow-900/90 border-yellow-700 text-yellow-200',
};

const TYPE_ICONS = {
  success: '✓',
  error: '✕',
  info: 'ℹ',
  warning: '⚠',
};

export function ToastContainer() {
  const toasts = useToastStore((s) => s.toasts);
  const removeToast = useToastStore((s) => s.removeToast);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`flex items-start gap-2 px-3 py-2 rounded-lg border shadow-lg text-xs animate-slide-in ${TYPE_STYLES[t.type]}`}
        >
          <span className="text-sm leading-none mt-0.5">{TYPE_ICONS[t.type]}</span>
          <span className="flex-1 leading-relaxed">{t.message}</span>
          <button
            onClick={() => removeToast(t.id)}
            className="text-white/40 hover:text-white/80 text-sm leading-none"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
