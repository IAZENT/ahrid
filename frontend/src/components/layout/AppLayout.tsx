import { Outlet, useLocation } from "react-router-dom";
import { useMemo } from "react";
import { AppShell } from "./AppShell";

const ROUTE_TITLES: Array<{ match: RegExp; title: string }> = [
  { match: /\/app\/training/, title: "Training" },
  { match: /\/app\/my-score/, title: "My Score" },
  { match: /\/app\/history/, title: "Session History" },
  { match: /\/app\/profile/, title: "Profile" },
  { match: /\/app\/dashboard/, title: "Dashboard" },
  { match: /\/app\/manager/, title: "Team Intelligence" },
  { match: /\/app\/admin/, title: "Admin" },
];

export function AppLayout() {
  const location = useLocation();
  const title = useMemo(() => {
    const hit = ROUTE_TITLES.find((t) => t.match.test(location.pathname));
    return hit?.title ?? "AHRID";
  }, [location.pathname]);

  return (
    <AppShell title={title}>
      <Outlet />
    </AppShell>
  );
}
