import { apiClient } from "./client";
import type { ScenarioPublic } from "../types/api";

export interface SessionStartResponse {
  session_id: string;
  scenarios: ScenarioPublic[];
  selection_meta: Record<string, unknown>;
}

export interface AnswerResponse {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  red_flags: string | null;
  learning_tip: string | null;
  mastery_update: { category: string; mastery: number };
  question_type: string;
}

export interface SessionSummary {
  session_id: string;
  total_questions: number;
  correct?: number;
  accuracy?: number;
  duration_seconds?: number;
  categories_covered?: string[];
  strongest_category_this_session?: string | null;
  weakest_category_this_session?: string | null;
  improvement_tips?: string[];
}

export interface AttemptDto {
  id: string;
  scenario_id: string;
  is_correct: boolean;
  response_time_ms: number | null;
  category: string;
  difficulty: number;
  session_id: string | null;
  created_at: string | null;
}

export interface SessionRow {
  session_id: string;
  started_at: string | null;
  ended_at: string | null;
  duration_seconds: number;
  total_questions: number;
  correct: number;
  accuracy: number;
  categories: { category: string; total: number; correct: number }[];
}

export interface CategoryDto {
  id: string;
  name: string;
  display_name: string;
  icon: string;
  description: string;
}

export interface TrainingConfig {
  quick_size: number;
  full_size: number;
  explanation_duration_seconds: number;
}

export const trainingApi = {
  async startSession(numQuestions?: number): Promise<SessionStartResponse> {
    const params: Record<string, string> = {};
    if (numQuestions) params.num_questions = String(numQuestions);
    const { data } = await apiClient.get<SessionStartResponse>("/training/session/start", { params });
    return data;
  },
  async submitAnswer(
    sessionId: string,
    payload: {
      scenario_id: string;
      answer: string;
      response_time_ms: number;
      presentation_token?: string;
    },
  ): Promise<AnswerResponse> {
    const { data } = await apiClient.post<AnswerResponse>(
      `/training/session/${sessionId}/answer`, payload,
    );
    return data;
  },
  async sessionSummary(sessionId: string): Promise<SessionSummary> {
    const { data } = await apiClient.get<SessionSummary>(
      `/training/session/${sessionId}/summary`,
    );
    return data;
  },
  async sessionDetail(sessionId: string) {
    const { data } = await apiClient.get(`/training/session/${sessionId}/detail`);
    return data;
  },
  async history(params?: { limit?: number; offset?: number; category?: string }) {
    const { data } = await apiClient.get<{
      attempts: AttemptDto[]; total: number; limit: number; offset: number;
    }>("/training/history", { params });
    return data;
  },
  async sessions(params?: { limit?: number; offset?: number }) {
    const { data } = await apiClient.get<{
      sessions: SessionRow[]; total: number; limit: number; offset: number;
    }>("/training/sessions", { params });
    return data;
  },
  async categories(): Promise<CategoryDto[]> {
    const { data } = await apiClient.get<CategoryDto[]>("/training/categories");
    return data;
  },
  async config(): Promise<TrainingConfig> {
    const { data } = await apiClient.get<TrainingConfig>("/training/config");
    return data;
  },
  async insights(): Promise<{ mistakes: unknown }> {
    const { data } = await apiClient.get("/training/insights");
    return data;
  },
};
