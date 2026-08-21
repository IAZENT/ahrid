# AHRIP - Feature Inventory (updated 2026-05-10)

**Project:** Adaptive Human Risk Intelligence Platform (AHRIP)  
**Thesis title:** *An adaptive human-risk intelligence platform with live threat-feed integration and behavioural risk scoring for non-technical SME staff in Kathmandu Valley, fusing OSINT threat APIs with Random Forest and clustering on user telemetry, assessed on prediction accuracy, awareness uplift, and usability, bounded by surveillance limits and risk-score transparency.*  
**Stack:** Flask 3 / Python 3.13 / SQLite (dev) · React 18 + Vite + TypeScript + TailwindCSS v3 · scikit-learn · SHAP · imbalanced-learn (SMOTE) · APScheduler.

> This file is a **strict audit** of what is in the source tree right now. Last verified: backend `pytest` passing, frontend `tsc --noEmit` clean.

---

## 1. Architecture

- **Backend** (`backend/`): Flask 3 app factory at `app/__init__.py` wiring SQLAlchemy, Flask-Migrate (Alembic), JWT-Extended (with blocklist), Bcrypt, Flask-Limiter, Flask-CORS, Flask-Talisman (production only), APScheduler. WSGI entry: `wsgi.py`. Runs locally with `python wsgi.py` on port 5000.
- **Frontend** (`frontend/`): React 18 SPA via Vite 5, TypeScript, TailwindCSS v3.4, Recharts, Framer Motion, Lucide icons, React Router 6, Zustand (in-memory access token).
- **ML artefacts** (`backend/ml_models/`): Pickled Random Forest classifier (`risk_rf_model.pkl`) and a single joblib bundle (`StandardScaler` + `KMeans`). Feature JSON manifests: `rf_features.json`, `kmeans_features.json`.
- **No LLM integration** - thesis scope excludes generative AI. All scenarios are hand-written or OSINT-derived; no Gemini, Ollama, or OpenAI calls anywhere.
- **Threat intel sources:** Phishing.Database (GitHub feed), AlienVault OTX. PhishTank is dead and removed.
- **Environments:** `development` (SQLite at `backend/ahrip_dev.sqlite3` with `db.create_all()` on boot), `testing` (in-memory SQLite, `RATELIMIT_ENABLED=False`, `BCRYPT_LOG_ROUNDS=4`), `production` (Talisman + HSTS + CSP enabled).

---

## 2. Authentication, Identity & Access Control

### 2.1 Auth blueprint (`app/api/auth.py`, prefix `/api/v1/auth`)
- `POST /register` - employee self-registration with bleach-sanitised inputs, bcrypt hashing, JWT access + refresh issued.
- `POST /login` - accepts `identifier` (email **or** username), rate-limited 10 per 15 min, 5-attempt lockout (HTTP 423 with `locked_until`).
- `POST /refresh` - rotates access token from refresh token.
- `POST /logout` - revokes JWT JTI via `token_blocklist` table.
- `GET /me`, `PATCH /me` - current user profile + safe edits.
- `POST /change-password`.
- `POST /forgot-password` - initiates password-reset flow.
- `POST /reset-password` - completes password-reset flow.

### 2.2 JWT hardening
- Access token = 15 min; refresh token = 30 days; blocklist enabled for both kinds.
- `token_blocklist` table; `is_token_revoked` callback wired in `app/__init__.py`.
- Structured JSON loaders for revoked / expired / invalid / missing tokens.
- Frontend keeps **access token in memory only** (Zustand); refresh token + user shell handled via Zustand persistence on `localStorage`.

### 2.3 Roles & RBAC
- Roles: `admin`, `manager`, `employee`. Sub-roles via `User.job_role` ∈ {`receptionist`, `accountant`, `hr`, `it`, `finance`, `sales`, `management`}.
- Decorators: `require_role`, `admin_required`, `manager_required`, `active_user_required` in `app/utils/decorators.py`.
- Frontend `ProtectedRoute` enforces role gates per route.

---

## 3. Data Model (`backend/app/models/`)

