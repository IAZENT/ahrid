"""Lightweight in-process background-job registry for admin-triggered tasks.

We deliberately keep this tiny  a single job per kind (``ingestion`` /
``retrain``) is enough for the admin UI. State is per-process; in a
multi-worker deployment a Redis/RQ backed store would replace this (Phase
13 hardening).
"""
from __future__ import annotations

import logging
import os
import threading
import traceback
import uuid
from datetime import datetime, timezone
from typing import Callable

LOG = logging.getLogger("background_jobs")


def _utc_iso() -> str:
    """RFC 3339 UTC timestamp ending in 'Z'.

    ``datetime.utcnow().isoformat()`` returns a naive string with no
    timezone marker, which JavaScript ``new Date(...)`` parses as
    *local* time. That mismatch made the admin dashboard show absurd
    durations (e.g. 345 min for a 1-second retrain in UTC+05:45). We
    always emit an explicit ``Z`` suffix so the browser parses the
    timestamp as UTC.
    """
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

_LOCK = threading.Lock()
_JOBS: dict[str, dict] = {}


def _set(kind: str, **patch) -> dict:
    with _LOCK:
        state = _JOBS.setdefault(kind, {"status": "idle"})
        state.update(patch)
        return dict(state)


def get_state(kind: str) -> dict:
    with _LOCK:
        return dict(_JOBS.get(kind, {"status": "idle"}))


def _run(kind: str, job_id: str, app, fn: Callable[[], dict | None]) -> None:
    """Worker function  pushes Flask app context then calls ``fn``."""
    with app.app_context():
        try:
            result = fn() or {}
            _set(
                kind,
                status="completed",
                job_id=job_id,
                finished_at=_utc_iso(),
                result=result,
                error=None,
            )
        except Exception as exc:  # pragma: no cover  best-effort logging
            LOG.exception("Background job %s failed", kind)
            _set(
                kind,
                status="failed",
                job_id=job_id,
                finished_at=_utc_iso(),
                error=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(limit=4),
            )


def launch(kind: str, app, fn: Callable[[], dict | None]) -> dict:
    """Start ``fn`` in a daemon thread if no job of ``kind`` is running."""
    with _LOCK:
        current = _JOBS.get(kind)
        if current and current.get("status") == "running":
            return {**current, "already_running": True}
    job_id = str(uuid.uuid4())
    _set(
        kind,
        status="running",
        job_id=job_id,
        started_at=_utc_iso(),
        finished_at=None,
        result=None,
        error=None,
    )
    # For local tests (TESTING / RUN_JOBS_SYNC), run synchronously so the
    # admin endpoint responses are deterministic.
    if os.environ.get("RUN_JOBS_SYNC") or app.config.get("TESTING"):
        _run(kind, job_id, app, fn)
    else:
        threading.Thread(
            target=_run, args=(kind, job_id, app, fn), daemon=True,
            name=f"ahrip-{kind}-{job_id[:8]}",
        ).start()
    return get_state(kind)
