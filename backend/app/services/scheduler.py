"""APScheduler-driven background jobs (BSc scope: 2 jobs only).

Jobs:
  * threat_ingestion  every 6 hours
  * risk_recalc       every 1 hour (no-op placeholder; recalc happens
                       per-attempt synchronously)

Other heavyweight jobs (RF retrain, KMeans recluster, news ingestion,
LLM scenario generation, weekly XP reset) have been removed in line with
the BSc scope reduction. RF / KMeans retrain is exposed as a manual
admin trigger via ``/api/v1/admin/retrain-models``.
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

LOG = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _wrap(app, fn, *args, **kwargs):
    def runner():
        with app.app_context():
            try:
                fn(*args, **kwargs)
            except Exception:
                LOG.exception("Scheduled job %s failed", fn.__name__)

    return runner


def _job_threat_ingestion():
    from app.services.threat_ingestion import ThreatIngestionService
    LOG.info("Scheduler → starting threat ingestion run")
    return ThreatIngestionService().run_ingestion()


def _job_recalc_risk_scores():
    """Hourly hook for batch risk recomputation. Per-attempt recalc is
    synchronous (see ``risk_scorer.recalculate_for_user``); this job is a
    placeholder for periodic full sweeps."""
    LOG.debug("Risk-score recalculation tick (no-op).")


def init_scheduler(app) -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    scheduler = BackgroundScheduler(daemon=True, timezone="UTC")
    refresh_hours = int(app.config.get("THREAT_FEED_REFRESH_HOURS", 6))

    scheduler.add_job(
        _wrap(app, _job_threat_ingestion),
        trigger=IntervalTrigger(hours=refresh_hours),
        id="threat_ingestion",
        replace_existing=True,
    )
    scheduler.add_job(
        _wrap(app, _job_recalc_risk_scores),
        trigger=IntervalTrigger(hours=1),
        id="risk_recalc",
        replace_existing=True,
    )

    if app.config.get("ENABLE_SCHEDULER", False):
        scheduler.start()
        LOG.info("Scheduler started  threat ingestion every %dh", refresh_hours)
    else:
        LOG.info("Scheduler initialised but not started (ENABLE_SCHEDULER=False).")

    _scheduler = scheduler
    return scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
