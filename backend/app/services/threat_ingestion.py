"""Multi-source OSINT threat ingestion pipeline.

Pipeline stages:
    1. FETCH        from PhishStats, OpenPhish, AlienVault OTX, URLScan.io
    2. VALIDATE     structural URL checks only (no network requests)
    3. DEDUPLICATE  collapse duplicates inside batch + last 48h DB rows
    4. CLASSIFY     scenario_classifier.classify_url
    5. SANITISE     scenario_generator.sanitise_url
    6. GENERATE     up to MAX_NEW_SCENARIOS_PER_RUN scenarios per run
    7. PERSIST      bulk insert ThreatFeedEntry + Scenario rows; return stats

The service is defensive: any single source can fail (no API key, network
error, malformed payload) without aborting the run.
"""
from __future__ import annotations

import csv
import io
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable
from urllib.parse import urlparse, urlunparse

import requests
from flask import current_app

from app.extensions import db
from app.models.scenario import Scenario
from app.models.threat_feed import ThreatFeedEntry
from app.services.scenario_classifier import classify_url
from app.services.scenario_generator import (
    generate_scenario_from_entry,
    sanitise_url,
)

LOG = logging.getLogger(__name__)

MAX_NEW_SCENARIOS_PER_RUN = 20
DEDUPE_WINDOW = timedelta(hours=48)
FETCH_TIMEOUT = 30

# Structural URL validation patterns
_URL_RE = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)
_MIN_HOST_PARTS = 2  # at least domain.tld


@dataclass
class RawThreat:
    source: str
    url: str
    target_brand: str | None = None
    otx_pulse_name: str | None = None
    urlscan_verdict: str | None = None


@dataclass
class IngestionStats:
    fetched: int = 0
    validated: int = 0
    deduplicated: int = 0
    classified: int = 0
    scenarios_created: int = 0
    invalid_urls_discarded: int = 0
    sources: dict[str, int] = field(
        default_factory=lambda: {
            "phishstats": 0,
            "openphish": 0,
            "otx": 0,
            "urlscan": 0,
        }
    )

    def to_dict(self) -> dict:
        return {
            "fetched": self.fetched,
            "validated": self.validated,
            "deduplicated": self.deduplicated,
            "classified": self.classified,
            "scenarios_created": self.scenarios_created,
            "invalid_urls_discarded": self.invalid_urls_discarded,
            "sources": dict(self.sources),
        }


def _normalise(url: str) -> str:
    try:
        parsed = urlparse(url.strip().lower())
        path = parsed.path.rstrip("/")
        return urlunparse(
            (parsed.scheme, parsed.netloc, path, "", parsed.query, "")
        )
    except Exception:  # pragma: no cover - defensive
        return url.strip().lower()


# ---------------------------------------------------------------------------
# Structural URL validation (no network requests)
# ---------------------------------------------------------------------------
def validate_url(url: str) -> bool:
    """Return True if the URL is structurally valid for processing.

    No HTTP HEAD probes — phishing URLs are expected to go offline fast,
    so network validation killed all conversions in the previous pipeline.
    """
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if not _URL_RE.match(url):
        return False
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        # Must have at least domain.tld
        if host.count(".") < 1:
            return False
        # No bare IP with only digits and dots (optional: allow if desired)
        # Reject obviously broken hosts
        if len(host) < 4:
            return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Fetchers — each returns ``list[RawThreat]`` and never raises.
# ---------------------------------------------------------------------------
def _fetch_phishstats(feed_url: str) -> list[RawThreat]:
    """Fetch a phishing URL list.

    The feed URL field is named ``PHISHSTATS_FEED_URL`` for backward
    compatibility, but the real PhishStats CSV (`phish_score.csv`) has been
    404 since early 2026. The default now points at the actively maintained
    **Phishing.Database** GitHub feed (no API key, daily refresh, plain text
    one-URL-per-line). Set ``PHISHSTATS_FEED_URL`` in ``.env`` to override.
    """
    if not feed_url:
        return []
    try:
        LOG.info("PhishURLs feed: fetching from %s", feed_url)
        resp = requests.get(
            feed_url,
            timeout=FETCH_TIMEOUT,
            headers={"User-Agent": "AHRID/2.0"},
        )
        resp.raise_for_status()
        text = resp.text
        out: list[RawThreat] = []

        # If it's CSV (legacy PhishStats), parse columns; otherwise treat as
        # one-URL-per-line plain text (Phishing.Database / URLhaus / etc.).
        first_non_comment = next(
            (l for l in text.splitlines() if l.strip() and not l.strip().startswith("#")),
            "",
        )
        if "," in first_non_comment and any(
            first_non_comment.startswith(p) for p in ("\"", "20")
        ):
            # CSV path — column index 2 is the URL in PhishStats schema.
            reader = csv.reader(io.StringIO(text))
            for row in reader:
                if not row or row[0].startswith("#"):
                    continue
                if len(row) >= 3 and row[2].strip().strip('"').startswith("http"):
                    out.append(RawThreat(source="phishstats", url=row[2].strip().strip('"')))
        else:
            # Plain-text path — every non-comment, non-blank http(s) line.
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and line.startswith("http"):
                    out.append(RawThreat(source="phishstats", url=line))

        LOG.info("PhishURLs feed: parsed %d entries", len(out))
        return out[:300]  # cap so we don't overwhelm the pipeline
    except Exception as exc:
        LOG.warning("PhishURLs feed fetch failed: %s", exc)
        return []


