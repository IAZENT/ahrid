"""RiskScore model  current composite + per-category risk for one user."""
from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models.base import uuid_fk, uuid_pk

RISK_LEVELS = ("critical", "high", "medium", "low", "unknown")


class RiskScore(db.Model):
    """One row per user  overwritten when risk is recomputed."""

    __tablename__ = "risk_scores"

    id = uuid_pk()
    user_id = uuid_fk("users.id", nullable=False, unique=True)

    composite_score = db.Column(db.Float, nullable=False, default=0.0)

    # Per-category sub-scores (0.0 = no risk, 100.0 = max risk)
    phishing_email_score = db.Column(db.Float, nullable=False, default=0.0)
    smishing_score = db.Column(db.Float, nullable=False, default=0.0)
    vishing_score = db.Column(db.Float, nullable=False, default=0.0)
    physical_security_score = db.Column(db.Float, nullable=False, default=0.0)
    password_hygiene_score = db.Column(db.Float, nullable=False, default=0.0)
    usb_baiting_score = db.Column(db.Float, nullable=False, default=0.0)
    social_engineering_score = db.Column(db.Float, nullable=False, default=0.0)
    data_handling_score = db.Column(db.Float, nullable=False, default=0.0)

    risk_level = db.Column(db.String(20), nullable=False, default="unknown", index=True)

    rf_predicted_risk = db.Column(db.Float, nullable=True)
    rf_confidence = db.Column(db.Float, nullable=True)

    # SHAP explanation cached from the most recent RF prediction.
    # Shape: see app.services.shap_explainer.explain_prediction.
    shap_summary = db.Column(db.JSON, nullable=True)

    attempts_count = db.Column(db.Integer, nullable=False, default=0)
    score_version = db.Column(db.Integer, nullable=False, default=1)

    calculated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="risk_score")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "composite_score": self.composite_score,
            "category_scores": {
                "phishing_email": self.phishing_email_score,
                "smishing": self.smishing_score,
                "vishing": self.vishing_score,
                "physical_security": self.physical_security_score,
                "password_hygiene": self.password_hygiene_score,
                "usb_baiting": self.usb_baiting_score,
                "social_engineering": self.social_engineering_score,
                "data_handling": self.data_handling_score,
            },
            "risk_level": self.risk_level,
            "rf_predicted_risk": self.rf_predicted_risk,
            "rf_confidence": self.rf_confidence,
            "attempts_count": self.attempts_count,
            "score_version": self.score_version,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RiskScore user={self.user_id} {self.risk_level} {self.composite_score:.1f}>"
