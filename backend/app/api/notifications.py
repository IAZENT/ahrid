"""Notifications API — list / count / read / delete for the logged-in user."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from flask import Blueprint, g, jsonify, request
from sqlalchemy import desc

from app.extensions import db
from app.models.notification import Notification
from app.utils.decorators import active_user_required

bp = Blueprint("notifications", __name__, url_prefix="/api/v1/notifications")

MAX_LIMIT = 100
DEFAULT_LIMIT = 30


def _uuid_or_none(raw: str) -> UUID | None:
    try:
        return UUID(raw)
    except (ValueError, TypeError, AttributeError):
        return None


@bp.get("")
@active_user_required
def list_notifications():
    user = g.current_user
    try:
        limit = min(MAX_LIMIT, max(1, int(request.args.get("limit", DEFAULT_LIMIT))))
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    try:
        offset = max(0, int(request.args.get("offset", 0)))
    except (TypeError, ValueError):
        offset = 0

    unread_only = request.args.get("unread") in ("1", "true", "True")
    q = Notification.query.filter_by(user_id=user.id)
    if unread_only:
        q = q.filter(Notification.read_at.is_(None))
    total = q.count()
    unread = (
        Notification.query.filter_by(user_id=user.id)
        .filter(Notification.read_at.is_(None))
        .count()
    )
    rows = q.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
    return jsonify({
        "items": [n.to_dict() for n in rows],
        "total": total,
        "unread": unread,
        "limit": limit,
        "offset": offset,
    }), 200


@bp.get("/unread-count")
@active_user_required
def unread_count():
    count = (
        Notification.query.filter_by(user_id=g.current_user.id)
        .filter(Notification.read_at.is_(None))
        .count()
    )
    return jsonify({"unread": count}), 200


@bp.patch("/<notif_id>/read")
@active_user_required
def mark_read(notif_id: str):
    nid = _uuid_or_none(notif_id)
    if nid is None:
        return jsonify({"error": "invalid_id"}), 400
    n = db.session.get(Notification, nid)
    if n is None or n.user_id != g.current_user.id:
        return jsonify({"error": "not_found"}), 404
    if n.mark_read():
        db.session.commit()
    return jsonify(n.to_dict()), 200


@bp.post("/read-all")
@active_user_required
def read_all():
    now = datetime.utcnow()
    updated = (
        Notification.query.filter_by(user_id=g.current_user.id)
        .filter(Notification.read_at.is_(None))
        .update({Notification.read_at: now}, synchronize_session=False)
    )
    db.session.commit()
    return jsonify({"updated": int(updated or 0)}), 200


@bp.delete("/<notif_id>")
@active_user_required
def delete_notification(notif_id: str):
    nid = _uuid_or_none(notif_id)
    if nid is None:
        return jsonify({"error": "invalid_id"}), 400
    n = db.session.get(Notification, nid)
    if n is None or n.user_id != g.current_user.id:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(n)
    db.session.commit()
    return jsonify({"status": "deleted", "id": str(nid)}), 200
