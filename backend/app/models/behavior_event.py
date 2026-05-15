"""UserBehaviorEvent  micro-interaction telemetry (Phase 18)."""
from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models.base import uuid_fk, uuid_pk


EVENT_TYPES = (
    "question_viewed",
    "answer_changed",
    "hint_requested",
    "answer_submitted",
    "scenario_skipped",
    "read_time_recorded",
    "category_dwell",
)


class UserBehaviorEvent(db.Model):
    __tablename__ = "user_behavior_events"

    id = uuid_pk()
    user_id = uuid_fk("users.id", nullable=False)
    session_id = db.Column(db.String(64), nullable=False, index=True)
    scenario_id = uuid_fk("scenarios.id", nullable=True)

    event_type = db.Column(db.String(50), nullable=False, index=True)
    payload = db.Column(db.Text, nullable=False, default="{}")

    category = db.Column(db.String(50), nullable=True, index=True)
    difficulty = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "session_id": self.session_id,
            "scenario_id": str(self.scenario_id) if self.scenario_id else None,
            "event_type": self.event_type,
            "payload": self.payload,
            "category": self.category,
            "difficulty": self.difficulty,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
