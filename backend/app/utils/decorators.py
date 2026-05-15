"""Authorisation decorators built on top of Flask-JWT-Extended."""
from __future__ import annotations

import uuid
from functools import wraps

from flask import g, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app.extensions import db
from app.models.user import User


def _load_user(user_id):
    if not user_id:
        return None
    try:
        return db.session.get(User, uuid.UUID(user_id))
    except (ValueError, TypeError):
        return None


def require_role(*roles: str):
    """Allow the request only if the JWT 'role' claim is in ``roles``."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in roles:
                return jsonify({"error": "forbidden", "required_roles": list(roles)}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


admin_required = require_role("admin")
manager_required = require_role("manager", "admin")


def active_user_required(fn):
    """Ensure the JWT subject still maps to an active user; load it onto ``g``."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = _load_user(get_jwt_identity())
        if not user or not user.is_active:
            return jsonify({"error": "user_inactive"}), 403
        g.current_user = user
        g.job_role = user.job_role
        return fn(*args, **kwargs)

    return wrapper


def job_role_context(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        g.job_role = get_jwt().get("job_role")
        return fn(*args, **kwargs)

    return wrapper
