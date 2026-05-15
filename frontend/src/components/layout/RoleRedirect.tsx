import { Navigate } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";
import { defaultLandingForRole } from "../../lib/routing";

export function RoleRedirect({ fallback = "/login" }: { fallback?: string }) {
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.accessToken);
  if (!user || !token) return <Navigate to={fallback} replace />;
  return <Navigate to={defaultLandingForRole(user.role)} replace />;
}
