"""Evaluation API — HAIS-Q awareness, SUS, RF metrics, awareness uplift.

Master spec §6.3-§6.5. All employee-facing routes require an authenticated
session; admin-only routes additionally require ``admin_required``.
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, stdev

from flask import Blueprint, current_app, g, jsonify, request

from app.extensions import db
from app.models.awareness_assessment import (
    AwarenessAssessment, PHASES, QUESTIONS as AWARENESS_QUESTIONS, score_awareness,
)
from app.models.sus_response import (
    SUSResponse, QUESTIONS as SUS_QUESTIONS, calculate_sus, sus_grade,
)
from app.models.user import User
from app.utils.decorators import active_user_required, admin_required

bp = Blueprint("evaluation", __name__, url_prefix="/api/v1/eval")


# ──────────────────────────── awareness ────────────────────────────

def _validate_likert(payload: dict, n: int) -> tuple[dict | None, str | None]:
    out: dict[str, int] = {}
    for i in range(1, n + 1):
        v = payload.get(f"q{i}")
        if v is None:
            return None, f"missing q{i}"
        try:
            iv = int(v)
        except (TypeError, ValueError):
            return None, f"q{i} must be an integer"
        if not 1 <= iv <= 5:
            return None, f"q{i} must be 1..5"
        out[f"q{i}"] = iv
    return out, None


@bp.get("/awareness/questions")
@active_user_required
def awareness_questions():
    return jsonify({
        "questions": [
            {"id": f"q{i+1}", "text": q} for i, q in enumerate(AWARENESS_QUESTIONS)
        ],
        "scale": [
            {"value": 1, "label": "Strongly Disagree"},
            {"value": 2, "label": "Disagree"},
            {"value": 3, "label": "Neutral"},
            {"value": 4, "label": "Agree"},
            {"value": 5, "label": "Strongly Agree"},
        ],
    }), 200


@bp.get("/awareness/me")
@active_user_required
def awareness_me():
    rows = AwarenessAssessment.query.filter_by(user_id=g.current_user.id).all()
    out = {p: None for p in PHASES}
    for r in rows:
        out[r.phase] = r.to_dict()
    delta = (
        out["post"]["score"] - out["pre"]["score"]
        if out["pre"] and out["post"] else None
    )
    return jsonify({**out, "delta": delta}), 200


@bp.post("/awareness")
@active_user_required
def awareness_submit():
    body = request.get_json(silent=True) or {}
    phase = (body.get("phase") or "").lower()
    if phase not in PHASES:
        return jsonify({"error": "validation_failed", "field": "phase"}), 400
    responses, err = _validate_likert(body.get("responses") or {}, n=7)
    if err:
        return jsonify({"error": "validation_failed", "field": err}), 400

    existing = AwarenessAssessment.query.filter_by(
        user_id=g.current_user.id, phase=phase,
    ).first()
    if existing is not None:
        return jsonify({"error": "already_submitted", "phase": phase}), 409

    score = score_awareness(responses)
    row = AwarenessAssessment(
        user_id=g.current_user.id, phase=phase,
        responses=responses, score=score,
    )
    db.session.add(row)
    db.session.commit()
    return jsonify(row.to_dict()), 201


# ─────────────────────────────── SUS ───────────────────────────────

@bp.get("/sus/questions")
@active_user_required
def sus_questions():
    return jsonify({
        "questions": [
            {"id": f"q{i+1}", "text": q} for i, q in enumerate(SUS_QUESTIONS)
        ],
    }), 200


@bp.post("/sus")
@active_user_required
def sus_submit():
    body = request.get_json(silent=True) or {}
    responses, err = _validate_likert(body.get("responses") or {}, n=10)
    if err:
        return jsonify({"error": "validation_failed", "field": err}), 400

    score = calculate_sus(responses)
    row = SUSResponse(
        user_id=g.current_user.id,
        responses=responses,
        sus_score=score,
    )
    db.session.add(row)
    db.session.commit()
    return jsonify({**row.to_dict(), "grade": sus_grade(score)}), 201


# ─────────────────────────── admin metrics ──────────────────────────

@bp.get("/rf-metrics")
@admin_required
@active_user_required
def rf_metrics():
    """Return the metrics emitted by ``train_models.py`` plus a baseline.

    The trainer writes ``rf_metrics.json`` next to the pickled model;
    we read that file rather than re-running the train/test split here.
    """
    rf_path = Path(current_app.config.get("RF_MODEL_PATH", "ml_models/risk_rf_model.pkl"))
    if not rf_path.is_absolute():
        rf_path = Path(current_app.root_path).parent / rf_path
    metrics_path = rf_path.with_name("rf_metrics.json")

    if not metrics_path.exists():
        return jsonify({"error": "not_trained", "message": "Train the RF first."}), 404

    raw = json.loads(metrics_path.read_text())
    report: dict = raw.get("classification_report", {})
    f1 = float((report.get("weighted avg") or {}).get("f1-score") or 0.0)
    n_test = int(raw.get("n_samples", 0))

    # Rule-based baseline: same labels, just thresholding overall_accuracy.
    # We don't actually run a held-out set here; we approximate using the
    # current per-user RiskScore rows for an honest comparison.
    from app.models.risk_score import RiskScore
    rows = RiskScore.query.all()
    correct_baseline = 0
    n_baseline = 0
    for r in rows:
        if r.attempts_count == 0:
            continue
        # acc = 1 - composite/100 (composite is 0..100, lower is better)
        acc = max(0.0, 1.0 - r.composite_score / 100.0)
        if acc < 0.40:
            pred = "high"
        elif acc < 0.70:
            pred = "medium"
        else:
            pred = "low"
        # The rule only knows {low, medium, high}; treat critical as high.
        actual = "high" if r.risk_level == "critical" else r.risk_level
        if pred == actual:
            correct_baseline += 1
        n_baseline += 1
    baseline_f1 = round(correct_baseline / n_baseline, 3) if n_baseline else 0.0

    class_distribution: dict[str, int] = {}
    for cls, info in report.items():
        if cls in ("accuracy", "macro avg", "weighted avg"):
            continue
        if isinstance(info, dict) and "support" in info:
            class_distribution[cls] = int(info["support"])

    return jsonify({
        "f1_weighted": round(f1, 3),
        "baseline_f1": baseline_f1,
        "improvement_pp": round((f1 - baseline_f1) * 100, 1),
        "n_test_samples": n_test,
        "class_distribution": class_distribution,
        "trained_at": raw.get("trained_at"),
    }), 200


@bp.get("/awareness-uplift")
@admin_required
@active_user_required
def awareness_uplift():
    rows = AwarenessAssessment.query.all()
    by_user: dict[str, dict[str, float]] = {}
    for r in rows:
        by_user.setdefault(str(r.user_id), {})[r.phase] = r.score

    pairs = [(d["pre"], d["post"]) for d in by_user.values() if "pre" in d and "post" in d]
    n = len(pairs)
    summary: dict = {
        "n_participants": n,
        "mean_pre_score": round(mean(p for p, _ in pairs), 2) if pairs else None,
        "mean_post_score": round(mean(q for _, q in pairs), 2) if pairs else None,
        "mean_delta": round(mean(q - p for p, q in pairs), 2) if pairs else None,
    }

    if n >= 2:
        deltas = [q - p for p, q in pairs]
        sd = stdev(deltas) if len(deltas) >= 2 else 0.0
        summary["cohens_d"] = round(mean(deltas) / sd, 3) if sd > 0 else None
        try:
            from scipy import stats  # type: ignore[import-not-found]
            t, p_value = stats.ttest_rel([a for a, _ in pairs], [b for _, b in pairs])
            summary["t_statistic"] = round(float(t), 3)
            summary["p_value"] = round(float(p_value), 4)
        except Exception:
            summary["p_value"] = None
    else:
        summary["cohens_d"] = None
        summary["p_value"] = None

    summary["participants"] = [
        {"user_id": uid, "pre": d["pre"], "post": d["post"], "delta": round(d["post"] - d["pre"], 2)}
        for uid, d in by_user.items() if "pre" in d and "post" in d
    ]
    return jsonify(summary), 200


@bp.get("/sus-summary")
@admin_required
@active_user_required
def sus_summary():
    scores = [r.sus_score for r in SUSResponse.query.all()]
    n = len(scores)
    if n == 0:
        return jsonify({"n": 0, "mean": None, "grade": None, "distribution": {}}), 200
    mean_score = round(mean(scores), 2)
    distribution: dict[str, int] = {"Awful": 0, "Poor": 0, "OK": 0, "Good": 0, "Excellent": 0}
    for s in scores:
        distribution[sus_grade(s)] += 1
    return jsonify({
        "n": n,
        "mean": mean_score,
        "grade": sus_grade(mean_score),
        "distribution": distribution,
    }), 200


# ───────────────────────── transparency policy ─────────────────────────

DEFAULT_POLICY = """\
AHRID Transparency Notice

What data is collected:
  Your quiz responses and response times during training sessions.

How risk scores are calculated:
  A machine-learning model trained on quiz performance patterns. The
  feature contributions for your most recent score are visible on your
  *My Score* page (SHAP explanation).

Who can see your score:
  Only you (employees) and anonymised aggregates (managers).

How to query or dispute your score:
  Contact your administrator.

Data retention:
  Personal data is deleted at the end of the study.
"""


@bp.get("/transparency-policy", strict_slashes=False)
def transparency_policy():
    """Public endpoint — no auth required (Master spec §7)."""
    text = current_app.config.get("TRANSPARENCY_POLICY", DEFAULT_POLICY)
    return jsonify({"policy": text}), 200
