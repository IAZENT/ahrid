"""Behavioural profiler  mistake clustering only (BSc scope).

Peer-cohort comparison and motivation profiling were removed because
they relied on multi-tenant org_id (peer cohort) and gamification
(motivation profile). Only the mistake-clustering signal remains and
is exposed via ``/api/v1/training/insights``.
"""
from __future__ import annotations

from collections import Counter

from app.models.attempt import Attempt

MISTAKE_LOOKBACK_LIMIT = 50
MISTAKE_MIN_FOR_CLUSTER = 2


def cluster_user_mistakes(user_id, limit: int = MISTAKE_LOOKBACK_LIMIT) -> dict:
    """Group recent wrong answers by (category, difficulty)."""
    rows = (
        Attempt.query.filter_by(user_id=user_id, is_correct=False)
        .order_by(Attempt.created_at.desc())
        .limit(limit)
        .all()
    )
    if not rows:
        return {
            "total_mistakes": 0,
            "dominant_category": None,
            "dominant_difficulty": None,
            "clusters": [],
            "signature": None,
        }

    counter: Counter = Counter()
    for a in rows:
        key = (a.category, a.difficulty)
        counter[key] += 1

    clusters = [
        {"category": cat, "difficulty": diff, "count": n}
        for (cat, diff), n in counter.most_common()
        if n >= MISTAKE_MIN_FOR_CLUSTER
    ]
    if not clusters and counter:
        (cat, diff), n = counter.most_common(1)[0]
        clusters = [{"category": cat, "difficulty": diff, "count": n}]

    cat_counter = Counter(a.category for a in rows)
    diff_counter = Counter(a.difficulty for a in rows)
    dom_cat = cat_counter.most_common(1)[0][0] if cat_counter else None
    dom_diff = diff_counter.most_common(1)[0][0] if diff_counter else None

    top = clusters[0] if clusters else None
    signature = f"{top['category']}|{top['difficulty']}" if top else None

    return {
        "total_mistakes": len(rows),
        "dominant_category": dom_cat,
        "dominant_difficulty": dom_diff,
        "clusters": clusters,
        "signature": signature,
    }


def build_insights(user_id) -> dict:
    return {"mistakes": cluster_user_mistakes(user_id)}
