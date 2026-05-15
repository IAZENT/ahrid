/**
 * Header bell that surfaces in-app notifications.
 *
 * Wires the previously orphaned `useNotifications` hook + `Toaster`
 * into the actual UI: shows unread count, opens a dropdown listing
 * recent notifications, and lets the user mark them read or dismiss.
 */
import { Bell, Check, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useNotifications } from "../../hooks/useNotifications";
import { cn } from "../../lib/utils";

const SEVERITY_COLOUR: Record<string, string> = {
  info: "text-text-secondary",
  success: "text-success",
  warning: "text-warning",
  critical: "text-risk-critical",
};

export function NotificationBell() {
  const { items, unread, markRead, markAllRead, dismiss } = useNotifications();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const ref = useRef<HTMLDivElement | null>(null);

  // Close when clicking outside.
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label="Notifications"
        className="relative flex h-9 w-9 items-center justify-center rounded-md text-text-muted transition-colors hover:bg-bg-elevated hover:text-text-primary"
      >
        <Bell className="h-4 w-4" />
        {unread > 0 && (
          <span className="absolute right-1 top-1 inline-flex min-w-[16px] items-center justify-center rounded-full bg-risk-critical px-1 text-[9px] font-semibold text-white">
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-2 w-80 origin-top-right animate-scale-in rounded-md border border-border-subtle bg-bg-elevated shadow-elevated">
          <div className="flex items-center justify-between border-b border-border-subtle px-3 py-2 text-xs">
            <span className="font-semibold text-text-primary">Notifications</span>
            {items.some((n) => !n.is_read) && (
              <button
                onClick={() => void markAllRead()}
                className="text-text-muted hover:text-text-primary"
              >
                Mark all read
              </button>
            )}
          </div>
          <ul className="max-h-80 overflow-y-auto divide-y divide-border-subtle">
            {items.length === 0 && (
              <li className="px-3 py-6 text-center text-xs text-text-muted">
                You're all caught up.
              </li>
            )}
            {items.map((n) => (
              <li
                key={n.id}
                className={cn(
                  "group relative flex items-start gap-2 px-3 py-2 text-xs",
                  !n.is_read && "bg-bg-overlay/40",
                )}
              >
                <span
                  className={cn(
                    "mt-1 inline-block h-1.5 w-1.5 shrink-0 rounded-full",
                    SEVERITY_COLOUR[n.severity] ?? "text-text-muted",
                    !n.is_read ? "bg-current" : "bg-transparent",
                  )}
                />
                <button
                  type="button"
                  onClick={() => {
                    void markRead(n.id);
                    if (n.link) {
                      setOpen(false);
                      navigate(n.link);
                    }
                  }}
                  className="flex-1 text-left"
                >
                  <div className="font-medium text-text-primary">{n.title}</div>
                  {n.body && (
                    <div className="mt-0.5 text-text-secondary line-clamp-2">{n.body}</div>
                  )}
                </button>
                <div className="flex flex-col gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                  {!n.is_read && (
                    <button
                      onClick={() => void markRead(n.id)}
                      aria-label="Mark read"
                      className="rounded p-0.5 text-text-muted hover:text-text-primary"
                    >
                      <Check className="h-3 w-3" />
                    </button>
                  )}
                  <button
                    onClick={() => void dismiss(n.id)}
                    aria-label="Dismiss"
                    className="rounded p-0.5 text-text-muted hover:text-risk-critical"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
