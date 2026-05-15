/** Evaluation API client (HAIS-Q awareness, SUS, RF metrics, transparency). */
import { apiClient } from "./client";

export interface AwarenessQuestion { id: string; text: string }
export interface ScalePoint        { value: number; label: string }
export interface AwarenessRow      {
  id: string; user_id: string; phase: "pre" | "post";
  responses: Record<string, number>; score: number; completed_at: string | null;
}
export interface AwarenessMe {
  pre: AwarenessRow | null;
  post: AwarenessRow | null;
  delta: number | null;
}
export interface SusRow {
  id: string; user_id: string;
  responses: Record<string, number>; sus_score: number; completed_at: string | null;
  grade?: string;
}
export interface RfMetrics {
  f1_weighted: number;
  baseline_f1: number;
  improvement_pp: number;
  n_test_samples: number;
  class_distribution: Record<string, number>;
  trained_at: string | null;
}
export interface AwarenessUplift {
  n_participants: number;
  mean_pre_score: number | null;
  mean_post_score: number | null;
  mean_delta: number | null;
  cohens_d: number | null;
  p_value: number | null;
  t_statistic?: number;
  participants: { user_id: string; pre: number; post: number; delta: number }[];
}
export interface SusSummary {
  n: number;
  mean: number | null;
  grade: string | null;
  distribution: Record<string, number>;
}

export const evalApi = {
  async awarenessQuestions() {
    const { data } = await apiClient.get<{
      questions: AwarenessQuestion[]; scale: ScalePoint[];
    }>("/eval/awareness/questions");
    return data;
  },
  async awarenessMe() {
    const { data } = await apiClient.get<AwarenessMe>("/eval/awareness/me");
    return data;
  },
  async submitAwareness(phase: "pre" | "post", responses: Record<string, number>) {
    const { data } = await apiClient.post<AwarenessRow>(
      "/eval/awareness", { phase, responses },
    );
    return data;
  },
  async susQuestions() {
    const { data } = await apiClient.get<{ questions: AwarenessQuestion[] }>(
      "/eval/sus/questions",
    );
    return data;
  },
  async submitSus(responses: Record<string, number>) {
    const { data } = await apiClient.post<SusRow>("/eval/sus", { responses });
    return data;
  },
  async rfMetrics() {
    const { data } = await apiClient.get<RfMetrics>("/eval/rf-metrics");
    return data;
  },
  async awarenessUplift() {
    const { data } = await apiClient.get<AwarenessUplift>("/eval/awareness-uplift");
    return data;
  },
  async susSummary() {
    const { data } = await apiClient.get<SusSummary>("/eval/sus-summary");
    return data;
  },
  async transparencyPolicy() {
    const { data } = await apiClient.get<{ policy: string }>(
      "/eval/transparency-policy",
    );
    return data;
  },
};
