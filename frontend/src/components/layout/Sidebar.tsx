import {
  BarChart, ClipboardList, FileText, History, KeyRound, LayoutDashboard, LogOut,
  Rss, ScrollText, Settings, Shield, Target, TrendingUp, Users, Award,
  type LucideIcon,
} from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { authApi } from "../../api/auth";
import { useAuthStore } from "../../store/authStore";
import type { UserRole } from "../../types/api";
import { cn } from "../../lib/utils";

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  roles?: UserRole[];
  tourKey?: string;
}

interface NavSection {
  id: string;
  label: string;
  roles?: UserRole[];
  items: NavItem[];
}

const SECTIONS: NavSection[] = [
  {
    id: "learn",
    label: "Learn",
    items: [
      { to: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard, tourKey: "tour-nav-dashboard" },
      { to: "/app/training", label: "Training", icon: Target, tourKey: "tour-nav-training" },
    ],
  },
  {
    id: "progress",
    label: "Progress",
    items: [
      { to: "/app/my-score", label: "My Score", icon: TrendingUp, tourKey: "tour-nav-my-score" },
      { to: "/app/history", label: "Session History", icon: History },
      { to: "/app/evaluation", label: "Evaluation", icon: ClipboardList },
      { to: "/app/transparency", label: "Transparency", icon: ScrollText },
    ],
  },
  {
    id: "team",
    label: "Team",
    roles: ["manager", "admin"],
    items: [
      { to: "/app/manager/dashboard", label: "Overview", icon: BarChart },
      { to: "/app/manager/team", label: "Team", icon: Users },
      { to: "/app/manager/clusters", label: "Clusters", icon: Award },
      { to: "/app/manager/reports", label: "Reports", icon: FileText },
    ],
  },
  {
    id: "admin",
    label: "Admin",
    roles: ["admin"],
    items: [
      { to: "/app/admin", label: "Admin Panel", icon: Settings },
      { to: "/app/admin/users", label: "Users", icon: Users },
      { to: "/app/admin/scenarios", label: "Scenarios", icon: FileText },
      { to: "/app/admin/threats", label: "Threat Feeds", icon: Rss },
      { to: "/app/admin/password-resets", label: "Password Resets", icon: KeyRound },
      { to: "/app/admin/evaluation", label: "Evaluation", icon: ClipboardList },
    ],
  },
];

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const user = useAuthStore((s) => s.user);
  const clear = useAuthStore((s) => s.clear);
  const navigate = useNavigate();
  const role = user?.role ?? "employee";

  const initials = user?.first_name
    ? `${user.first_name.charAt(0)}${(user.last_name ?? "").charAt(0)}`.toUpperCase()
    : "??";

  const signOut = async () => {
    try { await authApi.logout(); } catch { /* ignore */ }
    clear();
    navigate("/login", { replace: true });
  };

  return (
    <aside className="flex h-full w-60 flex-col border-r border-border-subtle bg-bg-overlay">
      <div className="flex items-center gap-2 px-5 py-5" data-tour="tour-sidebar-brand">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-accent/15 text-accent">
          <Shield className="h-4 w-4" />
        </div>
        <div className="leading-tight">
          <div className="text-md font-bold tracking-tight text-accent">AHRIP</div>
          <div className="text-2xs text-text-muted">Human Risk Intel</div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 pb-3">
        {SECTIONS.filter((s) => !s.roles || s.roles.includes(role)).map((section) => (
          <div key={section.id} className="mb-5">
            <div className="mb-1.5 px-2 text-[10px] font-semibold uppercase tracking-wider text-text-muted">
              {section.label}
            </div>
            <ul className="space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon;
                return (
                  <li key={item.to}>
                    <NavLink
                      to={item.to}
                      onClick={onNavigate}
                      {...(item.tourKey ? { "data-tour": item.tourKey } : {})}
                      className={({ isActive }) =>
                        cn(
                          "group flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm font-medium transition-colors duration-150",
                          isActive
                            ? "bg-bg-elevated text-text-primary border-l-2 border-accent pl-[10px]"
                            : "text-text-secondary hover:bg-bg-elevated hover:text-text-primary",
                        )
                      }
                    >
                      <Icon className="h-4 w-4" />
                      <span className="flex-1">{item.label}</span>
                    </NavLink>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      <div className="border-t border-border-subtle p-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent-muted text-xs font-semibold text-accent">
            {initials}
          </div>
          <div className="flex-1 overflow-hidden leading-tight">
            <div className="truncate text-xs font-medium text-text-primary">
              {user ? `${user.first_name ?? "User"} ${user.last_name ?? ""}`.trim() : "Not signed in"}
            </div>
            <div className="truncate text-[10px] uppercase tracking-wide text-text-muted">
              {role}
            </div>
          </div>
          <button
            onClick={signOut}
            aria-label="Sign out"
            className="rounded-md p-1.5 text-text-muted hover:bg-bg-elevated hover:text-text-primary transition-colors"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
