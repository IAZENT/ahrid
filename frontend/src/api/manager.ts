import { apiClient } from "./client";

export interface KpiCards {
  avg_score: number;
  critical_count: number;
  weekly_scenarios: number;
  trend_direction: "improving" | "stable" | "declining";
  trend_percent: number;
}

export interface TopRiskRow {
  user_id: string;
  risk_level: string;
  archetype: string | null;
  weakest_category: string;
}

export interface ClusterSummaryArchetype {
  cluster_id: number;
  label: string;
  count: number;
  percentage: number;
  colour: string;
  icon: string;
  intervention: string;
}

export interface ClusterSummary {
  archetypes: ClusterSummaryArchetype[];
  most_common_archetype: string | null;
  highest_risk_archetype_count: number;
  intervention_required: string[];
}

export interface DashboardResponse {
  kpi_cards: KpiCards;
  top_risk: TopRiskRow[];
  cluster_summary: ClusterSummary;
  threat_feed_status: { last_update: string | null; new_scenarios_this_week: number };
  org_category_weakness: { category: string; avg_score: number }[];
}

export interface TeamRow {
  user_id: string;
  job_role: string | null;
  department: string | null;
  risk_level: string;
  cluster_label: string | null;
  archetype_colour: string | null;
  archetype_icon: string | null;
  weakest_category: string | null;
  last_active: string | null;
  sessions_this_week: number;
}

export interface HistoryBucket {
  week_start: string;
  week_end: string;
  avg_accuracy: number | null;
  proxy_risk: number | null;
  attempts: number;
}

export const managerApi = {
  async dashboard(): Promise<DashboardResponse> {
    const { data } = await apiClient.get<DashboardResponse>("/manager/dashboard");
    return data;
  },
  async team(params?: { archetype?: string; dept?: string; sort?: string }) {
    const { data } = await apiClient.get<{ team: TeamRow[]; total: number }>(
      "/manager/team", { params },
    );
    return data;
  },
  async memberProfile(userId: string) {
    const { data } = await apiClient.get(`/manager/team/${userId}/profile`);
    return data;
  },
  async assignTraining(userId: string, payload: { categories: string[]; note?: string }) {
    const { data } = await apiClient.post(
      `/manager/team/${userId}/assign-training`, payload,
    );
    return data;
  },
  async history(weeks = 8): Promise<HistoryBucket[]> {
    const { data } = await apiClient.get<{ history: HistoryBucket[] }>(
      "/manager/history", { params: { weeks } },
    );
    return data.history;
  },
};