~12 SQLAlchemy models, UUID PKs via `uuid_pk()`, `TimestampMixin` for timestamps:

| Model | File | Purpose |
|-------|------|---------|
| `User` | `user.py` | Email, username, bcrypt password, role, job_role, department, org_id, cluster_label, lockout fields. |
| `Organisation` | `organisation.py` | Tenant; single org seeded in dev. |
| `Scenario` | `scenario.py` | 8 categories × difficulty 1-3, question types `mcq` / `true_false` / `identify_threat`, options A-D, explanation, learning_tip, red_flags JSON, visual_html, source, active toggle, role-targeting. |
| `Attempt` | `attempt.py` | One row per answered question; user_id, scenario_id, session_id, given answer (letter), is_correct, response_time_ms. |
| `RiskScore` | `risk_score.py` | 8 per-category scores + composite + risk_level + RF prediction + confidence + **shap_summary** (JSON). |
| `ThreatFeedEntry` | `threat_feed.py` | Raw URL, source, severity, classification lure type, ingested_at, scenarios_created. |
| `UserCluster` | `cluster.py` | Most recent cluster assignment per user (single row). |
| `TokenBlocklist` | `token_blocklist.py` | JWT JTI revocation list. |
| `AuditLog` | `audit_log.py` | Append-only admin action log with actor, action, target, IP, UA, metadata. |
| `Notification` | `notification.py` | 2 types (`training_assigned`, `risk_escalation`) × 4 severities, read_at tracking. |
| `AwarenessAssessment` | `awareness_assessment.py` | HAIS-Q 7-item pre/post questionnaire responses + computed score. |
| `SUSResponse` | `sus_response.py` | System Usability Scale 10-item responses + computed SUS score. |

Schema migrated via Flask-Migrate; dev SQLite auto-creates new tables on boot via `db.create_all()`.

---

## 4. Scenario Engine

### 4.1 Catalogue & seeding (`backend/seed_scenarios.py`, `seed_users.py`, `seed_eval_data.py`)
- **450 hand-crafted scenarios** across 8 categories with length-balanced A/B/C/D options (max 12-char spread between longest and shortest option).
- 8 categories: `phishing_email` (76), `smishing` (59), `vishing` (54), `physical_security` (55), `password_hygiene` (53), `usb_baiting` (40), `social_engineering` (53), `data_handling` (60).
- 3 difficulties (156 beginner / 191 intermediate / 103 advanced) with deterministic correct-answer placement via content hash to prevent positional bias.
- Nepal-contextualized: eSewa, Ncell, Khalti, Pathao, Daraz, WorldLink, IRD, NRB.
- Role-targeted scenarios for: finance, hr, receptionist, it, sales, management, all.
- `red_flags` and `learning_tip` fields on every scenario.
- Seeds 1 organisation + 5 role-typed demo users (admin/manager/receptionist/accountant/hr) + 5 eval demo employees.
- `seed_eval_data.py` creates demo employees, attempts, pre/post awareness assessments, and SUS responses for evaluation testing.

### 4.2 OSINT threat ingestion (`app/services/threat_ingestion.py`)
- **7-stage pipeline**: fetch → validate(HEAD) → dedupe → classify → sanitise → generate → persist.
- Sources:
  - **Phishing.Database** GitHub feed (default).
  - **Phishing.Database** plain-text feed.
  - **AlienVault OTX** - `/pulses/subscribed` + `/pulses/activity` (deduped); broad keyword filter; accepts URL/DOMAIN/HOSTNAME indicators.
  - **Phishing.Database** - free-tier query chain; skips 401/403.
- Per-source try/except so one dead source never kills the run.
- 48-hour dedupe window (case + trailing-slash collapsed).
- Per-run cap: 20 generated scenarios.
- **scenario_classifier.py**: 6-lure typology (banking, e-commerce, document-share, account-suspension, package-delivery, generic).
- **Sanitiser**: raw URL/host **never** appears in scenario content / options / explanation / visual_html.
- **Typosquat detection**: explicit `KNOWN_TYPOSQUATS` list to avoid false positives on real brand spellings.
- **Round-robin interleaving** ensures fair scenario conversion from all OSINT sources.

