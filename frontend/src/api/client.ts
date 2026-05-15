import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import { useAuthStore } from "../store/authStore";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000";

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${BASE_URL.replace(/\/$/, "")}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 10_000,
});

// ── Request: inject bearer token ─────────────────────────────────
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers = config.headers ?? {};
    (config.headers as Record<string, string>).Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response: on 401, attempt a single silent refresh before giving up. ──
// This fixes the "logged out after a few minutes" bug  the access token
// lives 15 min in memory, so once it expires any API call would bounce the
// user to /login. Instead we swap in a fresh access token using the
// persisted refresh token and retry the failing request.
let refreshInflight: Promise<string | null> | null = null;

async function performRefresh(): Promise<string | null> {
  const { refreshToken } = useAuthStore.getState();
  if (!refreshToken) return null;
  if (!refreshInflight) {
    // Lazy import to avoid a circular dep with auth.ts
    const { refreshAccessToken } = await import("./auth");
    refreshInflight = refreshAccessToken(refreshToken).finally(() => {
      refreshInflight = null;
    });
  }
  return refreshInflight;
}

apiClient.interceptors.response.use(
  (res) => res,
  async (err: AxiosError) => {
    const status = err.response?.status;
    const original = err.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean; url?: string })
      | undefined;

    // Never retry the refresh endpoint itself, and never retry twice.
    const isRefreshCall = original?.url?.includes("/auth/refresh");
    const canRetry = status === 401 && original && !original._retry && !isRefreshCall;

    if (canRetry) {
      const newAccess = await performRefresh();
      if (newAccess) {
        const store = useAuthStore.getState();
        store.setSession({
          accessToken: newAccess,
          refreshToken: store.refreshToken ?? undefined,
          user: store.user!, // user exists if refreshToken exists (set together)
        });
        original._retry = true;
        original.headers = original.headers ?? {};
        (original.headers as Record<string, string>).Authorization = `Bearer ${newAccess}`;
        return apiClient(original);
      }
      // Refresh failed → full sign-out so ProtectedRoute bounces user.
      useAuthStore.getState().clear();
    } else if (status === 401 && !isRefreshCall) {
      // No refresh token or already retried  clear if we thought we were signed in.
      const { accessToken, clear } = useAuthStore.getState();
      if (accessToken) clear();
    }
    return Promise.reject(err);
  },
);

/** Normalise the backend's `{error, message?, details?}` shape into a string. */
export function apiErrorMessage(err: unknown, fallback = "Something went wrong"): string {
  const ax = err as AxiosError<{ error?: string; message?: string; details?: unknown }>;
  const body = ax?.response?.data;

  // Marshmallow validation errors come back as
  //   { error: "validation_failed", details: { field: ["msg", ...], ... } }
  // Surface the first field message so the user knows *what* is invalid.
  if (body?.error === "validation_failed" && body.details && typeof body.details === "object") {
    const details = body.details as Record<string, unknown>;
    for (const [field, msgs] of Object.entries(details)) {
      const msg = Array.isArray(msgs) ? msgs[0] : msgs;
      if (typeof msg === "string" && msg.trim()) {
        const label = field.replace(/_/g, " ");
        // If the message already mentions the field, don't prefix.
        return msg.toLowerCase().includes(label) ? msg : `${label}: ${msg}`;
      }
    }
  }

  if (body?.message) return body.message;
  if (typeof body?.error === "string") {
    return body.error.replace(/_/g, " ");
  }
  if (ax?.message) return ax.message;
  return fallback;
}
