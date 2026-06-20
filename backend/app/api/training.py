"""Training API (BSc scope)  adaptive session, history, insights."""
from __future__ import annotations

import uuid

from flask import Blueprint, g, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db, limiter
from app.models.attempt import Attempt
from app.models.scenario import CATEGORIES, Scenario
from app.services.adaptive_engine import (
    get_session_summary,
    process_attempt,
    select_next_session,
)
from app.services.behavioral_profiler import build_insights
from app.services.option_shuffle import (
    attach_presentation,
    decode_presentation_token,
    translate_displayed_to_original,
)
from app.utils.decorators import active_user_required

bp = Blueprint("training", __name__, url_prefix="/api/v1/training")


_CATEGORY_META: dict[str, dict[str, str]] = {
    "phishing_email": {"display_name": "Phishing Email", "icon": "mail",
                       "description": "Spot malicious emails before they trick you."},
    "smishing": {"display_name": "Smishing (SMS)", "icon": "message-square",
                 "description": "Recognise scam texts and fake links."},
    "vishing": {"display_name": "Vishing (Voice)", "icon": "phone",
                "description": "Defend against phone-based social engineering."},
    "physical_security": {"display_name": "Physical Security", "icon": "shield",
                          "description": "Tailgating, badges, and office perimeter."},
    "password_hygiene": {"display_name": "Password Hygiene", "icon": "key",
                         "description": "Strong passwords, MFA, and storage."},
    "usb_baiting": {"display_name": "USB Baiting", "icon": "usb",
                    "description": "Handle unknown USB devices safely."},
    "social_engineering": {"display_name": "Social Engineering", "icon": "users",
                           "description": "Pretexts, urgency, and authority ploys."},
    "data_handling": {"display_name": "Data Handling", "icon": "database",
                      "description": "Classification, sharing, and retention."},
}


def _uuid_or_400(value: str):
    try:
        return uuid.UUID(value)
    except (ValueError, TypeError, AttributeError):
        return None


@bp.get("/session/start")
@limiter.limit("20/hour")
@active_user_required
def session_start():
    user = g.current_user
    job_filter = request.args.get("job_role_filter", "true").lower() != "false"
    job_role = user.job_role if job_filter else None

    try:
        num_questions = int(request.args.get("num_questions", 0)) or None
    except (TypeError, ValueError):
        num_questions = None

    payload = select_next_session(
        user.id, job_role=job_role, num_questions=num_questions, return_meta=True,
    )
    scenarios = payload["scenarios"]
    reasons = payload.get("selection_reasons", {})
    session_id = uuid.uuid4()
    serialised = []
    for s in scenarios:
        d = attach_presentation(s.to_public_dict())
        d["selection_reason"] = reasons.get(str(s.id))
        serialised.append(d)
    return jsonify({
        "session_id": str(session_id),
        "scenarios": serialised,
        "selection_meta": payload["meta"],
    }), 200


@bp.post("/session/<session_id>/answer")
@limiter.limit("60/hour")
@active_user_required
def session_answer(session_id: str):
    user = g.current_user
    sid = _uuid_or_400(session_id)
    if sid is None:
        return jsonify({"error": "invalid_session_id"}), 400

    body = request.get_json(silent=True) or {}
    scenario_id_raw = body.get("scenario_id")
    answer = (body.get("answer") or "").strip().upper()
    try:
        response_time_ms = int(body.get("response_time_ms") or 0)
    except (TypeError, ValueError):
        return jsonify({"error": "validation_failed", "field": "response_time_ms"}), 400
    if not (0 <= response_time_ms <= 300_000):
        return jsonify({"error": "validation_failed", "field": "response_time_ms"}), 400

    scenario_uuid = _uuid_or_400(scenario_id_raw)
    if scenario_uuid is None:
        return jsonify({"error": "validation_failed", "field": "scenario_id"}), 400

    scenario = db.session.get(Scenario, scenario_uuid)
    if scenario is None or not scenario.is_active:
        return jsonify({"error": "scenario_not_found"}), 404

    perm: dict[str, str] | None = None
    token = (body.get("presentation_token") or "").strip() or None
    if token:
        perm = decode_presentation_token(token, str(scenario_uuid))
        if perm is None:
            return jsonify({
                "error": "invalid_presentation_token",
                "message": "Your question session expired. Reload the session.",
            }), 400
        answer = translate_displayed_to_original(answer, perm)

    if answer not in ("A", "B", "C", "D"):
        return jsonify({"error": "validation_failed", "field": "answer"}), 400

    other_owner = (
        db.session.query(Attempt.user_id)
        .filter(Attempt.session_id == sid, Attempt.user_id != user.id)
        .first()
    )
    if other_owner is not None:
        return jsonify({"error": "forbidden"}), 403

    result = process_attempt(
        user_id=user.id,
        scenario_id=scenario_uuid,
        answer=answer,
        response_time_ms=response_time_ms,
        session_id=sid,
    )
    if isinstance(result, tuple):
        body_payload, status = result
        return jsonify(body_payload), status

    # Behavioural telemetry  never blocks response.
    try:
        from app.services.telemetry_service import record_event
        record_event(
            user_id=user.id,
            session_id=sid,
            scenario_id=scenario_uuid,
            event_type="answer_submitted",
            payload={
                "final_answer": answer,
                "response_time_ms": response_time_ms,
                "is_correct": bool(result.get("is_correct")),
            },
            category=scenario.category,
            difficulty=scenario.difficulty,
        )
        db.session.commit()
    except Exception:  # pragma: no cover
        db.session.rollback()

    if perm and isinstance(result, dict) and result.get("correct_answer"):
        original_to_displayed = {orig: disp for disp, orig in perm.items()}
        result["correct_answer"] = original_to_displayed.get(
            result["correct_answer"], result["correct_answer"],
        )
    return jsonify(result), 200