### 4.3 Visual rendering & sandboxing
- `visual_html` stores rich phishing email / SMS templates.
- **sanitize_visual_html** (`app/utils/validators.py`) - bleach allowlist for tags and attrs + linkify callback that **drops `javascript:` / `data:` / `vbscript:` hrefs**.
- Frontend renders inside sandboxed `<iframe>` (no scripts) with "Simulated Attack" warning banner.

---

## 5. Adaptive Engine & Risk Scoring

### 5.1 Adaptive engine (`app/services/adaptive_engine.py`)
- **Mastery** - recency-weighted accuracy per category, λ = 0.85 decay.
- `get_user_profile` - per-category mastery, current difficulty, trend, role priorities.
- `select_next_session` - 3 weakest-cat / 1 other / 1 challenge; role-targeted; 24h-correct exclusion; prefer-unseen sort; max 5 per session.
- **Difficulty progression** - promote at 80 %, demote at 40 %, clamp 1-3.
- `process_attempt` - risk recalc + difficulty promotion/demotion + `risk_escalation` notification (when level crosses medium→high or high→critical).
- `get_session_summary` - accuracy, risk delta, improvement tips.
- No gamification hooks (XP, badges, streaks removed per thesis scope).
- No Thompson Sampler (replaced with simple weakest-category-first selection).

### 5.2 Risk scorer (`app/services/risk_scorer.py`)
- 8 per-category scores + composite (mean of seen categories) + risk_level: `unknown` / `low` (0-20) / `medium` (20-40) / `high` (40-60) / `critical` (60-100).
- After every recompute, computes and persists **SHAP explanation** into `RiskScore.shap_summary`.

### 5.3 Random Forest predictor (`app/services/random_forest_model.py`)
- Lazy-loads `risk_rf_model.pkl`; degrades to `predict() = None` when missing.
- **14-feature vector**: avg_response_time, 5 per-cat accuracies (phishing, smishing, social_engineering, password_hygiene, physical_security), overall_accuracy, fast_attempt_rate, overconfident_rate, session_consistency, job_role_encoded, total_sessions, days_since_last_session, attempts_count.
- `train_models.py` - `RandomForestClassifier(n_estimators=200, max_depth=None, min_samples_split=5, min_samples_leaf=2, class_weight='balanced', random_state=42)`, 80/20 stratified split; persists `risk_rf_model.pkl` + `rf_features.json` + `rf_label_encoder.pkl`; skips below `MIN_TRAINING_SAMPLES` (default 20).
- **Latest metrics**: Accuracy=91.4%, F1=0.8878, PR-AUC=0.9166, Cohen's Kappa=0.8751, Baseline F1=0.3653, Gap=+0.5224.

### 5.4 K-Means clustering (`app/services/kmeans_clustering.py`)
- **6-feature vector**: avg_response_time_ms, overall_accuracy, accuracy_variance, rushed_rate, total_sessions, streak_consistency.
- `train_kmeans` fits `StandardScaler` + `KMeans(n_clusters=5, random_state=42, n_init=10)` → single joblib bundle.
- **5 archetypes** (label / colour / icon / intervention): Overconfident Clicker, Cautious Learner, Inconsistent Performer, Resilient Defender, Disengaged Completer.
- `assign_user_to_cluster` updates `User.cluster_label`.
- Min users to train: `MIN_USERS_FOR_KMEANS` (default 3).

### 5.5 SMOTE integration (`backend/train_models.py`)
- `imblearn.over_sampling.SMOTE` applied to training data before RF fitting.
- Adaptive `k_neighbors = min(5, min(class_counts) - 1)` to handle small classes safely.
- Logs before/after class distribution into `rf_metrics.json` under `"smote": {...}` for methodology reporting.

