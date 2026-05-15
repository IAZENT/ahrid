"""Composite + per-category risk scoring for a user.

Risk is the inverse of mastery: 0% mastery → 100 risk. We compute one row in
``risk_scores`` per user, refreshed when ``recalculate_for_user`` runs (called
synchronously after each attempt today; switched to async via the scheduler in
production).
"""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from app.extensions import db
from app.models.attempt import Attempt
from app.models.risk_score import RiskScore
from app.models.scenario import CATEGORIES

# Thresholds for the composite risk_level bucket --------------------------------
LEVEL_THRESHOLDS = (
    (80.0, "critical"),
    (60.0, "high"),
    (40.0, "medium"),
    (0.0, "low"),
)


def _category_score(attempts: Iterable[Attempt]) -> float:
    """Return risk for one category in [0, 100]: 100 = always wrong, 0 = always right."""
    attempts = list(attempts)
    if not attempts:
        return 0.0  # no signal → no risk recorded yet (use unknown bucket)
    accuracy = sum(1 for a in attempts if a.is_correct) / len(attempts)
    return round((1.0 - accuracy) * 100.0, 2)


def _level_for(score: float, attempts_count: int) -> str:
    if attempts_count == 0:
        return "unknown"
    for threshold, label in LEVEL_THRESHOLDS:
        if score >= threshold:
            return label
    return "low"


def recalculate_for_user(user_id) -> RiskScore:
    """Idempotent: returns the user's freshly computed RiskScore row.
    
    Excludes synthetic attempts from scoring — only real user attempts count.
    """
    cat_attempts: dict[str, list[Attempt]] = {c: [] for c in CATEGORIES}
    rows = (
        Attempt.query.filter_by(user_id=user_id, is_synthetic=False)
        .order_by(Attempt.created_at.desc())
        .all()
    )
    for a in rows:
        if a.category in cat_attempts:
            cat_attempts[a.category].append(a)

    cat_scores = {c: _category_score(cat_attempts[c]) for c in CATEGORIES}
    seen_categories = [c for c, atts in cat_attempts.items() if atts]
    composite = (
        round(sum(cat_scores[c] for c in seen_categories) / len(seen_categories), 2)
        if seen_categories
        else 0.0
    )
    risk_level = _level_for(composite, len(rows))

    risk = RiskScore.query.filter_by(user_id=user_id).first()
    if risk is None:
        risk = RiskScore(user_id=user_id)
        db.session.add(risk)

    risk.composite_score = composite
    risk.phishing_email_score = cat_scores["phishing_email"]
    risk.smishing_score = cat_scores["smishing"]
    risk.vishing_score = cat_scores["vishing"]
    risk.physical_security_score = cat_scores["physical_security"]
    risk.password_hygiene_score = cat_scores["password_hygiene"]
    risk.usb_baiting_score = cat_scores["usb_baiting"]
    risk.social_engineering_score = cat_scores["social_engineering"]
    risk.data_handling_score = cat_scores["data_handling"]
    risk.risk_level = risk_level
    risk.attempts_count = len(rows)
    risk.calculated_at = datetime.utcnow()

    # SHAP explanation — best effort, never blocks the score recompute.
    try:
        from app.services.random_forest_model import (
            FEATURE_NAMES, RiskForestPredictor,
            build_feature_vector_for_user,
        )
        from app.services.shap_explainer import explain_prediction
        if RiskForestPredictor().is_ready:
            vec = build_feature_vector_for_user(user_id)
            if vec is not None:
                risk.shap_summary = explain_prediction(vec, FEATURE_NAMES)
    except Exception:  # pragma: no cover  defensive
        risk.shap_summary = None

    db.session.flush()
    return risk
