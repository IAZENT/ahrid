"""K-Means user-clustering service (BSc scope).

5 archetypes, 6-feature vector. Multi-tenancy and gamification-derived
features have been dropped; ``streak_consistency`` is now derived from
``session_id`` activity over time instead of a streak counter.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from flask import current_app
from sqlalchemy import func

from app.extensions import db
from app.models.attempt import Attempt
from app.models.cluster import CLUSTER_ARCHETYPES, UserCluster
from app.models.user import User

LOG = logging.getLogger(__name__)

FEATURE_NAMES: list[str] = [
    "avg_response_time_ms",
    "overall_accuracy",
    "accuracy_variance",
    "fast_attempt_rate",
    "total_sessions",
    "session_consistency",
]
N_FEATURES = len(FEATURE_NAMES)
assert N_FEATURES == 6, "KMeans feature contract drift"

N_CLUSTERS_DEFAULT = 5
MIN_ATTEMPTS_FOR_CLUSTER = 5
MIN_USERS_FOR_CLUSTERING = 3

# Below this median response time we treat an attempt as "fast/rushed"
# (the title's behavioural-proxy signal  BSc replacement for VADER).
FAST_RESPONSE_MS = 4000

# Winsorization cap for avg_response_time_ms before clustering math only
# (display values stay raw). Stops a single very-slow user from anchoring
# their own KMeans cluster instead of joining the nearest archetype.
RESPONSE_TIME_CLIP_PERCENTILE = 95


def _per_category_accuracy(attempts: list[Attempt]) -> list[float]:
    by_cat: dict[str, list[bool]] = {}
    for a in attempts:
        by_cat.setdefault(a.category, []).append(bool(a.is_correct))
    return [sum(vals) / len(vals) for vals in by_cat.values() if vals]


def build_feature_vector_for_user(user_id) -> np.ndarray | None:
    attempts: list[Attempt] = Attempt.query.filter_by(user_id=user_id).all()
    if len(attempts) < MIN_ATTEMPTS_FOR_CLUSTER:
        return None

    response_times = [a.response_time_ms for a in attempts if a.response_time_ms]
    avg_rt = float(np.mean(response_times)) if response_times else 0.0
    overall_acc = sum(1 for a in attempts if a.is_correct) / len(attempts)

    per_cat = _per_category_accuracy(attempts)
    accuracy_variance = float(np.std(per_cat)) if len(per_cat) > 1 else 0.0

    fast_rate = (
        sum(1 for a in attempts if a.response_time_ms and a.response_time_ms < FAST_RESPONSE_MS)
        / len(attempts)
    )

    total_sessions = (
        db.session.query(func.count(func.distinct(Attempt.session_id)))
        .filter(Attempt.user_id == user_id)
        .scalar()
        or 0
    )

    # Session consistency: fraction of attempts that share the modal session
    # length (1.0 if every session has the same number of attempts; 0.0 if
    # they vary wildly). A simple proxy that does not require gamification.
    if total_sessions:
        rows = (
            db.session.query(Attempt.session_id, func.count(Attempt.id))
            .filter(Attempt.user_id == user_id)
            .group_by(Attempt.session_id)
            .all()
        )
        sizes = [int(c) for _, c in rows]
        modal = max(set(sizes), key=sizes.count) if sizes else 0
        same = sum(1 for s in sizes if s == modal)
        session_consistency = same / len(sizes) if sizes else 0.0
    else:
        session_consistency = 0.0

    return np.array(
        [
            avg_rt,
            overall_acc,
            accuracy_variance,
            fast_rate,
            float(total_sessions),
            float(session_consistency),
        ],
        dtype=float,
    )


def build_feature_dict_for_user(user_id) -> dict[str, float] | None:
    vec = build_feature_vector_for_user(user_id)
    if vec is None:
        return None
    return {name: float(v) for name, v in zip(FEATURE_NAMES, vec)}


def _default_model_path() -> str:
    try:
        return current_app.config["KMEANS_MODEL_PATH"]
    except RuntimeError:
        return os.environ.get("KMEANS_MODEL_PATH", "ml_models/user_clusters.pkl")


def _resolve_model_path(path: str | os.PathLike) -> Path:
    p = Path(path)
    if not p.is_absolute():
        try:
            p = Path(current_app.root_path).parent / p
        except RuntimeError:
            p = Path.cwd() / p
    return p


def train_kmeans(
    *,
    min_attempts_per_user: int = MIN_ATTEMPTS_FOR_CLUSTER,
    model_path: str | os.PathLike | None = None,
) -> dict[str, Any] | None:
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler

    user_ids = [
        uid for (uid,) in (
            db.session.query(Attempt.user_id)
            .group_by(Attempt.user_id)
            .having(func.count(Attempt.id) >= min_attempts_per_user)
            .all()
        )
    ]

    rows: list[np.ndarray] = []
    kept_ids: list[Any] = []
    for uid in user_ids:
        vec = build_feature_vector_for_user(uid)
        if vec is not None:
            rows.append(vec)
            kept_ids.append(uid)

    n_users = len(rows)
    if n_users < MIN_USERS_FOR_CLUSTERING:
        LOG.warning(
            "KMeans training skipped  only %d eligible users (need >= %d).",
            n_users, MIN_USERS_FOR_CLUSTERING,
        )
        return None

    n_clusters = min(N_CLUSTERS_DEFAULT, max(2, n_users // 2))

    X = np.vstack(rows)
    rt_clip = float(np.percentile(X[:, 0], RESPONSE_TIME_CLIP_PERCENTILE))
    X_clustering = X.copy()
    X_clustering[:, 0] = np.clip(X_clustering[:, 0], None, rt_clip)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clustering)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X_scaled)

    labels = kmeans.labels_
    cluster_sizes = {int(c): int((labels == c).sum()) for c in range(n_clusters)}

    silhouette: float | None = None
    if len(set(labels)) >= 2 and X.shape[0] > n_clusters:
        try:
            silhouette = float(silhouette_score(X_scaled, labels))
        except Exception as exc:  # noqa: BLE001
            LOG.warning("silhouette_score failed: %s", exc)

    bundle = {
        "scaler": scaler,
        "model": kmeans,
        "feature_names": FEATURE_NAMES,
        "n_clusters": n_clusters,
        "rt_clip": rt_clip,
        "trained_at": datetime.utcnow().isoformat(),
    }
    out_path = _resolve_model_path(model_path or _default_model_path())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, out_path)
    out_path.with_name("kmeans_features.json").write_text(json.dumps(FEATURE_NAMES))

    metrics_payload = {
        "trained_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "n_users": int(X.shape[0]),
        "n_features": int(X.shape[1]),
        "n_clusters": n_clusters,
        "inertia": float(kmeans.inertia_),
        "silhouette_score": silhouette,
        "cluster_sizes": cluster_sizes,
        "min_attempts_per_user": int(min_attempts_per_user),
        "feature_names": FEATURE_NAMES,
    }
    out_path.with_name("kmeans_metrics.json").write_text(
        json.dumps(metrics_payload, indent=2)
    )

    LOG.info(
        "KMeans trained on %d users → inertia=%.3f, silhouette=%s",
        X.shape[0], kmeans.inertia_,
        f"{silhouette:.3f}" if silhouette is not None else "n/a",
    )

    return {
        "inertia": float(kmeans.inertia_),
        "silhouette_score": silhouette,
        "cluster_sizes": cluster_sizes,
        "n_users": X.shape[0],
        "model_path": str(out_path),
    }


class UserClusterer:
    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = str(_resolve_model_path(model_path or _default_model_path()))
        self.scaler: Any = None
        self.model: Any = None
        self.feature_names: list[str] = FEATURE_NAMES
        self.rt_clip: float | None = None
        self.load()

    def load(self) -> None:
        try:
            bundle = joblib.load(self.model_path)
            self.scaler = bundle["scaler"]
            self.model = bundle["model"]
            self.feature_names = bundle.get("feature_names", FEATURE_NAMES)
            self.rt_clip = bundle.get("rt_clip")
            LOG.info("Loaded KMeans bundle from %s", self.model_path)
        except FileNotFoundError:
            self.scaler = None
            self.model = None
            LOG.info("KMeans bundle not found  clusterer in pass-through mode")

    @property
    def is_ready(self) -> bool:
        return self.scaler is not None and self.model is not None

    def predict_cluster(self, user_id) -> int | None:
        if not self.is_ready:
            return None
        vec = build_feature_vector_for_user(user_id)
        if vec is None:
            return None
        vec_clustering = vec.copy()
        if self.rt_clip is not None:
            vec_clustering[0] = min(vec_clustering[0], self.rt_clip)
        scaled = self.scaler.transform(vec_clustering.reshape(1, -1))
        return int(self.model.predict(scaled)[0])


def assign_user_to_cluster(user_id) -> dict | None:
    clusterer = UserClusterer()
    if not clusterer.is_ready:
        return None
    features = build_feature_dict_for_user(user_id)
    if features is None:
        return None
    cluster_id = clusterer.predict_cluster(user_id)
    if cluster_id is None:
        return None

    archetype = CLUSTER_ARCHETYPES.get(cluster_id, {})
    label = archetype.get("label", "Unclassified")
    description = archetype.get("description", "")
    colour = archetype.get("colour", "#6B7280")
    icon = archetype.get("icon", "help-circle")
    intervention = archetype.get("intervention", "")

    user = db.session.get(User, user_id)
    if user is not None:
        user.cluster_label = label
        user.cluster_assigned_at = datetime.utcnow()

    db.session.add(
        UserCluster(
            user_id=user_id,
            cluster_id=cluster_id,
            archetype_label=label,
            archetype_description=description,
            feature_vector=json.dumps(features),
        )
    )
    db.session.commit()

    return {
        "cluster_id": cluster_id,
        "archetype_label": label,
        "archetype_description": description,
        "archetype_colour": colour,
        "archetype_icon": icon,
        "intervention": intervention,
        "feature_values": features,
    }


def reassign_all_users(*, min_attempts_per_user: int = MIN_ATTEMPTS_FOR_CLUSTER) -> int:
    clusterer = UserClusterer()
    if not clusterer.is_ready:
        return 0
    user_ids = [
        uid for (uid,) in (
            db.session.query(Attempt.user_id)
            .group_by(Attempt.user_id)
            .having(func.count(Attempt.id) >= min_attempts_per_user)
            .all()
        )
    ]
    n = 0
    for uid in user_ids:
        if assign_user_to_cluster(uid) is not None:
            n += 1
    LOG.info("Reassigned %d users to clusters.", n)
    return n


def get_cluster_summary() -> dict:
    """Single-tenant cluster summary across all users."""
    users = User.query.all()
    total = len(users) or 1

    counts = {cid: 0 for cid in CLUSTER_ARCHETYPES}
    intervention_users: list[str] = []
    for u in users:
        label = u.cluster_label
        if not label:
            continue
        cid = next(
            (cid for cid, meta in CLUSTER_ARCHETYPES.items() if meta["label"] == label),
            None,
        )
        if cid is None:
            continue
        counts[cid] += 1
        if cid in (0, 4):
            display = (f"{u.first_name} {u.last_name}".strip() or u.email)
            intervention_users.append(display)

    archetypes_out = []
    for cid, meta in CLUSTER_ARCHETYPES.items():
        count = counts[cid]
        archetypes_out.append({
            "cluster_id": cid,
            "label": meta["label"],
            "count": count,
            "percentage": round(100.0 * count / total, 2),
            "colour": meta["colour"],
            "icon": meta["icon"],
            "intervention": meta["intervention"],
        })

    assigned = {cid: c for cid, c in counts.items() if c > 0}
    most_common = (
        CLUSTER_ARCHETYPES[max(assigned, key=assigned.get)]["label"]
        if assigned else None
    )

    return {
        "archetypes": archetypes_out,
        "most_common_archetype": most_common,
        "highest_risk_archetype_count": counts.get(0, 0),
        "intervention_required": intervention_users,
    }


# Back-compat alias for callers that used the multi-tenant signature.
def get_org_cluster_summary(_org_id=None) -> dict:
    return get_cluster_summary()
