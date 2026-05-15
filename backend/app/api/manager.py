"""Manager API — dashboard, team roster, profiles, reports (single-tenant)."""
from __future__ import annotations

import csv
import io
import uuid
from datetime import datetime, timedelta

from flask import Blueprint, Response, g, jsonify, request
from sqlalchemy import func

from app.extensions import db
from app.models.attempt import Attempt
from app.models.cluster import CLUSTER_ARCHETYPES
from app.models.risk_score import RiskScore
from app.models.scenario import CATEGORIES
from app.models.threat_feed import ThreatFeedEntry
from app.models.user import User
from app.services.adaptive_engine import get_user_profile
from app.services.kmeans_clustering import get_cluster_summary
from app.services.random_forest_model import RiskForestPredictor
from app.utils.decorators import active_user_required, admin_required, manager_required

bp = Blueprint("manager", __name__, url_prefix="/api/v1/manager")

_RISK_RANK = {"critical": 3, "high": 2, "medium": 1, "low": 0, "unknown": -1}


def _archetype_for(label: str | None) -> dict | None:
    if not label:
        return None
    for _, meta in CLUSTER_ARCHETYPES.items():
        if meta["label"] == label:
            return meta
    return None


def _uuid_or_400(value: str):
    try:
        return uuid.UUID(value)
    except (ValueError, TypeError, AttributeError):
        return None


@bp.get("/dashboard")
@manager_required
@active_user_required
def dashboard():
    users = User.query.filter_by(is_active=True).all()
    user_ids = [u.id for u in users]

    scores = (
        RiskScore.query.filter(RiskScore.user_id.in_(user_ids)).all()
        if user_ids else []
    )
    avg_score = (
        round(sum(s.composite_score for s in scores) / len(scores), 2)
        if scores else 0.0
    )
    critical_count = sum(1 for s in scores if s.risk_level in ("critical", "high"))

    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_scenarios = (
        db.session.query(func.count(Attempt.id))
        .filter(Attempt.user_id.in_(user_ids), Attempt.created_at >= week_ago)
        .scalar() or 0
    ) if user_ids else 0

    def _accuracy_in(days_ago_start: int, days_ago_end: int) -> float | None:
        start = datetime.utcnow() - timedelta(days=days_ago_start)
        end = datetime.utcnow() - timedelta(days=days_ago_end)
        rows = (
            db.session.query(Attempt.is_correct)
            .filter(
                Attempt.user_id.in_(user_ids),
                Attempt.created_at >= start,
                Attempt.created_at < end,
            ).all() if user_ids else []
        )
        if not rows:
            return None
        return sum(1 for (c,) in rows if c) / len(rows)

    this_wk = _accuracy_in(7, 0)
    last_wk = _accuracy_in(14, 7)
    if this_wk is None or last_wk is None:
        trend = "stable"
        trend_percent = 0.0
    else:
        trend_percent = round((this_wk - last_wk) * 100, 1)
        if trend_percent > 5:
            trend = "improving"
        elif trend_percent < -5:
            trend = "declining"
        else:
            trend = "stable"

    top_risk: list[dict] = []
    for u in users:
        s = next((x for x in scores if x.user_id == u.id), None)
        if s is None or s.risk_level in ("low", "unknown"):
            continue
        cat_scores = {cat: getattr(s, f"{cat}_score") for cat in CATEGORIES}
        weakest = max(cat_scores, key=cat_scores.get)
        top_risk.append({
            "user_id": str(u.id),
            "risk_level": s.risk_level,
            "archetype": u.cluster_label,
            "weakest_category": weakest,
        })
    top_risk.sort(key=lambda r: _RISK_RANK.get(r["risk_level"], -1), reverse=True)
    top_risk = top_risk[:3]

    org_cat_weakness: list[dict] = []
    if scores:
        for cat in CATEGORIES:
            avg = round(sum(getattr(s, f"{cat}_score") for s in scores) / len(scores), 2)
            org_cat_weakness.append({"category": cat, "avg_score": avg})
        org_cat_weakness.sort(key=lambda x: x["avg_score"], reverse=True)

    last_entry = (
        ThreatFeedEntry.query.order_by(ThreatFeedEntry.ingested_at.desc()).first()
    )
    new_scenarios_week = (
        db.session.query(func.count(ThreatFeedEntry.id))
        .filter(
            ThreatFeedEntry.ingested_at >= week_ago,
            ThreatFeedEntry.was_converted == True,  # noqa: E712
        )
        .scalar() or 0
    )

    return jsonify({
        "kpi_cards": {
            "avg_score": avg_score,
            "critical_count": critical_count,
            "weekly_scenarios": int(weekly_scenarios),
            "trend_direction": trend,
            "trend_percent": trend_percent,
        },
        "top_risk": top_risk,
        "cluster_summary": get_cluster_summary(),
        "threat_feed_status": {
            "last_update": last_entry.ingested_at.isoformat() if last_entry else None,
            "new_scenarios_this_week": int(new_scenarios_week),
        },
        "org_category_weakness": org_cat_weakness,
    }), 200


