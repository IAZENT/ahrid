"""Phase 18.1  behavioral telemetry recording + aggregation."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy import func

from app.extensions import db
from app.models.behavior_event import UserBehaviorEvent

LOG = logging.getLogger(__name__)


def record_event(
    *,
    user_id,
    session_id,
    scenario_id,
    event_type: str,
    payload: dict,
    category: str | None = None,
    difficulty: int | None = None,
):
    """Create + commit a UserBehaviorEvent. Never raises  returns row or None."""
    try:
        row = UserBehaviorEvent(
            user_id=user_id,
            session_id=str(session_id),
            scenario_id=scenario_id,
            event_type=event_type,
            payload=json.dumps(payload or {}),
            category=category,
            difficulty=difficulty,
        )
        db.session.add(row)
        # Flush, but rely on the caller's commit if there is one already
        # in progress  otherwise commit ourselves.
        try:
            db.session.flush()
        except Exception:  # pragma: no cover
            db.session.rollback()
            return None
        return row
    except Exception as exc:  # pragma: no cover
        LOG.warning("telemetry record_event failed: %s", exc)
        try:
            db.session.rollback()
        except Exception:
            pass
        return None


def _parse_payload(raw: str | None) -> dict:
    try:
        return json.loads(raw or "{}")
    except (ValueError, TypeError):
        return {}


def get_user_telemetry_summary(user_id, days: int = 30) -> dict:
    """Aggregate telemetry for the user over the last N days.

    Returns avg dwell per category, avg answer changes, hint-usage rate,
    fastest/slowest/most-revised categories, total event count.
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Dwell per category (from answer_submitted events' total_dwell_ms or read_time_recorded)
    dwell_rows = (
        db.session.query(UserBehaviorEvent.category, UserBehaviorEvent.payload)
        .filter(
            UserBehaviorEvent.user_id == user_id,
            UserBehaviorEvent.created_at >= cutoff,
            UserBehaviorEvent.event_type.in_(("answer_submitted", "read_time_recorded")),
            UserBehaviorEvent.category.isnot(None),
        )
        .all()
    )

    dwell_by_cat: dict[str, list[int]] = {}
    for category, raw in dwell_rows:
        p = _parse_payload(raw)
        ms = p.get("total_dwell_ms") or p.get("dwell_ms") or 0
        try:
            ms = int(ms)
        except (ValueError, TypeError):
            continue
        if ms > 0:
            dwell_by_cat.setdefault(category, []).append(ms)

    avg_dwell: dict[str, int] = {
        cat: int(round(sum(v) / len(v))) for cat, v in dwell_by_cat.items() if v
    }

    # Answer changes + hint usage
    submit_rows = (
        db.session.query(UserBehaviorEvent.payload, UserBehaviorEvent.category)
        .filter(
            UserBehaviorEvent.user_id == user_id,
            UserBehaviorEvent.created_at >= cutoff,
            UserBehaviorEvent.event_type == "answer_submitted",
        )
        .all()
    )
    total_changes = 0
    submits = 0
    changes_by_cat: dict[str, list[int]] = {}
    for raw, category in submit_rows:
        p = _parse_payload(raw)
        ac = p.get("answer_changes")
        try:
            ac = int(ac) if ac is not None else 0
        except (ValueError, TypeError):
            ac = 0
        total_changes += ac
        submits += 1
        if category:
            changes_by_cat.setdefault(category, []).append(ac)

    avg_changes = round(total_changes / submits, 2) if submits else 0.0

    hint_count = (
        db.session.query(func.count(UserBehaviorEvent.id))
        .filter(
            UserBehaviorEvent.user_id == user_id,
            UserBehaviorEvent.created_at >= cutoff,
            UserBehaviorEvent.event_type == "hint_requested",
        )
        .scalar()
        or 0
    )
    hint_rate = round(hint_count / submits, 3) if submits else 0.0

    fastest = min(avg_dwell, key=avg_dwell.get) if avg_dwell else None
    slowest = max(avg_dwell, key=avg_dwell.get) if avg_dwell else None

    most_revised = None
    if changes_by_cat:
        per_cat_avg = {c: sum(v) / len(v) for c, v in changes_by_cat.items() if v}
        if per_cat_avg:
            most_revised = max(per_cat_avg, key=per_cat_avg.get)

    total_events = (
        db.session.query(func.count(UserBehaviorEvent.id))
        .filter(
            UserBehaviorEvent.user_id == user_id,
            UserBehaviorEvent.created_at >= cutoff,
        )
        .scalar()
        or 0
    )

    return {
        "avg_dwell_ms_per_category": avg_dwell,
        "avg_answer_changes_per_scenario": avg_changes,
        "hint_usage_rate": hint_rate,
        "fastest_category": fastest,
        "slowest_category": slowest,
        "most_revised_category": most_revised,
        "total_events": int(total_events),
        "window_days": days,
    }


def get_category_engagement_scores(user_id) -> dict[str, float]:
    """Per-category struggle score (0-1). Higher = user struggles more."""
    summary = get_user_telemetry_summary(user_id, days=30)
    dwell = summary["avg_dwell_ms_per_category"]
    if not dwell:
        return {}
    max_dwell = max(dwell.values())
    min_dwell = min(dwell.values())
    span = (max_dwell - min_dwell) or 1
    out: dict[str, float] = {}
    for cat, ms in dwell.items():
        # Normalised dwell (0-1)
        dwell_score = (ms - min_dwell) / span
        # Blend with answer changes signal if we have it
        score = round(min(1.0, 0.6 * dwell_score + 0.4 * min(1.0, summary["avg_answer_changes_per_scenario"] / 2.0)), 3)
        out[cat] = score
    return out


__all__ = [
    "record_event", "get_user_telemetry_summary", "get_category_engagement_scores",
]
