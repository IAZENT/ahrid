# AHRIP v2  Master Build Prompt Document
## Adaptive Human Risk Intelligence Dashboard
### Complete Sequential Prompts for Claude Opus 4.7  Production-Ready Build

---

> ## HOW THIS DOCUMENT WORKS
>
> Feed each `PROMPT BLOCK` to Claude Opus 4.7 one at a time in Claude Code or Claude.ai.
>
> **Rules Claude Opus 4.7 must follow for every prompt:**
> - Read the FULL prompt before writing a single line of code
> - Complete the VERIFICATION CHECKLIST at the end before saying "done"
> - If verification fails → fix it, do not move on
> - Use XML tags internally to structure thinking
> - Write production-quality code only  no placeholders, no "TODO", no mock data in logic
> - Every file gets its full content  never truncate
>
> **Prompt structure that works best with Claude Opus 4.7:**
> - Role → Task → Context → Constraints → Exact file paths → Verification gate
>
> **Stack:** Python 3.11 · Flask · PostgreSQL · Scikit-learn (Random Forest + KMeans)
> · React 18 + Vite + TypeScript · Tailwind CSS v4 · Recharts · Framer Motion
> · Supabase · Render · Vercel · PhishTank · Phishing.Database · AlienVault OTX · Phishing.Database

---

> ## UPGRADED PROJECT  WHAT CHANGED FROM v1
>
> The original AHRIP only did phishing training with a basic quiz.
> v2 is a full Human Risk Intelligence Dashboard with:
>
> 1. **Role-based scenarios**  a receptionist gets front-desk social engineering;
>    an accountant gets invoice fraud; a manager gets CEO impersonation
> 2. **Multi-threat coverage**  phishing, vishing, smishing, physical security,
>    password hygiene, USB baiting, social engineering, data handling
> 3. **Visual scenarios**  screenshot-style fake email renders, fake login page
>    images, fake invoice images  employees see what a real attack looks like
> 4. **Gamification**  XP points, level system, badges, daily streaks, weekly
>    challenges, department leaderboard, friendly competition
> 5. **Sentiment analysis**  detects if an employee is rushed, overconfident,
>    or anxious during a session and flags it in the risk model
> 6. **Random Forest ML**  trained on user telemetry (response time, accuracy,
>    category, role, streak, time of day) to predict future phishing susceptibility
> 7. **K-Means clustering**  groups users into behavioural archetypes
>    (Overconfident Clicker, Cautious Learner, Inconsistent Performer, etc.)
> 8. **OSINT threat APIs**  PhishTank + Phishing.Database + AlienVault OTX + Phishing.Database
>    feed real-world classified threats into scenario generation
> 9. **Professional dark UI**  looks like a real enterprise SaaS, not a student project

---

## PROGRESS TRACKER

```
[ ] PHASE 0   Scaffolding, Environment, Database Schema
[ ] PHASE 1   Authentication + Role System
[ ] PHASE 2   OSINT Threat Intelligence Pipeline
[ ] PHASE 3   Scenario Engine (Visual + Role-Based)
[ ] PHASE 4   Adaptive Engine + Sentiment Detection
[ ] PHASE 5   Random Forest Risk Model
[ ] PHASE 6   K-Means User Clustering
[ ] PHASE 7   Gamification Engine
[ ] PHASE 8   Core Backend API
[ ] PHASE 9   Design System + Component Library
[ ] PHASE 10  Employee Training Interface
[ ] PHASE 11  Manager Intelligence Dashboard
[ ] PHASE 12  Admin Panel
[ ] PHASE 13  Security Hardening
[ ] PHASE 14  Testing Suite
[ ] PHASE 15  Production Deployment
```

---
---

# PHASE 0  Scaffolding, Environment & Database Schema

## PROMPT 0.1  Project Scaffolding

```xml
<role>
You are a senior full-stack engineer setting up a production-grade monorepo.
You write clean, complete code with no placeholders.
</role>

<task>
Create the complete directory structure and all configuration files for AHRIP v2.
Every file must be created with its full content  never leave a file empty.
</task>

<project_name>ahrip-v2</project_name>

<directory_structure>
ahrip-v2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── organisation.py
│   │   │   ├── scenario.py
│   │   │   ├── attempt.py
│   │   │   ├── risk_score.py
│   │   │   ├── threat_feed.py
│   │   │   ├── gamification.py
│   │   │   └── cluster.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── training.py
│   │   │   ├── scores.py
│   │   │   ├── manager.py
│   │   │   ├── admin.py
│   │   │   ├── gamification.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── adaptive_engine.py
│   │   │   ├── risk_scorer.py
│   │   │   ├── threat_ingestion.py
│   │   │   ├── scenario_classifier.py
│   │   │   ├── scenario_generator.py
│   │   │   ├── sentiment_analyzer.py
│   │   │   ├── random_forest_model.py
│   │   │   ├── kmeans_clustering.py
│   │   │   ├── gamification_engine.py
│   │   │   └── scheduler.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       ├── decorators.py
│   │       ├── security.py
│   │       └── logger.py
│   ├── ml_models/           (trained .pkl files saved here  gitignored)
│   ├── migrations/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_adaptive_engine.py
│   │   ├── test_risk_scorer.py
│   │   ├── test_random_forest.py
│   │   ├── test_gamification.py
│   │   └── test_api.py
│   ├── seed.py
│   ├── train_models.py      (script to train RF + KMeans on seed data)
│   ├── .env.example
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── wsgi.py
│   └── Procfile
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── auth.ts
│   │   │   ├── training.ts
│   │   │   ├── scores.ts
│   │   │   ├── manager.ts
│   │   │   └── gamification.ts
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── layout/
│   │   │   │   ├── AppShell.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── TopBar.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── training/
│   │   │   │   ├── ScenarioCard.tsx
│   │   │   │   ├── VisualScenario.tsx
│   │   │   │   ├── AnswerOptions.tsx
│   │   │   │   ├── FeedbackPanel.tsx
│   │   │   │   ├── ProgressRing.tsx
│   │   │   │   ├── CategoryBadge.tsx
│   │   │   │   └── SessionTimer.tsx
│   │   │   ├── gamification/
│   │   │   │   ├── XPBar.tsx
│   │   │   │   ├── BadgeGrid.tsx
│   │   │   │   ├── Leaderboard.tsx
│   │   │   │   ├── StreakCounter.tsx
│   │   │   │   ├── LevelUpModal.tsx
│   │   │   │   └── DailyChallenge.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── RiskHeatmap.tsx
│   │   │   │   ├── RiskTrendChart.tsx
│   │   │   │   ├── ClusterView.tsx
│   │   │   │   ├── TopRiskTable.tsx
│   │   │   │   ├── CategoryRadar.tsx
│   │   │   │   ├── ThreatFeedBadge.tsx
│   │   │   │   └── PredictionCard.tsx
│   │   │   └── shared/
│   │   │       ├── RiskBadge.tsx
│   │   │       ├── LoadingSpinner.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       └── AnimatedNumber.tsx
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   └── RegisterPage.tsx
│   │   │   ├── employee/
│   │   │   │   ├── TrainingPage.tsx
│   │   │   │   ├── MyScorePage.tsx
│   │   │   │   ├── BadgesPage.tsx
│   │   │   │   └── LeaderboardPage.tsx
│   │   │   ├── manager/
│   │   │   │   ├── DashboardPage.tsx
│   │   │   │   ├── TeamPage.tsx
│   │   │   │   ├── ClustersPage.tsx
│   │   │   │   └── ReportsPage.tsx
│   │   │   └── admin/
│   │   │       ├── AdminDashboardPage.tsx
│   │   │       ├── UsersPage.tsx
│   │   │       ├── ScenariosPage.tsx
│   │   │       └── ThreatFeedPage.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useTraining.ts
│   │   │   ├── useRiskScore.ts
│   │   │   ├── useGamification.ts
│   │   │   └── useManagerData.ts
│   │   ├── store/
│   │   │   ├── authStore.ts
│   │   │   ├── trainingStore.ts
│   │   │   └── gamificationStore.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── lib/
│   │   │   ├── utils.ts
│   │   │   └── animations.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── public/
│   │   └── scenarios/       (visual scenario images stored here)
│   ├── .env.example
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
├── .gitignore
└── README.md
</directory_structure>

<backend_requirements_txt>
Flask==3.1.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-JWT-Extended==4.6.0
Flask-Bcrypt==1.0.1
Flask-Talisman==1.1.0
Flask-CORS==4.0.0
Flask-Limiter==3.8.0
marshmallow==3.21.2
psycopg2-binary==2.9.9
pandas==2.2.2
numpy==1.26.4
scikit-learn==1.4.2
joblib==1.4.2
requests==2.32.3
APScheduler==3.10.4
python-dotenv==1.0.1
gunicorn==22.0.0
bleach==6.1.0
textblob==0.18.0
vaderSentiment==3.3.2
SQLAlchemy==2.0.30
</backend_requirements_txt>

<frontend_package_json>
{
  "name": "ahrip-v2-frontend",
  "private": true,
  "version": "2.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "axios": "^1.7.2",
    "recharts": "^2.12.7",
    "zustand": "^4.5.4",
    "framer-motion": "^11.3.0",
    "lucide-react": "^0.395.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.3.0",
    "date-fns": "^3.6.0",
    "react-confetti": "^6.1.0",
    "canvas-confetti": "^1.9.3"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.39",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.4.5",
    "vite": "^5.3.1"
  }
}
</frontend_package_json>

<env_example>
# Flask
FLASK_ENV=development
SECRET_KEY=replace-with-64-char-minimum-random-string
JWT_SECRET_KEY=replace-with-different-64-char-random-string

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ahrip_dev

# Threat Intelligence APIs
PHISHTANK_API_KEY=register-free-at-phishtank.org
OPENPHISH_FEED_URL=https://openphish.com/feed.txt
ALIENVAULT_OTX_KEY=register-free-at-otx.alienvault.com
URLSCAN_API_KEY=register-free-at-urlscan.io
THREAT_FEED_REFRESH_HOURS=6

# Security
ALLOWED_ORIGINS=http://localhost:5173
RATE_LIMIT_STORAGE=memory://

# ML Models
RF_MODEL_PATH=ml_models/risk_rf_model.pkl
KMEANS_MODEL_PATH=ml_models/user_clusters.pkl
MIN_TRAINING_SAMPLES=50

# App
LOG_LEVEL=DEBUG
APP_NAME=AHRIP
</env_example>

After creating all files, run:
python -c "from app import create_app; app = create_app(); print('Scaffolding OK')"
npm install (in frontend/)

Both must succeed with zero errors.
```

### ✅ PHASE 0.1 VERIFICATION
```
[ ] All directories created as specified
[ ] requirements.txt has scikit-learn, textblob, vaderSentiment, joblib
[ ] package.json has framer-motion and react-confetti
[ ] .env.example has all keys including OTX and URLScan
[ ] .gitignore excludes ml_models/*.pkl and .env
[ ] wsgi.py created correctly
[ ] train_models.py created as empty stub with correct imports
```

---

## PROMPT 0.2  Full Database Schema

