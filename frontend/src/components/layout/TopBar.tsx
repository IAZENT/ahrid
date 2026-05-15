import { Menu, User as UserIcon, LogOut } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../../api/auth";
import { useAuthStore } from "../../store/authStore";
import { cn } from "../../lib/utils";
import { NotificationBell } from "./NotificationBell";

interface TopBarProps {
  title: string;
  onToggleSidebar?: () => void;
}

export function TopBar({ title, onToggleSidebar }: TopBarProps) {
  const user = useAuthStore((s) => s.user);
  const clear = useAuthStore((s) => s.clear);
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const goTo = (path: string) => {
    setMenuOpen(false);
    navigate(path);
  };

  const handleSignOut = async () => {
    try { await authApi.logout(); } catch { /* ignore */ }
    clear();
    navigate("/login");
  };

  const initials = user?.first_name
    ? `${user.first_name.charAt(0)}${(user.last_name ?? "").charAt(0)}`.toUpperCase()
    : "??";

  return (
    <header className="relative z-40 flex h-14 items-center justify-between gap-4 border-b border-border-subtle bg-bg-surface/60 px-4 backdrop-blur-sm md:px-6">
      <div className="flex min-w-0 items-center gap-3">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            aria-label="Toggle sidebar"
            className="rounded-md p-2 text-text-muted hover:bg-bg-elevated hover:text-text-primary transition-colors md:hidden"
          >
            <Menu className="h-4 w-4" />
          </button>
        )}
        <div className="min-w-0 leading-tight">
          <h1 className="truncate text-md font-semibold text-text-primary">{title}</h1>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <NotificationBell />
        <div className="relative">
          <button
            onClick={() => setMenuOpen((v) => !v)}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-accent-muted text-xs font-semibold text-accent transition-colors hover:brightness-110"
          >
            {initials}
          </button>
          {menuOpen && (
            <div
              className={cn(
                "absolute right-0 mt-2 w-52 rounded-md border border-border-subtle bg-bg-elevated py-1 shadow-elevated",
                "animate-scale-in origin-top-right",
              )}
              onMouseLeave={() => setMenuOpen(false)}
            >
              <div className="px-3 py-2 text-[11px] leading-tight">
                <div className="truncate font-medium text-text-primary">
                  {user ? `${user.first_name ?? ""} ${user.last_name ?? ""}`.trim() || user.email : "Guest"}
                </div>
                {user?.email && (
                  <div className="truncate text-[10px] text-text-muted">{user.email}</div>
                )}
              </div>
              <div className="my-1 border-t border-border-subtle" />
              <button
                onClick={() => goTo("/app/profile")}
                className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs text-text-primary transition-colors hover:bg-bg-overlay"
              >
                <UserIcon className="h-3.5 w-3.5" />
                <span>Profile</span>
              </button>
              <div className="my-1 border-t border-border-subtle" />
              <button
                onClick={handleSignOut}
                className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs text-risk-critical transition-colors hover:bg-risk-critical/10"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Sign out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