### 5.6 SHAP explainability (`app/services/shap_explainer.py`)
- `TreeExplainer` on the trained RF model.
- 14 plain-language feature labels (e.g. "Phishing email detection accuracy", "Proportion of rushed answers").
- Returns `top_risk_factors` (3) and `top_protective_factors` (3) sorted by absolute SHAP value.
- Graceful degradation: if SHAP fails, stores `{"error": "SHAP unavailable"}` so the UI never crashes.

---

## 6. Notifications (`app/services/notifications.py` + `app/api/notifications.py`)

- **2 notification types** (thesis scope): `training_assigned`, `risk_escalation`.
- **4 severities**: `info` / `success` / `warning` / `critical`.
- **Defensive `emit()` helper** - coerces stringy UUIDs, rolls back on failure so primary user actions never break.
- **Typed helpers**: `emit_training_assigned`, `emit_risk_escalation`, `broadcast_to_org`.
- **Emission wiring**:
  - `adaptive_engine.process_attempt` - `risk_escalation` when risk level crosses threshold.
  - `manager.assign_training` - `training_assigned` to target employee (admin-only).
- **Frontend `<NotificationBell>`** - bell icon in TopBar, red unread-count badge, polling of `/unread-count`, dropdown with per-type Lucide icons + severity-tinted chip, optimistic mark-read / mark-all-read / dismiss.

---

## 7. REST API Surface (`/api/v1/*`)

Global JSON error handlers - every error path (`HTTPException` + raw `Exception`) returns `{error, message, status}` JSON, never HTML.

### 7.1 Auth (`/auth`)
`POST /register · POST /login · POST /refresh · POST /logout · GET /me · PATCH /me · POST /change-password · POST /forgot-password · POST /reset-password`

### 7.2 Training (`/training`, employee)
`GET /session/start · POST /session/<id>/answer · GET /session/<id>/summary · GET /session/<id>/detail · GET /history · GET /sessions · GET /categories`
- Rate limits: `session/start` 20/hr, `answer` 60/hr.
- `start` + active-question payloads **omit** `correct_answer` and `explanation`; `answer` reveals them post-submit.
- Session ownership enforced via `Attempt.user_id` check.

### 7.3 Scores (`/scores`)
`GET /me · GET /me/history · GET /me/cluster`
- `GET /me` now includes **`shap_explanation`** field when available.

### 7.4 Manager (`/manager`, manager + admin)
`GET /dashboard · GET /team · GET /team/<id>/profile · GET /history?weeks=N · GET /reports/summary` (CSV).
- Manager profile aggregates category_scores + profile and **omits raw attempts**.
- `/dashboard` includes `kpi_cards.trend_percent` (signed Δ vs prior week).
- `/history?weeks=8` returns weekly buckets `{avg_accuracy, proxy_risk = 100 − accuracy·100, attempts}`.
- **Team roster** filtered to `role == "employee"` and excludes the requesting user, preventing self-assigned notifications.

### 7.5 Admin (`/admin`, admin only)
- **Users**: `GET /users · PATCH /users/<id> · PATCH /users/<id>/toggle · PATCH /users/<id>/role`. Self-disable + self-demote blocked.
- **Scenarios**: `GET /scenarios · POST /scenarios · PATCH /scenarios/<id> · PATCH /scenarios/<id>/toggle`. Create runs `sanitize_visual_html` + bleach; rejects unknown category/difficulty/role; rate-limited 30/hr.
- **Threats**: `GET /threats · GET /threats/sources · POST /threats/run-ingestion · POST /trigger-feed-ingestion · GET /ingestion-status`.
- **System**: `GET /stats` (orgs, users, scenarios, 24h threats + attempts, RF/KMeans trained flags + last-trained timestamps, current bg-job state).
- **ML retrain**: `POST /retrain-models · GET /retrain-status` (RF + KMeans run independently).
- **Audit log**: `GET /audit-log`.
- **Evaluation** (new): `GET /eval/rf-metrics · GET /eval/awareness-uplift · GET /eval/sus-summary`.

