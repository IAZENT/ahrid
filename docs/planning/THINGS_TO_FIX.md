# AHRIP - Things To Fix (audited 2026-05-03)

Active bugs, blockers, and follow-ups. Resolved items move to the bottom.

Format: `[severity] [phase/area] short title - description`.
Severity: 🔴 blocker · 🟠 high · 🟡 medium · ⚪ low / cleanup.

---

## Open

### Functional bugs

- 🟠 **[tests] One auth test asserts non-existent industry normalisation** - `tests/test_auth.py::test_register_returns_201_with_job_role_and_industry` expects `organisation.industry == "finance"` but the endpoint persists the literal payload value (`"Security"`). Either implement a job_role → industry mapping or relax the assertion. CI will be red until fixed. _(opened 2026-05-03)_

### Production-readiness gaps (all deferred per user direction)

- 🔴 **[infra] Rate-limit / blocklist storage in-memory but Procfile runs 2 workers** - `RATE_LIMIT_STORAGE=memory://` + `gunicorn --workers 2` means each worker has its own limit counters and JWT blocklist. Move to Redis (`RATE_LIMIT_STORAGE=redis://…`) before any prod deploy.
- 🟠 **[infra] Secret defaults still permitted in production** - `BaseConfig.SECRET_KEY` / `JWT_SECRET_KEY` fall through to defaults if env vars are missing. `ProductionConfig` should refuse start-up when defaults are detected.
- 🟠 **[infra] No email delivery** - required for password reset, invite delivery, profile-change-request status. Add SMTP / Mailgun / SES adapter behind `notifications.emit()` with DB + email dual-write.
- 🟠 **[auth] No password-reset flow** - `change-password` exists, but no `forgot-password → token → email → reset` loop.
- 🟠 **[auth] No MFA / 2FA** - security-awareness SaaS without TOTP / WebAuthn is a credibility gap with enterprise buyers.
- 🟠 **[infra] No CI / container / deploy automation** - no `.github/`, no `Dockerfile`, no `docker-compose.yml`. `Procfile` alone won't pass enterprise procurement.
- 🟡 **[gdpr] No self-service data export / deletion** - `consent_timestamp` is recorded but `/me/data-export` and `/me/delete-account` are missing.
- 🟡 **[obs] Observability is bare** - no request IDs, no Sentry, no `/metrics`, only `logging.basicConfig`.
- 🟡 **[infra] Background-job registry is in-process only** - `services/background_jobs.py` uses a module dict + `threading.Thread`. Multi-worker prod will see divergent job state. Move to Redis or a `background_jobs` SQL table.

### Cleanup / tech debt

- 🟡 **[python] `datetime.utcnow()` deprecation** - still emits ~2,100 warnings per `pytest` run (Python 3.13). Migrate to `datetime.now(timezone.utc)` across `models/`, `utils/security.py`, `api/auth.py`, `services/scheduler.py`, `services/threat_ingestion.py`, `services/thompson_sampler.py`.
- 🟡 **[frontend] Single 1.14 MB JS chunk** - `vite build` warns. Use `React.lazy` on the admin / manager route trees and split Recharts + Framer Motion via `manualChunks`.
- ⚪ **[backend] Admin `retrain-models` imports `train_models` as a top-level module** - works because backend is cwd in dev. Either package `train_models` into `app/services/` or explicitly add `backend/` to `sys.path` at app start.
- ⚪ **[backend] CSP allows `'unsafe-inline'` for script + style** - needed for Vite-injected styles. Tighten with nonces pre-pentest.
- ⚪ **[backend] Manager `assign-training` not persisted** - endpoint returns 202 + emits a notification, but no `training_assignments` table yet. Adaptive engine therefore ignores assignments. See REMAINING_WORK.md §B.
- ⚪ **[backend] `/manager/history` uses accuracy as a risk proxy** - `RiskScore` rows are overwritten in place. Either weekly snapshots or `composite_history` JSON column.
- ⚪ **[backend] RiskHeatmap N+1** - first dashboard render fires one `/team/<id>/profile` request per user (capped at 60). Add `GET /manager/heatmap` for orgs > 30.
- ⚪ **[backend] `daily-challenge/complete` reuses `badges_earned` JSON as marker store** - works, but a proper `daily_challenge_completions` table is cleaner.
- ⚪ **[frontend] Tailwind pinned to 3.4.x** - v4 migration is mostly drop-in (tokens are CSS-variable based) but deferred.
- ⚪ **[frontend] Editor flags `Unknown at rule @tailwind`** - VS Code / Windsurf CSS server doesn't understand the directive without the Tailwind extension. PostCSS handles them correctly. Install the "Tailwind CSS IntelliSense" extension to silence locally.
- ⚪ **[frontend] RF "X% likely to click" is a heuristic mapping** - banded mapping (critical 82 / high 62 / medium 38 / low 12) until the RF model trains on real data; replace with `predict_proba`.

