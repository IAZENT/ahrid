"""Seed a small fixture of admin / manager / employee users (BSc demo).

No invites, no organisation, no super_admin. Run after wiping the dev DB:

    python seed_users.py
"""
from __future__ import annotations

from datetime import datetime

from app import create_app
from app.extensions import db
from app.models.user import User

USERS = [
    # email, username, password, role, job_role, first, last
    ("admin@ahrid.local",     "admin",     "Admin@SecurePass1!",   "admin",    "it",         "Asha",   "Sharma"),
    ("manager@ahrid.local",   "manager",   "Manager@SecurePass1!", "manager",  "management", "Bibek",  "Karki"),
    ("alice@ahrid.local",     "alice",     "User@SecurePass1!",    "employee", "finance",    "Alice",  "Tamang"),
    ("bob@ahrid.local",       "bob",       "User@SecurePass1!",    "employee", "sales",      "Bob",    "Magar"),
    ("carol@ahrid.local",     "carol",     "User@SecurePass1!",    "employee", "hr",         "Carol",  "Rai"),
    ("dilip@ahrid.local",     "dilip",     "User@SecurePass1!",    "employee", "accountant", "Dilip",  "Shrestha"),
    ("eva@ahrid.local",       "eva",       "User@SecurePass1!",    "employee", "receptionist", "Eva",  "Gurung"),
]


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()
        created = 0
        for email, username, password, role, job_role, first, last in USERS:
            # Skip if either email OR username already exists. Both columns
            # are UNIQUE so a partial match would otherwise crash the run.
            if User.query.filter(
                (User.email == email) | (User.username == username)
            ).first():
                continue
            u = User(
                email=email,
                username=username,
                first_name=first,
                last_name=last,
                role=role,
                job_role=job_role,
                is_active=True,
                is_verified=True,
                consent_given=True,
                consent_timestamp=datetime.utcnow(),
            )
            u.set_password(password)
            db.session.add(u)
            created += 1
        db.session.commit()
        print(f"Seeded {created} users (skipped {len(USERS) - created} existing).")


if __name__ == "__main__":
    main()