```xml
<role>
You are a database architect. Write production-quality SQLAlchemy models.
Every model is complete  no missing fields, no TODO comments.
</role>

<task>
Build ALL database models for AHRIP v2. Read every model specification below
carefully before writing any code.
</task>

<models>

MODEL 1: Organisation (backend/app/models/organisation.py)
Fields:
- id: UUID primary key
- name: String(200) not null
- domain: String(100) unique
- subscription_tier: String(20) default 'free'
- industry: String(80) nullable  ← NEW: used for role-based scenario matching
- is_active: Boolean default True
- max_users: Integer default 25
- created_at, updated_at timestamps
Methods:
- to_dict(): id, name, domain, industry, subscription_tier, user_count

MODEL 2: User (backend/app/models/user.py)
Fields:
- id: UUID primary key
- organisation_id: UUID FK not null
- email: String(254) unique not null
- password_hash: String(128) not null
- first_name: String(80)
- last_name: String(80)
- role: String(20) default 'employee'  [employee/manager/admin]
- job_role: String(80) nullable  ← NEW: receptionist/accountant/hr/it/finance/sales/management
- department: String(80) nullable
- is_active: Boolean default True
- is_verified: Boolean default False
- last_login: DateTime nullable
- failed_login_count: Integer default 0
- locked_until: DateTime nullable
- consent_given: Boolean default False
- consent_timestamp: DateTime nullable
- cluster_label: String(50) nullable  ← NEW: assigned by KMeans
- cluster_assigned_at: DateTime nullable
- created_at, updated_at
Methods:
- set_password(plain), check_password(plain), is_locked property
- to_dict(): NEVER include password_hash

MODEL 3: Scenario (backend/app/models/scenario.py)
CATEGORIES = [phishing_email, smishing, vishing, physical_security,
              password_hygiene, usb_baiting, social_engineering, data_handling]
DIFFICULTY = [1, 2, 3]
TARGET_ROLES = [all, receptionist, accountant, hr, it, finance, sales, management]

Fields:
- id: UUID primary key
- title: String(200) not null
- content: Text not null  (the text description shown to employee)
- visual_type: String(50) nullable  [email_screenshot/login_page/invoice/sms/none]
- visual_html: Text nullable  ← NEW: rendered HTML of fake email/login/invoice
- category: String(50) not null
- difficulty: Integer not null (1/2/3)
- target_roles: String(200) default 'all'  (comma-separated roles or 'all')
- correct_answer: String(1) not null (A/B/C/D)
- option_a, option_b, option_c, option_d: String(500) each
- explanation: Text not null
- red_flags: Text nullable  ← NEW: JSON list of specific red flags to spot
- learning_tip: String(500) nullable  ← NEW: one-line takeaway after answering
- source: String(50) default 'manual'
- threat_url: String(2000) nullable
- threat_brand: String(100) nullable
- is_active: Boolean default True
- times_served, times_correct: Integer default 0
- xp_reward: Integer default 10  ← NEW: XP earned for correct answer
- created_at, updated_at

MODEL 4: Attempt (backend/app/models/attempt.py)
Fields:
- id: UUID primary key
- user_id: UUID FK not null
- scenario_id: UUID FK not null
- answer_given: String(1) not null
- is_correct: Boolean not null
- response_time_ms: Integer nullable
- category, difficulty: denormalised for query speed
- session_id: UUID
- sentiment_label: String(20) nullable  ← NEW: rushed/overconfident/cautious/neutral
- sentiment_score: Float nullable  ← NEW: VADER compound score on interaction
- xp_earned: Integer default 0  ← NEW: XP awarded this attempt
- created_at  (immutable  no updated_at)

MODEL 5: RiskScore (backend/app/models/risk_score.py)
RISK_LEVELS = [critical, high, medium, low, unknown]

Fields:
- id: UUID primary key
- user_id: UUID FK unique (current score  one per user)
- composite_score: Float (0.0-100.0)
- phishing_email_score, smishing_score, vishing_score: Float each
- physical_security_score, password_hygiene_score: Float each
- usb_baiting_score, social_engineering_score, data_handling_score: Float each
- risk_level: String(20)
- rf_predicted_risk: Float nullable  ← NEW: Random Forest prediction
- rf_confidence: Float nullable  ← NEW: RF confidence score 0-1
- attempts_count: Integer
- score_version: Integer default 1
- calculated_at: DateTime
- created_at

MODEL 6: ThreatFeedEntry (backend/app/models/threat_feed.py)
Fields:
- id: UUID primary key
- source: String(50)  [phishtank/openphish/otx/urlscan]
- original_url: String(2000) not null
- target_brand: String(100) nullable
- category: String(50) nullable
- lure_type: String(100) nullable
- otx_pulse_name: String(200) nullable  ← NEW: AlienVault OTX pulse name
- urlscan_verdict: String(50) nullable  ← NEW: urlscan.io verdict
- was_converted: Boolean default False
- scenario_id: UUID FK nullable
- ingested_at: DateTime
- created_at

MODEL 7: UserGamification (backend/app/models/gamification.py)
Fields:
- id: UUID primary key
- user_id: UUID FK unique not null
- total_xp: Integer default 0
- current_level: Integer default 1
- current_streak: Integer default 0
- longest_streak: Integer default 0
- last_session_date: Date nullable
- badges_earned: Text default '[]'  (JSON array of badge IDs)
- weekly_xp: Integer default 0
- monthly_xp: Integer default 0
- rank_in_org: Integer nullable
- created_at, updated_at

XP_LEVEL_THRESHOLDS = {
  1: 0, 2: 100, 3: 250, 4: 500, 5: 900,
  6: 1400, 7: 2000, 8: 2750, 9: 3700, 10: 5000
}

MODEL 8: UserCluster (backend/app/models/cluster.py)
ARCHETYPES = {
  0: "Overconfident Clicker",      # fast, wrong, high risk
  1: "Cautious Learner",           # slow, mostly right, improving
  2: "Inconsistent Performer",     # high variance, category-specific gaps
  3: "Resilient Defender",         # fast AND right, low risk
  4: "Disengaged Completer"        # slow, random accuracy, low effort
}

Fields:
- id: UUID primary key
- user_id: UUID FK not null
- cluster_id: Integer not null (0-4)
- archetype_label: String(100) not null
- archetype_description: Text not null
- feature_vector: Text not null  (JSON of features used for clustering)
- clustered_at: DateTime
- created_at

</models>

After writing all models, run:
flask db init && flask db migrate -m "v2 schema" && flask db upgrade

Then verify:
python -c "
from app import create_app
from app.extensions import db
from app.models import *
app = create_app('testing')
with app.app_context():
    db.create_all()
    print('Tables:', list(db.engine.table_names()))
"

Must print all 8 table names. Zero errors.
```

### ✅ PHASE 0.2 VERIFICATION
```
[ ] All 8 models created with ALL specified fields
[ ] job_role field on User model (for role-based scenarios)
[ ] visual_html field on Scenario model
[ ] sentiment_label and sentiment_score on Attempt model
[ ] rf_predicted_risk and rf_confidence on RiskScore model
[ ] UserGamification model with XP_LEVEL_THRESHOLDS constant
[ ] UserCluster model with ARCHETYPES dict
[ ] flask db upgrade runs with zero errors
[ ] All 8 tables confirmed in output
[ ] password_hash NEVER appears in any to_dict() method
```

---
---

# PHASE 1  Authentication + Role System

## PROMPT 1.1  Flask Auth + JWT

```xml
<role>Senior security engineer. Production-quality auth only.</role>

<task>
Build the complete authentication system for AHRIP v2.
All security requirements below are MANDATORY, not optional.
</task>

<endpoints>
POST /api/v1/auth/register
  Rate limit: 5/hour per IP
  Body: {email, password, first_name, last_name, organisation_name,
         industry, job_role}
  Validation (marshmallow schema):
    email: valid format, max 254 chars, lowercase strip
    password: min 12 chars, requires uppercase + lowercase + digit + special char
    job_role: must be one of [receptionist/accountant/hr/it/finance/sales/management/other]
    industry: string max 80 chars
  Logic:
    1. Check email uniqueness → 409 if exists
    2. Create Organisation with industry
    3. Create User with role='admin', job_role from body
    4. Hash password with bcrypt (rounds=12)
    5. Set consent_given=True, consent_timestamp=utcnow()
    6. Create UserGamification record (total_xp=0, level=1)
    7. Return 201 {user: to_dict(), message: "Registration successful"}

POST /api/v1/auth/login
  Rate limit: 10/15min per IP (sliding window)
  Body: {email, password}
  Logic:
    1. Find user (case-insensitive email)
    2. Not found → 401 "Invalid credentials" (never say "user not found")
    3. is_active=False → 403
    4. is_locked → 423 {error: "Account locked", locked_until: timestamp}
    5. Wrong password → increment failed_login_count
       If count >= 5: lock for 15min, reset count
       → 401 "Invalid credentials"
    6. Correct → reset failed_login_count=0, locked_until=None
    7. Update last_login, increment login_count
    8. Create JWT with claims: {sub: user_id, role, org_id, job_role}
       access_token: 15 min expiry
       refresh_token: 30 day expiry
    9. Return 200 {access_token, refresh_token, user: to_dict()}

POST /api/v1/auth/refresh → new access_token only
POST /api/v1/auth/logout → blacklist both tokens (jwt_blocklist table)
GET  /api/v1/auth/me → current user + gamification data + cluster label

FILE: backend/app/utils/decorators.py
- require_role(*roles): checks JWT role claim, 403 if not permitted
- active_user_required: checks user.is_active in DB
- job_role_context: attaches user.job_role to Flask g for scenario filtering

FILE: backend/app/utils/validators.py
- RegistrationSchema with job_role validation
- LoginSchema
- sanitize_string(): bleach.clean(value, tags=[], strip=True)
</endpoints>

Test after building:
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"TestPass123!",
       "first_name":"Raj","last_name":"Sharma",
       "organisation_name":"Test SME","industry":"finance",
       "job_role":"accountant"}'
→ Must return 201 with user data and job_role field

curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"TestPass123!"}'
→ Must return 200 with access_token, refresh_token, and user including job_role
```

### ✅ PHASE 1 VERIFICATION
```
[ ] Register returns 201 with job_role and industry in response
[ ] Login returns 200 with tokens containing job_role in JWT claims
[ ] Wrong password → 401 (not 404, not 400)
[ ] After 5 wrong attempts → account locks for 15 min → 423
[ ] Token contains role AND job_role claims
[ ] /me returns user + gamification record (xp, level, streak, badges)
[ ] Rate limits fire correctly (test: 11 rapid requests → 429)
[ ] Password hash never in API response
[ ] bleach sanitization applied to all string inputs
```

---
---

# PHASE 2  OSINT Threat Intelligence Pipeline

## PROMPT 2.1  Multi-Source Threat Ingestion

