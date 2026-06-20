import axios from "axios";
import { apiClient } from "./client";
import type { User } from "../types/api";

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export async function refreshAccessToken(
  refreshToken: string,
): Promise<string | null> {
  try {
    const baseURL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000")
      .replace(/\/$/, "") + "/api/v1";
    const res = await axios.post<{ access_token: string }>(
      `${baseURL}/auth/refresh`,
      {},
      { headers: { Authorization: `Bearer ${refreshToken}` }, timeout: 10_000 },
    );
    return res.data.access_token ?? null;
  } catch {
    return null;
  }
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  job_role?: string;
  department?: string;
}

export const authApi = {
  async login(identifier: string, password: string): Promise<LoginResponse> {
    const { data } = await apiClient.post<LoginResponse>("/auth/login", {
      identifier, password,
    });
    return data;
  },

  async register(payload: RegisterPayload): Promise<LoginResponse> {
    const { data } = await apiClient.post<LoginResponse>("/auth/register", payload);
    return data;
  },

  async me(): Promise<User & { cluster_label: string | null }> {
    const { data } = await apiClient.get("/auth/me");
    return data;
  },

  async logout(): Promise<void> {
    await apiClient.post("/auth/logout");
  },

  async updateProfile(
    patch: Partial<Pick<User, "first_name" | "last_name" | "username" | "department" | "job_role">>,
  ): Promise<{ user: User; updated: string[] }> {
    const { data } = await apiClient.patch<{ user: User; updated: string[] }>(
      "/auth/me", patch,
    );
    return data;
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  async forgotPassword(identifier: string): Promise<{ status: string }> {
    const { data } = await apiClient.post<{ status: string }>(
      "/auth/forgot-password", { identifier },
    );
    return data;
  },

  async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiClient.post("/auth/reset-password", {
      token,
      new_password: newPassword,
    });
  },

  async completeTour(): Promise<void> {
    await apiClient.post("/auth/complete-tour");
  },
};