def _fetch_openphish(feed_url: str) -> list[RawThreat]:
    try:
        resp = requests.get(feed_url, timeout=20)
        resp.raise_for_status()
        return [
            RawThreat(source="openphish", url=line.strip())
            for line in resp.text.splitlines()
            if line.strip().startswith("http")
        ]
    except Exception as exc:
        LOG.warning("OpenPhish fetch failed: %s", exc)
        return []


def _fetch_otx(api_key: str | None) -> list[RawThreat]:
    """Fetch phishing indicators from AlienVault OTX.

    Free-tier-friendly strategy: hit ``/pulses/subscribed`` first (which IS
    populated by default — every OTX account auto-subscribes to a curated
    set), then if it returns nothing fall back to ``/pulses/activity`` (the
    public timeline that needs no subscriptions). Both endpoints return
    pulses with inlined indicator arrays. We then filter by phishing-related
    keywords in pulse name + tags.
    """
    if not api_key:
        LOG.info("OTX: skipped (no API key)")
        return []

    headers = {"X-OTX-API-KEY": api_key, "User-Agent": "AHRID/2.0"}
    phish_kw = (
        "phish", "credential", "smish", "vish", "scam", "fraud",
        "lure", "spoof", "imperson",
    )

    def _harvest(results: list[dict]) -> list[RawThreat]:
        out: list[RawThreat] = []
        for pulse in results or []:
            name = (pulse.get("name") or "").lower()
            tags = [t.lower() for t in (pulse.get("tags") or [])]
            relevant = (
                any(kw in name for kw in phish_kw)
                or any(any(kw in t for kw in phish_kw) for t in tags)
            )
            if not relevant:
                continue
            for ind in pulse.get("indicators") or []:
                ind_type = (ind.get("type") or "").upper()
                value = (ind.get("indicator") or "").strip()
                if not value:
                    continue
                if ind_type == "URL":
                    url = value if value.startswith("http") else f"http://{value}"
                elif ind_type in ("DOMAIN", "HOSTNAME"):
                    url = f"http://{value}"
                else:
                    continue
                out.append(
                    RawThreat(source="otx", url=url, otx_pulse_name=pulse.get("name")),
                )
        return out

    out: list[RawThreat] = []
    endpoints = [
        ("subscribed", "https://otx.alienvault.com/api/v1/pulses/subscribed"),
        ("activity",   "https://otx.alienvault.com/api/v1/pulses/activity"),
    ]
    for label, url in endpoints:
        try:
            LOG.info("OTX: fetching %s pulses", label)
            resp = requests.get(
                url, params={"limit": 50, "page": 1},
                headers=headers, timeout=FETCH_TIMEOUT,
            )
            resp.raise_for_status()
            results = (resp.json() or {}).get("results", []) or []
            LOG.info("OTX[%s]: %d pulses returned", label, len(results))
            harvested = _harvest(results)
            LOG.info("OTX[%s]: %d phishing-relevant indicators", label, len(harvested))
            out.extend(harvested)
            if len(out) >= 20:
                break  # got enough, don't burn rate-limit on the second endpoint
        except Exception as exc:
            LOG.warning("OTX[%s] fetch failed: %s", label, exc)

    # Dedupe by URL — both endpoints can return the same pulses.
    seen: set[str] = set()
    deduped: list[RawThreat] = []
    for r in out:
        if r.url in seen:
            continue
        seen.add(r.url)
        deduped.append(r)
    LOG.info("OTX: %d unique phishing indicators", len(deduped))
    return deduped[:200]


_URLSCAN_QUERIES = (
    # Most precise — paid keys hit this without 403; free keys often allowed too.
    'task.tags:"phishing"',
    # Verdict-based — covers anything URLScan's own classifier flagged.
    "verdicts.overall.malicious:true",
    # Broad fallback — pages whose URL screams "credential capture".
    'page.url:"login" OR page.url:"verify" OR page.url:"account"',
)


