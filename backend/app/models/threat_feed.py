"""ThreatFeedEntry model  raw OSINT intel ingested from external feeds."""
from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models.base import uuid_pk

SOURCES = ("phishstats", "openphish", "otx", "urlscan")


class ThreatFeedEntry(db.Model):
    __tablename__ = "threat_feed_entries"

    id = uuid_pk()

    source = db.Column(db.String(50), nullable=False, index=True)
    original_url = db.Column(db.String(2000), nullable=False)
    target_brand = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=True, index=True)
    lure_type = db.Column(db.String(100), nullable=True)

    otx_pulse_name = db.Column(db.String(200), nullable=True)
    urlscan_verdict = db.Column(db.String(50), nullable=True)

    was_converted = db.Column(db.Boolean, nullable=False, default=False, index=True)

    ingested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    scenario = db.relationship("Scenario", back_populates="threat_feed", uselist=False)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "source": self.source,
            "original_url": self.original_url,
            "target_brand": self.target_brand,
            "category": self.category,
            "lure_type": self.lure_type,
            "otx_pulse_name": self.otx_pulse_name,
            "urlscan_verdict": self.urlscan_verdict,
            "was_converted": self.was_converted,
            "ingested_at": self.ingested_at.isoformat() if self.ingested_at else None,
        }
