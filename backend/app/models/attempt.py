"""Attempt model — immutable record of a user's response to a scenario.

Behavioural signal kept: ``response_time_ms`` only (per BSc scope reduction).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Uuid

from app.extensions import db
from app.models.base import uuid_fk, uuid_pk


class Attempt(db.Model):
    __tablename__ = "attempts"

    id = uuid_pk()
    user_id = uuid_fk("users.id", nullable=False)
    scenario_id = uuid_fk("scenarios.id", nullable=False)

    answer_given = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, index=True)
    response_time_ms = db.Column(db.Integer, nullable=True)

    category = db.Column(db.String(50), nullable=False, index=True)
    difficulty = db.Column(db.Integer, nullable=False, index=True)

    session_id = db.Column(Uuid(as_uuid=True), nullable=False, default=uuid.uuid4, index=True)

    is_synthetic = db.Column(db.Boolean, nullable=False, default=False, index=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = db.relationship("User", back_populates="attempts")
    scenario = db.relationship("Scenario", back_populates="attempts")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "scenario_id": str(self.scenario_id),
            "answer_given": self.answer_given,
            "is_correct": self.is_correct,
            "response_time_ms": self.response_time_ms,
            "category": self.category,
            "difficulty": self.difficulty,
            "session_id": str(self.session_id) if self.session_id else None,
            "is_synthetic": self.is_synthetic,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