@bp.get("/team")
@manager_required
@active_user_required
def team():
    # Only employees are trainable targets — admins/managers training
    # themselves was producing self-assigned notifications. The team
    # roster also excludes the requesting user explicitly so an admin
    # who happens to also have role="employee" still cannot click
    # Assign on their own row.
    q = (
        User.query
        .filter(User.is_active.is_(True))
        .filter(User.role == "employee")
        .filter(User.id != g.current_user.id)
    )
    archetype_filter = request.args.get("archetype")
    if archetype_filter:
        q = q.filter(User.cluster_label == archetype_filter)
    dept = request.args.get("dept")
    if dept:
        q = q.filter(User.department == dept)

    users = q.all()
    out: list[dict] = []
    for u in users:
        s = u.risk_score
        weakest = None
        if s is not None:
            cat_scores = {cat: getattr(s, f"{cat}_score") for cat in CATEGORIES}
            weakest = max(cat_scores, key=cat_scores.get)
        archetype = _archetype_for(u.cluster_label)

        last_attempt = (
            Attempt.query.filter_by(user_id=u.id)
            .order_by(Attempt.created_at.desc()).first()
        )
        week_ago = datetime.utcnow() - timedelta(days=7)
        sessions_this_week = (
            db.session.query(func.count(func.distinct(Attempt.session_id)))
            .filter(Attempt.user_id == u.id, Attempt.created_at >= week_ago)
            .scalar() or 0
        )

        out.append({
            "user_id": str(u.id),
            "job_role": u.job_role,
            "department": u.department,
            "risk_level": s.risk_level if s else "unknown",
            "cluster_label": u.cluster_label,
            "archetype_colour": archetype["colour"] if archetype else None,
            "archetype_icon": archetype["icon"] if archetype else None,
            "weakest_category": weakest,
            "last_active": last_attempt.created_at.isoformat() if last_attempt else None,
            "sessions_this_week": int(sessions_this_week),
        })

    sort_key = request.args.get("sort", "risk_level")
    if sort_key == "risk_level":
        out.sort(key=lambda r: _RISK_RANK.get(r["risk_level"], -1), reverse=True)
    elif sort_key == "last_active":
        out.sort(key=lambda r: r["last_active"] or "", reverse=True)

    return jsonify({"team": out, "total": len(out)}), 200


@bp.get("/team/<user_id>/profile")
@manager_required
@active_user_required
def team_member_profile(user_id: str):
    uid = _uuid_or_400(user_id)
    if uid is None:
        return jsonify({"error": "invalid_user_id"}), 400
    target = db.session.get(User, uid)
    if target is None:
        return jsonify({"error": "not_found"}), 404

    profile = get_user_profile(target.id)
    predictor = RiskForestPredictor()
    rf_pred = predictor.predict(target.id) if predictor.is_ready else None
    score = target.risk_score
    archetype = _archetype_for(target.cluster_label)

    return jsonify({
        "user_id": str(target.id),
        "job_role": target.job_role,
        "department": target.department,
        "risk_level": score.risk_level if score else "unknown",
        "composite_score": score.composite_score if score else None,
        "category_scores": score.to_dict()["category_scores"] if score else None,
        "profile": profile,
        "cluster": (
            {
                "label": target.cluster_label,
                "colour": archetype["colour"],
                "icon": archetype["icon"],
                "description": archetype["description"],
                "intervention": archetype["intervention"],
            }
            if archetype else None
        ),
        "rf_prediction": rf_pred,
    }), 200


