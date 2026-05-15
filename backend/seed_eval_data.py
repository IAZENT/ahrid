"""Demo data for the evaluation panel (Master spec §11).

Creates:
  * 5 demo employees (receptionist / accountant / hr / it / finance)
  * 10+ Attempt records per user spread across categories
  * Pre-assessment for 3 of them, post-assessment for 3 of them
  * 2 SUS responses

Idempotent: existing rows (matched by email) are reused.

    python seed_eval_data.py
"""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models.attempt import Attempt
from app.models.awareness_assessment import AwarenessAssessment, score_awareness
from app.models.scenario import Scenario
from app.models.sus_response import SUSResponse, calculate_sus
from app.models.user import User
from app.services.risk_scorer import recalculate_for_user

random.seed(7)

DEMO_USERS = [
    # email,                 username,    job_role,       first,   last
    ("rec.demo@ahrid.local",  "rec_demo",  "receptionist", "Rita",  "Limbu"),
    ("acc.demo@ahrid.local",  "acc_demo",  "accountant",   "Anuj",  "Thapa"),
    ("hr.demo@ahrid.local",   "hr_demo",   "hr",           "Hema",  "Khadka"),
    ("it.demo@ahrid.local",   "it_demo",   "it",           "Ishan", "Bista"),
    ("fin.demo@ahrid.local",  "fin_demo",  "finance",      "Fina",  "Adhikari"),
]
PASSWORD = "User@SecurePass1!"


def _ensure_user(email, username, job_role, first, last) -> User:
    existing = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()
    if existing is not None:
        return existing
    u = User(
        email=email, username=username, role="employee",
        job_role=job_role, first_name=first, last_name=last,
        is_active=True, is_verified=True,
        consent_given=True, consent_timestamp=datetime.utcnow(),
    )
    u.set_password(PASSWORD)
    db.session.add(u)
    db.session.flush()
    return u


def _seed_attempts(user: User, n: int = 14) -> int:
    """Generate ``n`` attempts spread across distinct categories.

    Per-user accuracy is biased by ``user.job_role`` so the demo manager
    dashboard shows a meaningful spread of risk levels.
    """
    if Attempt.query.filter_by(user_id=user.id).count() >= n:
        return 0

    accuracy_by_role = {
        "receptionist": 0.55,  # weakest
        "accountant":   0.70,
        "hr":           0.65,
        "it":           0.92,  # strongest
        "finance":      0.78,
    }
    target_acc = accuracy_by_role.get(user.job_role or "", 0.7)

    scenarios = (
        Scenario.query.filter_by(is_active=True, question_type="mcq")
        .order_by(Scenario.created_at.desc())
        .limit(120).all()
    )
    if len(scenarios) < n:
        return 0

    chosen = random.sample(scenarios, n)
    sid = uuid.uuid4()
    now = datetime.utcnow()
    created = 0
    for i, sc in enumerate(chosen):
        is_correct = random.random() < target_acc
        # Generate a plausible response time: shorter when correct.
        rt = random.randint(2500, 7500) if is_correct else random.randint(4000, 12000)
        answer = sc.correct_answer if is_correct else random.choice(
            [a for a in ("A", "B", "C", "D") if a != sc.correct_answer]
        )
        att = Attempt(
            user_id=user.id, scenario_id=sc.id,
            answer_given=answer, is_correct=is_correct,
            response_time_ms=rt,
            category=sc.category, difficulty=sc.difficulty,
            session_id=sid,
            is_synthetic=False,
            created_at=now - timedelta(days=14 - i, hours=random.randint(0, 8)),
        )
        db.session.add(att)
        created += 1
    db.session.flush()
    return created


def _seed_assessment(user: User, phase: str, score_target: float) -> bool:
    """Insert an awareness assessment if the user doesn't have one for ``phase``.

    ``score_target`` is the desired 0-100 score; we sample Likert
    responses to roughly match it.
    """
    existing = AwarenessAssessment.query.filter_by(user_id=user.id, phase=phase).first()
    if existing is not None:
        return False
    # mean Likert ≈ score_target / 20
    target_mean = score_target / 20.0
    responses = {}
    for i in range(1, 8):
        # Bias around the target mean with ±1 jitter.
        v = max(1, min(5, int(round(random.gauss(target_mean, 0.6)))))
        responses[f"q{i}"] = v
    score = score_awareness(responses)
    db.session.add(AwarenessAssessment(
        user_id=user.id, phase=phase, responses=responses, score=score,
        completed_at=datetime.utcnow() - timedelta(days=20 if phase == "pre" else 1),
    ))
    return True


def _seed_sus(user: User) -> bool:
    if SUSResponse.query.filter_by(user_id=user.id).first() is not None:
        return False
    # Mostly favourable responses, with mild noise.
    responses = {}
    for i in range(1, 11):
        if i % 2 == 1:                    # positive items → high
            responses[f"q{i}"] = random.choice([4, 4, 5, 5, 3])
        else:                              # negative items → low
            responses[f"q{i}"] = random.choice([1, 2, 2, 1, 3])
    score = calculate_sus(responses)
    db.session.add(SUSResponse(user_id=user.id, responses=responses, sus_score=score))
    return True


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        users: list[User] = []
        for email, uname, role, first, last in DEMO_USERS:
            users.append(_ensure_user(email, uname, role, first, last))
        db.session.commit()

        attempts_added = 0
        for u in users:
            attempts_added += _seed_attempts(u)
        db.session.commit()

        # Recompute risk for each so the manager dashboard shows numbers.
        for u in users:
            recalculate_for_user(u.id)
        db.session.commit()

        # Pre/post awareness:
        #   - first 3 users get pre + post (so cohen's d / p-value have data)
        #   - 4th gets pre only, 5th gets post only
        pre_targets  = [55, 50, 60, 58, None]
        post_targets = [78, 72, 81, None, 75]
        awareness_added = 0
        for u, pre, post in zip(users, pre_targets, post_targets):
            if pre is not None:
                awareness_added += _seed_assessment(u, "pre", pre)
            if post is not None:
                awareness_added += _seed_assessment(u, "post", post)

        sus_added = 0
        for u in users[:2]:
            sus_added += _seed_sus(u)

        db.session.commit()

        print(
            f"Demo eval data ready: users={len(users)}, "
            f"attempts+={attempts_added}, awareness_rows+={awareness_added}, "
            f"sus_rows+={sus_added}."
        )


if __name__ == "__main__":
    main()
