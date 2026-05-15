"""Revoked JWT tokens  looked up on every authenticated request."""
from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models.base import uuid_pk


class TokenBlocklist(db.Model):
    """Stores revoked access/refresh JWTs by their ``jti`` claim."""

    __tablename__ = "token_blocklist"

    id = uuid_pk()
    jti = db.Column(db.String(36), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(10), nullable=False)  # access | refresh
    user_id = db.Column(db.String(36), nullable=True, index=True)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TokenBlocklist jti={self.jti} type={self.token_type}>"