def _fetch_urlscan(api_key: str | None) -> list[RawThreat]:
    """Fetch recent phishing-likely scans from URLScan.io.

    Tries 3 progressively-broader queries; stops at the first one that
    actually returns rows on this API key (free tier sometimes 403s on the
    most precise queries). All queries are read-only ``/search`` calls.
    """
    if not api_key:
        LOG.info("URLScan: skipped (no API key)")
        return []

    headers = {"API-Key": api_key, "User-Agent": "AHRID/2.0"}
    for query in _URLSCAN_QUERIES:
        try:
            LOG.info("URLScan: trying query %r", query)
            resp = requests.get(
                "https://urlscan.io/api/v1/search/",
                params={"q": query, "size": 100},
                headers=headers, timeout=FETCH_TIMEOUT,
            )
            if resp.status_code in (401, 403):
                LOG.info("URLScan: %d on query %r, trying broader fallback", resp.status_code, query)
                continue
            resp.raise_for_status()
            results = (resp.json() or {}).get("results", []) or []
            LOG.info("URLScan[%r]: got %d results", query, len(results))
            if not results:
                continue
            out: list[RawThreat] = []
            for item in results:
                page = item.get("page") or {}
                verdicts = (item.get("verdicts") or {}).get("overall") or {}
                url = page.get("url")
                if not url:
                    continue
                out.append(
                    RawThreat(
                        source="urlscan",
                        url=url,
                        urlscan_verdict=(
                            "phishing" if verdicts.get("malicious") else "suspicious"
                        ),
                    )
                )
            LOG.info("URLScan: extracted %d URLs (query=%r)", len(out), query)
            return out
        except Exception as exc:
            LOG.warning("URLScan query %r failed: %s", query, exc)
    return []


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------
class ThreatIngestionService:
    """End-to-end ingestion run. Stateless except for the SQLAlchemy session."""

    def __init__(self, *, fetcher_overrides: dict | None = None) -> None:
        self._overrides = fetcher_overrides or {}

    def _cfg(self, key: str, default=None):
        try:
            return current_app.config.get(key, default)
        except RuntimeError:
            return default

    # --- Stage 1 ------------------------------------------------------------
    def fetch_all(self) -> list[RawThreat]:
        sources = {
            "phishstats": lambda: _fetch_phishstats(
                self._cfg("PHISHSTATS_FEED_URL", "https://phishstats.info/phish_score.csv")
            ),
            "openphish": lambda: _fetch_openphish(
                self._cfg("OPENPHISH_FEED_URL", "https://openphish.com/feed.txt")
            ),
            "otx": lambda: _fetch_otx(self._cfg("ALIENVAULT_OTX_KEY")),
            "urlscan": lambda: _fetch_urlscan(self._cfg("URLSCAN_API_KEY")),
        }
        sources.update(self._overrides)
        out: list[RawThreat] = []
        for name, fn in sources.items():
            try:
                items = fn() or []
                LOG.info("Fetched %d threats from %s", len(items), name)
                out.extend(items)
            except Exception as exc:  # pragma: no cover
                LOG.warning("Source %s raised: %s", name, exc)
        return out

    # --- Stage 2 (structural only — no HEAD probes) -------------------------
    def validate_urls(self, raws: Iterable[RawThreat]) -> tuple[list[RawThreat], int]:
        """Structural validation only. No HTTP requests to phishing URLs."""
        valid: list[RawThreat] = []
        invalid = 0
        for raw in raws:
            if validate_url(raw.url):
                valid.append(raw)
            else:
                invalid += 1
                LOG.debug("URL structurally invalid, discarded: %s", raw.url[:80])
        return valid, invalid

    # --- Stage 3 ------------------------------------------------------------
    def deduplicate(self, raws: Iterable[RawThreat]) -> list[RawThreat]:
        cutoff = datetime.utcnow() - DEDUPE_WINDOW
        seen_db = {
            _normalise(u)
            for (u,) in db.session.query(ThreatFeedEntry.original_url)
            .filter(ThreatFeedEntry.ingested_at >= cutoff)
            .all()
        }
        seen_batch: set[str] = set()
        out: list[RawThreat] = []
        for raw in raws:
            norm = _normalise(raw.url)
            if norm in seen_db or norm in seen_batch:
                continue
            seen_batch.add(norm)
            out.append(raw)
        return out

    # --- Stages 4–7 ---------------------------------------------------------
    def run_ingestion(self) -> dict:
        stats = IngestionStats()
        raw = self.fetch_all()
        stats.fetched = len(raw)
        for r in raw:
            stats.sources[r.source] = stats.sources.get(r.source, 0) + 1

        valid, invalid = self.validate_urls(raw)
        stats.validated = len(valid)
        stats.invalid_urls_discarded = invalid

        unique = self.deduplicate(valid)
        stats.deduplicated = len(unique)

        new_entries: list[ThreatFeedEntry] = []
        for r in unique:
            entry = ThreatFeedEntry(
                source=r.source,
                original_url=r.url,
                target_brand=r.target_brand,
                otx_pulse_name=r.otx_pulse_name,
                urlscan_verdict=r.urlscan_verdict,
            )
            new_entries.append(entry)

        # Bulk-add feed entries first so we have IDs for FK
        if new_entries:
            db.session.add_all(new_entries)
            db.session.flush()

        # Stage 4 + 5 + 6 — produce up to MAX_NEW_SCENARIOS_PER_RUN scenarios.
        # We process *just-fetched* entries first, then top up the same budget
        # from previously-ingested entries that were never converted (e.g.
        # because earlier runs hit their cap). Without this, the unconverted
        # backlog (typically 800+ rows after a few PhishStats / OpenPhish
        # pulls) would sit in the DB unused even though every scheduled run
        # produces only ~20 conversions.
        candidates: list[ThreatFeedEntry] = list(new_entries)
        if len(candidates) < MAX_NEW_SCENARIOS_PER_RUN * 4:
            backlog = (
                db.session.query(ThreatFeedEntry)
                .filter(ThreatFeedEntry.was_converted.is_(False))
                .filter(~ThreatFeedEntry.id.in_([e.id for e in new_entries]) if new_entries else True)
                .order_by(ThreatFeedEntry.ingested_at.desc())
                .limit(MAX_NEW_SCENARIOS_PER_RUN * 4)
                .all()
            )
            candidates.extend(backlog)

        # Round-robin interleave by source so every feed (PhishStats,
        # OpenPhish, OTX, URLScan) contributes at least a few scenarios per
        # run instead of the first one in dict order monopolising the
        # MAX_NEW_SCENARIOS_PER_RUN budget. Without this, OpenPhish and OTX
        # entries pile up in the DB but never produce a Scenario.
        by_source: dict[str, list[ThreatFeedEntry]] = {}
        for c in candidates:
            by_source.setdefault(c.source or "unknown", []).append(c)
        interleaved: list[ThreatFeedEntry] = []
        while any(by_source.values()):
            for src in list(by_source.keys()):
                if by_source[src]:
                    interleaved.append(by_source[src].pop(0))
        candidates = interleaved

        # Pre-load (brand, lure_type) keys from scenarios already created in
        # the last 14 days so a feed full of *technically distinct* URLs
        # pointing at the same brand (e.g. 50 redirector subdomains of
        # `000webhostapp.com`) doesn't blow up into 50 visually identical
        # MCQ rows. We collapse on (brand, lure_type) which is the level at
        # which the user-facing template differs.
        brand_lure_seen: set[tuple[str, str]] = set()
        recent_brand_cutoff = datetime.utcnow() - timedelta(days=14)
        for brand, lure in db.session.query(
            Scenario.threat_brand, ThreatFeedEntry.lure_type
        ).join(
            ThreatFeedEntry, Scenario.threat_feed_id == ThreatFeedEntry.id
        ).filter(
            Scenario.is_active.is_(True),
            Scenario.created_at >= recent_brand_cutoff,
            Scenario.threat_brand.isnot(None),
            ThreatFeedEntry.lure_type.isnot(None),
        ):
            brand_lure_seen.add(((brand or "").lower(), (lure or "").lower()))

        budget = MAX_NEW_SCENARIOS_PER_RUN
        for entry in candidates:
            classification = classify_url(
                entry.original_url, entry.target_brand, entry.otx_pulse_name
            )
            stats.classified += 1

            if budget <= 0:
                continue

            try:
                sanitised = sanitise_url(entry.original_url)
                scenario = generate_scenario_from_entry(entry, sanitised, classification)
            except Exception as exc:
                LOG.error(
                    "[RESULT] ✗ failed to generate scenario for %s: %s",
                    entry.original_url[:60], exc,
                )
                continue

            key = (
                (scenario.threat_brand or "").lower(),
                (classification.lure_type or "").lower(),
            )
            if key in brand_lure_seen:
                # Same brand + same lure type already covered. Mark the
                # feed entry as classified so we don't reconsider it next
                # run, but skip scenario creation.
                entry.was_converted = True
                entry.category = classification.category
                entry.lure_type = classification.lure_type
                continue

            db.session.add(scenario)
            db.session.flush()
            entry.was_converted = True
            entry.category = classification.category
            entry.lure_type = classification.lure_type
            brand_lure_seen.add(key)
            stats.scenarios_created += 1
            budget -= 1
            LOG.info(
                "[RESULT] ✓ scenario created: '%s' (cat=%s, diff=%d)",
                scenario.title[:60], scenario.category, scenario.difficulty,
            )

        db.session.commit()
        LOG.info("Threat ingestion run complete: %s", stats.to_dict())
        return stats.to_dict()
