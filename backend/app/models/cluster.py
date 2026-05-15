"""UserCluster model  KMeans assignment + behavioural archetype label."""
from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models.base import uuid_fk, uuid_pk

ARCHETYPES: dict[int, dict[str, str]] = {
    0: {
        "label": "Overconfident Clicker",
        "description": (
            "Answers quickly but gets it wrong. High risk of clicking phishing "
            "links in the real world because they trust their instincts without "
            "checking."
        ),
        "colour": "#EF4444",
        "icon": "zap",
        "intervention": (
            "Needs slowed-down scenario practice with explicit red-flag "
            "identification training."
        ),
    },
    1: {
        "label": "Cautious Learner",
        "description": (
            "Takes time to think and mostly gets it right. Improving steadily. "
            "On track to become a security asset."
        ),
        "colour": "#22C55E",
        "icon": "shield-check",
        "intervention": (
            "Needs challenge scenarios at higher difficulty to build advanced "
            "recognition skills."
        ),
    },
    2: {
        "label": "Inconsistent Performer",
        "description": (
            "Excellent in some categories but has dangerous blind spots in "
            "others. May have false confidence."
        ),
        "colour": "#F59E0B",
        "icon": "alert-triangle",
        "intervention": (
            "Needs targeted training in their weakest categories with extra "
            "visual scenario practice."
        ),
    },
    3: {
        "label": "Resilient Defender",
        "description": (
            "Fast, accurate, and consistent across all categories. Completed "
            "streak training. A security role model."
        ),
        "colour": "#3B82F6",
        "icon": "award",
        "intervention": (
            "Can act as a peer mentor. Needs advanced threat scenarios to stay "
            "engaged."
        ),
    },
    4: {
        "label": "Disengaged Completer",
        "description": (
            "Completes sessions slowly with inconsistent results. Likely not "
            "focused during training. High hidden risk."
        ),
        "colour": "#8B5CF6",
        "icon": "eye-off",
        "intervention": (
            "Needs shorter, more frequent gamified sessions. Manager should "
            "check in personally."
        ),
    },
}

# Alias matching the master-doc constant name so both services and tests can
# import it under either name without duplicating the source of truth.
CLUSTER_ARCHETYPES = ARCHETYPES


class UserCluster(db.Model):
    """Append-only history of K-Means cluster assignments for a user."""

    __tablename__ = "user_clusters"

    id = uuid_pk()
    user_id = uuid_fk("users.id", nullable=False)

    cluster_id = db.Column(db.Integer, nullable=False, index=True)
    archetype_label = db.Column(db.String(100), nullable=False)
    archetype_description = db.Column(db.Text, nullable=False)

    feature_vector = db.Column(db.Text, nullable=False)  # JSON

    clustered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="clusters")

    @classmethod
    def archetype_for(cls, cluster_id: int) -> dict[str, str]:
        return ARCHETYPES.get(
            cluster_id,
            {"label": "Unclassified", "description": "No archetype assigned."},
        )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "cluster_id": self.cluster_id,
            "archetype_label": self.archetype_label,
            "archetype_description": self.archetype_description,
            "feature_vector": self.feature_vector,
            "clustered_at": self.clustered_at.isoformat() if self.clustered_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<UserCluster user={self.user_id} c{self.cluster_id} {self.archetype_label}>"
