# AHRIP - Remaining Work Backlog (audited 2026-05-04)

Source-of-truth task list of what is **not yet implemented**. Anything previously listed here that ships in the current code has been removed. Cross-references to `THINGS_TO_FIX.md` for known bugs.

Legend: ✅ done · ⬜ pending · 🟡 partial.

---

## SuperAdmin / SaaS-owner control plane - ✅ shipped

The role hierarchy `super_admin → admin → manager → employee` is wired end-to-end. `super_admin` is an **additive** role: a super_admin still runs their own tenant as an admin/manager/employee and gains cross-tenant "Platform" nav on top.

**Done**
- `super_admin_required` decorator; `admin_required`/`manager_required` accept super_admins transparently.
- Frontend `ProtectedRoute` + sidebar treat `super_admin` as a super-set of every lower role, so they see Learn / Team / Admin / Platform sections.
- `/api/v1/super-admin/stats` returns org / user / 24-h-attempt counts with `pending_organisations` / `rejected_organisations` breakdown.
- `/api/v1/super-admin/organisations[?status=…]` + `.../<id>/{approve,reject}` - tenant approval workflow. New registrations land in `approval_status='pending'` with their admin `is_active=False`; login returns `org_pending_approval` until approved. Tests run with auto-approve to keep existing fixtures simple.
- `/api/v1/super-admin/admins` lists every super_admin; `/api/v1/super-admin/{promote,users/<id>/promote,users/<id>/demote}` mint and remove super_admins. Guardrails: cannot promote unapproved-tenant users, cannot self-promote/demote, cannot demote the last super_admin.
- Forgot-password chain: `POST /auth/forgot-password` routes to `super_admin` for admins / to `admin` for everyone else; approval mints a 24-hour single-use token (SHA-256 hashed at rest); `POST /auth/reset-password` consumes the token and clears lock-state.
- Admin queue: `/api/v1/admin/password-reset-requests[/<id>/{approve,reject}]`.
- Public pages: `/forgot-password`, `/reset-password?token=…`.
- Super_admin pages: `/app/super-admin` (overview), `/app/super-admin/organisations` (approval inbox), `/app/super-admin/platform-admins` (promote / demote), `/app/super-admin/password-resets` (admin-reset queue).
- Admin page: `/app/admin/password-resets` (employee-reset queue).
- `backend/create_super_admin.py` bootstrap CLI: idempotent on email or username; `--org-id` flag to attach to an existing real tenant (which is force-approved); defaults to auto-creating an "AHRIP Platform" org otherwise.

**Pending**
- Per-org drill-down stats on `/app/super-admin` (click a tenant → see its attempts, risk distribution, admins). The data is already on the existing admin endpoints but they're org-scoped; adding a `?organisation_id=` query param to the admin stats endpoint for super_admin callers would be the smallest diff.
- Out-of-band token delivery - the super_admin currently has to copy the token from the UI banner and send it via chat/phone; needs SMTP integration (already on the production-readiness backlog).
- Cross-tenant audit log (who approved which tenant, who promoted which super_admin). We record `approved_by` / `approved_at` on the rows but there's no unified audit view yet.

---

## A. Production Readiness (formerly "Phase 15") - ⬜ Deferred

These are blockers for any non-local deployment. None are on the current sprint per user direction.

- **Containerisation**: no `Dockerfile`, no `docker-compose.yml`, no `.github/` CI. Add `Dockerfile` for backend + frontend, GitHub Actions running `pytest`, `vitest`, `tsc --noEmit`, `npm audit`, image build.
- **Rate-limit / blocklist storage**: `RATE_LIMIT_STORAGE=memory://` is in-process. `Procfile` runs `gunicorn --workers 2`, so limits + JWT blocklist diverge per worker. Move to Redis before any prod deploy.
- **Secret hardening**: `ProductionConfig` should refuse start-up when `SECRET_KEY` / `JWT_SECRET_KEY` still match the dev defaults.
- **Email delivery**: no SMTP adapter. Required for password reset, invite delivery, profile-change-request status, account verification.
- **Password reset flow**: `change-password` exists but no `forgot-password → token → email → reset` loop.
- **MFA / 2FA**: no TOTP / WebAuthn. Considered enterprise-required for a security-awareness product.
- **GDPR**: `consent_timestamp` is recorded but no `/me/data-export` or `/me/delete-account`.
- **Observability**: only `logging.basicConfig`. No request IDs, no Sentry / OpenTelemetry, no `/metrics`, no structured JSON logs.
- **OpenAPI / Swagger**: no machine-readable spec.
- **Deployment runbooks**: no documented backup / restore plan; no migration playbook.

