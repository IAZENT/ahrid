"""Password-reset request workflow.

BSc scope: a user files a forgot-password request; an admin reviews it,
approves to mint a single-use token, and the user consumes it via the
public reset endpoint.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta

from app.extensions import db
from app.models.base import TimestampMixin, uuid_fk, uuid_pk

STATUS_PENDING = "pending"
STATUS_TOKEN_ISSUED = "token_issued"
STATUS_CONSUMED = "consumed"
STATUS_REJECTED = "rejected"
STATUS_EXPIRED = "expired"
STATUSES = (STATUS_PENDING, STATUS_TOKEN_ISSUED, STATUS_CONSUMED, STATUS_REJECTED, STATUS_EXPIRED)

TOKEN_TTL_HOURS = 24


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class PasswordResetRequest(db.Model, TimestampMixin):
    __tablename__ = "password_reset_requests"

    id = uuid_pk()
    user_id = uuid_fk("users.id")
    token_hash = db.Column(db.String(128), nullable=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING, index=True)
    approved_by = uuid_fk("users.id", nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    consumed_at = db.Column(db.DateTime, nullable=True)

    @staticmethod
    def issue_token() -> tuple[str, str, datetime]:
        raw = secrets.token_urlsafe(32)
        return raw, _hash_token(raw), datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS)

    @staticmethod
    def verify_token(raw_token: str) -> "PasswordResetRequest | None":
        if not raw_token:
            return None
        h = _hash_token(raw_token)
        row = PasswordResetRequest.query.filter_by(token_hash=h).first()
        if row is None or row.status != STATUS_TOKEN_ISSUED:
            return None
        if row.token_expires_at and row.token_expires_at < datetime.utcnow():
            row.status = STATUS_EXPIRED
            db.session.commit()
            return None
        return row

    def to_dict(self, *, include_user_email: bool = False) -> dict:
        d = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "status": self.status,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "consumed_at": self.consumed_at.isoformat() if self.consumed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_user_email:
            from app.models.user import User
            user = db.session.get(User, self.user_id)
            if user is not None:
                d["user_email"] = user.email
                d["user_username"] = user.username
        return d
