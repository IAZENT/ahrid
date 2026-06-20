"""Generate synthetic training data for ML models.

Creates synthetic users with realistic attempt patterns across all risk
levels (low/medium/high/critical) so the RF classifier and KMeans
clusterer have enough data to train meaningfully.

Also generates awareness assessments (pre+post) and SUS responses for
each synthetic user so the admin evaluation panel shows meaningful data.

All attempts are marked ``is_synthetic=True`` so the rule-based risk
scorer excludes them from live scoring  they exist purely to bootstrap
the ML pipeline.

Usage:
    python seed_synthetic_ml_data.py
"""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models.attempt import Attempt
from app.models.awareness_assessment import AwarenessAssessment, score_awareness
from app.models.scenario import CATEGORIES, Scenario
from app.models.sus_response import SUSResponse, calculate_sus, sus_grade
from app.models.user import User

random.seed(42)

CATEGORIES_LIST = list(CATEGORIES)
JOB_ROLES = ["receptionist", "accountant", "hr", "it", "finance", "sales", "management"]

# Profile definitions: (label, base_accuracy, rt_correct_range, rt_wrong_range,
#                       n_users, attempts_per_user_range)
PROFILES = [
    # critical: very low accuracy, fast/guessing, overconfident
    ("critical", 0.15, (1500, 3500), (1200, 3000), 200, (20, 35)),
    # high: low accuracy, rushed
    ("high", 0.35, (2000, 5000), (1500, 4000), 200, (18, 30)),
    # medium: moderate accuracy, some categories weak
    ("medium", 0.60, (2500, 6000), (3000, 7000), 250, (15, 25)),
    # low: good accuracy, careful
    ("low", 0.82, (3000, 7000), (4000, 10000), 250, (15, 30)),
    # very low risk: excellent accuracy, fast but correct
    ("very_low", 0.92, (2500, 5500), (5000, 12000), 150, (20, 40)),
]

# Per-user jitter so users within a tier aren't clones of the profile mean.
PER_USER_ACCURACY_JITTER = 0.07

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Sai", "Reyansh", "Krishna", "Ishaan",
    "Shaurya", "Atharv", "Diya", "Ananya", "Priya", "Kavya", "Aisha", "Nisha",
    "Meera", "Riya", "Simran", "Pooja", "Rahul", "Rohan", "Amit", "Vikram",
    "Sanjay", "Deepak", "Manoj", "Kiran", "Sunita", "Geeta", "Suresh", "Prakash",
    "Sachin", "Rajesh", "Ashok", "Nitin", "Mohan", "Ramesh", "Vikas", "Suman",
]

LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Jha", "Reddy", "Nair",
    "Mishra", "Pandey", "Tiwari", "Verma", "Choudhary", "Rao", "Menon",
    "Desai", "Kulkarni", "Chatterjee", "Banerjee", "Mukherjee", "Iyer",
    "Bhat", "Kamath", "Pillai", "Thakur", "Sinha", "Yadav", "Chauhan",
    "Mehta", "Shah", "Dave", "Joshi", "Kapoor", "Malhotra", "Khanna",
]


def _pick_name(idx: int) -> tuple[str, str]:
    return FIRST_NAMES[idx % len(FIRST_NAMES)], LAST_NAMES[idx % len(LAST_NAMES)]


def _make_user(idx: int, email: str, job_role: str, first: str, last: str) -> User:
    u = User(
        email=email,
        username=f"synthetic_{idx:04d}",
        role="employee",
        job_role=job_role,
        first_name=first,
        last_name=last,
        is_active=True,
        is_verified=True,
        consent_given=True,
        consent_timestamp=datetime.utcnow(),
    )
    u.set_password("SyntheticPass123!")
    return u


def _generate_attempts(
    user: User,
    scenarios: list[Scenario],
    base_accuracy: float,
    rt_correct: tuple[int, int],
    rt_wrong: tuple[int, int],
    n_attempts: int,
    session_spread: int = 5,
) -> list[Attempt]:
    """Generate realistic attempts for a user."""
    if not scenarios:
        return []

    attempts = []
    n_sessions = random.randint(2, max(3, session_spread))
    per_session = n_attempts // n_sessions
    remainder = n_attempts - per_session * n_sessions

    base_date = datetime.utcnow() - timedelta(days=random.randint(7, 60))

    for sess_idx in range(n_sessions):
        sid = uuid.uuid4()
        sess_size = per_session + (1 if sess_idx < remainder else 0)
        sess_date = base_date + timedelta(days=sess_idx * random.randint(1, 3))

        # Per-session category focus (not all categories equally likely)
        focused_cats = random.sample(CATEGORIES_LIST, k=random.randint(3, 6))

        for _ in range(sess_size):
            sc = random.choice(scenarios)
            # Bias toward focused categories
            if random.random() < 0.6:
                candidates = [s for s in scenarios if s.category in focused_cats]
                if candidates:
                    sc = random.choice(candidates)

            # Accuracy varies by difficulty
            diff_modifier = {1: 0.10, 2: 0.0, 3: -0.15}.get(sc.difficulty, 0)
            category_modifier = random.gauss(0, 0.08)
            effective_acc = max(0.05, min(0.95, base_accuracy + diff_modifier + category_modifier))

            is_correct = random.random() < effective_acc
            rt = random.randint(*rt_correct) if is_correct else random.randint(*rt_wrong)

            # Occasional very fast overconfident answers
            if is_correct and random.random() < 0.05:
                rt = random.randint(800, 1500)
            if not is_correct and random.random() < 0.15:
                rt = random.randint(1000, 2500)

            answer = sc.correct_answer if is_correct else random.choice(
                [a for a in ("A", "B", "C", "D") if a != sc.correct_answer]
            )

            attempts.append(Attempt(
                user_id=user.id,
                scenario_id=sc.id,
                answer_given=answer,
                is_correct=is_correct,
                response_time_ms=rt,
                category=sc.category,
                difficulty=sc.difficulty,
                session_id=sid,
                is_synthetic=True,
                created_at=sess_date + timedelta(hours=random.randint(0, 6)),
            ))

    return attempts


