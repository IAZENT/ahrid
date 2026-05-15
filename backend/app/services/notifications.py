"""Notification emission service (BSc scope: 2 types only)."""
from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from app.extensions import db
from app.models.notification import (
    NOTIF_RISK_ESCALATION,
    NOTIF_TRAINING_ASSIGNED,
    NOTIF_TYPES,
    Notification,
)

log = logging.getLogger(__name__)


def emit(
    *,
    user_id,
    type: str,
    title: str,
    body: Optional[str] = None,
    link: Optional[str] = None,
    severity: str = "info",
    meta: Optional[dict] = None,
) -> Optional[Notification]:
    if type not in NOTIF_TYPES:
        log.warning("notifications.emit: unsupported type=%s, dropping", type)
        return None
    try:
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return None
        n = Notification(
            user_id=user_id,
            type=type,
            severity=severity if severity in ("info", "success", "warning", "critical") else "info",
            title=title[:160],
            body=(body or None) and body[:480],
            link=(link or None) and link[:240],
        )
        if meta:
            n.meta = meta
        db.session.add(n)
        db.session.flush()
        return n
    except Exception:  # pragma: no cover
        log.exception("notifications.emit failed for user_id=%s", user_id)
        db.session.rollback()
        return None


def emit_training_assigned(
    user_id, *, assigned_by_name: str, categories: list[str], note: str | None = None,
) -> Optional[Notification]:
    cats_summary = ", ".join(categories[:3]) or "focus area"
    if len(categories) > 3:
        cats_summary += f" +{len(categories) - 3} more"
    body = f"{assigned_by_name} wants you to practise: {cats_summary}."
    if note:
        body += f' Note: "{note[:120]}"'
    return emit(
        user_id=user_id,
        type=NOTIF_TRAINING_ASSIGNED,
        title="New training assignment",
        body=body,
        link="/app/training",
        severity="warning",
        meta={"assigned_by": assigned_by_name, "categories": categories, "note": note},
    )


def emit_risk_escalation(user_id, *, new_level: str, composite: float) -> Optional[Notification]:
    return emit(
        user_id=user_id,
        type=NOTIF_RISK_ESCALATION,
        title=f"Risk level raised to {new_level}",
        body=f"Your composite score is now {composite:.0f}. Review your weak categories.",
        link="/app/my-score",
        severity="critical" if new_level == "critical" else "warning",
        meta={"risk_level": new_level, "composite": float(composite)},
    )
