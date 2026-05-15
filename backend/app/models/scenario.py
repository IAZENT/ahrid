"""Scenario model — MCQ/TF/identify_threat training items."""
from __future__ import annotations

from app.extensions import db
from app.models.base import TimestampMixin, uuid_fk, uuid_pk

CATEGORIES = (
    "phishing_email",
    "smishing",
    "vishing",
    "physical_security",
    "password_hygiene",
    "usb_baiting",
    "social_engineering",
    "data_handling",
)
DIFFICULTIES = (1, 2, 3)

QUESTION_TYPES = ("mcq", "true_false", "identify_threat")
TARGET_ROLES = (
    "all", "receptionist", "accountant", "hr", "it",
    "finance", "sales", "management",
)
VISUAL_TYPES = ("email_screenshot", "login_page", "invoice", "sms", "none")
SOURCES = ("manual", "phishstats", "openphish", "otx", "urlscan")


class Scenario(db.Model, TimestampMixin):
    __tablename__ = "scenarios"

    id = uuid_pk()

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    visual_type = db.Column(db.String(50), nullable=True)
    visual_html = db.Column(db.Text, nullable=True)

    question_type = db.Column(db.String(20), nullable=False, default="mcq")
    category = db.Column(db.String(50), nullable=False, index=True)
    difficulty = db.Column(db.Integer, nullable=False, index=True)
    target_roles = db.Column(db.String(200), nullable=False, default="all", index=True)

    correct_answer = db.Column(db.String(1), nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)

    explanation = db.Column(db.Text, nullable=False)
    red_flags = db.Column(db.Text, nullable=True)
    learning_tip = db.Column(db.String(500), nullable=True)

    tf_statement = db.Column(db.Text, nullable=True)

    source = db.Column(db.String(50), nullable=False, default="manual")
    threat_url = db.Column(db.String(2000), nullable=True)
    threat_brand = db.Column(db.String(100), nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    times_served = db.Column(db.Integer, nullable=False, default=0)
    times_correct = db.Column(db.Integer, nullable=False, default=0)

    threat_feed_id = uuid_fk("threat_feed_entries.id", nullable=True)
    threat_feed = db.relationship("ThreatFeedEntry", back_populates="scenario", uselist=False)
    attempts = db.relationship(
        "Attempt", back_populates="scenario", cascade="all, delete-orphan", lazy="dynamic"
    )

    @property
    def accuracy_rate(self) -> float:
        if not self.times_served:
            return 0.0
        return round(self.times_correct / self.times_served, 4)

    def applies_to_role(self, job_role: str | None) -> bool:
        roles = {r.strip().lower() for r in (self.target_roles or "all").split(",")}
        if "all" in roles:
            return True
        return (job_role or "").lower() in roles

    def to_public_dict(self) -> dict:
        d = {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "visual_type": self.visual_type,
            "visual_html": self.visual_html,
            "question_type": self.question_type,
            "category": self.category,
            "difficulty": self.difficulty,
            "options": {
                "A": self.option_a or "",
                "B": self.option_b or "",
                "C": self.option_c or "",
                "D": self.option_d or "",
            },
        }
        if self.tf_statement:
            d["tf_statement"] = self.tf_statement
        return d

    def to_dict(self) -> dict:
        d = self.to_public_dict()
        d.update({
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "red_flags": self.red_flags,
            "learning_tip": self.learning_tip,
            "tf_statement": self.tf_statement,
            "target_roles": self.target_roles,
            "source": self.source,
            "threat_url": self.threat_url,
            "threat_brand": self.threat_brand,
            "is_active": self.is_active,
            "times_served": self.times_served,
            "times_correct": self.times_correct,
            "accuracy_rate": self.accuracy_rate,
        })
        return d