@bp.post("/team/<user_id>/assign-training")
@admin_required
@active_user_required
def assign_training(user_id: str):
    uid = _uuid_or_400(user_id)
    if uid is None:
        return jsonify({"error": "invalid_user_id"}), 400
    target = db.session.get(User, uid)
    if target is None or not target.is_active:
        return jsonify({"error": "not_found"}), 404

    # Defensive: never let the assigner notify themselves, and never
    # assign to another admin/manager (training is for employees).
    if target.id == g.current_user.id:
        return jsonify({"error": "cannot_assign_to_self"}), 400
    if target.role != "employee":
        return jsonify({"error": "target_must_be_employee"}), 400

    body = request.get_json(silent=True) or {}
    cats = body.get("categories") or []
    if not isinstance(cats, list) or any(c not in CATEGORIES for c in cats):
        return jsonify({"error": "validation_failed", "field": "categories"}), 400

    from app.services.notifications import emit_training_assigned
    manager_name = (
        f"{g.current_user.first_name or ''} {g.current_user.last_name or ''}".strip()
        or g.current_user.email
    )
    emit_training_assigned(
        target.id,
        assigned_by_name=manager_name,
        categories=cats,
        note=body.get("note"),
    )
    db.session.commit()

    return jsonify({
        "status": "accepted",
        "user_id": str(target.id),
        "categories": cats,
        "note": body.get("note"),
    }), 202


@bp.get("/history")
@manager_required
@active_user_required
def history():
    try:
        weeks = max(1, min(26, int(request.args.get("weeks", 8))))
    except (TypeError, ValueError):
        return jsonify({"error": "validation_failed"}), 400

    user_ids = [
        uid for (uid,) in db.session.query(User.id).filter_by(is_active=True).all()
    ]

    now = datetime.utcnow()
    buckets: list[dict] = []
    for w in reversed(range(weeks)):
        end = now - timedelta(days=7 * w)
        start = end - timedelta(days=7)
        if not user_ids:
            buckets.append({
                "week_start": start.date().isoformat(),
                "week_end": end.date().isoformat(),
                "avg_accuracy": None,
                "proxy_risk": None,
                "attempts": 0,
            })
            continue
        rows = (
            db.session.query(Attempt.is_correct)
            .filter(
                Attempt.user_id.in_(user_ids),
                Attempt.created_at >= start,
                Attempt.created_at < end,
            ).all()
        )
        if rows:
            accuracy = sum(1 for (c,) in rows if c) / len(rows)
            buckets.append({
                "week_start": start.date().isoformat(),
                "week_end": end.date().isoformat(),
                "avg_accuracy": round(accuracy, 4),
                "proxy_risk": round(100 - accuracy * 100, 1),
                "attempts": len(rows),
            })
        else:
            buckets.append({
                "week_start": start.date().isoformat(),
                "week_end": end.date().isoformat(),
                "avg_accuracy": None,
                "proxy_risk": None,
                "attempts": 0,
            })
    return jsonify({"history": buckets}), 200


@bp.get("/reports/summary")
@manager_required
@active_user_required
def reports_summary():
    try:
        weeks = max(1, min(52, int(request.args.get("weeks", 4))))
    except (TypeError, ValueError):
        return jsonify({"error": "validation_failed"}), 400

    user_ids = [
        uid for (uid,) in db.session.query(User.id).filter_by(is_active=True).all()
    ]

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["week_start", "week_end", "attempts", "accuracy", "unique_users"])

    now = datetime.utcnow()
    for w in range(weeks):
        end = now - timedelta(days=7 * w)
        start = end - timedelta(days=7)
        if not user_ids:
            writer.writerow([start.date(), end.date(), 0, "", 0])
            continue
        rows = (
            db.session.query(Attempt.is_correct, Attempt.user_id)
            .filter(
                Attempt.user_id.in_(user_ids),
                Attempt.created_at >= start,
                Attempt.created_at < end,
            ).all()
        )
        if rows:
            correct = sum(1 for (c, _) in rows if c)
            accuracy = round(correct / len(rows), 4)
            unique_users = len({uid for (_, uid) in rows})
        else:
            accuracy = ""
            unique_users = 0
        writer.writerow([start.date(), end.date(), len(rows), accuracy, unique_users])

    csv_bytes = buffer.getvalue().encode("utf-8")
    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=ahrid_weekly_summary.csv"},
    )