### 7.6 Evaluation (`/eval`, new)
- `GET /eval/awareness/questions` - returns HAIS-Q 7-item questionnaire.
- `POST /eval/awareness` - submit pre/post assessment (employee).
- `GET /eval/awareness/me` - get own assessment status.
- `GET /eval/sus/questions` - returns SUS 10-item questionnaire.
- `POST /eval/sus` - submit SUS form (employee).
- `GET /eval/rf-metrics` - admin only; returns F1, Precision-Recall AUC, Cohen's Kappa vs rule-based baseline.
- `GET /eval/awareness-uplift` - admin only; returns mean delta, Cohen's d, p-value (paired t-test via scipy).
- `GET /eval/sus-summary` - admin only; returns mean SUS + grade distribution.
- `GET /eval/transparency-policy` - public, no auth; returns governance notice text from config.

### 7.7 Health (`/health`)
`GET /health` → `{status, db, rf_model_loaded, kmeans_loaded}`.

### 7.8 Notifications (`/notifications`)
`GET / · GET /unread-count · PATCH /<id>/read · POST /read-all · DELETE /<id>` - user-scoped, cross-user IDs return 404. Supports `?unread=1` filter + `?limit/offset` pagination (cap 100, default 30).

---

## 8. Background Jobs (`app/services/scheduler.py`, `background_jobs.py`)

APScheduler registers **2 jobs** (auto-start gated by `ENABLE_SCHEDULER` env flag):

| Job | Cadence |
|-----|---------|
| `threat_ingestion` | Every `THREAT_FEED_REFRESH_HOURS` (default 6 h) |
| `risk_recalc` | Every 1 h |

ML retrain (RF + KMeans) is **manual admin trigger only** via `POST /admin/retrain-models`.

In-process job registry (`background_jobs.py`) runs synchronously under `TESTING` / `RUN_JOBS_SYNC` for deterministic tests; timestamps use RFC 3339 UTC with explicit `Z` suffix so browser parses them correctly (fixes prior 345 min duration bug in UTC+05:45).

---

## 9. Frontend Application

### 9.1 Routes (`frontend/src/App.tsx`)
- **Public**: `/login`, `/register`.
- **Employee** (`/app/*`, protected): `dashboard`, `training`, `my-score`, `history`, `profile`, `settings`, `evaluation`, `transparency`.
- **Manager** (`/app/manager/*`, manager + admin): `dashboard`, `team`, `clusters`, `reports`.
- **Admin** (`/app/admin/*`, admin only): `admin` (panel), `users`, `scenarios`, `threats`, `password-resets`, `evaluation`.
- `RoleRedirect` sends each role to its appropriate landing page; fallback for unknown routes.
- `useSessionBootstrap` redeems refresh token on hard reload before rendering protected routes.

### 9.2 Design system
- CSS variable tokens in `frontend/src/index.css` (`--bg-*`, `--border-*`, `--text-*`, `--risk-*`, `--accent-*`).
- Light theme rebalanced to **WCAG 2.1 AA** body-text contrast (≥ 4.5 : 1).
- Mirrored in `tailwind.config.ts`. Tailwind pinned to `v3.4.x`.
- Global `:focus-visible` ring (2 px accent outline) and `prefers-reduced-motion: reduce` guard in `@layer base`.
- **UI primitives** (`components/ui/`): Button (5 variants × 3 sizes + loading), Card (Header/Title/Body/Footer), Input (leftIcon + error/hint), Badge (6 tones + dot), Dialog (Esc + backdrop + scroll-lock).
- **Shared**: `RiskBadge`, `AnimatedNumber`, `LoadingSpinner` / `Skeleton`, `ErrorBoundary`, `EmptyState`, `Toaster`.
- Lucide icons + Framer Motion throughout.

### 9.3 Employee Training UI
- Idle / Active / Complete 3-state flow; sandboxed visual iframe; immediate (<200 ms) answer feedback.
- Answer highlighting shows correct/incorrect states with colour-coded borders.
- Explicit **Start Training** button on Training page.