```xml
<role>
Security engineer building a production threat intelligence pipeline.
Write robust, defensive code that handles all error conditions gracefully.
</role>

<task>
Build the complete OSINT threat intelligence pipeline using FOUR sources.
This pipeline converts real-world threat intelligence into training scenarios.
Every stage is specified precisely below  implement all of them.
</task>

<file>backend/app/services/threat_ingestion.py</file>

<pipeline_stages>

STAGE 1  FETCH from four sources:

Source A: PhishTank
  URL: https://data.phishtank.com/data/online-valid.csv
  User-Agent: phishtank/{PHISHTANK_API_KEY}
  Timeout: 30s
  Parse with pandas, filter: verified='yes' AND online='yes'
  Extract: url, target (brand), submission_time

Source B: Phishing.Database
  URL: https://openphish.com/feed.txt
  Timeout: 20s
  Parse: one URL per line
  No brand data available (null brand)

Source C: AlienVault OTX
  Endpoint: https://otx.alienvault.com/api/v1/pulses/subscribed
  Header: X-OTX-API-KEY: {ALIENVAULT_OTX_KEY}
  Extract from each pulse:
    - indicators where type='URL'
    - pulse_name as context
    - tags for classification
  Timeout: 30s

Source D: Phishing.Database
  Endpoint: https://urlscan.io/api/v1/search/?q=page.domain:phishing&size=100
  Header: API-Key: {URLSCAN_API_KEY}
  Extract: page.url, page.domain, verdicts.overall.malicious=true only
  Timeout: 30s

STAGE 2  VALIDATE (critical  solves dead URL problem)
  For each URL from all sources:
  - HEAD request with 5s timeout
  - If response is 4xx/5xx or ConnectionError → mark as dead, discard
  - If SSL error → mark as dead, discard
  - Expected discard rate: 40-60%  this is normal, log it
  - Only keep URLs where HEAD returns 2xx or 3xx

STAGE 3  DEDUPLICATE
  - Normalise URLs: lowercase, strip trailing slash, decode %XX
  - Check against threat_feed_entries WHERE ingested_at > NOW() - 48h
  - Also deduplicate within current batch
  - Only keep URLs not seen in last 48 hours

STAGE 4  CLASSIFY
  LURE_TYPE_PATTERNS = {
    'credential_harvest': ['login', 'signin', 'account', 'verify', 'password',
                           'secure', 'update', 'confirm', 'validate'],
    'invoice_fraud': ['invoice', 'payment', 'billing', 'receipt', 'transaction',
                      'order', 'po', 'purchase-order'],
    'delivery_notification': ['delivery', 'parcel', 'shipment', 'dhl', 'fedex',
                               'ups', 'usps', 'track', 'package'],
    'it_support': ['microsoft', 'google', 'apple', 'support', 'help',
                   'alert', 'warning', 'security', 'teams'],
    'ceo_impersonation': ['ceo', 'director', 'urgent', 'wire', 'transfer',
                          'confidential', 'board'],
    'prize_scam': ['winner', 'congratulation', 'prize', 'award', 'selected',
                   'reward', 'claim'],
  }

  BRAND_TO_CATEGORY = {
    'paypal': 'credential_harvest', 'microsoft': 'credential_harvest',
    'google': 'credential_harvest', 'apple': 'credential_harvest',
    'amazon': 'credential_harvest', 'netflix': 'credential_harvest',
    'dhl': 'delivery_notification', 'fedex': 'delivery_notification',
    'bank': 'credential_harvest', 'invoice': 'invoice_fraud',
  }

  classify_url(url, brand, pulse_name) → {lure_type, category, difficulty}

  DIFFICULTY HEURISTICS:
    1 (obvious): domain typosquat (paypa1.com), HTTP not HTTPS,
                 free hosting (.tk/.ml/.ga/.cf/blogspot/weebly/000webhost)
    2 (subtle):  lookalike domain (paypal-secure.com), valid TLD wrong brand
    3 (advanced): subdomain attack (paypal.attacker.com), Unicode homograph,
                  legitimate cloud (Azure/AWS S3/Firebase/Netlify),
                  compromised legitimate domain

STAGE 5  SANITISE (CRITICAL SAFETY REQUIREMENT)
  The raw malicious URL MUST NEVER appear in any employee-facing content.
  
  sanitise_url(url) → {
    'redacted_display': '[REDACTED-DOMAIN]',
    'domain_pattern': extract_pattern(url),  # e.g., "typosquat of paypal.com"
    'tld': extract_tld(url),
    'uses_https': url.startswith('https'),
    'subdomain_depth': count_subdomains(url),
    'lure_indicators': list_suspicious_indicators(url)
  }

STAGE 6  GENERATE SCENARIO
  generate_scenario_from_entry(feed_entry, sanitised_info) → Scenario

  Template system per lure_type and difficulty:
  Each template must produce:
    - content: realistic narrative WITHOUT the actual URL
    - visual_html: rendered fake email/SMS/login page HTML
      (NO REAL URLs in visual_html  use [REDACTED] or example.com placeholders)
    - 4 answer options where option C is always correct and others are plausible traps
    - explanation: detailed educational explanation
    - red_flags: JSON list of specific things to spot
    - learning_tip: one-line takeaway
    - target_roles: matched from lure_type
      (invoice_fraud → accountant,finance; ceo_impersonation → management,finance;
       delivery_notification → all; credential_harvest → all)
    - xp_reward: difficulty-based (1→10xp, 2→15xp, 3→25xp)

  MAX 20 new scenarios per ingestion run  prevent pool flooding

STAGE 7  SAVE & REPORT
  Bulk insert new ThreatFeedEntry records
  Create Scenario records for converted entries
  Return stats: {
    fetched: int, validated: int, deduplicated: int,
    classified: int, scenarios_created: int,
    dead_urls_discarded: int, sources: {phishtank: int, openphish: int,
    otx: int, urlscan: int}
  }
  Log at INFO level with full stats

</pipeline_stages>

<scheduler_file>backend/app/services/scheduler.py</scheduler_file>

Build APScheduler with:
  - Threat feed ingestion: every 6 hours
  - Risk score recalculation: every 1 hour
  - RF model retrain: every 7 days (only if >= MIN_TRAINING_SAMPLES new attempts)
  - KMeans reclustering: every 7 days (alongside RF retrain)
  - Weekly XP reset: every Monday 00:00 UTC

Test manually:
python -c "
from app import create_app
from app.services.threat_ingestion import ThreatIngestionService
app = create_app()
with app.app_context():
    s = ThreatIngestionService()
    r = s.run_ingestion()
    print(r)
"
→ Must return dict with all stat keys and zero Python errors
```

### ✅ PHASE 2 VERIFICATION
```
[ ] All four sources implemented (PhishTank, OTX)
[ ] Stage 2 validation discards dead URLs (HEAD request logic present)
[ ] Stage 5 sanitisation: raw URL NEVER appears in visual_html or content
[ ] All 6 lure types in LURE_TYPE_PATTERNS
[ ] Difficulty 1/2/3 heuristics implemented
[ ] visual_html generated per scenario (even if simple HTML template)
[ ] target_roles assigned per lure_type
[ ] xp_reward set correctly by difficulty
[ ] Max 20 scenarios per run enforced
[ ] Return stats dict has all required keys
[ ] Scheduler initialises without error in create_app()
[ ] Manual test runs without Python exceptions
```

---
---

# PHASE 3  Scenario Engine (Role-Based + Visual)

## PROMPT 3.1  Seed Scenarios (Role-Based + Visual)

```xml
<role>
Cybersecurity educator creating realistic, role-specific training scenarios.
Write professional, believable scenarios that feel like real workplace situations.
</role>

<task>
Create the seed.py script with:
1. One test organisation (Himalayan Finance Ltd, industry: finance)
2. Five users across different job roles
3. 48 hand-crafted scenarios covering all 8 categories × 3 difficulties
   with role-specific targeting and visual HTML where applicable

The scenarios must be realistic, not generic.
Role-specific means: a receptionist gets a front-desk visitor scenario,
an accountant gets an invoice fraud scenario, HR gets a fake job offer scenario.
</task>

<users>
admin@himalayan.test    / AdminPass123!    / role=admin     / job_role=management
manager@himalayan.test  / ManagerPass123!  / role=manager   / job_role=management
reception@himalayan.test/ RecepPass123!    / role=employee  / job_role=receptionist
accounts@himalayan.test / AccPass123!      / role=employee  / job_role=accountant
hr@himalayan.test       / HRPass123!       / role=employee  / job_role=hr
</users>

<scenario_requirements>
Write 6 scenarios per category (8 categories × 6 = 48 total).
For each category, write 2 at difficulty 1, 2 at difficulty 2, 2 at difficulty 3.

CATEGORY 1: phishing_email
  Include scenarios targeting: receptionist (fake vendor email),
  accountant (fake bank notification), hr (fake LinkedIn message)
  
  EXAMPLE DIFFICULTY 1 SCENARIO (write similar quality for all):
  title: "Urgent PayPal Account Suspension"
  content: "You receive this email at work:
    From: security@paypa1-support.com
    Subject: URGENT: Your PayPal account suspended
    
    Dear Valued Customer,
    Your PayPal account has been suspended due to unusual activity.
    Click below within 24 hours to restore access or your account will be closed.
    [Restore My Account]"
  
  visual_html: Full HTML rendering of a fake PayPal suspension email
    - Use PayPal color scheme (#003087 blue)
    - Include PayPal logo placeholder (text-based, no external images)
    - Show the spoofed From address clearly
    - Button that says "Restore My Account" (href="#" - not a real link)
    - Must look convincingly like a real PayPal email
    - NEVER use the actual malicious URL from the threat feed
    - This HTML is shown to employees to train visual recognition
  
  correct_answer: C
  option_a: "Click the link immediately to avoid losing access"
  option_b: "Forward to a colleague to check if it looks real"
  option_c: "Report it as phishing  the sender domain 'paypa1-support.com'
             uses '1' instead of 'l' (typosquat attack)"
  option_d: "Reply asking the sender to confirm their identity"
  explanation: "This is a classic typosquat phishing attack. The sender
    domain 'paypa1-support.com' replaces the letter 'l' with number '1'.
    Always check sender domains character by character. PayPal never sends
    account suspension notices from third-party domains. The urgency tactic
    ('24 hours') is designed to bypass your rational thinking."
  red_flags: '["Sender domain uses number 1 instead of letter l",
               "Urgency pressure: 24-hour deadline",
               "Requests clicking a link for account action",
               "Generic greeting: Dear Valued Customer"]'
  learning_tip: "Always check the sender domain, not just the display name."
  target_roles: "all"
  xp_reward: 10

CATEGORY 2: smishing  (SMS phishing  mobile)
  target_roles: all
  visual_html: Rendered SMS message bubble UI (dark phone mockup style)

CATEGORY 3: vishing  (voice phishing  phone calls)
  visual_html: null (voice-based, describe the phone scenario in text)
  target_roles: receptionist,hr,management

CATEGORY 4: physical_security  (tailgating, shoulder surfing, piggybacking)
  target_roles: receptionist,all
  visual_html: simple floor-plan diagram or description image

CATEGORY 5: password_hygiene
  target_roles: all
  Include scenarios about: reusing passwords, weak passwords,
  writing passwords on sticky notes, sharing credentials

CATEGORY 6: usb_baiting  (malicious USB drops)
  target_roles: all
  content: finding USB drives in car parks, breakrooms, marked "Salary 2025"

CATEGORY 7: social_engineering  (pretexting, impersonation in person or email)
  target_roles: hr,management,receptionist,accountant
  Scenarios: fake IT support calling, fake vendor visiting, fake auditor

CATEGORY 8: data_handling  (mishandling sensitive data, sharing inappropriately)
  target_roles: all
  Scenarios: sending wrong attachment, CCing wrong person, storing on personal device

Write ALL 48 scenarios at the quality level of the example above.
Every scenario must have:
- Realistic, specific content (not generic "you receive a suspicious email")
- visual_html where specified (full HTML, not empty)
- red_flags as JSON array with 3-5 specific items
- learning_tip: one memorable sentence
- Plausible wrong answers (not obviously stupid options)
</scenario_requirements>

After running seed.py, verify:
python seed.py
→ Must print "Created 48 scenarios across 8 categories"
→ Visual HTML scenarios must have non-empty visual_html field
→ Run: SELECT category, COUNT(*) FROM scenarios GROUP BY category;
   Must show 6 per category
```

### ✅ PHASE 3 VERIFICATION
```
[ ] 48 scenarios created (6 per category × 8 categories)
[ ] visual_html present for phishing_email, smishing categories
[ ] red_flags is valid JSON array on all scenarios
[ ] target_roles set correctly (not all scenarios target 'all')
[ ] xp_reward matches difficulty (10/15/25)
[ ] learning_tip present on all scenarios
[ ] No scenario uses a real malicious URL in content or visual_html
[ ] Accountant-specific scenarios exist (invoice fraud at difficulty 2+)
[ ] Receptionist-specific scenarios exist (visitor/tailgating)
[ ] HR-specific scenarios exist (fake job offer, social engineering)
```

---
---

# PHASE 4  Adaptive Engine + Sentiment Analyzer

## PROMPT 4.1  Adaptive Engine (Formal Algorithm)

