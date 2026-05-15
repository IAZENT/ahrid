"""Shared SQLAlchemy column types and mixins."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid

from app.extensions import db


def uuid_pk():
    """Return a Column suitable for a UUID primary key (dialect-agnostic)."""
    return db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)


def uuid_fk(target: str, *, nullable: bool = False, unique: bool = False):
    """Return a Column for a UUID foreign key referencing ``target`` (e.g. ``users.id``)."""
    return db.Column(
        Uuid(as_uuid=True),
        db.ForeignKey(target, ondelete="CASCADE"),
        nullable=nullable,
        unique=unique,
        index=True,
    )


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` columns."""

    created_at = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
