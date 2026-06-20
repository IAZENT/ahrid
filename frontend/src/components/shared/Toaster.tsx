import { AnimatePresence, motion } from "framer-motion";
import {
  AlertTriangle,
  CheckCircle2,
  Info,
  X,
  XCircle,
} from "lucide-react";
import type { ComponentType } from "react";
import { create } from "zustand";
import { cn } from "../../lib/utils";

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------
export type ToastTone = "info" | "success" | "warning" | "error";

export interface Toast {
  id: string;
  tone: ToastTone;
  title: string;
  description?: string;
  /** ms before auto-dismiss. 0 = sticky. Default 4500. */
  duration?: number;
}

interface ToastState {
  toasts: Toast[];
  push: (t: Omit<Toast, "id"> & { id?: string }) => string;
  dismiss: (id: string) => void;
  clear: () => void;
}

export const useToastStore = create<ToastState>((set, get) => ({
  toasts: [],
  push: (t) => {
    const id = t.id ?? `t-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    const toast: Toast = { duration: 4500, ...t, id };
    set((s) => {
      // De-dupe on id so rapid repeat emits don't pile up.
      if (s.toasts.some((x) => x.id === id)) return s;
      return { toasts: [...s.toasts, toast].slice(-5) };
    });
    if (toast.duration && toast.duration > 0) {
      window.setTimeout(() => get().dismiss(id), toast.duration);
    }
    return id;
  },
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
  clear: () => set({ toasts: [] }),
}));

/** Imperative helper  call from anywhere (outside React components too). */
export const toast = {
  info: (title: string, description?: string) =>
    useToastStore.getState().push({ tone: "info", title, description }),
  success: (title: string, description?: string) =>
    useToastStore.getState().push({ tone: "success", title, description }),
  warning: (title: string, description?: string) =>
    useToastStore.getState().push({ tone: "warning", title, description }),
  error: (title: string, description?: string) =>
    useToastStore.getState().push({ tone: "error", title, description, duration: 6500 }),
  dismiss: (id: string) => useToastStore.getState().dismiss(id),
};

// ---------------------------------------------------------------------------
// UI
// ---------------------------------------------------------------------------
const TONE_META: Record<
  ToastTone,
  { icon: ComponentType<{ className?: string }>; ring: string; iconColor: string }
> = {
  info: {
    icon: Info,
    ring: "border-accent/40",
    iconColor: "text-accent",
  },
  success: {
    icon: CheckCircle2,
    ring: "border-risk-low/40",
    iconColor: "text-risk-low",
  },
  warning: {
    icon: AlertTriangle,
    ring: "border-risk-medium/40",
    iconColor: "text-risk-medium",
  },
  error: {
    icon: XCircle,
    ring: "border-risk-critical/40",
    iconColor: "text-risk-critical",
  },
};

export function Toaster() {
  const toasts = useToastStore((s) => s.toasts);
  const dismiss = useToastStore((s) => s.dismiss);

  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2"
    >
      <AnimatePresence initial={false}>
        {toasts.map((t) => {
          const meta = TONE_META[t.tone];
          const Icon = meta.icon;
          return (
            <motion.div
              key={t.id}
              role="status"
              layout
              initial={{ opacity: 0, x: 24, scale: 0.96 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 24, scale: 0.96 }}
              transition={{ type: "spring", stiffness: 380, damping: 30 }}
              className={cn(
                "pointer-events-auto relative flex gap-3 rounded-lg border bg-bg-elevated p-3 pr-8 shadow-elevated",
                meta.ring,
              )}
            >
              <Icon className={cn("mt-0.5 h-4 w-4 flex-shrink-0", meta.iconColor)} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-semibold text-text-primary">{t.title}</p>
                {t.description && (
                  <p className="mt-0.5 line-clamp-3 text-[11px] leading-snug text-text-muted">
                    {t.description}
                  </p>
                )}
              </div>
              <button
                onClick={() => dismiss(t.id)}
                aria-label="Dismiss"
                className="absolute right-1 top-1 rounded p-1 text-text-muted transition-colors hover:bg-bg-surface hover:text-text-primary"
              >
                <X className="h-3 w-3" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