```xml
<role>Learning science engineer implementing Cognitive Load Theory in code.</role>

<task>
Build the complete adaptive engine and sentiment analyzer.
Every constant, threshold, and algorithm must match the specifications exactly.
</task>

<file>backend/app/services/adaptive_engine.py</file>

<constants>
PROMOTION_THRESHOLD = 0.80   # Mastery must exceed this to promote
DEMOTION_THRESHOLD = 0.40    # Mastery must fall below this to demote
MIN_ATTEMPTS_FOR_DECISION = 5
RECENCY_WINDOW = 10          # Last N attempts for mastery calculation
DECAY_FACTOR = 0.85          # λ  Ebbinghaus forgetting curve
MAX_DIFFICULTY = 3
MIN_DIFFICULTY = 1
SESSION_SIZE = 5             # Scenarios per session

SCENARIO_SELECTION_RATIO = {
  'weakest_category': 0.60,   # 60% from weakest category
  'other_categories': 0.30,   # 30% distributed across others
  'challenge': 0.10           # 10% one level above current difficulty
}

ROLE_CATEGORY_PRIORITY = {
  'receptionist': ['phishing_email', 'physical_security', 'social_engineering'],
  'accountant': ['phishing_email', 'smishing', 'data_handling'],
  'hr': ['social_engineering', 'phishing_email', 'data_handling'],
  'it': ['phishing_email', 'usb_baiting', 'password_hygiene'],
  'finance': ['phishing_email', 'social_engineering', 'data_handling'],
  'sales': ['phishing_email', 'smishing', 'social_engineering'],
  'management': ['vishing', 'social_engineering', 'phishing_email'],
  'other': ['phishing_email', 'password_hygiene', 'social_engineering'],
}
</constants>

<algorithms>

def calculate_mastery(attempts: list[Attempt]) -> float:
  """
  Recency-weighted accuracy using exponential decay.
  Most recent attempt = weight 1.0
  Attempt N steps ago = weight DECAY_FACTOR^N
  
  mastery = Σ(result_i × λ^i) / Σ(λ^i)
  where i=0 is most recent, result_i ∈ {0, 1}
  Returns float in [0.0, 1.0]
  """

def get_user_profile(user_id: UUID) -> dict:
  """
  For each of 8 categories:
    - Get last RECENCY_WINDOW attempts
    - Calculate mastery score
    - Determine current_difficulty:
        If < MIN_ATTEMPTS_FOR_DECISION: difficulty = 1 (cold start)
        If mastery >= PROMOTION_THRESHOLD: min(current+1, MAX_DIFFICULTY)
        If mastery <= DEMOTION_THRESHOLD: max(current-1, MIN_DIFFICULTY)
        Else: maintain current
    - trend: 'improving'|'declining'|'stable'|'insufficient_data'
  
  Also factor in job_role:
    - Bump priority for categories matching ROLE_CATEGORY_PRIORITY[job_role]
    - These categories get served more frequently even if not weakest
  
  Return: {
    user_id, job_role,
    categories: {cat_name: {mastery, difficulty, total_attempts, trend}},
    overall_mastery: float,
    weakest_category: str,
    role_priority_categories: list[str],
    strongest_category: str,
  }
  """

def select_next_session(user_id: UUID, job_role: str) -> list[Scenario]:
  """
  Select 5 scenarios for the next session.
  
  Priority order for scenario selection:
  1. Scenarios user has never seen (always prefer new over repeated)
  2. Scenarios not seen in last 7 days
  3. Scenarios answered correctly in last 24h are EXCLUDED
  
  Distribution (SESSION_SIZE = 5):
  - 3 scenarios from weakest_category at user's current difficulty for that category
    (or role_priority_categories if weakest is already low risk)
  - 1 scenario from any other category at respective difficulty
  - 1 challenge scenario at difficulty + 1 (capped at 3)
  
  Filter by target_roles:
    Include scenarios where target_roles == 'all'
    OR target_roles contains user's job_role
  
  Shuffle before returning.
  Return list of Scenario objects.
  """

def process_attempt(user_id, scenario_id, answer, response_time_ms, 
                    session_id, sentiment_data=None) -> dict:
  """
  1. Validate inputs
  2. Determine is_correct
  3. Calculate XP: if correct → scenario.xp_reward, else → 0
     Streak bonus: if streak >= 3 → xp × 1.5; if streak >= 7 → xp × 2.0
  4. Create Attempt record (include sentiment_label, sentiment_score, xp_earned)
  5. Update scenario.times_served, times_correct
  6. Update UserGamification: add XP, check level up, update streak
  7. Check for badge awards (call gamification_engine)
  8. Trigger async risk score recalculation
  9. Return: {
     is_correct, correct_answer, explanation, red_flags, learning_tip,
     xp_earned, streak_bonus: bool, new_level: int|None,
     badges_earned: list[str], mastery_update: dict
  }
  """

def get_session_summary(user_id, session_id) -> dict:
  """
  Return: {
    session_id, total_questions, correct, accuracy, duration_seconds,
    xp_this_session, streak_after, categories_covered,
    strongest_category_this_session, weakest_category_this_session,
    score_change: float (negative = improved),
    improvement_tips: list[str] (based on what went wrong),
  }
  """

</algorithms>

<file>backend/app/services/sentiment_analyzer.py</file>

<sentiment_algorithm>
Use VADER SentimentIntensityAnalyzer for response time pattern analysis.

SENTIMENT LABELS based on user interaction patterns:
  'rushed':        response_time_ms < 2000 AND is_correct = False
                   (answering too fast without thinking)
  'overconfident': response_time_ms < 3000 AND difficulty >= 2 AND is_correct = False
                   (fast but wrong on harder questions)
  'cautious':      response_time_ms > 12000 AND is_correct = True
                   (taking time, getting it right)
  'anxious':       response_time_ms > 20000  (very slow, possibly panicking)
  'neutral':       everything else

For the session as a whole, calculate dominant sentiment label.
The sentiment label goes into Attempt.sentiment_label.

Also calculate VADER score on the scenario content itself
(compound score of the scenario text  measures emotional intensity of threat scenario)
Store in attempt.sentiment_score.

Aggregate per user over time: if user is consistently 'rushed' or 'overconfident' →
flag this in their risk profile as a behavioral pattern.

def analyze_interaction(response_time_ms, is_correct, difficulty, scenario_content) -> dict:
  return {
    'sentiment_label': str,  # rushed/overconfident/cautious/anxious/neutral
    'sentiment_score': float,  # VADER compound on scenario content
    'behavioral_flag': str|None  # 'speed_over_accuracy' / 'analysis_paralysis' / None
  }
</sentiment_algorithm>

Write unit tests in backend/tests/test_adaptive_engine.py:
1. test_mastery_decay_weights: recent attempts weighted more than old
2. test_promotion_at_80_percent: 4 correct in 5 → promote
3. test_demotion_at_40_percent: 2 correct in 5 → demote
4. test_no_promotion_above_3: difficulty stays at 3
5. test_no_demotion_below_1: difficulty stays at 1
6. test_role_priority_affects_selection: receptionist gets physical_security
7. test_24h_exclusion: recently correct scenarios excluded
8. test_session_returns_5_scenarios: exactly 5 returned
9. test_sentiment_rushed_detected: <2000ms wrong → rushed
10. test_sentiment_cautious_detected: >12000ms correct → cautious

Run: python -m pytest tests/test_adaptive_engine.py -v
All 10 must pass.
```

### ✅ PHASE 4 VERIFICATION
```
[ ] calculate_mastery() uses DECAY_FACTOR = 0.85 correctly
[ ] Promotion at >= 80%, demotion at < 40%, min 5 attempts
[ ] Difficulty clamped 1-3
[ ] ROLE_CATEGORY_PRIORITY dict used in selection
[ ] target_roles filtering: only serve scenarios matching user's job_role
[ ] XP calculated correctly with streak bonuses (1.5x at 3, 2.0x at 7)
[ ] UserGamification updated on each attempt
[ ] Sentiment: rushed/overconfident/cautious/anxious/neutral all implemented
[ ] VADER sentiment score calculated on scenario content
[ ] All 10 unit tests pass
```

---
---

# PHASE 5  Random Forest Risk Model

## PROMPT 5.1  ML Risk Prediction

```xml
<role>
Machine learning engineer building a production Random Forest classifier
for predicting employee phishing susceptibility.
</role>

<task>
Build the Random Forest model for risk prediction.
The model uses user telemetry to predict future risk levels.
Include the training script and the inference service.
</task>

<file>backend/app/services/random_forest_model.py</file>

<feature_engineering>
FEATURES used to train and predict (14 features total):

Behavioral features (from Attempt history):
1. avg_response_time_ms: mean response time across all attempts
2. phishing_accuracy: accuracy specifically in phishing_email category
3. smishing_accuracy: accuracy in smishing category
4. social_engineering_accuracy: accuracy in social_engineering
5. password_hygiene_accuracy: accuracy in password_hygiene
6. physical_security_accuracy: accuracy in physical_security
7. overall_accuracy: accuracy across all categories
8. rushed_attempt_rate: proportion of attempts labeled 'rushed'
9. overconfident_rate: proportion labeled 'overconfident'
10. streak_consistency: (longest_streak / total_sessions)  habit formation

User profile features:
11. job_role_encoded: integer encoding of job_role
    (receptionist=0, accountant=1, hr=2, it=3, finance=4, sales=5, management=6, other=7)
12. total_sessions: total number of training sessions completed
13. days_since_last_session: recency of engagement
14. weekly_xp: engagement indicator (higher XP = more engaged)

TARGET: risk_level_encoded
  critical=3, high=2, medium=1, low=0
  (derived from current decay-weighted composite score)
</feature_engineering>

<training_script>
FILE: backend/train_models.py

def prepare_training_data(db_session) -> tuple[np.ndarray, np.ndarray]:
  """
  Query all users with >= 10 attempts.
  For each user, calculate all 14 features.
  Target: their current risk_level_encoded.
  Return X (features), y (labels).
  """

def train_random_forest(X, y) -> RandomForestClassifier:
  """
  from sklearn.ensemble import RandomForestClassifier
  from sklearn.model_selection import train_test_split
  from sklearn.preprocessing import StandardScaler
  
  Split: 80% train, 20% test (stratified by risk level)
  
  Model params:
    n_estimators=100
    max_depth=8
    min_samples_split=5
    min_samples_leaf=2
    class_weight='balanced'  (handles class imbalance)
    random_state=42
  
  Train model. Evaluate on test set.
  Print: accuracy, precision, recall, F1, confusion matrix.
  Save model as joblib pickle to ml_models/risk_rf_model.pkl
  Save feature names list as ml_models/rf_features.json
  Save label encoder as ml_models/rf_label_encoder.pkl
  """

If MIN_TRAINING_SAMPLES not reached: print warning, do not train, do not crash.
</training_script>

<inference_service>
FILE: backend/app/services/random_forest_model.py

class RiskForestPredictor:
  def __init__(self):
    self.model = None
    self.feature_names = None
    self.load_model()  # Load on init; graceful fallback if not trained yet
  
  def load_model(self):
    try:
      self.model = joblib.load(RF_MODEL_PATH)
      with open('ml_models/rf_features.json') as f:
        self.feature_names = json.load(f)
    except FileNotFoundError:
      self.model = None  # model not trained yet  that's OK
      logger.info("RF model not trained yet  using rule-based scoring only")
  
  def build_feature_vector(self, user_id: UUID) -> np.ndarray | None:
    """Build the 14-feature vector for a user. Return None if < 10 attempts."""
  
  def predict(self, user_id: UUID) -> dict | None:
    """
    If model is None or < 10 attempts → return None (use rule-based score)
    
    Build feature vector, predict class and probability.
    Return: {
      predicted_risk_level: str,  # critical/high/medium/low
      confidence: float,          # probability of predicted class
      feature_importances: dict,  # top 3 features driving the prediction
                                  # (use model.feature_importances_)
    }
    """
  
  def get_feature_importances_for_user(self, user_id) -> dict:
    """
    Return top 3 factors driving this user's risk prediction.
    Format: {'phishing_accuracy': 0.28, 'rushed_attempt_rate': 0.21, ...}
    Used in employee dashboard: "Your risk is driven by: ..."
    """

</inference_service>

Write tests in backend/tests/test_random_forest.py:
1. test_feature_vector_length: returns 14 features
2. test_feature_vector_none_if_insufficient_data: < 10 attempts → None
3. test_predict_returns_valid_risk_level: output in [critical/high/medium/low]
4. test_predict_confidence_between_0_and_1: confidence ∈ [0.0, 1.0]
5. test_graceful_fallback_if_no_model: no pickle file → predict returns None

Run: python -m pytest tests/test_random_forest.py -v
All 5 must pass (even without a trained model).
```

### ✅ PHASE 5 VERIFICATION
```
[ ] 14 features exactly as specified
[ ] job_role_encoded integer mapping implemented
[ ] class_weight='balanced' in RandomForestClassifier
[ ] Model saves to ml_models/ directory
[ ] Graceful fallback when model not yet trained (returns None, no crash)
[ ] feature_importances returned in predict() output
[ ] train_models.py handles case where insufficient training data
[ ] All 5 unit tests pass without a trained model
```

---
---

# PHASE 6  K-Means User Clustering

## PROMPT 6.1  Behavioural Archetypes

