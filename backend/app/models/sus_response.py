"""System Usability Scale (SUS)  standard 10-item instrument. Master spec §6.2."""
from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models.base import uuid_fk, uuid_pk

QUESTIONS = [
    "I think that I would like to use this system frequently.",
    "I found the system unnecessarily complex.",
    "I thought the system was easy to use.",
    "I think that I would need the support of a technical person to use this system.",
    "I found the various functions in this system were well integrated.",
    "I thought there was too much inconsistency in this system.",
    "I would imagine that most people would learn to use this system very quickly.",
    "I found the system very cumbersome to use.",
    "I felt very confident using the system.",
    "I needed to learn a lot of things before I could get going with this system.",
]


class SUSResponse(db.Model):
    __tablename__ = "sus_responses"

    id = uuid_pk()
    user_id = uuid_fk("users.id", nullable=False)
    responses = db.Column(db.JSON, nullable=False)   # {"q1":1..5, ..., "q10":1..5}
    sus_score = db.Column(db.Float, nullable=False)  # 0-100
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "responses": self.responses,
            "sus_score": self.sus_score,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


def calculate_sus(responses: dict) -> float:
    """Standard SUS scoring formula → 0-100."""
    odd = sum(int(responses[f"q{i}"]) - 1 for i in (1, 3, 5, 7, 9))
    even = sum(5 - int(responses[f"q{i}"]) for i in (2, 4, 6, 8, 10))
    return round((odd + even) * 2.5, 2)


def sus_grade(score: float) -> str:
    """Standard SUS grade buckets (Bangor et al., 2008)."""
    if score >= 85:  return "Excellent"
    if score >= 72:  return "Good"
    if score >= 52:  return "OK"
    if score >= 38:  return "Poor"
    return "Awful"
