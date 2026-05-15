import { apiClient } from "./client";
import type { RiskScoreDto } from "../types/api";

export interface HistoryBucket {
  week_start: string;
  week_end: string;
  accuracy: number | null;
  composite_score: number | null;
  attempt_count: number;
}

export interface ClusterResponse {
  cluster_id: number | null;
  archetype_label: string | null;
  archetype_description?: string;
  archetype_colour?: string;
  archetype_icon?: string;
  intervention?: string;
  assigned_at?: string | null;
  message?: string;
}

export const scoresApi = {
  async me(): Promise<RiskScoreDto | { risk_level: "unknown"; message: string }> {
    const { data } = await apiClient.get("/scores/me");
    return data;
  },
  async history(): Promise<HistoryBucket[]> {
    const { data } = await apiClient.get<{ history: HistoryBucket[] }>("/scores/me/history");
    return data.history;
  },
  async cluster(): Promise<ClusterResponse> {
    const { data } = await apiClient.get<ClusterResponse>("/scores/me/cluster");
    return data;
  },
};
