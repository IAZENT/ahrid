import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiErrorMessage } from "../api/client";
import { authApi } from "../api/auth";
import { useAuthStore } from "../store/authStore";

export function useAuth() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.accessToken);
  const setSession = useAuthStore((s) => s.setSession);
  const clear = useAuthStore((s) => s.clear);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(
    async (identifier: string, password: string): Promise<boolean> => {
      setLoading(true);
      setError(null);
      try {
        const res = await authApi.login(identifier, password);
        setSession({
          accessToken: res.access_token,
          refreshToken: res.refresh_token,
          user: res.user,
        });
        return true;
      } catch (err) {
        setError(apiErrorMessage(err, "Unable to sign in"));
        return false;
      } finally {
        setLoading(false);
      }
    },
    [setSession],
  );

  const logout = useCallback(async () => {
    try {
      if (token) await authApi.logout();
    } catch { /* ignore */ }
    finally {
      clear();
      navigate("/login", { replace: true });
    }
  }, [clear, navigate, token]);

  return {
    user,
    isAuthenticated: Boolean(user && token),
    loading,
    error,
    login,
    logout,
  };
}