---

## Resolved (2026-05-03)

- ✅ **Phase-23 Phase-2 - profile-change-request workflow** - employees file `job_role` / `department` change requests from the Profile page; admins approve / reject from a new inbox page; sidebar shows live pending-count badge (60 s polling); approval atomically updates the user row and emits a notification.
- ✅ **Backend tests - 202/203 passing** - fixed two test bugs:
  - `test_request_supersedes_prior_pending_for_same_field`: cast string PKs with `uuid.UUID(...)` for `db.session.get(ProfileChangeRequest, ...)`.
  - `test_thompson_sampler_hints.py`: pass UUID `_USER_ID` instead of a string literal so SQLAlchemy UUID-column binding works.
- ✅ **Light-theme WCAG 2.1 AA pass** - accent / risk / muted / xp tokens rebalanced; global `:focus-visible` ring + `prefers-reduced-motion` guard added.
- ✅ **`<NotificationBell>` + Toaster + `<EmptyState>` shipped** - event-driven notifications system covering level-up, badge-earned, streak-milestone, training-assigned, risk-escalation, announcements, and profile-change-request approvals/rejections.
- ✅ **Free-text question types** - 3 new question types (`short_answer`, `descriptive`, `fill_in_blank`) with Ollama-driven rubric grading + heuristic fallback. Backend never calls Gemini for grading (quota preservation).
- ✅ **Username login** - `/auth/login` accepts `identifier` (email **or** username); both lowercased server-side.
- ✅ **Admin coaching** - `coaching_note` + `coaching_hints` (`category_boost`, `difficulty_pin`, `ban_categories`, `focus_keywords`) consumed by Thompson Sampler + adaptive engine.
- ✅ **Training session `localStorage` persistence** - mid-session refresh resumes on the same scenario index with the same answers.
- ✅ **Silent JWT refresh interceptor** - `frontend/src/api/client.ts` swaps in a fresh access token on 401 and replays the request once.
- ✅ **AI generation page rebuilt** - proper design tokens, live A/B/C/D distribution bar, Gemini + Ollama provider tiles, `/admin/ollama/health` probe never pings Gemini.
- ✅ **Threat feed cleanup** - PhishTank removed (dead since 2024), Phishing.Database GitHub feed wired, OTX free-tier resilience (subscribed + activity) 3-query fallback chain.
- ✅ **Paid-LLM purge** - Groq, NVIDIA, Kimi, Magpie TTS, Supabase Storage all removed. LLM stack is strictly Gemini 2.5 Flash + Ollama `gemma4:e4b` (`think=false`).
- ✅ **Streak counter 6-tier progression** - day 0 ember → day 30 legendary gold (was 2-tier).
- ✅ **JWT `InsecureKeyLengthWarning`** - dev `.env` ships a 32-byte (256-bit) base64 key; example file documents the requirement.

---

## Watch List

- 🟡 **textblob corpora** - needs `python -m textblob.download_corpora` on first run; `bootstrap.sh` covers this.
- 🟡 **VADER vs TextBlob** - VADER is the primary compound-score source; TextBlob is optional.
- 🟡 **MIN_TRAINING_SAMPLES = 20** - RF won't train until threshold; graceful fallback already in place.
- 🟡 **Talisman is prod-only** - dev uses plain Flask to avoid HSTS caching + `force_https` redirects fighting Vite HMR. Verify prod headers with `curl` once a deploy target exists.
- ⚪ **psycopg2-binary** - Supabase / managed Postgres prefers connection pooling; verify SSL params in `DATABASE_URL` when Phase 15 lands.
