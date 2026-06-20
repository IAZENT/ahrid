"""SHAP explainability for the Random Forest risk classifier.

Produces per-user, plain-language feature explanations. Called after
RF prediction; the returned dict is persisted in
``RiskScore.shap_summary`` (JSON column).

Master spec §5. Designed to be **defensive**: any failure inside SHAP
returns a structured error rather than crashing the request that
triggered the recompute.
"""
from __future__ import annotations

import logging
from typing import Iterable

import numpy as np

LOG = logging.getLogger(__name__)

# Human-readable labels for each of the 14 RF features. Keys must match
# the FEATURE_NAMES list in random_forest_model.py exactly.
FEATURE_LABELS: dict[str, str] = {
    "avg_response_time_ms":        "How quickly you answer questions",
    "phishing_accuracy":           "Phishing email detection accuracy",
    "smishing_accuracy":           "SMS phishing detection accuracy",
    "social_engineering_accuracy": "Social engineering resistance",
    "password_hygiene_accuracy":   "Password hygiene knowledge",
    "physical_security_accuracy":  "Physical security awareness",
    "overall_accuracy":            "Overall quiz accuracy",
    "fast_attempt_rate":           "Proportion of rushed answers",
    "overconfident_rate":          "Proportion of overconfident answers",
    "session_consistency":         "Consistency across training sessions",
    "job_role_encoded":            "Job role",
    "total_sessions":              "Total training sessions completed",
    "days_since_last_session":     "Days since you last trained",
    "attempts_count":              "Total training attempts",
}


def explain_prediction(
    feature_vector: np.ndarray,
    feature_names: Iterable[str],
) -> dict:
    """Return a SHAP explanation dict for ``feature_vector``.

    Result shape::

        {
          "shap_values": [{feature, label, shap_value, direction}, ...],
          "top_risk_factors":       ["...", "...", "..."],
          "top_protective_factors": ["...", "...", "..."],
          "predicted_class_index":  int,
        }

    On any failure, returns ``{"error": "..."}``  the caller persists
    that as-is so the UI can degrade gracefully.
    """
    try:
        import shap  # local import  keeps cold-path imports off boot
        from app.services.random_forest_model import RiskForestPredictor

        predictor = RiskForestPredictor()
        if not predictor.is_ready or predictor.model is None:
            return {"error": "rf_not_ready"}

        names = list(feature_names)
        x = np.asarray(feature_vector, dtype=float).reshape(1, -1)

        explainer = shap.TreeExplainer(predictor.model)
        raw = explainer.shap_values(x, check_additivity=False)

        # ``raw`` shape varies by sklearn / shap version. We normalise
        # to a 1-D array of length n_features for the predicted class.
        predicted_class_idx = int(predictor.model.predict(x)[0])
        if isinstance(raw, list):
            class_shap = np.asarray(raw[predicted_class_idx])[0]
        else:
            arr = np.asarray(raw)
            if arr.ndim == 3:
                # (n_samples, n_features, n_classes)
                class_shap = arr[0, :, predicted_class_idx]
            elif arr.ndim == 2:
                class_shap = arr[0]
            else:
                class_shap = arr.reshape(-1)

        results: list[dict] = []
        for i, fname in enumerate(names):
            val = float(class_shap[i])
            results.append({
                "feature": fname,
                "label": FEATURE_LABELS.get(fname, fname.replace("_", " ").title()),
                "shap_value": round(val, 4),
                "direction": "increases_risk" if val > 0 else "reduces_risk",
            })
        results.sort(key=lambda r: abs(r["shap_value"]), reverse=True)

        risk_factors = [
            f"{r['label']} is contributing to your elevated risk."
            for r in results if r["direction"] == "increases_risk" and abs(r["shap_value"]) > 1e-4
        ][:3]
        protective_factors = [
            f"{r['label']} is helping keep your risk low."
            for r in results if r["direction"] == "reduces_risk" and abs(r["shap_value"]) > 1e-4
        ][:3]

        return {
            "shap_values": results,
            "top_risk_factors": risk_factors,
            "top_protective_factors": protective_factors,
            "predicted_class_index": predicted_class_idx,
        }
    except Exception as exc:  # pragma: no cover  defensive
        LOG.exception("SHAP explanation failed")
        return {"error": f"{type(exc).__name__}: {exc}"}