### 9.4 My Score, History, Profile
- **MyScorePage**: mastery `ProgressRing` + `RfPredictionCard` + cluster archetype card + Recharts `RadarChart` + 8-week `LineChart` + per-category horizontal risk bars + **SHAP explanation panel** (`ShapExplanationPanel` with top risk / protective factors and transparency disclaimer).
- **HistoryPage**: per-session attempts drilldown.
- **ProfilePage**: account details + password change.
- **SettingsPage**: notification / display preferences.
- **EvaluationPage**: 3-stage flow - HAIS-Q pre-assessment → post-assessment (after ≥3 sessions) → SUS questionnaire → confirmation screen with delta.
- **TransparencyPage**: fetches policy text from `GET /eval/transparency-policy`; monospace render of governance notice.

### 9.5 Manager Intelligence Dashboard
- 12-column grid: 4 KPIs → Heatmap (8) + AreaChart (4) → TopRiskTable / ClusterPie / CategoryBars → ThreatFeed (full width).
- Components: `KpiCard`, `RiskHeatmap`, `RiskTrendChart`, `TopRiskTable`, `ClusterView` (PieChart), `CategoryWeaknessChart`, `ThreatFeedBadge`.
- **TeamPage**: search + dept + risk + archetype + sort, URL-synced; row expansion loads `/team/<id>/profile`; CSV export. **Assign Training button visible to admin only**; managers see read-only roster.
- **ClustersPage**: 5 archetype cards.
- **ReportsPage**: CSV download.

