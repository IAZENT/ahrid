"""HAIS-Q style 7-item awareness assessment (pre / post). Master spec §6.1."""
from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models.base import uuid_fk, uuid_pk

PHASES = ("pre", "post")

QUESTIONS = [
    "I know how to identify a phishing email.",
    "I always check the sender's email address before clicking links.",
    "I understand the risks of connecting unknown USB devices.",
    "I know what to do if I receive a suspicious phone call asking for my password.",
    "I am confident I would report a suspected cyber incident to my manager.",
    "I understand why using strong, unique passwords for each account is important.",
    "I can recognise signs that a website may be fake or malicious.",
]


class AwarenessAssessment(db.Model):
    __tablename__ = "awareness_assessments"

    id = uuid_pk()
    user_id = uuid_fk("users.id", nullable=False)
    phase = db.Column(db.String(10), nullable=False)  # "pre" or "post"
    responses = db.Column(db.JSON, nullable=False)    # {"q1": 1..5, ..., "q7": 1..5}
    score = db.Column(db.Float, nullable=False)       # 0-100, mean*20
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "phase", name="uq_awareness_user_phase"),
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "phase": self.phase,
            "responses": self.responses,
            "score": self.score,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


def score_awareness(responses: dict) -> float:
    """Mean of 7 Likert (1-5) → 0-100."""
    vals = [int(responses[f"q{i}"]) for i in range(1, 8)]
    return round(sum(vals) / len(vals) / 5.0 * 100.0, 2)
