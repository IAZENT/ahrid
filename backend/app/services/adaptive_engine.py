"""Adaptive scenario selection + attempt processing (BSc scope).

Simplifications vs. the production build:
* Thompson Sampling removed  pure mastery-based weighted selection.
* Sentiment / VADER signals removed  only ``response_time_ms`` is kept
  as a behavioural proxy on the Attempt row.
* Free-text grading paths removed  only MCQ / TF / identify_threat.
* Gamification (XP, streaks, badges) removed.
"""
from __future__ import annotations

import math
import random
from datetime import datetime, timedelta

from sqlalchemy import func

from app.extensions import db
from app.models.attempt import Attempt
from app.models.risk_score import RiskScore
from app.models.scenario import CATEGORIES, Scenario
from app.models.user import User
from app.services.risk_scorer import recalculate_for_user

# Mastery thresholds (master doc Phase 4)
PROMOTION_THRESHOLD = 0.80
DEMOTION_THRESHOLD = 0.40
MIN_ATTEMPTS_FOR_DECISION = 5
RECENCY_WINDOW = 10
DECAY_FACTOR = 0.85
MAX_DIFFICULTY = 3
MIN_DIFFICULTY = 1
SESSION_SIZE = 20

SCENARIO_SELECTION_RATIO = {
    "weakest_category": 0.50,
    "other_categories": 0.25,
    "challenge": 0.25,
}

# Live-feed slot
THREAT_FEED_SOURCES = ("phishstats", "openphish", "otx", "urlscan")
RECENT_THREAT_WINDOW_HOURS = 48

# Spaced repetition by risk band (hours before a correct answer can re-appear)
RISK_LEVEL_TO_SPACING_HOURS = {
    "critical": 12,
    "high":     24,
    "medium":   48,
    "low":      72,
    "unknown":  24,
}

ROLE_CATEGORY_PRIORITY: dict[str, list[str]] = {
    "receptionist": ["phishing_email", "physical_security", "social_engineering"],
    "accountant": ["phishing_email", "smishing", "data_handling"],
    "hr": ["social_engineering", "phishing_email", "data_handling"],
    "it": ["phishing_email", "usb_baiting", "password_hygiene"],
    "finance": ["phishing_email", "social_engineering", "data_handling"],
    "sales": ["phishing_email", "smishing", "social_engineering"],
    "management": ["vishing", "social_engineering", "phishing_email"],
    "other": ["phishing_email", "password_hygiene", "social_engineering"],
}

_CATEGORY_DISPLAY: dict[str, str] = {
    "phishing_email": "phishing email detection",
    "smishing": "SMS phishing awareness",
    "vishing": "voice phishing defence",
    "physical_security": "physical security awareness",
    "password_hygiene": "password hygiene",
    "usb_baiting": "USB baiting awareness",
    "social_engineering": "social engineering resistance",
    "data_handling": "data handling practices",
}

_ROLE_DISPLAY: dict[str, str] = {
    "receptionist": "reception",
    "accountant": "accounting",
    "hr": "HR",
    "it": "IT",
    "finance": "finance",
    "sales": "sales",
    "management": "management",
    "other": "your",
}


# ---------------------------------------------------------------------------
# Mastery + user profile
# ---------------------------------------------------------------------------
def calculate_mastery(attempts: list[Attempt]) -> float:
    """Recency-weighted accuracy. attempts[0] must be the MOST recent."""
    if not attempts:
        return 0.0
    weights = [DECAY_FACTOR**i for i in range(len(attempts))]
    weighted = sum(int(a.is_correct) * w for a, w in zip(attempts, weights))
    return weighted / sum(weights)


def _trend(attempts: list[Attempt]) -> str:
    if len(attempts) < MIN_ATTEMPTS_FOR_DECISION:
        return "insufficient_data"
    half = len(attempts) // 2
    recent = attempts[:half]
    older = attempts[half:]
    if not older:
        return "stable"
    recent_acc = sum(int(a.is_correct) for a in recent) / len(recent)
    older_acc = sum(int(a.is_correct) for a in older) / len(older)
    diff = recent_acc - older_acc
    if diff > 0.1:
        return "improving"
    if diff < -0.1:
        return "declining"
    return "stable"


def _next_difficulty(current: int, mastery: float, total_attempts: int) -> int:
    if total_attempts < MIN_ATTEMPTS_FOR_DECISION:
        return MIN_DIFFICULTY
    if mastery >= PROMOTION_THRESHOLD:
        return min(current + 1, MAX_DIFFICULTY)
    if mastery <= DEMOTION_THRESHOLD:
        return max(current - 1, MIN_DIFFICULTY)
    return current


