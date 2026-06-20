"""Scores API  personal risk + cluster (employee view)."""
from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, g, jsonify

from app.extensions import db
from app.models.attempt import Attempt
from app.models.cluster import CLUSTER_ARCHETYPES
from app.models.risk_score import RiskScore
from app.services.random_forest_model import RiskForestPredictor
from app.utils.decorators import active_user_required

bp = Blueprint("scores", __name__, url_prefix="/api/v1/scores")


@bp.get("/me")
@active_user_required
def me():
    user = g.current_user
    score: RiskScore | None = user.risk_score

    if score is None:
        return jsonify({
            "risk_level": "unknown",
            "message": "Not enough attempts yet to compute a risk score.",
        }), 200

    predictor = RiskForestPredictor()
    rf_pred = predictor.predict(user.id) if predictor.is_ready else None

    return jsonify({
        **score.to_dict(),
        "rf_prediction": rf_pred,
        "cluster_label": user.cluster_label,
        "shap_explanation": score.shap_summary,
    }), 200


@bp.get("/me/history")
@active_user_required
def history():
    user = g.current_user
    now = datetime.utcnow()
    buckets: list[dict] = []

    for w in range(8):
        end = now - timedelta(days=7 * w)
        start = end - timedelta(days=7)
        rows = (
            db.session.query(Attempt.is_correct)
            .filter(
                Attempt.user_id == user.id,
                Attempt.created_at >= start,
                Attempt.created_at < end,
            )
            .all()
        )
        if rows:
            correct = sum(1 for (c,) in rows if c)
            accuracy = round(correct / len(rows), 4)
            composite = round((1 - accuracy) * 100, 2)
        else:
            accuracy = None
            composite = None
        buckets.append({
            "week_start": start.date().isoformat(),
            "week_end": end.date().isoformat(),
            "accuracy": accuracy,
            "composite_score": composite,
            "attempt_count": len(rows),
        })

    return jsonify({"history": list(reversed(buckets))}), 200


@bp.get("/me/cluster")
@active_user_required
def cluster():
    user = g.current_user
    label = user.cluster_label
    if not label:
        return jsonify({
            "cluster_id": None,
            "archetype_label": None,
            "message": "You haven't been clustered yet. Complete more training first.",
        }), 200

    meta = next(
        ((cid, m) for cid, m in CLUSTER_ARCHETYPES.items() if m["label"] == label),
        None,
    )
    if meta is None:
        return jsonify({"cluster_id": None, "archetype_label": label}), 200

    cid, m = meta
    return jsonify({
        "cluster_id": cid,
        "archetype_label": m["label"],
        "archetype_description": m["description"],
        "archetype_colour": m["colour"],
        "archetype_icon": m["icon"],
        "intervention": m["intervention"],
        "assigned_at": (
            user.cluster_assigned_at.isoformat()
            if user.cluster_assigned_at else None
        ),
    }), 200
