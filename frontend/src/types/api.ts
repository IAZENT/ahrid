import type { CategoryId } from "../lib/categories";

export type RiskLevel = "critical" | "high" | "medium" | "low" | "unknown";
export type UserRole = "employee" | "manager" | "admin";

export interface User {
  id: string;
  email: string;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  role: UserRole;
  job_role: string | null;
  department: string | null;
  cluster_label: string | null;
  is_active: boolean;
  is_verified: boolean;
  consent_given: boolean;
  created_at: string | null;
  last_login: string | null;
}

export type QuestionType = "mcq" | "true_false" | "identify_threat";

export interface ScenarioPublic {
  id: string;
  title: string;
  content: string;
  visual_html?: string | null;
  visual_type?: string | null;
  question_type: QuestionType;
  category: CategoryId | string;
  difficulty: 1 | 2 | 3;
  options: { A: string; B: string; C: string; D: string };
  tf_statement?: string | null;
  /** HMAC-signed token issued at session start. Echo back with the answer. */
  presentation_token?: string;
}

export interface RiskScoreDto {
  composite_score: number;
  category_scores: Record<string, number>;
  risk_level: RiskLevel;
  rf_predicted_risk: number | null;
  rf_confidence: number | null;
  attempts_count?: number;
  calculated_at: string | null;
  rf_prediction: null | {
    predicted_risk_level: RiskLevel;
    confidence: number;
    feature_importances: Record<string, number>;
  };
  cluster_label: string | null;
  /** SHAP per-feature contributions cached from the most recent RF prediction. */
  shap_explanation?: null | {
    shap_values?: {
      feature: string;
      label: string;
      shap_value: number;
      direction: "increases_risk" | "reduces_risk";
    }[];
    top_risk_factors?: string[];
    top_protective_factors?: string[];
    predicted_class_index?: number;
    error?: string;
  };
}

export type NotificationType = "training_assigned" | "risk_escalation";
export type NotificationSeverity = "info" | "success" | "warning" | "critical";

export interface NotificationDto {
  id: string;
  type: NotificationType;
  severity: NotificationSeverity;
  title: string;
  body: string | null;
  link: string | null;
  meta: Record<string, unknown>;
  read_at: string | null;
  is_read: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  items: NotificationDto[];
  total: number;
  unread: number;
  limit: number;
  offset: number;
}