def get_user_profile(user_id) -> dict:
    user = db.session.get(User, user_id)
    job_role = (user.job_role if user else None) or "other"

    categories: dict[str, dict] = {}
    for cat in CATEGORIES:
        recent = (
            Attempt.query.filter_by(user_id=user_id, category=cat)
            .order_by(Attempt.created_at.desc())
            .limit(RECENCY_WINDOW)
            .all()
        )
        total = (
            db.session.query(func.count(Attempt.id))
            .filter_by(user_id=user_id, category=cat)
            .scalar()
            or 0
        )
        mastery = calculate_mastery(recent)
        if total < MIN_ATTEMPTS_FOR_DECISION:
            difficulty = MIN_DIFFICULTY
        else:
            anchor = max(set(a.difficulty for a in recent), key=[a.difficulty for a in recent].count)
            difficulty = _next_difficulty(anchor, mastery, total)
        categories[cat] = {
            "mastery": round(mastery, 4),
            "difficulty": difficulty,
            "total_attempts": total,
            "trend": _trend(recent),
        }

    masteries = [c["mastery"] for c in categories.values()]
    overall_mastery = round(sum(masteries) / len(masteries), 4)
    weakest_category = min(categories, key=lambda c: categories[c]["mastery"])
    strongest_category = max(categories, key=lambda c: categories[c]["mastery"])
    priorities = ROLE_CATEGORY_PRIORITY.get(job_role, ROLE_CATEGORY_PRIORITY["other"])

    return {
        "user_id": str(user_id),
        "job_role": job_role,
        "categories": categories,
        "overall_mastery": overall_mastery,
        "weakest_category": weakest_category,
        "strongest_category": strongest_category,
        "role_priority_categories": priorities,
    }


# ---------------------------------------------------------------------------
# Scenario selection
# ---------------------------------------------------------------------------
def _spacing_window_hours_for_user(user_id) -> int:
    rs = RiskScore.query.filter_by(user_id=user_id).first()
    level = rs.risk_level if rs else "unknown"
    return RISK_LEVEL_TO_SPACING_HOURS.get(level, RISK_LEVEL_TO_SPACING_HOURS["unknown"])


def _eligible_for_user(user_id, job_role: str) -> list[Scenario]:
    spacing_hours = _spacing_window_hours_for_user(user_id)
    cutoff = datetime.utcnow() - timedelta(hours=spacing_hours)
    recent_correct_ids = {
        sid
        for (sid,) in db.session.query(Attempt.scenario_id).filter(
            Attempt.user_id == user_id,
            Attempt.is_correct == True,  # noqa: E712
            Attempt.created_at >= cutoff,
        )
    }
    pool = Scenario.query.filter_by(is_active=True).all()
    return [
        s for s in pool
        if s.applies_to_role(job_role) and s.id not in recent_correct_ids
    ]


def _seen_scenario_ids(user_id) -> set:
    return {sid for (sid,) in db.session.query(Attempt.scenario_id).filter_by(user_id=user_id)}


def _seen_in_last_7_days(user_id) -> set:
    cutoff = datetime.utcnow() - timedelta(days=7)
    return {
        sid
        for (sid,) in db.session.query(Attempt.scenario_id).filter(
            Attempt.user_id == user_id, Attempt.created_at >= cutoff
        )
    }


def _prefer_unseen(scenarios: list[Scenario], seen_ids: set, recent_ids: set) -> list[Scenario]:
    unseen = [s for s in scenarios if s.id not in seen_ids]
    seen_old = [s for s in scenarios if s.id in seen_ids and s.id not in recent_ids]
    seen_recent = [s for s in scenarios if s.id in recent_ids]
    random.shuffle(unseen)
    random.shuffle(seen_old)
    random.shuffle(seen_recent)
    return [*unseen, *seen_old, *seen_recent]


def _recent_threat_scenarios(eligible: list[Scenario]) -> list[Scenario]:
    cutoff = datetime.utcnow() - timedelta(hours=RECENT_THREAT_WINDOW_HOURS)
    fresh = [
        s for s in eligible
        if s.source in THREAT_FEED_SOURCES and s.created_at and s.created_at >= cutoff
    ]
    fresh.sort(key=lambda s: s.created_at, reverse=True)
    return fresh


def _pick(filtered: list[Scenario], n: int, taken: set) -> list[Scenario]:
    out: list[Scenario] = []
    for s in filtered:
        if len(out) >= n:
            break
        if s.id in taken:
            continue
        out.append(s)
        taken.add(s.id)
    return out


