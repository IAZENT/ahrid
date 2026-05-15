"""Notification model — minimal: training_assigned + risk_escalation only."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.extensions import db
from app.models.base import TimestampMixin, uuid_fk, uuid_pk

NOTIF_TRAINING_ASSIGNED = "training_assigned"
NOTIF_RISK_ESCALATION = "risk_escalation"

NOTIF_TYPES = (NOTIF_TRAINING_ASSIGNED, NOTIF_RISK_ESCALATION)
NOTIF_SEVERITIES = ("info", "success", "warning", "critical")


class Notification(db.Model, TimestampMixin):
    __tablename__ = "notifications"

    id = uuid_pk()
    user_id = uuid_fk("users.id", nullable=False)

    type = db.Column(db.String(40), nullable=False, index=True)
    severity = db.Column(db.String(16), nullable=False, default="info")

    title = db.Column(db.String(160), nullable=False)
    body = db.Column(db.String(480), nullable=True)
    link = db.Column(db.String(240), nullable=True)
    meta_json = db.Column(db.Text, nullable=True)

    read_at = db.Column(db.DateTime, nullable=True, index=True)

    user = db.relationship("User", foreign_keys=[user_id])

    @property
    def meta(self) -> dict:
        if not self.meta_json:
            return {}
        try:
            parsed = json.loads(self.meta_json)
            return parsed if isinstance(parsed, dict) else {}
        except (TypeError, ValueError):
            return {}

    @meta.setter
    def meta(self, value: Any) -> None:
        self.meta_json = None if value is None else json.dumps(value, default=str)

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    def mark_read(self) -> bool:
        if self.read_at is None:
            self.read_at = datetime.utcnow()
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "type": self.type,
            "severity": self.severity,
            "title": self.title,
            "body": self.body,
            "link": self.link,
            "meta": self.meta,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
