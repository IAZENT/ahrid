"""Health check endpoint  reports DB + RF + KMeans + timestamp."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from app.extensions import db
from app.models.attempt import Attempt

bp = Blueprint("health", __name__, url_prefix="/api/v1")

APP_VERSION = "0.9.0"  # bumped each phase


def _resolve(path_key: str, default: str) -> Path:
    path = Path(current_app.config.get(path_key, default))
    if not path.is_absolute():
        path = Path(current_app.root_path).parent / path
    return path


@bp.get("/health")
def health():
    # 1. DB round-trip
    db_ok = True
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001  we want to flatten any driver error
        db_ok = False

    # 2. Model artefacts
    rf_path = _resolve("RF_MODEL_PATH", "ml_models/risk_rf_model.pkl")
    kmeans_path = _resolve("KMEANS_MODEL_PATH", "ml_models/user_clusters.pkl")

    # 3. Training sample counts
    real_samples = 0
    total_samples = 0
    threshold = current_app.config.get("MIN_TRAINING_SAMPLES", 20)
    try:
        total_samples = Attempt.query.count()
        real_samples = Attempt.query.filter_by(is_synthetic=False).count()
    except Exception:
        pass  # table may not exist yet

    rf_exists = rf_path.exists()
    kmeans_exists = kmeans_path.exists()

    body = {
        "status": "ok" if db_ok else "degraded",
        "version": APP_VERSION,
        "db": "up" if db_ok else "down",
        # Backwards-compatible fields (tests expect these)
        "rf_model_loaded": rf_exists,
        "kmeans_loaded": kmeans_exists,
        # New detailed ML info
        "ml": {
            "random_forest": "trained" if rf_exists else "untrained",
            "kmeans": "trained" if kmeans_exists else "untrained",
            "training_samples_real": real_samples,
            "training_samples_total": total_samples,
            "threshold": threshold,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return jsonify(body), (200 if db_ok else 503)
