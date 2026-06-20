"""Admin API (BSc scope)  users, scenarios, threats, stats, retrains.

Removed: invite system, profile-change-request workflow, AI scenario
generation, multi-tenant org_id scoping, coaching note + hints.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from pathlib import Path

from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import func

from app.extensions import db, limiter
from app.models.attempt import Attempt
from app.models.audit_log import record_action
from app.models.password_reset import (
    PasswordResetRequest,
    STATUS_PENDING,
    STATUS_REJECTED,
    STATUS_TOKEN_ISSUED,
)
from app.models.scenario import (
    CATEGORIES,
    DIFFICULTIES,
    QUESTION_TYPES,
    Scenario,
)
from app.models.threat_feed import ThreatFeedEntry
from app.models.user import JOB_ROLES, ROLES, User
from app.services import background_jobs
from app.services.answer_utils import validate_options
from app.utils.decorators import active_user_required, admin_required
from app.utils.validators import PASSWORD_RE, USERNAME_RE, sanitize_string

bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


def _uuid_or_400(value: str):
    try:
        return uuid.UUID(value)
    except (ValueError, TypeError, AttributeError):
        return None


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
@bp.get("/users")
@admin_required
@active_user_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"users": [u.to_dict() for u in users], "total": len(users)}), 200


@bp.post("/users")
@admin_required
@active_user_required
@limiter.limit("60/hour")
def create_user():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    username = (body.get("username") or "").strip().lower()
    password = body.get("password") or ""
    role = body.get("role") or "employee"
    job_role = body.get("job_role")

    if not email or "@" not in email:
        return jsonify({"error": "validation_failed", "field": "email"}), 400
    if not USERNAME_RE.match(username):
        return jsonify({"error": "validation_failed", "field": "username"}), 400
    if not PASSWORD_RE.match(password):
        return jsonify({"error": "validation_failed", "field": "password"}), 400
    if role not in ROLES:
        return jsonify({"error": "validation_failed", "field": "role"}), 400
    if job_role and job_role not in JOB_ROLES:
        return jsonify({"error": "validation_failed", "field": "job_role"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_exists"}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username_exists"}), 409

    user = User(
        email=email,
        username=username,
        first_name=sanitize_string(body.get("first_name")),
        last_name=sanitize_string(body.get("last_name")),
        role=role,
        job_role=job_role,
        department=sanitize_string(body.get("department")),
        is_active=True,
        is_verified=True,
        consent_given=True,
        consent_timestamp=datetime.utcnow(),
    )
    user.set_password(password)
    db.session.add(user)
    record_action(
        "admin.create_user",
        actor_id=g.current_user.id,
        target_type="User",
        target_id=str(user.id) if user.id else email,
    )
    db.session.commit()
    return jsonify({"user": user.to_dict()}), 201


@bp.patch("/users/<user_id>")
@admin_required
@active_user_required
def update_user(user_id: str):
    admin = g.current_user
    uid = _uuid_or_400(user_id)
    if uid is None:
        return jsonify({"error": "invalid_user_id"}), 400
    target = db.session.get(User, uid)
    if target is None:
        return jsonify({"error": "not_found"}), 404

    body = request.get_json(silent=True) or {}

    if "role" in body:
        if body["role"] not in ROLES:
            return jsonify({"error": "validation_failed", "field": "role"}), 400
        target.role = body["role"]
    if "is_active" in body:
        target.is_active = bool(body["is_active"])
    if "department" in body:
        target.department = sanitize_string(body["department"]) if body["department"] else None
    if "job_role" in body:
        jr = body["job_role"]
        if jr is not None and jr not in JOB_ROLES:
            return jsonify({"error": "validation_failed", "field": "job_role"}), 400
        target.job_role = jr
    if "first_name" in body:
        target.first_name = sanitize_string(body["first_name"]) or None
    if "last_name" in body:
        target.last_name = sanitize_string(body["last_name"]) or None
    if "username" in body:
        new_username = (sanitize_string(body["username"]) or "").strip().lower()
        if not USERNAME_RE.match(new_username):
            return jsonify({"error": "validation_failed", "field": "username"}), 400
        clash = User.query.filter(
            User.username == new_username, User.id != target.id
        ).first()
        if clash is not None:
            return jsonify({"error": "username_exists"}), 409
        target.username = new_username

    record_action(
        "admin.update_user",
        actor_id=admin.id,
        target_type="User",
        target_id=str(target.id),
        extra={"fields": sorted(body.keys())},
    )
    db.session.commit()
    return jsonify({"user": target.to_dict()}), 200


# --------------------------------------------------------------------------- #
# Scenarios
# --------------------------------------------------------------------------- #
@bp.get("/scenarios")
@admin_required
@active_user_required
def list_scenarios():
    try:
        limit = max(1, min(500, int(request.args.get("limit", 50))))
        offset = max(0, int(request.args.get("offset", 0)))
    except (TypeError, ValueError):
        return jsonify({"error": "validation_failed"}), 400

    q = Scenario.query
    category = request.args.get("category")
    if category:
        if category not in CATEGORIES:
            return jsonify({"error": "unknown_category"}), 400
        q = q.filter_by(category=category)
    source = request.args.get("source")
    if source:
        q = q.filter_by(source=source)

    total = q.with_entities(func.count(Scenario.id)).scalar() or 0
    rows = q.order_by(Scenario.created_at.desc()).offset(offset).limit(limit).all()
    return jsonify({
        "scenarios": [s.to_dict() for s in rows],
        "total": int(total),
    }), 200


@bp.post("/scenarios")
@admin_required
@active_user_required
@limiter.limit("30/hour")
def create_scenario():
    body = request.get_json(silent=True) or {}
    qtype = str(body.get("question_type") or "mcq").strip().lower()
    if qtype not in QUESTION_TYPES:
        qtype = "mcq"

    required = [
        "title", "content", "category", "difficulty",
        "option_a", "option_b", "option_c", "option_d",
        "correct_answer", "explanation",
    ]
    missing = [k for k in required if not body.get(k)]
    if missing:
        return jsonify({"error": "validation_failed", "missing": missing}), 400
    if body["category"] not in CATEGORIES:
        return jsonify({"error": "validation_failed", "field": "category"}), 400
    if int(body["difficulty"]) not in DIFFICULTIES:
        return jsonify({"error": "validation_failed", "field": "difficulty"}), 400
    if (body.get("correct_answer") or "").upper() not in ("A", "B", "C", "D"):
        return jsonify({"error": "validation_failed", "field": "correct_answer"}), 400
    stubs = validate_options(body, question_type=qtype)
    if stubs:
        return jsonify({"error": "validation_failed", "stubs": stubs}), 400

    scenario = Scenario(
        title=body["title"][:200],
        content=body["content"],
        question_type=qtype,
        category=body["category"],
        difficulty=int(body["difficulty"]),
        target_roles=body.get("target_roles") or "all",
        correct_answer=body["correct_answer"].upper(),
        option_a=body["option_a"],
        option_b=body["option_b"],
        option_c=body["option_c"],
        option_d=body["option_d"],
        explanation=body["explanation"],
        red_flags=body.get("red_flags"),
        learning_tip=body.get("learning_tip"),
        tf_statement=body.get("tf_statement"),
        source=body.get("source") or "manual",
        is_active=True,
    )
    db.session.add(scenario)
    record_action(
        "admin.create_scenario",
        actor_id=g.current_user.id,
        target_type="Scenario",
        target_id=str(scenario.id) if scenario.id else None,
    )
    db.session.commit()
    return jsonify({"scenario": scenario.to_dict()}), 201


@bp.patch("/scenarios/<scenario_id>")
@admin_required
@active_user_required
def update_scenario(scenario_id: str):
    sid = _uuid_or_400(scenario_id)
    if sid is None:
        return jsonify({"error": "invalid_scenario_id"}), 400
    scenario = db.session.get(Scenario, sid)
    if scenario is None:
        return jsonify({"error": "not_found"}), 404

    body = request.get_json(silent=True) or {}
    if "is_active" in body:
        scenario.is_active = bool(body["is_active"])
    if "difficulty" in body:
        if body["difficulty"] not in DIFFICULTIES:
            return jsonify({"error": "validation_failed", "field": "difficulty"}), 400
        scenario.difficulty = int(body["difficulty"])
    if "target_roles" in body and isinstance(body["target_roles"], str):
        scenario.target_roles = body["target_roles"]

    db.session.commit()
    return jsonify({"scenario": scenario.to_dict()}), 200


# --------------------------------------------------------------------------- #
# Threat feed
# --------------------------------------------------------------------------- #
@bp.get("/threats")
@admin_required
@active_user_required
def list_threats():
    try:
        limit = max(1, min(500, int(request.args.get("limit", 50))))
        offset = max(0, int(request.args.get("offset", 0)))
    except (TypeError, ValueError):
        return jsonify({"error": "validation_failed"}), 400

    source = (request.args.get("source") or "").strip().lower() or None
    converted_param = request.args.get("converted")

    q = ThreatFeedEntry.query
    if source:
        q = q.filter(ThreatFeedEntry.source == source)
    if converted_param is not None:
        if converted_param.lower() in ("true", "1", "yes"):
            q = q.filter(ThreatFeedEntry.was_converted.is_(True))
        elif converted_param.lower() in ("false", "0", "no"):
            q = q.filter(ThreatFeedEntry.was_converted.is_(False))

    total = q.with_entities(func.count(ThreatFeedEntry.id)).scalar() or 0
    rows = q.order_by(ThreatFeedEntry.ingested_at.desc()).offset(offset).limit(limit).all()
    return jsonify({"threats": [t.to_dict() for t in rows], "total": int(total)}), 200


@bp.get("/threats/sources")
@admin_required
@active_user_required
def threats_by_source():
    rows = (
        db.session.query(
            ThreatFeedEntry.source,
            func.count(ThreatFeedEntry.id).label("total"),
            func.sum(func.cast(ThreatFeedEntry.was_converted, db.Integer)).label("converted"),
            func.max(ThreatFeedEntry.ingested_at).label("latest"),
        )
        .group_by(ThreatFeedEntry.source)
        .all()
    )
    return jsonify({
        "sources": {
            r.source: {
                "total": int(r.total or 0),
                "converted": int(r.converted or 0),
                "latest": r.latest.isoformat() if r.latest else None,
            }
            for r in rows
        },
    }), 200


@bp.post("/threats/run-ingestion")
@admin_required
@active_user_required
def run_ingestion():
    from app.services.threat_ingestion import ThreatIngestionService
    result = ThreatIngestionService().run_ingestion()
    return jsonify({"status": "completed", **(result or {})}), 200


# --------------------------------------------------------------------------- #
# System stats + ML model health
# --------------------------------------------------------------------------- #
@bp.get("/stats")
@admin_required
@active_user_required
def admin_stats():
    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)

    total_users = db.session.query(func.count(User.id)).scalar() or 0
    active_users = (
        db.session.query(func.count(User.id))
        .filter(User.is_active.is_(True)).scalar() or 0
    )
    total_scenarios = db.session.query(func.count(Scenario.id)).scalar() or 0
    active_scenarios = (
        db.session.query(func.count(Scenario.id))
        .filter(Scenario.is_active.is_(True)).scalar() or 0
    )
    threats_24h = (
        db.session.query(func.count(ThreatFeedEntry.id))
        .filter(ThreatFeedEntry.ingested_at >= day_ago).scalar() or 0
    )
    attempts_24h = (
        db.session.query(func.count(Attempt.id))
        .filter(Attempt.created_at >= day_ago).scalar() or 0
    )

    def _file_stat(key: str) -> dict:
        path_str = current_app.config.get(key)
        if not path_str:
            return {"trained": False, "last_trained": None, "path": None, "metrics": None}
        path = Path(path_str)
        if not path.exists():
            return {"trained": False, "last_trained": None, "path": str(path), "metrics": None}
        result: dict = {
            "trained": True,
            "last_trained": datetime.utcfromtimestamp(path.stat().st_mtime).isoformat(),
            "path": str(path),
            "metrics": None,
        }
        # Load sibling metrics JSON if present
        metrics_path = path.with_name(path.stem.replace("_model", "_metrics") + ".json")
        if not metrics_path.exists():
            # Fallback: try kmeans_metrics / rf_metrics
            for suffix in ("kmeans_metrics", "rf_metrics"):
                candidate = path.with_name(suffix + ".json")
                if candidate.exists():
                    metrics_path = candidate
                    break
        if metrics_path.exists():
            try:
                import json as _json
                result["metrics"] = _json.loads(metrics_path.read_text())
            except Exception:
                pass
        return result

    return jsonify({
        "totals": {
            "users": int(total_users),
            "active_users": int(active_users),
            "scenarios": int(total_scenarios),
            "active_scenarios": int(active_scenarios),
            "threats_last_24h": int(threats_24h),
            "attempts_last_24h": int(attempts_24h),
        },
        "ml_models": {
            "random_forest": _file_stat("RF_MODEL_PATH"),
            "kmeans": _file_stat("KMEANS_MODEL_PATH"),
        },
        "background_jobs": {
            "ingestion": background_jobs.get_state("ingestion"),
            "retrain": background_jobs.get_state("retrain"),
        },
        "generated_at": now.isoformat(),
    }), 200


# --------------------------------------------------------------------------- #
# Background-triggered jobs
# --------------------------------------------------------------------------- #
@bp.post("/trigger-feed-ingestion")
@admin_required
@active_user_required
@limiter.limit("30/hour")
def trigger_feed_ingestion():
    app = current_app._get_current_object()  # type: ignore[attr-defined]

    def work() -> dict:
        from app.services.threat_ingestion import ThreatIngestionService
        return ThreatIngestionService().run_ingestion() or {}

    record_action("admin.trigger_threat_ingestion", actor_id=g.current_user.id)
    db.session.commit()
    state = background_jobs.launch("ingestion", app, work)
    return jsonify(state), 202


@bp.get("/ingestion-status")
@admin_required
@active_user_required
def ingestion_status():
    return jsonify(background_jobs.get_state("ingestion")), 200


@bp.post("/retrain-models")
@admin_required
@active_user_required
@limiter.limit("30/hour")
def retrain_models():
    app = current_app._get_current_object()  # type: ignore[attr-defined]

    def work() -> dict:
        from app.services.kmeans_clustering import reassign_all_users, train_kmeans
        from app.services.random_forest_model import RiskForestPredictor

        summary: dict = {}
        try:
            from train_models import (  # type: ignore[import-not-found]
                prepare_training_data, train_random_forest,
            )
            min_total = int(current_app.config.get("MIN_TRAINING_SAMPLES", 20))
            total = db.session.query(func.count(Attempt.id)).scalar() or 0
            if total < min_total:
                summary["rf"] = {
                    "status": "skipped",
                    "reason": f"attempts {total} < min {min_total}",
                }
            else:
                X, y = prepare_training_data()
                n_users = int(len(y)) if y is not None else 0
                n_classes = len(set(y.tolist())) if n_users else 0
                if X is not None and n_users >= 4 and n_classes >= 2:
                    train_random_forest(
                        X, y,
                        Path(current_app.config.get("RF_MODEL_PATH", "ml_models/risk_rf_model.pkl")),
                    )
                    RiskForestPredictor().load_model()
                    summary["rf"] = {
                        "status": "trained", "users": n_users, "classes": n_classes,
                    }
                else:
                    summary["rf"] = {
                        "status": "skipped",
                        "reason": (
                            f"need ≥4 users with ≥10 attempts and ≥2 risk classes "
                            f"(have {n_users} users, {n_classes} classes)"
                        ),
                    }
        except Exception as exc:
            summary["rf"] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}

        try:
            result = train_kmeans()
            if result is None:
                summary["kmeans"] = {"status": "skipped", "reason": "insufficient_users"}
            else:
                reassign_all_users()
                summary["kmeans"] = {
                    "status": "trained",
                    **{k: v for k, v in result.items() if k != "model"},
                }
        except Exception as exc:
            summary["kmeans"] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}

        return summary

    record_action("admin.retrain_models", actor_id=g.current_user.id)
    db.session.commit()
    state = background_jobs.launch("retrain", app, work)
    return jsonify(state), 202


@bp.get("/retrain-status")
@admin_required
@active_user_required
def retrain_status():
    return jsonify(background_jobs.get_state("retrain")), 200


# --------------------------------------------------------------------------- #
# Audit log viewer
# --------------------------------------------------------------------------- #
@bp.get("/audit-log")
@admin_required
@active_user_required
def audit_log():
    from app.models.audit_log import AuditLog
    limit = max(1, min(200, int(request.args.get("limit", 50))))
    offset = max(0, int(request.args.get("offset", 0)))
    action_filter = (request.args.get("action") or "").strip() or None

    q = AuditLog.query
    if action_filter:
        q = q.filter(AuditLog.action.like(f"{action_filter}%"))

    total = q.with_entities(func.count(AuditLog.id)).scalar() or 0
    rows = q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return jsonify({
        "items": [r.to_dict() for r in rows],
        "total": int(total),
        "limit": limit,
        "offset": offset,
    }), 200


# --------------------------------------------------------------------------- #
# Password-reset queue (admin reviews user-filed forgot-password requests)
# --------------------------------------------------------------------------- #
@bp.get("/password-resets")
@admin_required
@active_user_required
def list_password_resets():
    status = (request.args.get("status") or "pending").strip().lower()
    q = PasswordResetRequest.query
    if status != "all":
        q = q.filter_by(status=status)
    rows = q.order_by(PasswordResetRequest.created_at.desc()).limit(200).all()
    return jsonify({
        "requests": [r.to_dict(include_user_email=True) for r in rows],
    }), 200


@bp.post("/password-resets/<req_id>/approve")
@admin_required
@active_user_required
def approve_password_reset(req_id: str):
    rid = _uuid_or_400(req_id)
    if rid is None:
        return jsonify({"error": "invalid_id"}), 400
    pr = db.session.get(PasswordResetRequest, rid)
    if pr is None:
        return jsonify({"error": "not_found"}), 404
    if pr.status != STATUS_PENDING:
        return jsonify({"error": "not_pending", "status": pr.status}), 409

    raw, token_hash, expires_at = PasswordResetRequest.issue_token()
    pr.token_hash = token_hash
    pr.token_expires_at = expires_at
    pr.status = STATUS_TOKEN_ISSUED
    pr.approved_by = g.current_user.id
    pr.approved_at = datetime.utcnow()
    record_action(
        "admin.approve_password_reset",
        actor_id=g.current_user.id,
        target_type="PasswordResetRequest",
        target_id=str(pr.id),
    )
    db.session.commit()
    # Token returned ONCE here so the admin can hand it to the user
    # (e.g. by email or in person). Never stored in plain text.
    return jsonify({"request": pr.to_dict(), "reset_token": raw}), 200


@bp.post("/password-resets/<req_id>/reject")
@admin_required
@active_user_required
def reject_password_reset(req_id: str):
    rid = _uuid_or_400(req_id)
    if rid is None:
        return jsonify({"error": "invalid_id"}), 400
    pr = db.session.get(PasswordResetRequest, rid)
    if pr is None:
        return jsonify({"error": "not_found"}), 404
    if pr.status != STATUS_PENDING:
        return jsonify({"error": "not_pending", "status": pr.status}), 409
    pr.status = STATUS_REJECTED
    record_action(
        "admin.reject_password_reset",
        actor_id=g.current_user.id,
        target_type="PasswordResetRequest",
        target_id=str(pr.id),
    )
    db.session.commit()
    return jsonify({"request": pr.to_dict()}), 200
