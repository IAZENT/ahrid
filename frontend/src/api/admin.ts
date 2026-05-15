import { apiClient } from "./client";
import type { User } from "../types/api";

export interface ScenarioDto {
  id: string;
  title: string;
  content: string;
  question_type: string;
  category: string;
  difficulty: number;
  target_roles: string;
  correct_answer: string;
  option_a: string; option_b: string; option_c: string; option_d: string;
  explanation: string;
  red_flags: string | null;
  learning_tip: string | null;
  source: string;
  is_active: boolean;
  times_served: number;
  times_correct: number;
  accuracy_rate: number;
}

export interface ThreatRow {
  id: string;
  source: string;
  original_url: string;
  target_brand: string | null;
  category: string | null;
  lure_type: string | null;
  was_converted: boolean;
  ingested_at: string | null;
}

export interface AdminStats {
  totals: {
    users: number; active_users: number; scenarios: number; active_scenarios: number;
    threats_last_24h: number; attempts_last_24h: number;
  };
  ml_models: Record<string, { trained: boolean; last_trained: string | null; path: string | null }>;
  background_jobs: Record<string, unknown>;
  generated_at: string;
}

export interface PasswordResetRow {
  id: string;
  user_id: string;
  user_email?: string;
  user_username?: string;
  status: string;
  approved_at: string | null;
  token_expires_at: string | null;
  created_at: string | null;
}

export const adminApi = {
  async listUsers() {
    const { data } = await apiClient.get<{ users: User[]; total: number }>("/admin/users");
    return data;
  },
  async createUser(payload: {
    email: string; username: string; password: string;
    role: string; job_role?: string;
    first_name?: string; last_name?: string; department?: string;
  }) {
    const { data } = await apiClient.post<{ user: User }>("/admin/users", payload);
    return data;
  },
  async updateUser(userId: string, patch: Partial<User>) {
    const { data } = await apiClient.patch<{ user: User }>(`/admin/users/${userId}`, patch);
    return data;
  },

  async listScenarios(params?: { limit?: number; offset?: number; category?: string; source?: string }) {
    const { data } = await apiClient.get<{ scenarios: ScenarioDto[]; total: number }>(
      "/admin/scenarios", { params },
    );
    return data;
  },
  async createScenario(payload: Partial<ScenarioDto>) {
    const { data } = await apiClient.post<{ scenario: ScenarioDto }>("/admin/scenarios", payload);
    return data;
  },
  async updateScenario(id: string, patch: Partial<ScenarioDto>) {
    const { data } = await apiClient.patch<{ scenario: ScenarioDto }>(
      `/admin/scenarios/${id}`, patch,
    );
    return data;
  },

  async listThreats(params?: { limit?: number; source?: string; converted?: boolean }) {
    const { data } = await apiClient.get<{ threats: ThreatRow[]; total: number }>(
      "/admin/threats", { params },
    );
    return data;
  },
  async threatsBySource() {
    const { data } = await apiClient.get<{
      sources: Record<string, { total: number; converted: number; latest: string | null }>;
    }>("/admin/threats/sources");
    return data;
  },
  async runIngestion() {
    const { data } = await apiClient.post("/admin/threats/run-ingestion");
    return data;
  },

  async stats(): Promise<AdminStats> {
    const { data } = await apiClient.get<AdminStats>("/admin/stats");
    return data;
  },

  async triggerFeedIngestion() {
    const { data } = await apiClient.post("/admin/trigger-feed-ingestion");
    return data;
  },
  async ingestionStatus() {
    const { data } = await apiClient.get("/admin/ingestion-status");
    return data;
  },
  async retrainModels() {
    const { data } = await apiClient.post("/admin/retrain-models");
    return data;
  },
  async retrainStatus() {
    const { data } = await apiClient.get("/admin/retrain-status");
    return data;
  },

  async auditLog(params?: { limit?: number; offset?: number; action?: string }) {
    const { data } = await apiClient.get("/admin/audit-log", { params });
    return data;
  },

  async listPasswordResets(status: string = "pending") {
    const { data } = await apiClient.get<{ requests: PasswordResetRow[] }>(
      "/admin/password-resets", { params: { status } },
    );
    return data;
  },
  async approvePasswordReset(reqId: string) {
    const { data } = await apiClient.post<{ request: PasswordResetRow; reset_token: string }>(
      `/admin/password-resets/${reqId}/approve`,
    );
    return data;
  },
  async rejectPasswordReset(reqId: string) {
    const { data } = await apiClient.post(`/admin/password-resets/${reqId}/reject`);
    return data;
  },
};
