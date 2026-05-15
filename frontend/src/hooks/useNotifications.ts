import { useCallback, useEffect, useRef, useState } from "react";
import { notificationsApi } from "../api/notifications";
import type { NotificationDto, NotificationSeverity } from "../types/api";
import { useAuthStore } from "../store/authStore";
import { toast, type ToastTone } from "../components/shared/Toaster";

const POLL_INTERVAL_MS = 60_000;

const SEVERITY_TO_TONE: Record<NotificationSeverity, ToastTone> = {
  info: "info",
  success: "success",
  warning: "warning",
  critical: "error",
};

interface State {
  items: NotificationDto[];
  unread: number;
  total: number;
  loading: boolean;
  error: string | null;
}

export function useNotifications() {
  const isAuthed = useAuthStore((s) => !!s.accessToken);
  const [state, setState] = useState<State>({
    items: [], unread: 0, total: 0, loading: false, error: null,
  });
  const pollTimer = useRef<number | null>(null);
  const toastedIds = useRef<Set<string>>(new Set());
  const hasHydrated = useRef(false);

  const maybeToast = useCallback((items: NotificationDto[]) => {
    if (!hasHydrated.current) {
      items.forEach((n) => toastedIds.current.add(n.id));
      hasHydrated.current = true;
      return;
    }
    for (const n of items) {
      if (n.is_read) continue;
      if (toastedIds.current.has(n.id)) continue;
      toastedIds.current.add(n.id);
      toast[SEVERITY_TO_TONE[n.severity] ?? "info"](n.title, n.body ?? undefined);
    }
  }, []);

  const refresh = useCallback(async () => {
    if (!isAuthed) return;
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const data = await notificationsApi.list({ limit: 30 });
      maybeToast(data.items);
      setState({
        items: data.items, unread: data.unread, total: data.total,
        loading: false, error: null,
      });
    } catch (err) {
      setState((s) => ({
        ...s, loading: false,
        error: err instanceof Error ? err.message : "Failed to load notifications",
      }));
    }
  }, [isAuthed, maybeToast]);

  const refreshCount = useCallback(async () => {
    if (!isAuthed) return;
    try {
      const unread = await notificationsApi.unreadCount();
      setState((prev) => {
        if (prev.unread === unread) return prev;
        if (unread > prev.unread) void refresh();
        return { ...prev, unread };
      });
    } catch { /* ignore */ }
  }, [isAuthed, refresh]);

  useEffect(() => {
    if (!isAuthed) return;
    void refresh();
    pollTimer.current = window.setInterval(refreshCount, POLL_INTERVAL_MS);
    return () => {
      if (pollTimer.current !== null) window.clearInterval(pollTimer.current);
      pollTimer.current = null;
    };
  }, [isAuthed, refresh, refreshCount]);

  const markRead = useCallback(async (id: string) => {
    setState((s) => {
      const items = s.items.map((n) =>
        n.id === id && !n.is_read
          ? { ...n, is_read: true, read_at: new Date().toISOString() }
          : n,
      );
      const unread = items.filter((n) => !n.is_read).length;
      return { ...s, items, unread };
    });
    try { await notificationsApi.markRead(id); } catch { /* ignore */ }
  }, []);

  const markAllRead = useCallback(async () => {
    setState((s) => ({
      ...s,
      items: s.items.map((n) =>
        n.is_read ? n : { ...n, is_read: true, read_at: new Date().toISOString() },
      ),
      unread: 0,
    }));
    try { await notificationsApi.markAllRead(); } catch { /* ignore */ }
  }, []);

  const dismiss = useCallback(async (id: string) => {
    setState((s) => {
      const items = s.items.filter((n) => n.id !== id);
      const unread = items.filter((n) => !n.is_read).length;
      return { ...s, items, unread, total: Math.max(0, s.total - 1) };
    });
    try { await notificationsApi.dismiss(id); } catch { /* ignore */ }
  }, []);

  return { ...state, refresh, refreshCount, markRead, markAllRead, dismiss };
}