```xml
<role>Data scientist implementing K-Means clustering for user archetype detection.</role>

<task>
Build K-Means clustering that groups users into 5 behavioural archetypes.
This tells managers what type of security risk each user represents,
not just a number.
</task>

<file>backend/app/services/kmeans_clustering.py</file>

<archetypes>
CLUSTER_ARCHETYPES = {
  0: {
    "label": "Overconfident Clicker",
    "description": "Answers quickly but gets it wrong. High risk of clicking phishing links in the real world because they trust their instincts without checking.",
    "colour": "#EF4444",
    "icon": "zap",
    "intervention": "Needs slowed-down scenario practice with explicit red-flag identification training."
  },
  1: {
    "label": "Cautious Learner",
    "description": "Takes time to think and mostly gets it right. Improving steadily. On track to become a security asset.",
    "colour": "#22C55E",
    "icon": "shield-check",
    "intervention": "Needs challenge scenarios at higher difficulty to build advanced recognition skills."
  },
  2: {
    "label": "Inconsistent Performer",
    "description": "Excellent in some categories but has dangerous blind spots in others. May have false confidence.",
    "colour": "#F59E0B",
    "icon": "alert-triangle",
    "intervention": "Needs targeted training in their weakest categories with extra visual scenario practice."
  },
  3: {
    "label": "Resilient Defender",
    "description": "Fast, accurate, and consistent across all categories. Completed streak training. A security role model.",
    "colour": "#3B82F6",
    "icon": "award",
    "intervention": "Can act as a peer mentor. Needs advanced threat scenarios to stay engaged."
  },
  4: {
    "label": "Disengaged Completer",
    "description": "Completes sessions slowly with inconsistent results. Likely not focused during training. High hidden risk.",
    "colour": "#8B5CF6",
    "icon": "eye-off",
    "intervention": "Needs shorter, more frequent gamified sessions. Manager should check in personally."
  },
}
</archetypes>

<clustering_features>
Use 6 features for clustering (simpler than RF  better for archetypes):
1. avg_response_time_ms (normalised 0-1)
2. overall_accuracy (0-1)
3. accuracy_variance (std across categories  measures inconsistency)
4. rushed_attempt_rate (0-1)
5. total_sessions (normalised)
6. streak_consistency (0-1)
</clustering_features>

<algorithm>
def train_kmeans(db_session):
  """
  Get all users with >= 5 attempts.
  Build 6-feature matrix.
  Normalise with StandardScaler.
  Train KMeans(n_clusters=5, random_state=42, n_init=10)
  Save: ml_models/user_clusters.pkl (the scaler + model together)
  Return: inertia, cluster sizes
  """

def assign_user_to_cluster(user_id: UUID) -> dict:
  """
  Build feature vector for user.
  Load scaler + KMeans model.
  Predict cluster for user.
  Look up archetype from CLUSTER_ARCHETYPES.
  Update User.cluster_label and UserCluster table.
  Return: {
    cluster_id: int,
    archetype_label: str,
    archetype_description: str,
    archetype_colour: str,
    archetype_icon: str,
    intervention: str,
    feature_values: dict  (the 6 features for this user)
  }
  """

def get_org_cluster_summary(org_id: UUID) -> dict:
  """
  For manager dashboard  show how many users in each archetype.
  Return: {
    archetypes: [
      {cluster_id, label, count, percentage, colour, icon, intervention}
    ],
    most_common_archetype: str,
    highest_risk_archetype_count: int,  # Overconfident Clickers count
    intervention_required: list[str]    # user names needing intervention
  }
  """
</algorithm>

Integrate clustering into the scheduler: re-cluster every 7 days.
Also allow manual re-clustering from admin panel endpoint.
```

### ✅ PHASE 6 VERIFICATION
```
[ ] 5 archetypes exactly as specified with colours and icons
[ ] 6 features used for clustering (not 14  keep it interpretable)
[ ] StandardScaler applied before KMeans
[ ] KMeans saved with scaler (so prediction uses same scaling)
[ ] User.cluster_label and UserCluster table updated on assignment
[ ] get_org_cluster_summary returns correct structure
[ ] Graceful fallback: returns None if model not trained
[ ] Scheduler calls kmeans reclustering every 7 days
```

---
---

# PHASE 7  Gamification Engine

## PROMPT 7.1  XP, Levels, Badges, Streaks, Leaderboard

```xml
<role>Game designer + backend engineer building an engaging gamification system.</role>

<task>
Build the complete gamification engine. This is what makes AHRIP feel like
a product people want to use, not a compliance checkbox.
Every badge is meaningful. Every level feels earned.
</task>

<file>backend/app/services/gamification_engine.py</file>

<xp_system>
XP_LEVEL_THRESHOLDS = {
  1: 0,     2: 100,   3: 250,   4: 500,
  5: 900,   6: 1400,  7: 2000,  8: 2750,
  9: 3700,  10: 5000
}

XP_REWARDS = {
  'correct_answer_d1': 10,
  'correct_answer_d2': 15,
  'correct_answer_d3': 25,
  'session_completion': 20,      # bonus for finishing a full session
  'daily_streak_3': 15,          # 3-day streak bonus
  'daily_streak_7': 30,          # 7-day streak
  'daily_streak_14': 60,         # 14-day streak
  'daily_streak_30': 100,        # 30-day streak
  'daily_challenge_complete': 25,
  'perfect_session': 50,         # 5/5 correct in one session
  'first_session': 30,           # welcome bonus
  'category_mastery': 40,        # first time mastering a category (>80%)
}

STREAK_MULTIPLIERS = {
  3: 1.5,   # 1.5x XP on all correct answers
  7: 2.0,   # 2x XP
  14: 2.5,  # 2.5x XP
  30: 3.0,  # 3x XP (legendary streak)
}

def calculate_level(total_xp: int) -> int:
  """Return current level based on total XP"""

def xp_to_next_level(total_xp: int) -> int:
  """Return XP needed to reach next level"""

def add_xp(user_id, xp_amount, reason) -> dict:
  """
  Add XP to UserGamification record.
  Check if level up occurred.
  Update weekly_xp and monthly_xp.
  Return: {new_total_xp, new_level, leveled_up: bool, xp_to_next: int}
  """
</xp_system>

<badges>
BADGES = {
  # Milestone badges
  'first_blood': {
    'name': 'First Line of Defence',
    'description': 'Completed your first training session',
    'icon': '🛡️', 'rarity': 'common', 'xp_bonus': 20
  },
  'phishing_spotter': {
    'name': 'Phishing Spotter',
    'description': 'Correctly identified 10 phishing attempts',
    'icon': '🎣', 'rarity': 'common', 'xp_bonus': 30
  },
  'week_warrior': {
    'name': 'Week Warrior',
    'description': 'Maintained a 7-day training streak',
    'icon': '🔥', 'rarity': 'rare', 'xp_bonus': 50
  },
  'month_defender': {
    'name': 'Month Defender',
    'description': 'Maintained a 30-day training streak',
    'icon': '⚡', 'rarity': 'epic', 'xp_bonus': 100
  },
  'perfect_session': {
    'name': 'Flawless',
    'description': 'Answered all 5 scenarios correctly in one session',
    'icon': '💎', 'rarity': 'rare', 'xp_bonus': 50
  },
  'phishing_master': {
    'name': 'Phishing Master',
    'description': 'Achieved >80% mastery in phishing recognition',
    'icon': '🦅', 'rarity': 'rare', 'xp_bonus': 40
  },
  'social_shield': {
    'name': 'Social Shield',
    'description': 'Mastered social engineering defence',
    'icon': '🤺', 'rarity': 'rare', 'xp_bonus': 40
  },
  'all_rounder': {
    'name': 'All Rounder',
    'description': 'Achieved mastery in all 8 security categories',
    'icon': '🏆', 'rarity': 'legendary', 'xp_bonus': 200
  },
  'speed_reader': {
    'name': 'Quick Thinker',
    'description': 'Correctly answered 5 scenarios in under 30 seconds each',
    'icon': '⚡', 'rarity': 'rare', 'xp_bonus': 40
  },
  'level_5': {
    'name': 'Cyber Aware',
    'description': 'Reached Level 5',
    'icon': '🌟', 'rarity': 'uncommon', 'xp_bonus': 30
  },
  'level_10': {
    'name': 'Cyber Guardian',
    'description': 'Reached Level 10  Elite Security Defender',
    'icon': '👑', 'rarity': 'legendary', 'xp_bonus': 150
  },
  'usb_aware': {
    'name': 'USB Aware',
    'description': 'Correctly handled all USB baiting scenarios',
    'icon': '🔌', 'rarity': 'uncommon', 'xp_bonus': 25
  },
}

RARITY_COLOURS = {
  'common': '#9CA3AF',
  'uncommon': '#22C55E',
  'rare': '#3B82F6',
  'epic': '#8B5CF6',
  'legendary': '#F59E0B',
}

def check_and_award_badges(user_id: UUID, attempt_data: dict) -> list[str]:
  """
  After each attempt, check all badge conditions.
  Award any newly earned badges.
  Add badge_id to UserGamification.badges_earned (JSON list).
  Add XP bonus for each badge earned.
  Return list of newly earned badge IDs (empty list if none).
  """

def get_daily_challenge(user_id: UUID) -> dict:
  """
  Generate a daily challenge appropriate for the user's level and weaknesses.
  Daily challenges reset at midnight UTC.
  
  Examples:
  - "Answer 3 difficulty-3 phishing scenarios correctly"
  - "Complete a session without any rushed attempts"
  - "Identify all red flags in today's featured scenario"
  
  Return: {
    challenge_id: str, title: str, description: str,
    xp_reward: int, deadline: datetime, completed: bool
  }
  """
</badges>

<leaderboard>
def get_org_leaderboard(org_id: UUID, metric: str = 'weekly_xp') -> list[dict]:
  """
  Metric options: 'weekly_xp' | 'level' | 'streak' | 'improvement'
  
  Return top 10 + current user's position.
  
  PRIVACY: Show first name + last initial only (anonymised).
  Never show absolute risk scores on leaderboard.
  Improvement metric = (current week accuracy - last week accuracy).
  
  Return: [
    {rank, display_name, value, badge_count, level, is_current_user: bool}
  ]
  """
</leaderboard>

Write tests in backend/tests/test_gamification.py:
1. test_level_calculation: 0xp→L1, 100xp→L2, 5000xp→L10
2. test_streak_multiplier_3: streak=3 gives 1.5x correct answer XP
3. test_streak_multiplier_7: streak=7 gives 2.0x XP
4. test_badge_first_blood_on_first_session
5. test_badge_perfect_session_on_5_of_5
6. test_leaderboard_anonymises_names: no full names in output
7. test_daily_challenge_resets_at_midnight

All 7 must pass.
```

### ✅ PHASE 7 VERIFICATION
```
[ ] XP_LEVEL_THRESHOLDS matches spec exactly
[ ] All 14 badges implemented with correct conditions
[ ] RARITY_COLOURS defined and used
[ ] Streak multipliers: 3→1.5x, 7→2.0x, 14→2.5x, 30→3.0x
[ ] Daily challenge generates correctly per user
[ ] Leaderboard shows first name + last initial only
[ ] Badge XP bonuses added to user total when earned
[ ] All 7 unit tests pass
```

---
---

# PHASE 8  Core Backend API

## PROMPT 8.1  All API Endpoints

```xml
<role>API engineer. Every endpoint is production-quality, fully implemented.</role>

<task>
Build ALL remaining API endpoints. Each must:
- Have correct rate limits
- Return JSON always (never HTML errors)
- Validate all inputs
- Log at appropriate levels
</task>

<training_api>FILE: backend/app/api/training.py  /api/v1/training/

GET /session/start
  Auth: employee | Rate: 20/hour
  Query: ?job_role_filter=true (optional  filter by user's job_role)
  Logic: adaptive_engine.select_next_session(user_id, job_role)
  Response: {
    session_id: uuid,
    scenarios: [ScenarioPublic]  ← NEVER include correct_answer or explanation
    ScenarioPublic contains: id, title, content, visual_html, category,
    difficulty, target_roles, option_a, option_b, option_c, option_d,
    visual_type, xp_reward
  }

POST /session/{session_id}/answer
  Auth: employee | Rate: 60/hour
  Body: {scenario_id, answer, response_time_ms}
  Validation: answer ∈ ['A','B','C','D'], response_time_ms ∈ [0, 300000]
  Logic: 
    1. Validate session ownership
    2. Run sentiment analysis: analyze_interaction(response_time_ms, ...)
    3. process_attempt() with sentiment_data
  Response: {
    is_correct, correct_answer, explanation, red_flags, learning_tip,
    xp_earned, streak_bonus, new_level, badges_earned,
    sentiment_label, mastery_update
  }

GET /session/{session_id}/summary
  Auth: employee (owns session)
  Response: session_summary from adaptive_engine

GET /history
  Auth: employee | Query: ?limit=20&offset=0&category=
  Response: {attempts: list, total: int}

GET /categories
  Auth: any | Cache: 1 hour
  Response: [{id, name, display_name, icon, description}]

GET /daily-challenge
  Auth: employee
  Response: daily challenge for this user
</training_api>

<scores_api>FILE: backend/app/api/scores.py  /api/v1/scores/

GET /me
  Returns: RiskScore + RF prediction + cluster + category breakdown
  If no score: {risk_level: 'unknown', message: '...'}

GET /me/history
  Returns: 8-week score history for trend chart

GET /me/cluster
  Returns: user's cluster archetype details

GET /me/badges
  Returns: all badges (earned + locked) with progress toward unearned ones

GET /leaderboard
  Query: ?metric=weekly_xp (weekly_xp|level|streak|improvement)
  Returns: ANONYMISED leaderboard top 10 + user rank
</scores_api>

<manager_api>FILE: backend/app/api/manager.py  /api/v1/manager/

GET /dashboard
  Auth: manager|admin
  Returns: {
    kpi_cards: {avg_score, critical_count, weekly_scenarios, trend_direction},
    top_risk: [max 3 users  risk level + archetype + weakest category ONLY],
    cluster_summary: from kmeans_clustering.get_org_cluster_summary(),
    threat_feed_status: {last_update, new_scenarios_this_week},
    org_category_weakness: [{category, avg_score, sorted by worst first}]
  }

GET /team
  Query: ?sort=risk_level&dept=&archetype=
  Returns: all users with {risk_level, cluster_label, archetype_colour,
           weakest_category, last_active, sessions_this_week}
  NO raw attempt data

GET /team/{user_id}/profile
  Returns: category breakdown + trend + cluster + RF prediction
  NO individual attempt data

POST /team/{user_id}/assign-training
  Body: {categories: list, note: str}
  Marks categories for priority in next session

GET /reports/summary
  Query: ?weeks=4
  Response: CSV download (no individual user data)
</manager_api>

<gamification_api>FILE: backend/app/api/gamification.py  /api/v1/gamification/

GET /me
  Returns: {level, total_xp, xp_to_next, weekly_xp, streak, badges_earned,
             level_progress_percent}

GET /leaderboard/{metric}
  Returns anonymised leaderboard

GET /badges
  Returns all badges with earned status and progress

POST /daily-challenge/complete
  Marks daily challenge as complete, awards XP
</gamification_api>

<health_api>FILE: backend/app/api/health.py
GET /api/v1/health
  No auth required
  Returns: {status, version, db, rf_model_loaded, kmeans_loaded, timestamp}
  HTTP 200 if healthy, 503 if DB down
</health_api>
```

