import { useEffect, useState } from "react";
import { refreshAccessToken } from "../api/auth";
import { useAuthStore } from "../store/authStore";

/**
 * On mount, if we have a persisted refresh token but no access token in
 * memory (typical hard reload), redeem the refresh token for a fresh
 * access token before rendering the protected app shell. Returns true
 * once the bootstrap attempt has settled (success OR failure).
 */
export function useSessionBootstrap(): boolean {
  const accessToken = useAuthStore((s) => s.accessToken);
  const refreshToken = useAuthStore((s) => s.refreshToken);
  const user = useAuthStore((s) => s.user);
  const setSession = useAuthStore((s) => s.setSession);
  const clear = useAuthStore((s) => s.clear);
  const [ready, setReady] = useState(!refreshToken || Boolean(accessToken));

  useEffect(() => {
    if (ready) return;
    if (!refreshToken || !user) {
      setReady(true);
      return;
    }
    let cancelled = false;
    void (async () => {
      const newAccess = await refreshAccessToken(refreshToken);
      if (cancelled) return;
      if (newAccess) {
        setSession({ accessToken: newAccess, refreshToken, user });
      } else {
        clear();
      }
      setReady(true);
    })();
    return () => { cancelled = true; };
  }, [ready, refreshToken, user, setSession, clear]);

  return ready;
}