@bp.get("/session/<session_id>/summary")
@active_user_required
def session_summary(session_id: str):
    user = g.current_user
    sid = _uuid_or_400(session_id)
    if sid is None:
        return jsonify({"error": "invalid_session_id"}), 400

    owner_row = (
        db.session.query(Attempt.user_id)
        .filter(Attempt.session_id == sid)
        .first()
    )
    if owner_row is not None and owner_row[0] != user.id:
        return jsonify({"error": "forbidden"}), 403

    return jsonify(get_session_summary(user.id, sid)), 200


@bp.get("/history")
@active_user_required
def history():
    user = g.current_user
    try:
        limit = max(1, min(100, int(request.args.get("limit", 20))))
        offset = max(0, int(request.args.get("offset", 0)))
    except (TypeError, ValueError):
        return jsonify({"error": "validation_failed"}), 400

    q = Attempt.query.filter_by(user_id=user.id)
    category = request.args.get("category")
    if category:
        if category not in CATEGORIES:
            return jsonify({"error": "unknown_category"}), 400
        q = q.filter_by(category=category)

    total = q.with_entities(func.count(Attempt.id)).scalar() or 0
    rows = q.order_by(Attempt.created_at.desc()).offset(offset).limit(limit).all()
    return jsonify({
        "attempts": [a.to_dict() for a in rows],
        "total": int(total),
        "limit": limit,
        "offset": offset,
    }), 200


@bp.get("/sessions")
@active_user_required
def sessions_history():
    user = g.current_user
    try:
        limit = max(1, min(50, int(request.args.get("limit", 20))))
        offset = max(0, int(request.args.get("offset", 0)))
    except (TypeError, ValueError):
        return jsonify({"error": "validation_failed"}), 400

    session_rows = (
        db.session.query(
            Attempt.session_id,
            func.count(Attempt.id).label("total"),
            func.sum(func.cast(Attempt.is_correct, db.Integer)).label("correct"),
            func.min(Attempt.created_at).label("started_at"),
            func.max(Attempt.created_at).label("ended_at"),
        )
        .filter(Attempt.user_id == user.id, Attempt.is_synthetic.is_(False))
        .group_by(Attempt.session_id)
        .order_by(func.max(Attempt.created_at).desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    total_sessions = (
        db.session.query(func.count(func.distinct(Attempt.session_id)))
        .filter(Attempt.user_id == user.id, Attempt.is_synthetic.is_(False))
        .scalar()
        or 0
    )

    sessions_payload: list[dict] = []
    for row in session_rows:
        sid = row.session_id
        total = int(row.total or 0)
        correct = int(row.correct or 0)
        accuracy = round(correct / total, 4) if total else 0.0
        duration = (
            (row.ended_at - row.started_at).total_seconds()
            if row.ended_at and row.started_at else 0.0
        )

        cat_rows = (
            db.session.query(
                Attempt.category,
                func.count(Attempt.id).label("n"),
                func.sum(func.cast(Attempt.is_correct, db.Integer)).label("c"),
            )
            .filter(Attempt.user_id == user.id, Attempt.session_id == sid)
            .group_by(Attempt.category)
            .all()
        )
        categories = [
            {"category": cr.category, "total": int(cr.n or 0), "correct": int(cr.c or 0)}
            for cr in cat_rows
        ]

        sessions_payload.append({
            "session_id": str(sid),
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "ended_at": row.ended_at.isoformat() if row.ended_at else None,
            "duration_seconds": round(duration, 1),
            "total_questions": total,
            "correct": correct,
            "accuracy": accuracy,
            "categories": categories,
        })

    return jsonify({
        "sessions": sessions_payload,
        "total": int(total_sessions),
        "limit": limit,
        "offset": offset,
    }), 200


@bp.get("/session/<session_id>/detail")
@active_user_required
def session_detail(session_id: str):
    user = g.current_user
    sid = _uuid_or_400(session_id)
    if sid is None:
        return jsonify({"error": "invalid_session_id"}), 400

    attempts = (
        Attempt.query.filter_by(user_id=user.id, session_id=sid)
        .order_by(Attempt.created_at.asc())
        .all()
    )
    if not attempts:
        return jsonify({"error": "not_found"}), 404

    items = []
    for a in attempts:
        scen = a.scenario
        items.append({
            "attempt_id": str(a.id),
            "scenario": scen.to_public_dict() if scen else None,
            "answer_given": a.answer_given,
            "is_correct": a.is_correct,
            "response_time_ms": a.response_time_ms,
            "category": a.category,
            "difficulty": a.difficulty,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "correct_answer": scen.correct_answer if scen else None,
            "explanation": scen.explanation if scen else None,
            "learning_tip": scen.learning_tip if scen else None,
        })

    return jsonify({
        "session_id": str(sid),
        "items": items,
        "summary": get_session_summary(user.id, sid),
    }), 200


@bp.get("/categories")
@jwt_required()
def categories():
    return jsonify([
        {
            "id": cat,
            "name": cat,
            "display_name": _CATEGORY_META[cat]["display_name"],
            "icon": _CATEGORY_META[cat]["icon"],
            "description": _CATEGORY_META[cat]["description"],
        }
        for cat in CATEGORIES
    ]), 200


@bp.get("/config")
@jwt_required()
def config():
    """Return training session configuration for the frontend."""
    from app.services.adaptive_engine import SESSION_SIZE
    return jsonify({
        "quick_size": 5,
        "full_size": SESSION_SIZE,
        "explanation_duration_seconds": 12,
    }), 200


@bp.get("/insights")
@active_user_required
def insights():
    return jsonify(build_insights(g.current_user.id)), 200
