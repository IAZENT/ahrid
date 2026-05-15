"""Append-only audit log for sensitive admin / manager actions.

A security-training platform that doesn't log who did what, when, and from
where can't be defended in court — or in a thesis viva. This table captures:

  * actor_id        the user who performed the action (nullable for system
                    actions like the scheduler)
  * action          a short verb + noun string, e.g. "scenario.approve"
  * target_type     optional, e.g. "Scenario", "User"
  * target_id       optional, the affected row's UUID/string id
  * metadata        free-form JSON-as-string for extra context (e.g. before/
                    after values, error messages, query params)
  * ip_address      remote address from Flask's request, captured at write
  * user_agent      request UA string (useful for spotting automated abuse)
  * created_at      indexed for time-window queries

Append-only by convention: there is no update or delete API. Pruning is
done out-of-band via a retention job, not a model method.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from flask import has_request_context, request

from app.extensions import db
from app.models.base import uuid_pk


class AuditLog(db.Model):
    """One row per sensitive action."""

    __tablename__ = "audit_logs"

    id = uuid_pk()

    actor_id = db.Column(
        db.Uuid(as_uuid=True), db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    action = db.Column(db.String(80), nullable=False, index=True)
    target_type = db.Column(db.String(50), nullable=True, index=True)
    target_id = db.Column(db.String(100), nullable=True, index=True)

    extra = db.Column(db.Text, nullable=True)  # JSON-encoded metadata
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "actor_id": str(self.actor_id) if self.actor_id else None,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "extra": json.loads(self.extra) if self.extra else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def record_action(
    action: str,
    *,
    actor_id: uuid.UUID | str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    extra: dict | None = None,
) -> AuditLog:
    """Write one audit row. Never raises — failure to audit must NOT break the
    user request. The caller is responsible for ``db.session.commit()`` if it
    wants the row durable, but most call-sites in this codebase commit later
    in the same transaction so we just flush here.
    """
    ip = None
    ua = None
    if has_request_context():
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        ua = (request.user_agent.string or "")[:255] if request.user_agent else None

    row = AuditLog(
        actor_id=actor_id,
        action=action[:80],
        target_type=target_type[:50] if target_type else None,
        target_id=str(target_id)[:100] if target_id is not None else None,
        extra=json.dumps(extra, default=str) if extra else None,
        ip_address=ip,
        user_agent=ua,
    )
    try:
        db.session.add(row)
        db.session.flush()
    except Exception:  # noqa: BLE001
        db.session.rollback()
    return row
