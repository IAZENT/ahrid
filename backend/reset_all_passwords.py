"""Reset all user passwords to a single value. One-time use."""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone

from app import create_app
from app.extensions import db
from app.models.user import User

NEW_PASSWORD = "P@ssw0rd1@!!"
BATCH_SIZE = 100


def reset_all():
    app = create_app("development")
    with app.app_context():
        total = db.session.query(User).count()
        print(f"Found {total} users. Resetting passwords to '{NEW_PASSWORD}' ...")
        start = time.time()

        users = User.query.all()
        for i, user in enumerate(users, 1):
            user.set_password(NEW_PASSWORD)
            user.failed_login_count = 0
            user.locked_until = None
            if i % BATCH_SIZE == 0:
                db.session.commit()
                print(f"  {i}/{total} done")

        db.session.commit()
        elapsed = time.time() - start
        print(f"Done. {total} passwords reset in {elapsed:.1f}s")


if __name__ == "__main__":
    reset_all()
