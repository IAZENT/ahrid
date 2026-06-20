import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { User } from "../types/api";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setSession: (params: {
    accessToken: string;
    refreshToken?: string;
    user: User;
  }) => void;
  updateUser: (patch: Partial<User>) => void;
  clear: () => void;
}

const REFRESH_STORAGE_KEY = "ahrip_rt";
const USER_STORAGE_KEY = "ahrip_user";

function readPersisted(): { refreshToken: string | null; user: User | null } {
  if (typeof window === "undefined") return { refreshToken: null, user: null };
  try {
    const rt = window.localStorage.getItem(REFRESH_STORAGE_KEY);
    const raw = window.localStorage.getItem(USER_STORAGE_KEY);
    const user = raw ? (JSON.parse(raw) as User) : null;
    return { refreshToken: rt, user };
  } catch {
    return { refreshToken: null, user: null };
  }
}

function writePersisted(refreshToken: string | null, user: User | null) {
  if (typeof window === "undefined") return;
  if (refreshToken) window.localStorage.setItem(REFRESH_STORAGE_KEY, refreshToken);
  else window.localStorage.removeItem(REFRESH_STORAGE_KEY);
  if (user) window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  else window.localStorage.removeItem(USER_STORAGE_KEY);
}

const bootstrap = readPersisted();

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: bootstrap.refreshToken,
      user: bootstrap.user,
      setSession: ({ accessToken, refreshToken, user }) => {
        const nextRefresh = refreshToken ?? get().refreshToken;
        set({ accessToken, refreshToken: nextRefresh, user });
        writePersisted(nextRefresh, user);
      },
      updateUser: (patch) => {
        const u = get().user;
        if (!u) return;
        const next = { ...u, ...patch };
        set({ user: next });
        writePersisted(get().refreshToken, next);
      },
      clear: () => {
        set({ accessToken: null, refreshToken: null, user: null });
        writePersisted(null, null);
      },
    }),
    {
      name: "ahrip-auth-session",
      storage: createJSONStorage(() => ({
        getItem: () => null,
        setItem: () => undefined,
        removeItem: () => undefined,
      })),
      partialize: () => ({}),
    },
  ),
);