def _generate_awareness(user: User, risk_profile: str) -> int:
    """Generate pre+post awareness assessments. Returns rows created."""
    created = 0
    # Pre-assessment: lower scores for worse profiles
    pre_base = {"critical": 25, "high": 40, "medium": 55, "low": 70, "very_low": 82}
    # Post-assessment: improvement varies by profile
    post_improvement = {"critical": 8, "high": 12, "medium": 15, "low": 10, "very_low": 5}

    for phase, base_key, offset_key in [("pre", "pre_base", "post_improvement"), ("post", "pre_base", "post_improvement")]:
        existing = AwarenessAssessment.query.filter_by(user_id=user.id, phase=phase).first()
        if existing is not None:
            continue
        base = pre_base[risk_profile]
        if phase == "post":
            base = min(95, base + post_improvement[risk_profile])
        target_mean = base / 20.0
        responses = {}
        for i in range(1, 8):
            v = max(1, min(5, int(round(random.gauss(target_mean, 0.7)))))
            responses[f"q{i}"] = v
        score = score_awareness(responses)
        db.session.add(AwarenessAssessment(
            user_id=user.id, phase=phase, responses=responses, score=score,
            completed_at=datetime.utcnow() - timedelta(days=30 if phase == "pre" else 2),
        ))
        created += 1
    return created


def _generate_sus(user: User) -> int:
    """Generate a SUS response. Returns rows created."""
    if SUSResponse.query.filter_by(user_id=user.id).first() is not None:
        return 0
    responses = {}
    for i in range(1, 11):
        if i % 2 == 1:
            responses[f"q{i}"] = random.choice([3, 4, 4, 5, 5])
        else:
            responses[f"q{i}"] = random.choice([1, 2, 2, 3, 3])
    score = calculate_sus(responses)
    db.session.add(SUSResponse(user_id=user.id, responses=responses, sus_score=score))
    return 1


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        scenarios = Scenario.query.filter_by(is_active=True).all()
        if len(scenarios) < 20:
            print(f"ERROR: Only {len(scenarios)} active scenarios. Need at least 20.")
            return
        print(f"Found {len(scenarios)} active scenarios")

        # Count existing synthetic users
        existing = User.query.filter(User.username.like("synthetic_%")).count()
        if existing > 0:
            print(f"Found {existing} existing synthetic users. Skipping user creation.")
        else:
            user_idx = 0
            total_users = 0
            total_attempts = 0

            for label, base_acc, rt_c, rt_w, n_users, (att_min, att_max) in PROFILES:
                users_created = 0
                for _ in range(n_users):
                    first, last = _pick_name(user_idx)
                    email = f"synthetic_{user_idx:04d}@ahrid.local"
                    job_role = random.choice(JOB_ROLES)
                    user = _make_user(user_idx, email, job_role, first, last)
                    db.session.add(user)
                    db.session.flush()

                    n_att = random.randint(att_min, att_max)
                    user_acc = max(0.05, min(0.97, random.gauss(base_acc, PER_USER_ACCURACY_JITTER)))
                    attempts = _generate_attempts(user, scenarios, user_acc, rt_c, rt_w, n_att)
                    for a in attempts:
                        db.session.add(a)
                    total_attempts += len(attempts)
                    users_created += 1
                    total_users += 1
                    user_idx += 1

                print(f"  {label}: {users_created} users, accuracy={base_acc:.0%}")

            db.session.commit()
            print(f"\nCreated {total_users} synthetic users with {total_attempts} attempts")

        # Generate awareness assessments and SUS responses for all synthetic users
        synthetic_users = User.query.filter(User.username.like("synthetic_%")).all()
        profile_map = {}
        idx = 0
        for label, base_acc, rt_c, rt_w, n_users, (att_min, att_max) in PROFILES:
            for _ in range(n_users):
                if idx < len(synthetic_users):
                    profile_map[str(synthetic_users[idx].id)] = label
                idx += 1

        awareness_added = 0
        sus_added = 0
        for u in synthetic_users:
            risk_profile = profile_map.get(str(u.id), "medium")
            awareness_added += _generate_awareness(u, risk_profile)
            sus_added += _generate_sus(u)

        db.session.commit()
        print(f"Generated {awareness_added} awareness assessments and {sus_added} SUS responses")


if __name__ == "__main__":
    main()