### ✅ PHASE 8 VERIFICATION
```
[ ] GET /training/session/start returns ScenarioPublic (NO correct_answer)
[ ] POST /answer returns correct_answer ONLY after answering
[ ] Sentiment analysis runs on every attempt
[ ] Manager cannot see raw individual attempt data (test directly)
[ ] Leaderboard only shows first name + last initial
[ ] /health endpoint shows rf_model_loaded and kmeans_loaded status
[ ] /me/cluster returns archetype with colour and icon
[ ] All endpoints return JSON for error states (never HTML)
[ ] Rate limits applied and testable (429 on excess)
```

---
---

# PHASE 9  Design System + Professional UI

## PROMPT 9.1  Design Tokens & Component Library

```xml
<role>
Senior UI engineer. You build UIs that look like Vercel, Linear, or Notion 
not like a student project. Dark, precise, professional.
You NEVER produce "AI slop" aesthetic.
</role>

<task>
Build the complete design system and core UI components for AHRIP v2.
This is the foundation every page is built on.
The aesthetic is: dark enterprise SaaS  think security operations centre
meets modern product design. Not playful. Not corporate clip-art. Professional.
</task>

<design_tokens>
FILE: frontend/src/index.css

/* ── Colour System ────────────────────────────────────────────── */
:root {
  /* Backgrounds  layered dark */
  --bg-base:        #080C14;   /* darkest  page background */
  --bg-surface:     #0F1521;   /* cards, modals */
  --bg-elevated:    #162030;   /* hover states, dropdowns */
  --bg-overlay:     #1D2A3F;   /* sidebars, panel headers */

  /* Borders */
  --border-subtle:  #1E2D42;
  --border-default: #2A3F5C;
  --border-strong:  #3A5578;

  /* Text */
  --text-primary:   #F0F4F8;
  --text-secondary: #8BA4BF;
  --text-muted:     #4E6882;
  --text-inverse:   #080C14;

  /* Risk colours */
  --risk-critical:  #EF4444;
  --risk-high:      #F97316;
  --risk-medium:    #EAB308;
  --risk-low:       #22C55E;
  --risk-unknown:   #6B7280;

  /* Accent */
  --accent:         #3B82F6;   /* blue  primary action */
  --accent-hover:   #2563EB;
  --accent-muted:   #1E3A5F;

  /* Success / Warning / Error */
  --success:        #10B981;
  --warning:        #F59E0B;
  --error:          #EF4444;

  /* XP / Gamification */
  --xp-gold:        #F59E0B;
  --xp-silver:      #94A3B8;
  --xp-bronze:      #D97706;

  /* Rarity colours */
  --rarity-common:    #6B7280;
  --rarity-uncommon:  #22C55E;
  --rarity-rare:      #3B82F6;
  --rarity-epic:      #8B5CF6;
  --rarity-legendary: #F59E0B;
}

/* Typography: use Inter from Google Fonts */
/* Font sizes: 11/12/13/14/16/18/20/24/32/40px */
/* Letter spacing: tight on headings, normal on body */
/* Line height: 1.4 on body, 1.2 on headings */
</design_tokens>

<core_components>
Build these components with the exact aesthetic described:

1. FILE: frontend/src/components/shared/RiskBadge.tsx
   Props: level ('critical'|'high'|'medium'|'low'|'unknown'), size?
   Design: pill badge with coloured dot + text
   Colors from --risk-* variables
   Animate: subtle pulse on 'critical' level

2. FILE: frontend/src/components/shared/AnimatedNumber.tsx
   Smoothly counts up/down to target number when value changes
   Uses requestAnimationFrame, duration 600ms
   Used for: XP counter, score displays, KPI cards

3. FILE: frontend/src/components/training/ProgressRing.tsx
   SVG-based circular progress ring
   Props: percentage, size, colour, label, animated
   Animation: 1s ease-out fill on mount
   Shows: percentage number in centre + label below

4. FILE: frontend/src/components/training/CategoryBadge.tsx
   Props: category (one of 8 categories)
   Each category has unique icon (lucide) + colour:
     phishing_email: Mail icon, #3B82F6
     smishing: MessageSquare, #8B5CF6
     vishing: Phone, #F97316
     physical_security: Lock, #EF4444
     password_hygiene: Key, #EAB308
     usb_baiting: Usb, #EC4899
     social_engineering: Users, #14B8A6
     data_handling: Database, #22C55E

5. FILE: frontend/src/components/gamification/XPBar.tsx
   Horizontal progress bar showing XP progress to next level
   Shows: level number, XP earned, XP needed, progress fill
   Animated fill when XP changes
   Colour: --xp-gold gradient on fill

6. FILE: frontend/src/components/gamification/BadgeGrid.tsx
   Grid of badge cards
   Earned badges: full colour, glow effect on hover
   Unearned badges: greyscale, locked icon overlay, progress bar below
   Rarity colours from --rarity-* variables

7. FILE: frontend/src/components/gamification/StreakCounter.tsx
   Shows current streak with fire emoji animation
   Streak ≥ 7: animated flame, gold glow
   Streak ≥ 30: pulsing legendary effect

8. FILE: frontend/src/components/gamification/LevelUpModal.tsx
   Full-screen modal that appears when user levels up
   Confetti explosion (react-confetti)
   Large level number animation
   New perks unlocked display
   "Continue Training" button

9. FILE: frontend/src/lib/animations.ts
   Framer Motion variants for common animations:
   fadeIn, slideUp, scaleIn, shimmer, pulse
   Used throughout all components
</core_components>

<layout_files>
FILE: frontend/src/components/layout/AppShell.tsx
Two-column layout:
  Left: Sidebar (240px desktop, collapsible mobile)
  Right: TopBar + main content

FILE: frontend/src/components/layout/Sidebar.tsx
Design requirements:
  - Background: --bg-overlay
  - AHRIP logo: stylised text "AHRIP" in --accent, smaller tagline below
  - Navigation sections with labels:
    
    LEARN:
      Dashboard (LayoutDashboard icon) → /app/dashboard
      Training (Target icon) → /app/training
      Daily Challenge (Flame icon) → /app/challenge [shows badge if new challenge]
    
    PROGRESS:
      My Score (TrendingUp icon) → /app/my-score
      Badges (Award icon) → /app/badges
      Leaderboard (Trophy icon) → /app/leaderboard
    
    TEAM (manager/admin only):
      Overview (BarChart icon) → /app/manager/dashboard
      Team (Users icon) → /app/manager/team
      Reports (FileText icon) → /app/manager/reports
    
    ADMIN (admin only):
      Admin Panel (Settings icon) → /app/admin
      Threat Feeds (Rss icon) → /app/admin/threats
    
  - Bottom section: XP mini-bar + level + user avatar + logout
  - Active route: left border accent, background --bg-elevated
  - Hover: background --bg-elevated, transition 150ms
  - XP mini-bar shows current level progress

FILE: frontend/src/components/layout/TopBar.tsx
  - Page title (dynamic)
  - Right: streak badge + notification bell (placeholder) + user dropdown
  - User dropdown: Profile, Settings, Logout
  - Organisation name in subtle text
</layout_files>
```

### ✅ PHASE 9 VERIFICATION
```
[ ] All --bg-*, --text-*, --risk-*, --accent-* CSS variables defined
[ ] All 8 CategoryBadge categories have unique colours and icons
[ ] XPBar animates when XP value changes
[ ] LevelUpModal shows confetti and new level number
[ ] BadgeGrid shows greyscale + lock for unearned badges
[ ] StreakCounter has animated flame at streak >= 7
[ ] Sidebar shows XP mini-bar at bottom
[ ] AppShell layout works on mobile (sidebar collapses)
[ ] All animations use Framer Motion or CSS transitions (not JS setTimeout hacks)
[ ] No placeholder or mock data in component logic
```

---
---

# PHASE 10  Employee Training Interface

## PROMPT 10.1  Training Page (Core Employee Experience)

```xml
<role>
Product designer + React engineer building the core training experience.
This page is what employees will use daily. It must be engaging, clear,
and educational. Think Duolingo meets a cybersecurity operations centre.
</role>

<task>
Build the complete employee training experience across 3 states.
Use the design system from Phase 9. Every interaction is polished.
</task>

<file>frontend/src/pages/employee/TrainingPage.tsx</file>

<state_1_idle>
Show when no active session:

Layout (centred, max-width 720px):
  TOP: User's current risk badge + XP bar + streak counter
  
  HERO CARD (--bg-surface, border --border-default):
    "Today's Focus"  category badge for their weakest category
    Description: why this category matters for their job role
    [Start Training Session] button  large, --accent colour
    Subtitle: "5 questions · ~5 minutes · Live threat scenarios"
  
  ROW OF 3 STAT CARDS:
    - Scenarios completed this week
    - Current streak (with flame icon)
    - Weekly XP earned
  
  DAILY CHALLENGE CARD (if available):
    Gold border, flame icon, challenge description
    XP reward shown, deadline shown
    [Start Challenge] button
  
  RECENT BADGES (last 3 earned):
    Small badge previews with "View All Badges" link
</state_1_idle>

<state_2_active_session>
FILE: frontend/src/components/training/ScenarioCard.tsx

Layout:
  TOP BAR: "Question 2 of 5" + category badge + difficulty shields + timer
  
  VISUAL SCENARIO (if visual_html present):
    Rendered iframe or dangerouslySetInnerHTML with visual_html content
    Sandboxed: sandbox="allow-same-origin"  no scripts execute
    Border: --border-default, rounded corners
    Label above: "⚠️ Simulated Attack  This is a training scenario"
    NEVER render with real external URLs  all URLs in visual_html are placeholders
  
  SCENARIO TEXT:
    Large readable text (16px min)
    Typography: --text-primary on --bg-surface
  
  FILE: frontend/src/components/training/AnswerOptions.tsx
  4 answer cards full-width:
    Before answer:
      - --bg-surface border --border-default
      - Hover: --bg-elevated, border --border-strong
    After answer (immediate visual feedback):
      - Correct selected: --success background, check icon
      - Wrong selected: --error background, X icon
      - Correct answer (if wrong selected): green outline
      - Wrong options: greyed out
    Transition: 200ms all
  
  FILE: frontend/src/components/training/FeedbackPanel.tsx
  Slides in from bottom after answering:
    - is_correct ? "✓ Correct!" : "✗ Incorrect"
    - Explanation text
    - Red flags list (with warning icons per item)
    - Learning tip (highlighted box)
    - Sentiment feedback: if 'rushed' → "Tip: Take a moment to read carefully"
    - XP earned + any badges earned (animated entrance)
    - [Next Question] button
</state_2_active_session>

<state_3_complete>
Session summary page:

  SCORE HEADER: X/5 correct, percentage ring (ProgressRing component)
  
  XP SUMMARY:
    Base XP earned this session
    Streak bonus (if any)  animated gold highlight
    Badge bonuses (if any)
    Total XP this session
    XP bar progress update (animated)
  
  CATEGORY BREAKDOWN:
    Mini table: category | questions | correct | mastery change (↑↓)
  
  RISK SCORE CHANGE:
    Before/after score display
    If improved: green text "+ X points improvement"
    If worsened: amber text "- X points  practice more"
  
  BADGES EARNED (if any):
    Animated badge reveal cards
  
  IMPROVEMENT TIPS:
    Based on what went wrong this session
    "You struggled with: [category]  here's why it matters..."
  
  TWO BUTTONS:
    [Start Another Session] and [View My Score]
</state_3_complete>

Build also:
FILE: frontend/src/pages/employee/MyScorePage.tsx
  - Large ProgressRing for composite score
  - Radar chart (Recharts) for 8 categories
  - RF prediction card: "AI Prediction: You are [X]% likely to click a 
    real phishing link without training"
  - Cluster archetype card with description and intervention tip
  - 8-week trend LineChart (Recharts)
  - Category breakdown bars (custom  not library)
  - Disclaimer: "Scores reflect training performance only"

FILE: frontend/src/pages/employee/BadgesPage.tsx
  - BadgeGrid component
  - Filter tabs: All / Earned / Locked
  - Progress bar for each locked badge

FILE: frontend/src/pages/employee/LeaderboardPage.tsx
  - Metric selector: Weekly XP / Level / Streak / Improvement
  - Top 10 table with rank, anonymised name, value, level badge
  - Current user row highlighted
  - Trophy icons for top 3
  - "Rankings refresh weekly. Names are anonymised for privacy." disclaimer
```

