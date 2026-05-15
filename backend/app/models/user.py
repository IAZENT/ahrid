"""User model — auth, role, KMeans cluster label."""
from __future__ import annotations

from datetime import datetime

from app.extensions import bcrypt, db
from app.models.base import TimestampMixin, uuid_pk

ROLES = ("employee", "manager", "admin")
JOB_ROLES = (
    "receptionist",
    "accountant",
    "hr",
    "it",
    "finance",
    "sales",
    "management",
)


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = uuid_pk()

    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)

    role = db.Column(db.String(20), nullable=False, default="employee")
    job_role = db.Column(db.String(80), nullable=True)
    department = db.Column(db.String(80), nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)

    last_login = db.Column(db.DateTime, nullable=True)
    failed_login_count = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    consent_given = db.Column(db.Boolean, nullable=False, default=False)
    consent_timestamp = db.Column(db.DateTime, nullable=True)

    cluster_label = db.Column(db.String(50), nullable=True)
    cluster_assigned_at = db.Column(db.DateTime, nullable=True)

    attempts = db.relationship(
        "Attempt", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )
    risk_score = db.relationship(
        "RiskScore", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    clusters = db.relationship(
        "UserCluster", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    def set_password(self, plain: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(plain).decode("utf-8")

    def check_password(self, plain: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, plain)

    @property
    def is_locked(self) -> bool:
        return bool(self.locked_until and self.locked_until > datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "job_role": self.job_role,
            "department": self.department,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "consent_given": self.consent_given,
            "cluster_label": self.cluster_label,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email} role={self.role}>"