### 9.6 Admin Panel
- **AdminDashboardPage**: 4 KPI tiles + 2 ML-model cards + 2 background-job tiles (4 s polling while running).
- **UsersPage**: search + role/status filters + inline role changer + Disable/Re-enable toggle.
- **ScenariosPage**: 4 filters + per-row Preview modal + active toggle + Create modal.
- **ThreatFeedPage**: 4 source cards + ingestion trigger + history table.
- **PasswordResetsPage**: admin-initiated password reset workflow.
- **EvaluationAdminPage**: 3 thesis cards - RF Metrics (F1 vs baseline), Awareness Uplift (Cohen's d + p-value), SUS Summary (mean + grade distribution bar chart).

### 9.7 State, hooks, API clients
- `frontend/src/api/`: `client.ts` (axios, 10 s timeout, 401 silent-refresh interceptor) + per-domain clients: `auth.ts`, `training.ts`, `scores.ts`, `manager.ts`, `admin.ts`, `evaluation.ts`, `notifications.ts`.
- `store/authStore.ts` - Zustand, access token in memory only.
- Hooks: `useSessionBootstrap`, `useTraining`, `useManagerData`, `useNotifications`.
- `lib/`: `categories.ts`, `archetypes.ts` (mirrors backend `CLUSTER_ARCHETYPES`).

---

## 10. Security Hardening

### 10.1 Backend
- **Flask-Talisman** wired but skipped in dev (gated on `not DEBUG and not TESTING`): CSP, `force_https=True`, HSTS 1 year + subdomains, `Referrer-Policy: strict-origin-when-cross-origin`, Permissions-Policy, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`.
- **CORS**: `supports_credentials=False`, explicit methods + allow_headers, origins from `ALLOWED_ORIGINS` env (no wildcards).
- **Input sanitisation**: bleach on registration + scenario create; `sanitize_visual_html` on `visual_html`.
- **Rate limiting** via Flask-Limiter: auth (5/hr register, 10/15 min login), admin create (30/hr), training (20/hr start, 60/hr answer). `RATELIMIT_ENABLED` flippable per env.
- **Password policy + lockout**: bcrypt (12 rounds, 4 in tests), 5-attempt lockout (423 + `locked_until`).
- **Audit log**: append-only, captures IP + UA, no update/delete API.

### 10.2 Frontend
- `vercel.json` ships 6 security headers ready for any future static-host deploy.
- Axios 10 s timeout + silent-refresh interceptor.
- Access token in React memory only.

---

## 11. Testing & Quality

### 11.1 Backend - pytest passing
- Test files spanning auth, threat pipeline, seed, adaptive engine, risk scorer, RF, KMeans, API smoke, security, admin + manager, notifications, threat ingestion, audit log, synthetic data handling.
- `tests/conftest.py` exposes `admin` / `manager` / `employee` fixtures + matching `*_headers` bearer helpers.

### 11.2 Frontend - Vitest passing
- `vitest@4` + `@testing-library/{react,jest-dom,user-event}` + `jsdom`.
- `src/test/setup.ts` polyfills `matchMedia` + `ResizeObserver` for Recharts.
- `tsc --noEmit` clean. `vite build` ok.

---

## 12. Configuration & Local Run

### 12.1 Env vars (`backend/.env.example`)
- **Flask**: `SECRET_KEY`, `JWT_SECRET_KEY`, `FLASK_ENV`, `LOG_LEVEL`, `APP_NAME`.
- **DB**: `DATABASE_URL` (defaults to local SQLite at `backend/ahrid_dev.sqlite3`).
- **CORS / rate**: `ALLOWED_ORIGINS`, `RATELIMIT_ENABLED`, `RATE_LIMIT_STORAGE`.
- **Threat intel**: `PHISHSTATS_FEED_URL`, `OPENPHISH_FEED_URL`, `ALIENVAULT_OTX_KEY`, `URLSCAN_API_KEY`, `THREAT_FEED_REFRESH_HOURS`.
- **ML**: `RF_MODEL_PATH`, `KMEANS_MODEL_PATH`, `MIN_TRAINING_SAMPLES` (20), `MIN_USERS_FOR_KMEANS` (3).
- **Scheduler**: `ENABLE_SCHEDULER`.
- **Transparency**: `TRANSPARENCY_POLICY` (config string for governance notice).

### 12.2 Local run
- **Backend**: `python wsgi.py` from `backend/` (port 5000).
- **Frontend**: `npm run dev` from `frontend/` (port 5173).
- `bootstrap.sh` handles venv, dependency install, migrations, seeding.

### 12.3 CLI / ops scripts (`backend/`)
- `seed_users.py` - idempotent user seeding (rebranded to `@ahrid.local`).
- `seed_scenarios.py` - 450 hand-crafted, length-balanced scenarios across 8 categories.
- `seed_eval_data.py` - demo employees + attempts + awareness + SUS for evaluation testing.
- `train_models.py` - RF + KMeans + SMOTE; `--rf-only` flag skips KMeans.
- `patch_db.py` - ad-hoc schema patch helper for dev sqlite.

---

## 13. Thesis Alignment & Acceptance

| Thesis element | System component | Evidence |
|---|---|---|
| RQ1 - Prediction accuracy | RF Metrics endpoint + admin panel | F1, PR-AUC, Cohen's Kappa vs rule-based baseline |
| RQ1 - Awareness uplift | HAIS-Q pre/post + Awareness Uplift endpoint | Cohen's d, p-value from paired t-test |
| RQ1 - Usability | SUS questionnaire + SUS Summary endpoint | Mean SUS score ≥ 68 target |
| RQ2 - Risk-score transparency | SHAP panel on My Score + Transparency Policy page | Plain-English feature explanations + governance notice |
| H1 - Prediction accuracy | RF vs baseline comparison | Admin Evaluation card |
| H2 - Surveillance limits | Aggregate-only manager view; employee sees own score only | Manager dashboard omits raw attempts; My Score is personal |

---

## 14. Cross-Cutting Characteristics

- **Single-tenancy**: one org seeded in dev; no multi-tenancy expansion.
- **Anonymisation**: leaderboards removed; manager view shows aggregates only.
- **Graceful degradation**: missing RF/KMeans artefacts → predictors return `None`; dead threat source → pipeline continues.
- **Deterministic testability**: `RUN_JOBS_SYNC` forces synchronous job execution under `TESTING`.
- **No SMTP dependency**: password resets and notifications are in-app only.
- **No paid LLMs**: thesis scope excludes generative AI entirely.
- **Accessibility**: `prefers-reduced-motion` honoured globally; keyboard-navigable Dialog; sandboxed iframes isolate simulated attacks; WCAG 2.1 AA contrast in light theme.
- **Observability**: global JSON error handler; health endpoint reports DB + ML model liveness; admin dashboard polls background-job status every 4 s.