### ✅ PHASE 10 VERIFICATION
```
[ ] All 3 training states (idle/active/complete) implemented
[ ] visual_html rendered in sandboxed iframe (no script execution)
[ ] "⚠️ Simulated Attack" warning shown above visual scenario
[ ] Answer feedback is immediate (< 200ms) after click
[ ] FeedbackPanel shows red_flags, learning_tip, and sentiment tip
[ ] XP animation on session complete
[ ] LevelUpModal fires if user levels up during session
[ ] ProgressRing animates on MyScorePage mount
[ ] Radar chart shows all 8 categories
[ ] RF prediction card shows "likely to click" percentage
[ ] Cluster archetype card shows colour-coded archetype
[ ] Leaderboard shows anonymised names only
[ ] All pages mobile responsive (test at 375px)
[ ] No console errors on any page
```

---
---

# PHASE 11  Manager Intelligence Dashboard

## PROMPT 11.1  Manager Dashboard (Full Build)

```xml
<role>
Dashboard UX engineer building intelligence tools for non-technical managers.
Design principle: every number has context. Every chart has a plain-English title.
A manager with no security knowledge must understand everything at a glance.
</role>

<task>
Build the complete manager-facing dashboard. All data from the manager API.
Show cluster archetypes, RF predictions, and risk intelligence clearly.
</task>

<file>frontend/src/pages/manager/DashboardPage.tsx</file>

<layout>
12-column grid layout.

ROW 1  KPI Cards (4 cards):
  Card 1: Team Risk Score (average composite, trend arrow, "Lower is better")
  Card 2: Staff Needing Attention (critical+high count, red badge, click→team filtered)
  Card 3: Training Activity (scenarios this week, progress bar vs target)
  Card 4: Trend (+/-% vs last week, green if improved red if not)
  
  Each card: --bg-surface, --border-subtle, subtle shadow
  AnimatedNumber for the main metric

ROW 2  Main Content (8 cols + 4 cols):

  LEFT (8 cols):
  FILE: frontend/src/components/dashboard/RiskHeatmap.tsx
    CSS Grid: rows=users, columns=8 categories
    Cell colour: green→yellow→orange→red based on category score
    Cell tooltip: "Sarah M.  Phishing: 72/100 (High)"
    Category icons in column headers
    Paginate if > 15 users (show 15 at a time)
    Legend below
  
  RIGHT (4 cols):
  FILE: frontend/src/components/dashboard/RiskTrendChart.tsx
    Recharts AreaChart, 8-week trend of org average
    Reference line at 50 (medium threshold)
    Fill colour changes: red above 70, amber 50-70, green below 50

ROW 3  Intelligence Cards (4 cols + 4 cols + 4 cols):

  CARD 1:
  FILE: frontend/src/components/dashboard/TopRiskTable.tsx
    "Staff Needing Attention" (max 3)
    Columns: Name | Risk Level | Archetype | Weakest Area | Action
    Archetype shown as coloured badge with icon
    [Assign Training] button per row → opens modal
    Privacy disclaimer below
    If 0 critical/high: "✅ All staff at acceptable risk level"
  
  CARD 2:
  FILE: frontend/src/components/dashboard/ClusterView.tsx
    "Your Team's Behavioural Profiles"
    Recharts PieChart of archetype distribution
    Legend: each archetype with colour dot, count, percentage
    Click archetype → navigates to team page filtered by that archetype
    "Most common: [archetype name]" callout
    "Action needed: [count] Overconfident Clickers" if > 0
  
  CARD 3:
  FILE: frontend/src/components/dashboard/CategoryWeaknessChart.tsx
    Recharts HorizontalBarChart  8 bars, sorted worst-first
    Each bar coloured by risk level
    "Where Your Team Struggles Most" title
    Click bar → team page filtered by that category

ROW 4  Threat Intelligence Row:
  FILE: frontend/src/components/dashboard/ThreatFeedBadge.tsx
  Full-width card showing:
    - "Live Threat Intelligence Status"
    - Last updated: [X hours ago] + coloured dot (green<12h, amber<24h, red>24h)
    - New scenarios this week: X
    - Sources active: PhishTank ✓ Phishing.Database ✓ AlienVault OTX ✓ URLScan ✓
    - "Scenarios derived from real attacks, updated every 6 hours"
</layout>

<team_page>
FILE: frontend/src/pages/manager/TeamPage.tsx

Header:
  Filters: Department dropdown, Risk Level dropdown, Archetype dropdown, Search
  Sort: Risk Level / Name / Last Active / Sessions This Week
  Export CSV button

Table columns:
  Avatar + Name | Job Role | Department | Risk Level Badge | 
  Archetype Badge (coloured) | Weakest Category | Sessions This Week | Actions

Row expansion (click → inline):
  Category breakdown bars (no raw attempts)
  RF prediction: "AI predicts [X]% susceptibility to real attacks"
  Recommended action based on archetype

Assign Training Modal:
  Employee name in title
  Category checkboxes
  Note/reason field
  Submit → POST /manager/team/{id}/assign-training
  Success toast notification (bottom-right, auto-dismiss 3s)
</team_page>

<clusters_page>
FILE: frontend/src/pages/manager/ClustersPage.tsx

"Behavioural Intelligence" page:

5 archetype cards in a grid:
  Each card:
    - Archetype name + icon + rarity-style colour
    - Description
    - Count in org + percentage
    - Intervention recommendation
    - [View These Staff] link → team page filtered
  
Below: explanation of how clustering works (plain English, no ML jargon)
"These profiles are calculated from training behaviour patterns,
 not from personal or HR data."
</clusters_page>
```

### ✅ PHASE 11 VERIFICATION
```
[ ] All 4 KPI cards with AnimatedNumber and trend indicators
[ ] RiskHeatmap renders all 8 category columns with colour coding
[ ] ClusterView PieChart shows 5 archetypes with correct colours
[ ] TopRiskTable shows archetype badge with colour and icon
[ ] ThreatFeedBadge shows all 4 sources (PhishTank, OTX)
[ ] TeamPage has all 3 filter dropdowns + search working
[ ] RF prediction shown in row expansion ("AI predicts X%")
[ ] Assign Training modal submits successfully
[ ] ClustersPage shows intervention recommendation per archetype
[ ] Privacy disclaimer present on all tables showing individual data
[ ] All charts render with real API data (no dummy data hardcoded)
[ ] Pages work on tablet viewport (768px)
```

---
---

# PHASE 12  Admin Panel

## PROMPT 12.1  Admin Interface

```xml
<task>
Build the admin panel for AHRIP v2.
Admins can: manage users, manage scenarios, view threat feed status,
trigger manual ingestion, retrain ML models.
</task>

<pages>
FILE: frontend/src/pages/admin/AdminDashboardPage.tsx
  System stats: total orgs, users, scenarios, threat entries last 24h
  ML model status: RF trained? KMeans trained? Last training date?
  [Retrain Models] button → POST /admin/retrain-models
  [Trigger Feed Ingestion] button → POST /admin/trigger-feed-ingestion
  Live ingestion log (poll /admin/ingestion-status every 3s while running)

FILE: frontend/src/pages/admin/ScenariosPage.tsx
  Table: Title | Category | Difficulty | Source | Target Roles | Active | Accuracy | XP
  Toggle active/inactive per scenario
  Filter by source (manual/phishtank/openphish/otx/urlscan) + category + difficulty
  [Preview] → shows scenario as employee sees it (modal)
  [Add Manual Scenario] → form to create new scenario

FILE: frontend/src/pages/admin/ThreatFeedPage.tsx
  Feed status cards (one per source)
  Feed history table: source, count, scenarios_created, timestamp
  [Trigger Manual Ingestion] button per source or all sources

FILE: frontend/src/pages/admin/UsersPage.tsx
  Users table with all fields
  Toggle active/inactive (soft-disable only  no hard delete)
  Change role (promote to manager)
  View risk score and cluster
  Search by name or email
</pages>

<admin_api>
Add to backend/app/api/admin.py:

POST /api/v1/admin/trigger-feed-ingestion
  Auth: admin only | Runs ingestion in background thread
  Returns: {status: 'triggered', job_id: uuid}

GET /api/v1/admin/ingestion-status
  Returns current ingestion job status and last stats

POST /api/v1/admin/retrain-models
  Auth: admin only
  Triggers RF + KMeans retraining in background
  Returns: {status: 'triggered', message: str}

GET /api/v1/admin/scenarios → paginated scenario list
PATCH /api/v1/admin/scenarios/{id}/toggle → toggle active
POST /api/v1/admin/scenarios → create manual scenario

GET /api/v1/admin/users → paginated user list
PATCH /api/v1/admin/users/{id}/toggle → toggle active
PATCH /api/v1/admin/users/{id}/role → change role
</admin_api>
```

---
---

# PHASE 13  Security Hardening

## PROMPT 13.1  Production Security