def select_next_session(
    user_id,
    job_role: str | None = None,
    *,
    num_questions: int | None = None,
    return_meta: bool = False,
):
    """Return up to num_questions scenarios using the doc's distribution."""
    session_size = max(1, min(50, num_questions or SESSION_SIZE))
    profile = get_user_profile(user_id)
    job_role = job_role or profile["job_role"]
    eligible = _eligible_for_user(user_id, job_role)
    spacing_hours = _spacing_window_hours_for_user(user_id)

    meta: dict = {
        "session_size": session_size,
        "spacing_window_hours": spacing_hours,
        "threat_slot_used": False,
        "selector": "mastery_weighted",
    }
    reasons: dict[str, str] = {}  # scenario.id → transparency label
    role_label = _ROLE_DISPLAY.get(job_role, job_role or "your")

    if not eligible:
        return ({"scenarios": [], "meta": meta, "selection_reasons": {}}) if return_meta else []

    threat_pool = _recent_threat_scenarios(eligible)
    threat_pick: list[Scenario] = []
    if threat_pool:
        threat_pick = [threat_pool[0]]
        meta["threat_slot_used"] = True
        meta["threat_scenario_age_hours"] = round(
            (datetime.utcnow() - threat_pool[0].created_at).total_seconds() / 3600, 1
        )
        reasons[str(threat_pool[0].id)] = "Based on a real phishing threat detected in the last 48 hours."

    seen_ids = _seen_scenario_ids(user_id)
    recent_ids = _seen_in_last_7_days(user_id)

    weakest_cat = profile["weakest_category"]
    weakest_diff = profile["categories"][weakest_cat]["difficulty"]

    in_weakest = _prefer_unseen(
        [s for s in eligible if s.category == weakest_cat and s.difficulty == weakest_diff],
        seen_ids, recent_ids,
    )
    if not in_weakest:
        in_weakest = _prefer_unseen(
            [s for s in eligible if s.category == weakest_cat],
            seen_ids, recent_ids,
        )

    others = _prefer_unseen(
        [s for s in eligible if s.category != weakest_cat],
        seen_ids, recent_ids,
    )

    challenge_diff = max(MIN_DIFFICULTY, min(MAX_DIFFICULTY, weakest_diff + 1))
    challenge_pool = _prefer_unseen(
        [s for s in eligible if s.difficulty == challenge_diff],
        seen_ids, recent_ids,
    )

    remaining = session_size - len(threat_pick)
    n_weak = math.ceil(remaining * SCENARIO_SELECTION_RATIO["weakest_category"])
    n_chal = max(1, round(remaining * SCENARIO_SELECTION_RATIO["challenge"]))
    n_other = max(0, remaining - n_weak - n_chal)

    taken: set = {s.id for s in threat_pick}
    selection: list[Scenario] = list(threat_pick)

    weak_picks = _pick(in_weakest, n_weak, taken)
    cat_display = _CATEGORY_DISPLAY.get(weakest_cat, weakest_cat.replace("_", " "))
    for s in weak_picks:
        reasons[str(s.id)] = (
            f"Targets your weakest area: {cat_display}. "
            f"Priority for {role_label} role."
        )
    selection += weak_picks

    other_picks = _pick(others, n_other, taken)
    priorities = profile["role_priority_categories"]
    for s in other_picks:
        s_cat_display = _CATEGORY_DISPLAY.get(s.category, s.category.replace("_", " "))
        if s.category in priorities:
            reasons[str(s.id)] = (
                f"Selected for your {role_label} role: {s_cat_display}."
            )
        else:
            reasons[str(s.id)] = f"Broadening your awareness: {s_cat_display}."
    selection += other_picks

    chal_picks = _pick(challenge_pool, n_chal, taken)
    for s in chal_picks:
        s_cat_display = _CATEGORY_DISPLAY.get(s.category, s.category.replace("_", " "))
        reasons[str(s.id)] = (
            f"Challenge: {s_cat_display} at higher difficulty to stretch your skills."
        )
    selection += chal_picks

    if len(selection) < session_size:
        backfill = _prefer_unseen(eligible, seen_ids, recent_ids)
        selection += _pick(backfill, session_size - len(selection), taken)

    # Hard guarantee: every session is exactly session_size questions.
    # If the spacing window has filtered the pool too aggressively (small
    # corpus / heavy use), we relax it and pull from the full active pool,
    # role-filter included but spacing ignored. The user never gets a
    # stub session.
    if len(selection) < session_size:
        relaxed_pool = [
            s for s in Scenario.query.filter_by(is_active=True).all()
            if s.applies_to_role(job_role)
        ]
        relaxed_order = _prefer_unseen(relaxed_pool, seen_ids, recent_ids)
        selection += _pick(relaxed_order, session_size - len(selection), taken)
        meta["spacing_relaxed"] = True

    random.shuffle(selection)
    result = selection[:session_size]
    meta["delivered_size"] = len(result)
    return ({"scenarios": result, "meta": meta, "selection_reasons": reasons}) if return_meta else result