---

## B. Backend Functional Gaps

- 🟡 **Manager `assign-training` persistence** - endpoint emits a notification + returns 202, but no `training_assignments` table exists yet. Adaptive engine therefore ignores assignments. Spec: table (`user_id`, `categories JSON`, `note`, `assigned_by`, `assigned_at`, `consumed_at`) + a hook in `adaptive_engine.select_next_session` that prefers assigned categories for ~24-48 h.
- ⬜ **Risk-score history snapshots** - `RiskScore` rows are overwritten in place. `/manager/history` currently uses `proxy_risk = 100 − accuracy·100`. Either write a weekly `risk_score_snapshots` row per user, or add a `composite_history` JSON column.
- ⬜ **Heatmap N+1** - `RiskHeatmap` fan-outs `/team/<id>/profile` per row. Add `GET /manager/heatmap` returning `[{user_id, category_scores}]` in a single query for orgs > 30 users.
- ⬜ **Daily-challenge completions** - currently stashed as `_challenge_<date>` markers inside `UserGamification.badges_earned`. Replace with a `daily_challenge_completions` table once analytics needs accurate history.
- ⬜ **`api/users.py` self-service surface** - currently merged into `admin.py`. Split out only if a self-service users surface beyond `/auth/me` is needed.

---

## C. Frontend Functional Gaps

- ⬜ **Bundle code-splitting** - single 1.14 MB JS chunk. Use `React.lazy` on the manager + admin route trees and split Recharts / Framer Motion into vendor chunks via `manualChunks`.
- ⬜ **OpenAPI-driven types** - `types/api.ts` is hand-maintained; drifts can cause runtime mismatches (e.g. snake/camel field names).
- ⬜ **i18n** - strings are hard-coded English.

---

## D. Cleanup / Tech Debt

- 🟡 **`datetime.utcnow()` deprecation sweep** - still emits ~2,100 warnings per `pytest` run (Python 3.13). Migrate all call sites to `datetime.now(timezone.utc)`. Runs across `models/`, `utils/security.py`, `api/auth.py`, `services/scheduler.py`, `services/threat_ingestion.py`, `services/thompson_sampler.py`.
- ⬜ **One known-broken test**: `tests/test_auth.py::test_register_returns_201_with_job_role_and_industry` asserts `body["organisation"]["industry"] == "finance"` while the endpoint persists the raw value (`"Security"`). Either implement a job_role → industry mapping or update the test fixture. CI gate will be red until fixed.
- ⬜ **Scheduler hard-coded admin import** in `/admin/retrain-models`: imports `train_models` as a top-level module, depends on backend cwd.
- ⬜ **Tailwind v4 migration** - currently pinned to 3.4.x; tokens already CSS-variable-based so migration is mostly drop-in (`@import "tailwindcss"` + `@tailwindcss/postcss`).

---

## E. Bonus / Stretch

- ⬜ **Evaluation data collection scripts** - capture longitudinal cohort metrics for thesis evaluation.
- ⬜ **Calibrated RF probability** - replace banded-mapping `RfPredictionCard` with `predict_proba` once the RF model trains on real data.

---

## Recently Completed (already in source - no longer "remaining")

- ✅ Free-text question types + Ollama-graded answers (Phase 21).
- ✅ Event-driven notifications + `<NotificationBell>` + Toaster + `<EmptyState>` (Phase 22).
- ✅ Light-theme WCAG AA contrast pass + global focus ring + reduced-motion guard.
- ✅ Username login (alongside email).
- ✅ Admin coaching note + coaching hints (Thompson Sampler integration).
- ✅ Profile-change-request workflow - employee Profile page, admin inbox page, sidebar live count badge (Phase 23 Phase-2).
- ✅ Training session `localStorage` persistence (mid-session refresh resume).
- ✅ Silent JWT refresh interceptor.
- ✅ AI Generation page rebuild (Gemini + Ollama provider tiles, A/B/C/D distribution bar, `/admin/ollama/health` probe).
- ✅ Threat feed cleanup: PhishTank removed, Phishing.Database GitHub feed wired, OTX + URLScan free-tier resilience.
- ✅ Paid-LLM purge: Groq / NVIDIA / Kimi / Magpie / Supabase Storage all removed.