```xml
<role>
Security engineer performing production security hardening.
Every item below is MANDATORY. None are optional.
This is an Ethical Hacking & Cybersecurity project  the application itself
must be a security exemplar.
</role>

<task>
Apply complete production security hardening.
After this phase, the application must pass a basic security audit.
</task>

<backend_hardening>
1. Flask-Talisman (already imported)  configure for production:
   CSP = {
     default-src: "'self'",
     script-src: ["'self'", "'unsafe-inline'"],
     style-src: ["'self'", "'unsafe-inline'", "fonts.googleapis.com"],
     font-src: ["'self'", "fonts.gstatic.com"],
     img-src: ["'self'", "data:"],
     connect-src: ["'self'"],
     frame-src: "'none'",  ← prevent clickjacking
     frame-ancestors: "'none'",
     form-action: "'self'",
     base-uri: "'self'",
   }
   force_https=True (production only)
   strict_transport_security=True
   referrer_policy='strict-origin-when-cross-origin'
   permissions_policy: camera=(), microphone=(), geolocation=()

2. SQL injection audit:
   Run: grep -r "f\"SELECT\|execute.*%\|format.*SELECT" backend/app/
   → Must return ZERO results
   All queries MUST use SQLAlchemy ORM or parameterised queries

3. Input sanitisation:
   bleach.clean() on ALL string inputs before any processing
   Length limits enforced BEFORE any processing
   Verify: RegistrationSchema, LoginSchema use sanitize_string()

4. JWT security:
   Algorithm: HS256
   Access token: 15 min
   Implement @jwt.token_in_blocklist_loader checking jwt_blocklist table
   Every protected endpoint checks blocklist

5. CORS lockdown:
   ALLOWED_ORIGINS from environment variable
   NO wildcard (*) origins
   Development: localhost:5173 only
   Production: Vercel URL only

6. Rate limits audit  verify ALL exist:
   POST /auth/register: 5/hour per IP
   POST /auth/login: 10/15min per IP
   POST /training/session/answer: 60/hour per user
   POST /admin/*: 30/hour per admin user
   Run: grep -r "@limiter.limit" backend/app/api/ → must show all groups

7. visual_html safety:
   Scenario visual_html content MUST be sanitised before storage
   Use bleach.clean() with allowed tags:
   allowed_tags = ['div','p','span','table','tr','td','th','thead','tbody',
                   'img','a','h1','h2','h3','strong','em','br','ul','li',
                   'button','input','label','form','style']
   allowed_attrs = {'*': ['class','id','style'], 'a': ['href'], 'img': ['src','alt']}
   Strip any 'href' that starts with 'javascript:' or 'data:'
   In frontend iframe: sandbox="allow-same-origin" (no allow-scripts)
</backend_hardening>

<frontend_hardening>
FILE: frontend/vercel.json:
{
  "rewrites": [{"source": "/(.*)", "destination": "/index.html"}],
  "headers": [{
    "source": "/(.*)",
    "headers": [
      {"key": "X-Content-Type-Options", "value": "nosniff"},
      {"key": "X-Frame-Options", "value": "DENY"},
      {"key": "X-XSS-Protection", "value": "1; mode=block"},
      {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
      {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"}
    ]
  }]
}

Access token: Zustand memory ONLY  never localStorage
Refresh token: localStorage key 'ahrip_rt' (acceptable tradeoff)
No API keys or secrets in any .js file
All requests over HTTPS in production (env check)
Axios timeout: 10000ms on all requests
</frontend_hardening>

<security_test_checklist>
Run all 8 tests manually after hardening:
1. SQL injection: email = "' OR 1=1 --" → 401 (no DB error in logs)
2. XSS in registration: first_name = "<script>alert(1)</script>" → 201 but script stripped
3. JWT tamper: modify payload → 422 (invalid signature)
4. Wrong role access: employee → GET /api/v1/manager/dashboard → 403
5. Wrong org access: user from org A → GET /api/v1/manager/team (org B data) → 403
6. Rate limit: 11 login requests in 1 min → 429 on 11th
7. visual_html injection: submit scenario with onclick in visual_html → stripped
8. CORS: curl with -H "Origin: https://evil.com" → no CORS headers returned

ALL 8 MUST PASS before moving to deployment.
</security_test_checklist>
```

### ✅ PHASE 13 VERIFICATION
```
[ ] CSP headers present in production config (verify in browser DevTools)
[ ] grep for raw SQL returns zero results
[ ] bleach sanitization on all text inputs including visual_html
[ ] JWT blocklist check on every protected request
[ ] CORS allows only specified origin (no wildcard)
[ ] Rate limits: all 4 groups verified with grep
[ ] visual_html iframe has sandbox="allow-same-origin" (no allow-scripts)
[ ] Access token in Zustand memory only
[ ] All 8 security tests pass
[ ] X-Frame-Options: DENY on all responses
```

---
---

# PHASE 14  Testing Suite

## PROMPT 14.1  Comprehensive Tests

```xml
<task>
Build the complete test suite. Target: 75% backend coverage.
Run all tests. Fix all failures before calling this phase done.
</task>

<backend_tests>
FILE: backend/tests/conftest.py
Fixtures: app (testing), client, db (in-memory SQLite),
seeded_db (1 org, 5 users with different job_roles, 48 scenarios),
employee_token (accountant job_role), manager_token, admin_token,
all header fixtures

FILE: backend/tests/test_auth.py (minimum 12 tests):
  test_register_success_with_job_role
  test_register_duplicate_email_409
  test_register_weak_password_422
  test_register_xss_name_sanitised
  test_register_invalid_job_role_422
  test_login_success_returns_tokens_with_job_role_in_claims
  test_login_wrong_password_401
  test_login_lockout_after_5_failures
  test_login_locked_returns_423
  test_refresh_returns_new_token
  test_logout_blacklists_token
  test_rate_limit_login_429

FILE: backend/tests/test_api.py (minimum 12 tests):
  test_session_start_excludes_correct_answer
  test_session_filters_by_job_role
  test_answer_returns_sentiment_label
  test_cant_answer_same_scenario_twice_in_session
  test_employee_blocked_from_manager_endpoint
  test_manager_blocked_from_other_org_data
  test_risk_score_me_unknown_before_10_attempts
  test_manager_dashboard_excludes_raw_attempts
  test_leaderboard_anonymises_names
  test_health_shows_ml_model_status
  test_daily_challenge_returns_correct_structure
  test_xp_added_on_correct_answer

FILE: backend/tests/test_random_forest.py (5 tests  already specified Phase 5)
FILE: backend/tests/test_adaptive_engine.py (10 tests  already specified Phase 4)
FILE: backend/tests/test_gamification.py (7 tests  already specified Phase 7)
FILE: backend/tests/test_risk_scorer.py (minimum 6 tests):
  test_unknown_risk_if_less_than_10_attempts
  test_phishing_weight_highest
  test_decay_factor_reduces_old_attempt_weight
  test_composite_clamps_0_to_100
  test_risk_level_thresholds_correct (70→critical, 50→high, 30→medium)
  test_category_scores_all_present_in_output

FILE: backend/tests/test_threat_ingestion.py (7 tests):
  test_dead_url_discarded_in_stage2
  test_raw_url_not_in_scenario_content
  test_raw_url_not_in_visual_html
  test_lure_type_classified_correctly
  test_difficulty_1_for_obvious_typosquat
  test_difficulty_3_for_subdomain_attack
  test_xp_reward_matches_difficulty
</backend_tests>

Run all: python -m pytest tests/ -v --cov=app --cov-report=term-missing
Target: >= 75% coverage
Zero failures

Frontend tests (Vitest):
  test: ScenarioCard does not show correct_answer prop
  test: AnswerOptions shows green on correct selection
  test: XPBar increases on value change (animation triggers)
  test: LevelUpModal fires on level change
  test: leaderboard shows anonymised names only (no full surnames)

Run: npm run test
All must pass.
```

---
---

# PHASE 15  Production Deployment

## PROMPT 15.1  Supabase + Render + Vercel

```xml
<task>
Deploy the complete AHRIP v2 to production.
Follow these steps exactly. Verify each step before proceeding.
</task>

<step1_supabase>
1. Create Supabase project: name=ahrip-v2-prod, region=ap-southeast-1 (Singapore)
2. Copy connection string from Settings → Database → URI format
3. Run migrations: DATABASE_URL=[supabase-url] flask db upgrade
4. Run seed: DATABASE_URL=[supabase-url] python seed.py
5. Verify all 8 tables exist in Supabase table editor
6. Enable RLS on users table (defence in depth  app handles auth)
7. Run train_models.py against production DB to train RF + KMeans
   (will fail gracefully if < 50 samples  that's expected for fresh deployment)
</step1_supabase>

<step2_render>
FILE: backend/render.yaml:
services:
  - type: web
    name: ahrip-v2-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn wsgi:app --workers 2 --timeout 120 --log-level info
    healthCheckPath: /api/v1/health
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        sync: false
      - key: PHISHTANK_API_KEY
        sync: false
      - key: ALIENVAULT_OTX_KEY
        sync: false
      - key: URLSCAN_API_KEY
        sync: false
      - key: ALLOWED_ORIGINS
        sync: false

After deploy:
curl https://[render-url].onrender.com/api/v1/health
→ MUST return: {"status": "healthy", "db": "connected", "version": "2.0.0"}
</step2_render>

<step3_vercel>
FILE: frontend/vercel.json  already built in Phase 13

Deploy: connect GitHub repo → select frontend/ as root
Build: npm run build, output: dist

Environment variables:
  VITE_API_BASE_URL: https://[render-url].onrender.com/api/v1

After deploy: update ALLOWED_ORIGINS on Render to Vercel URL.
</step3_vercel>

<final_smoke_test>
Run all 10 of these manually after deployment:
1. Visit /login → login page loads
2. Login as accountant → redirects to training dashboard
3. Check sidebar shows XP bar + streak counter
4. Start training session → 5 scenarios load, no correct_answer visible
5. Answer a phishing scenario → feedback shows with red_flags
6. Complete session → XP animation, possible level-up modal
7. Visit /app/my-score → risk score, radar chart, cluster archetype visible
8. Visit /app/leaderboard → only anonymised names shown
9. Login as manager → dashboard loads with KPI cards
10. Manager dashboard cluster view shows 5 archetype segments

IF ALL 10 PASS → DEPLOYMENT COMPLETE ✅
</final_smoke_test>
```

---
---

# POST-DEPLOYMENT: Academic Evaluation Setup

## PROMPT BONUS  Evaluation Data Collection

```xml
<task>
Configure AHRIP v2 to collect the data needed for academic evaluation.
The controlled study (Group A adaptive vs Group B static) requires:
1. Ability to put users into "static mode" (no adaptation, no risk score feedback)
2. Pre/post accuracy measurement per category
3. Export of comparison data for statistical analysis

Add these admin features:
</task>

<features>
1. User flag: training_mode ('adaptive'|'static')  default 'adaptive'
   Admin can toggle this per user or per group
   Static mode: adaptive engine returns random scenarios at difficulty 1 only,
   no category weighting, no role filtering

2. Pre-study baseline capture:
   Admin endpoint: POST /admin/capture-baseline/{user_id}
   Stores current accuracy per category as baseline snapshot in user profile

3. Study export:
   GET /admin/study-export?weeks=4
   Returns CSV with:
   user_id (anonymised), training_mode, job_role, baseline_accuracy_per_category,
   week4_accuracy_per_category, improvement_per_category, sentiment_dominant,
   cluster_archetype, sessions_completed, total_scenarios
   NO names, emails, or identifying information
   This is the dataset for the t-test

4. Statistical summary endpoint:
   GET /admin/study-statistics
   Returns: {
     adaptive_group: {n, mean_improvement, std_improvement},
     static_group:   {n, mean_improvement, std_improvement},
     cohens_d: float,  (calculated server-side)
     note: "Run independent samples t-test on mean_improvement values"
   }
</features>
```

---

# APPENDIX  Quick Reference

## API Endpoints Summary
```
AUTH:    POST /register  /login  /refresh  /logout  GET /me
TRAIN:   GET /session/start  POST /session/{id}/answer  GET /session/{id}/summary
         GET /history  GET /categories  GET /daily-challenge
SCORES:  GET /me  /me/history  /me/cluster  /me/badges  /leaderboard
MANAGER: GET /dashboard  /team  /team/{id}/profile  /clusters
         POST /team/{id}/assign-training  GET /reports/summary
GAMIF:   GET /me  /leaderboard/{metric}  /badges  POST /daily-challenge/complete
ADMIN:   POST /trigger-feed-ingestion  /retrain-models  GET /ingestion-status
         GET /scenarios  PATCH /scenarios/{id}/toggle  POST /scenarios
         GET /users  PATCH /users/{id}/toggle  PATCH /users/{id}/role
         POST /capture-baseline/{id}  GET /study-export  /study-statistics
HEALTH:  GET /health
```

## Threat Coverage
```
8 Categories: phishing_email · smishing · vishing · physical_security
              password_hygiene · usb_baiting · social_engineering · data_handling
8 Job Roles: receptionist · accountant · hr · it · finance · sales · management · other
OSINT Sources: PhishTank · Phishing.Database · AlienVault OTX · Phishing.Database
```

## ML Models
```
Random Forest: 14 features → predicts risk level (critical/high/medium/low)
K-Means:       6 features → assigns behavioural archetype (0-4)
Sentiment:     VADER + interaction pattern → rushed/overconfident/cautious/anxious/neutral
Adaptive:      Rule-based (Cognitive Load Theory) → difficulty 1/2/3 per category
```

---

**END OF AHRIP v2 MASTER BUILD PROMPT DOCUMENT**
*15 Phases · 24 Prompts · Production-Ready · For Claude Opus 4.7*
*BSc (Hons) Ethical Hacking & Cybersecurity  Softwarica × Coventry University*
*Revised Title: An adaptive human-risk intelligence dashboard with live threat-feed*
*integration and behavioural risk scoring for non-technical SME staff in Kathmandu Valley*