# ---------------------------------------------------------------------------
# Attempt processing
# ---------------------------------------------------------------------------
def process_attempt(
    *,
    user_id,
    scenario_id,
    answer: str | None = None,
    response_time_ms: int | None,
    session_id,
):
    """Persist an Attempt, recompute risk, return feedback dict."""
    scenario = db.session.get(Scenario, scenario_id)
    if scenario is None or not scenario.is_active:
        return {"error": "scenario_not_found"}, 404

    answer_letter = (answer or "").strip().upper()[:1] or "?"
    is_correct = answer_letter == scenario.correct_answer

    # Track risk-level change so we can fire a risk_escalation notification.
    prev_score = RiskScore.query.filter_by(user_id=user_id).first()
    prev_level = prev_score.risk_level if prev_score else "unknown"

    attempt = Attempt(
        user_id=user_id,
        scenario_id=scenario.id,
        answer_given=answer_letter,
        is_correct=is_correct,
        response_time_ms=response_time_ms,
        category=scenario.category,
        difficulty=scenario.difficulty,
        session_id=session_id,
    )
    db.session.add(attempt)

    scenario.times_served = (scenario.times_served or 0) + 1
    if is_correct:
        scenario.times_correct = (scenario.times_correct or 0) + 1

    db.session.flush()
    new_score = recalculate_for_user(user_id)

    # Risk escalation notification (only when level worsens).
    LEVEL_RANK = {"unknown": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    if (
        new_score
        and LEVEL_RANK.get(new_score.risk_level, 0) > LEVEL_RANK.get(prev_level, 0)
        and new_score.risk_level in ("medium", "high", "critical")
    ):
        from app.services.notifications import emit_risk_escalation
        emit_risk_escalation(
            user_id, new_level=new_score.risk_level, composite=new_score.composite_score,
        )

    db.session.commit()

    mastery_after = calculate_mastery(
        Attempt.query.filter_by(user_id=user_id, category=scenario.category)
        .order_by(Attempt.created_at.desc())
        .limit(RECENCY_WINDOW)
        .all()
    )

    return {
        "is_correct": is_correct,
        "correct_answer": scenario.correct_answer,
        "explanation": scenario.explanation,
        "red_flags": scenario.red_flags,
        "learning_tip": scenario.learning_tip,
        "mastery_update": {
            "category": scenario.category,
            "mastery": round(mastery_after, 4),
        },
        "question_type": scenario.question_type,
    }


# ---------------------------------------------------------------------------
# Session summary
# ---------------------------------------------------------------------------
def get_session_summary(user_id, session_id) -> dict:
    attempts = (
        Attempt.query.filter_by(user_id=user_id, session_id=session_id)
        .order_by(Attempt.created_at.asc())
        .all()
    )
    total = len(attempts)
    if total == 0:
        return {"session_id": str(session_id), "total_questions": 0}

    correct = sum(1 for a in attempts if a.is_correct)
    accuracy = round(correct / total, 4)
    duration = (attempts[-1].created_at - attempts[0].created_at).total_seconds()

    by_cat: dict[str, list[Attempt]] = {}
    for a in attempts:
        by_cat.setdefault(a.category, []).append(a)
    cat_acc = {
        c: sum(int(x.is_correct) for x in atts) / len(atts)
        for c, atts in by_cat.items()
    }

    strongest = max(cat_acc, key=cat_acc.get) if cat_acc else None
    weakest = min(cat_acc, key=cat_acc.get) if cat_acc else None

    tips = [a.scenario.learning_tip for a in attempts if not a.is_correct and a.scenario]
    tips = list(dict.fromkeys(t for t in tips if t))[:5]

    return {
        "session_id": str(session_id),
        "total_questions": total,
        "correct": correct,
        "accuracy": accuracy,
        "duration_seconds": round(duration, 1),
        "categories_covered": sorted(by_cat.keys()),
        "strongest_category_this_session": strongest,
        "weakest_category_this_session": weakest,
        "improvement_tips": tips,
    }
