"""Authentication-side security helpers: lockout policy + token revocation."""
from __future__ import annotations

from datetime import datetime, timedelta

from app.extensions import db
from app.models.token_blocklist import TokenBlocklist
from app.models.user import User

MAX_FAILED_LOGINS = 5
LOCKOUT_DURATION = timedelta(minutes=15)


def register_failed_login(user: User) -> None:
    """Increment the user's failed-login counter and lock if threshold hit."""
    user.failed_login_count = (user.failed_login_count or 0) + 1
    if user.failed_login_count >= MAX_FAILED_LOGINS:
        user.locked_until = datetime.utcnow() + LOCKOUT_DURATION
        user.failed_login_count = 0


def reset_login_state(user: User) -> None:
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()


def revoke_token(jti: str, token_type: str, user_id: str | None = None) -> None:
    """Insert ``jti`` into the blocklist so subsequent uses fail."""
    db.session.add(
        TokenBlocklist(jti=jti, token_type=token_type, user_id=user_id)
    )
    db.session.commit()


def is_token_revoked(jti: str) -> bool:
    return (
        db.session.query(TokenBlocklist.id).filter_by(jti=jti).first() is not None
    )
