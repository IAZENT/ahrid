"""Manual RF + KMeans trainer for the BSc build.

Usage:
    python train_models.py

Re-trains the Random Forest risk classifier and the K-Means user
clusterer from real attempt data. Both are guarded by minimum-sample
thresholds (config: MIN_TRAINING_SAMPLES); training is skipped with a
clear message when the floor isn't met.

Persists artefacts to ``RF_MODEL_PATH`` / ``KMEANS_MODEL_PATH`` plus
sibling JSON files describing the feature contract and metrics.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np

from app import create_app
from app.extensions import db
from app.models.attempt import Attempt
from app.services.kmeans_clustering import reassign_all_users, train_kmeans
from app.services.random_forest_model import (
    FEATURE_NAMES as RF_FEATURE_NAMES,
    RISK_LEVEL_ENCODING,
    build_feature_vector_for_user,
)
from app.services.risk_scorer import recalculate_for_user
from sqlalchemy import func


MIN_ATTEMPTS_FOR_USER = 10


def prepare_training_data():
    """Return (X, y) numpy arrays for RF training, or (None, None) if too small."""
    user_ids = [
        uid for (uid,) in (
            db.session.query(Attempt.user_id)
            .group_by(Attempt.user_id)
            .having(func.count(Attempt.id) >= MIN_ATTEMPTS_FOR_USER)
            .all()
        )
    ]
    rows: list[np.ndarray] = []
    labels: list[int] = []
    for uid in user_ids:
        # Make sure each user has a current RiskScore so we have a label.
        score = recalculate_for_user(uid)
        db.session.commit()
        if score.risk_level not in RISK_LEVEL_ENCODING:
            continue
        vec = build_feature_vector_for_user(uid)
        if vec is None:
            continue
        rows.append(vec)
        labels.append(RISK_LEVEL_ENCODING[score.risk_level])
    if not rows:
        return None, None
    return np.vstack(rows), np.array(labels)


def train_random_forest(X, y, model_path: Path) -> dict:
    from collections import Counter
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if len(set(y)) > 1 else None,
    )

    # SMOTE oversampling — addresses class imbalance per master spec §9.
    # We log the before/after distribution so the methodology chapter
    # can report exact numbers. SMOTE requires k_neighbors < smallest
    # minority class size, so we adapt k dynamically and skip if any
    # class has fewer than 2 samples (in which case SMOTE is undefined).
    pre_dist = dict(Counter(int(v) for v in y_train))
    smote_status = {"applied": False, "before": pre_dist, "after": pre_dist}
    smallest = min(pre_dist.values()) if pre_dist else 0
    if smallest >= 2 and len(pre_dist) >= 2:
        try:
            from imblearn.over_sampling import SMOTE  # type: ignore[import-not-found]
            k = max(1, min(5, smallest - 1))
            smote = SMOTE(random_state=42, k_neighbors=k)
            X_train, y_train = smote.fit_resample(X_train, y_train)
            post_dist = dict(Counter(int(v) for v in y_train))
            smote_status = {"applied": True, "k_neighbors": k,
                            "before": pre_dist, "after": post_dist}
            print(f"SMOTE: {pre_dist} → {post_dist} (k={k})")
        except Exception as exc:
            print(f"SMOTE skipped: {type(exc).__name__}: {exc}")
    else:
        print(f"SMOTE skipped: smallest class={smallest} (need >= 2).")

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = float(accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    import joblib
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    model_path.with_name("rf_features.json").write_text(json.dumps(RF_FEATURE_NAMES))
    model_path.with_name("rf_metrics.json").write_text(json.dumps({
        "trained_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "n_samples": int(X.shape[0]),
        "n_test_samples": int(X_test.shape[0]),
        "accuracy": accuracy,
        "classification_report": report,
        "feature_names": RF_FEATURE_NAMES,
        "smote": smote_status,
    }, indent=2))
    print(f"RF trained on {X.shape[0]} samples → accuracy={accuracy:.3f}")
    return {"accuracy": accuracy, "n_samples": int(X.shape[0])}


def main() -> None:
    app = create_app()
    with app.app_context():
        from flask import current_app
        rf_path = Path(current_app.config.get("RF_MODEL_PATH", "ml_models/risk_rf_model.pkl"))

        X, y = prepare_training_data()
        if X is None:
            print(f"RF: not enough labelled users (need ≥{MIN_ATTEMPTS_FOR_USER} attempts each).")
        elif len(set(y.tolist())) < 2:
            print("RF: only one risk class present — skipping.")
        else:
            train_random_forest(X, y, rf_path)

        kmeans_result = train_kmeans()
        if kmeans_result is None:
            print("KMeans: not enough users to cluster — skipping.")
        else:
            n = reassign_all_users()
            print(f"KMeans: trained + assigned {n} users (inertia={kmeans_result['inertia']:.3f}).")


if __name__ == "__main__":
    main()
