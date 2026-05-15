"""Authentication endpoints (BSc scope).

Mounted at ``/api/v1/auth``.

Endpoints:
  POST /login              identifier + password → tokens
  POST /refresh            refresh → fresh access token
  POST /logout             revoke the supplied token
  GET  /me                 current user
  PATCH /me                edit safe profile fields
  POST /change-password    self-service password change
  POST /forgot-password    file an admin-routed reset request
  POST /reset-password     consume a single-use admin-issued token

Multi-tenant registration, invite acceptance, profile-change requests,
and super_admin queues are all out of scope and have been removed.
Users are seeded directly via ``seed_users.py``.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError

from app.extensions import db, limiter
from app.models.password_reset import (
    PasswordResetRequest,
    STATUS_CONSUMED,
    STATUS_PENDING,
)
from app.models.user import User
from app.utils.security import register_failed_login, reset_login_state, revoke_token
from app.utils.validators import (
    JOB_ROLE_CHOICES,
    LoginSchema,
    PASSWORD_RE,
    USERNAME_RE,
    sanitize_string,
)
import re

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
_login_schema = LoginSchema()


def _token_payload(user: User) -> tuple[str, str]:
    additional_claims = {"role": user.role, "job_role": user.job_role}
    access = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh = create_refresh_token(identity=str(user.id), additional_claims=additional_claims)
    return access, refresh


def _load_user(user_id: str | None) -> User | None:
    if not user_id:
        return None
    try:
        return db.session.get(User, uuid.UUID(user_id))
    except (ValueError, TypeError):
        return None


@bp.post("/register")
@limiter.limit("5/hour")
def register():
    """Self-service employee registration into the AHRID organisation.

    Body: { email, username, password, first_name, last_name, job_role?, department? }
    Always assigns role="employee". Returns access/refresh tokens on success.
    """
    body = request.get_json(silent=True) or {}

    email = (body.get("email") or "").strip().lower()
    username = (body.get("username") or "").strip().lower()
    password = body.get("password") or ""
    first_name = sanitize_string(body.get("first_name")) or None
    last_name = sanitize_string(body.get("last_name")) or None
    job_role = (sanitize_string(body.get("job_role")) or "").lower() or None
    department = sanitize_string(body.get("department")) or None

    errors: dict[str, str] = {}
    if not _EMAIL_RE.match(email) or len(email) > 254:
        errors["email"] = "valid email required"
    if not USERNAME_RE.match(username):
        errors["username"] = "3-32 chars, letters/digits/._-"
    if not PASSWORD_RE.match(password):
        errors["password"] = (
            "min 12 chars with uppercase, lowercase, digit, special character"
        )
    if not first_name or not last_name:
        errors["name"] = "first_name and last_name required"
    if job_role and job_role not in JOB_ROLE_CHOICES:
        errors["job_role"] = f"must be one of {JOB_ROLE_CHOICES}"
    if errors:
        return jsonify({"error": "validation_failed", "details": errors}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_exists"}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username_exists"}), 409

    user = User(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        role="employee",
        job_role=job_role,
        department=department,
        is_active=True,
        is_verified=True,
        consent_given=True,
        consent_timestamp=datetime.utcnow(),
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access, refresh = _token_payload(user)
    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "user": user.to_dict(),
    }), 201


@bp.post("/login")
@limiter.limit("10/15 minutes")
def login():
    try:
        data = _login_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_failed", "details": err.messages}), 400

    ident = data["identifier"]
    user = User.query.filter(
        (User.email == ident) | (User.username == ident)
    ).first()
    if not user:
        return jsonify({"error": "invalid_credentials"}), 401
    if not user.is_active:
        return jsonify({"error": "account_disabled"}), 403
    if user.is_locked:
        return jsonify({
            "error": "account_locked",
            "locked_until": user.locked_until.isoformat(),
        }), 423
    if not user.check_password(data["password"]):
        register_failed_login(user)
        db.session.commit()
        return jsonify({"error": "invalid_credentials"}), 401

    reset_login_state(user)
    db.session.commit()

    access, refresh = _token_payload(user)
    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "user": user.to_dict(),
    }), 200


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user = _load_user(get_jwt_identity())
    if not user or not user.is_active:
        return jsonify({"error": "user_inactive"}), 403
    additional_claims = {"role": user.role, "job_role": user.job_role}
    access = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    return jsonify({"access_token": access}), 200


@bp.post("/logout")
@jwt_required(verify_type=False)
def logout():
    jwt_data = get_jwt()
    revoke_token(
        jti=jwt_data["jti"],
        token_type=jwt_data.get("type", "access"),
        user_id=get_jwt_identity(),
    )
    return jsonify({"message": "logged_out"}), 200


@bp.get("/me")
@jwt_required()
def me():
    user = _load_user(get_jwt_identity())
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    payload = user.to_dict()
    payload["cluster_label"] = user.cluster_label
    return jsonify(payload), 200


@bp.patch("/me")
@jwt_required()
def update_me():
    user = _load_user(get_jwt_identity())
    if not user or not user.is_active:
        return jsonify({"error": "user_not_found"}), 404

    body = request.get_json(silent=True) or {}
    forbidden = {"email", "role", "is_active"}
    if forbidden.intersection(body.keys()):
        return jsonify({
            "error": "forbidden_field",
            "forbidden": sorted(forbidden.intersection(body.keys())),
        }), 403

    editable = ("first_name", "last_name", "username", "department", "job_role")
    changed: dict = {}
    for field in editable:
        if field not in body:
            continue
        raw = body.get(field)
        if raw is None:
            if field == "username":
                return jsonify({"error": "validation_failed", "field": field}), 400
            setattr(user, field, None)
            changed[field] = None
            continue
        value = sanitize_string(raw)
        if value is None:
            continue
        if field == "username":
            value = value.strip().lower()
            if not USERNAME_RE.match(value):
                return jsonify({
                    "error": "validation_failed", "field": "username",
                }), 400
            clash = User.query.filter(
                User.username == value, User.id != user.id
            ).first()
            if clash is not None:
                return jsonify({"error": "username_exists"}), 409
        elif len(value) > 120:
            return jsonify({"error": "validation_failed", "field": field}), 400
        setattr(user, field, value)
        changed[field] = value

    db.session.commit()
    return jsonify({"user": user.to_dict(), "updated": list(changed.keys())}), 200


@bp.post("/change-password")
@limiter.limit("5/hour")
@jwt_required()
def change_password():
    user = _load_user(get_jwt_identity())
    if not user or not user.is_active:
        return jsonify({"error": "user_not_found"}), 404

    body = request.get_json(silent=True) or {}
    current = body.get("current_password") or ""
    new = body.get("new_password") or ""

    if not user.check_password(current):
        return jsonify({"error": "invalid_credentials"}), 401
    if current == new:
        return jsonify({
            "error": "validation_failed", "field": "new_password",
            "message": "new_password must differ from current_password",
        }), 400
    if not PASSWORD_RE.match(new):
        return jsonify({
            "error": "validation_failed",
            "details": {"new_password": [
                "Password must be at least 12 chars and include uppercase, "
                "lowercase, digit, and special character.",
            ]},
        }), 400

    user.set_password(new)
    db.session.commit()
    return jsonify({"message": "password_changed"}), 200


@bp.post("/forgot-password")
@limiter.limit("5/hour")
def forgot_password():
    """File a password-reset request; an admin reviews and issues a token."""
    body = request.get_json(silent=True) or {}
    identifier = (body.get("identifier") or body.get("email") or "").strip().lower()
    if not identifier:
        return jsonify({"error": "validation_failed", "field": "identifier"}), 400

    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()
    if user is None:
        # Don't expose account existence.
        return jsonify({"status": "queued"}), 202

    existing = (
        PasswordResetRequest.query
        .filter_by(user_id=user.id, status=STATUS_PENDING)
        .first()
    )
    if existing is None:
        pr = PasswordResetRequest(user_id=user.id, status=STATUS_PENDING)
        db.session.add(pr)
        db.session.commit()
    return jsonify({"status": "queued"}), 202


@bp.post("/reset-password")
@limiter.limit("10/hour")
def reset_password():
    body = request.get_json(silent=True) or {}
    token = (body.get("token") or "").strip()
    new_password = body.get("new_password") or ""

    pr = PasswordResetRequest.verify_token(token)
    if pr is None:
        return jsonify({"error": "invalid_or_expired_token"}), 400
    if not PASSWORD_RE.match(new_password):
        return jsonify({
            "error": "validation_failed",
            "details": {"new_password": [
                "Password must be at least 12 chars and include uppercase, "
                "lowercase, digit, and special character.",
            ]},
        }), 400

    user = db.session.get(User, pr.user_id)
    if user is None:
        return jsonify({"error": "user_not_found"}), 404

    user.set_password(new_password)
    reset_login_state(user)
    pr.status = STATUS_CONSUMED
    pr.consumed_at = datetime.utcnow()
    pr.token_hash = None
    db.session.commit()
    return jsonify({"message": "password_reset"}), 200
