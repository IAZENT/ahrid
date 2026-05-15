"""Random Forest risk-prediction inference service (BSc scope).

14-feature vector preserved (master doc Phase 5). Dropped sentiment/XP
features have been replaced with response-time-derived behavioural
proxies so the contract length is unchanged.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from flask import current_app
from sqlalchemy import func

from app.extensions import db
from app.models.attempt import Attempt
from app.models.user import User

LOG = logging.getLogger(__name__)

JOB_ROLE_ENCODING = {
    "receptionist": 0, "accountant": 1, "hr": 2, "it": 3,
    "finance": 4, "sales": 5, "management": 6, "other": 7,
}

RISK_LEVEL_ENCODING = {"low": 0, "medium": 1, "high": 2, "critical": 3}
RISK_LEVEL_DECODING = {v: k for k, v in RISK_LEVEL_ENCODING.items()}

# Behavioural-proxy thresholds (BSc replacement for VADER sentiment).
FAST_RESPONSE_MS = 4000      # under this => "rushed"
OVERCONFIDENT_MS = 2000      # under this AND wrong => "overconfident"

FEATURE_NAMES: list[str] = [
    "avg_response_time_ms",
    "phishing_accuracy",
    "smishing_accuracy",
    "social_engineering_accuracy",
    "password_hygiene_accuracy",
    "physical_security_accuracy",
    "overall_accuracy",
    "fast_attempt_rate",
    "overconfident_rate",
    "session_consistency",
    "job_role_encoded",
    "total_sessions",
    "days_since_last_session",
    "attempts_count",
]
N_FEATURES = len(FEATURE_NAMES)
assert N_FEATURES == 14, "Feature count drift — master doc requires exactly 14"

MIN_ATTEMPTS_FOR_PREDICT = 10


def _category_accuracy(attempts: list[Attempt], category: str) -> float:
    cat = [a for a in attempts if a.category == category]
    if not cat:
        return 0.0
    return sum(1 for a in cat if a.is_correct) / len(cat)


def build_feature_vector_for_user(user_id) -> np.ndarray | None:
    attempts: list[Attempt] = (
        Attempt.query.filter_by(user_id=user_id)
        .order_by(Attempt.created_at.desc())
        .all()
    )
    if len(attempts) < MIN_ATTEMPTS_FOR_PREDICT:
        return None

    user = db.session.get(User, user_id)
    job_role = (user.job_role if user else None) or "other"

    response_times = [a.response_time_ms for a in attempts if a.response_time_ms]
    avg_rt = float(np.mean(response_times)) if response_times else 0.0
    overall_acc = sum(1 for a in attempts if a.is_correct) / len(attempts)

    fast_rate = (
        sum(1 for a in attempts if a.response_time_ms and a.response_time_ms < FAST_RESPONSE_MS)
        / len(attempts)
    )
    overconfident_rate = (
        sum(
            1 for a in attempts
            if a.response_time_ms
            and a.response_time_ms < OVERCONFIDENT_MS
            and not a.is_correct
        )
        / len(attempts)
    )

    total_sessions = (
        db.session.query(func.count(func.distinct(Attempt.session_id)))
        .filter(Attempt.user_id == user_id)
        .scalar()
        or 0
    )
    last_session_at = max(a.created_at for a in attempts)
    days_since = max(0, (datetime.utcnow() - last_session_at).days)

    # Session consistency: same modal-length proxy used by KMeans.
    if total_sessions:
        rows = (
            db.session.query(Attempt.session_id, func.count(Attempt.id))
            .filter(Attempt.user_id == user_id)
            .group_by(Attempt.session_id)
            .all()
        )
        sizes = [int(c) for _, c in rows]
        modal = max(set(sizes), key=sizes.count) if sizes else 0
        same = sum(1 for s in sizes if s == modal)
        session_consistency = same / len(sizes) if sizes else 0.0
    else:
        session_consistency = 0.0

    return np.array(
        [
            avg_rt,
            _category_accuracy(attempts, "phishing_email"),
            _category_accuracy(attempts, "smishing"),
            _category_accuracy(attempts, "social_engineering"),
            _category_accuracy(attempts, "password_hygiene"),
            _category_accuracy(attempts, "physical_security"),
            overall_acc,
            fast_rate,
            overconfident_rate,
            float(session_consistency),
            float(JOB_ROLE_ENCODING.get(job_role, JOB_ROLE_ENCODING["other"])),
            float(total_sessions),
            float(days_since),
            float(len(attempts)),
        ],
        dtype=float,
    )


class RiskForestPredictor:
    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path or self._default_model_path()
        self.features_path = Path(self.model_path).with_name("rf_features.json")
        self.model: Any = None
        self.feature_names: list[str] | None = None
        self.load_model()

    @staticmethod
    def _default_model_path() -> str:
        try:
            return current_app.config["RF_MODEL_PATH"]
        except RuntimeError:
            return os.environ.get("RF_MODEL_PATH", "ml_models/risk_rf_model.pkl")

    def load_model(self) -> None:
        try:
            self.model = joblib.load(self.model_path)
            with open(self.features_path) as f:
                self.feature_names = json.load(f)
            LOG.info("Loaded RF model from %s", self.model_path)
        except FileNotFoundError:
            self.model = None
            self.feature_names = FEATURE_NAMES
            LOG.info("RF model not trained yet — predictor in pass-through mode")

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    def build_feature_vector(self, user_id) -> np.ndarray | None:
        return build_feature_vector_for_user(user_id)

    def predict(self, user_id) -> dict | None:
        if not self.is_ready:
            return None
        vec = self.build_feature_vector(user_id)
        if vec is None:
            return None
        x = vec.reshape(1, -1)
        proba = self.model.predict_proba(x)[0]
        cls_idx = int(np.argmax(proba))
        cls = int(self.model.classes_[cls_idx])
        confidence = float(proba[cls_idx])
        return {
            "predicted_risk_level": RISK_LEVEL_DECODING.get(cls, "unknown"),
            "confidence": round(confidence, 4),
            "feature_importances": self._top_importances(),
        }

    def _top_importances(self, k: int = 3) -> dict[str, float]:
        if not self.is_ready:
            return {}
        importances = self.model.feature_importances_
        names = self.feature_names or FEATURE_NAMES
        ranked = sorted(zip(names, importances), key=lambda p: -p[1])[:k]
        return {name: round(float(weight), 4) for name, weight in ranked}

    def get_feature_importances_for_user(self, user_id) -> dict:
        return self._top_importances()
