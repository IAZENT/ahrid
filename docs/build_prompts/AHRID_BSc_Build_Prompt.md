# AHRIP - BSc Build Prompt
**Adaptive Human-Risk Intelligence Dashboard (Scoped for Final-Year BSc)**

> Give this entire document to Claude (or any AI coding assistant) at the start of a new session. It is a complete, self-contained specification of what to build, what already exists, what to strip, and what to add.

---

## 0. Context & Ground Rules

You are helping a BSc final-year student refactor and complete a cybersecurity research project called **AHRIP** (Adaptive Human-Risk Intelligence Dashboard). The student over-built the original system; this prompt scopes it back to match their thesis title exactly:

> *"An adaptive human-risk intelligence dashboard with live threat-feed integration and behavioural risk scoring for non-technical SME staff in Kathmandu Valley, fusing OSINT threat APIs with Random Forest and clustering on user telemetry, assessed on prediction accuracy, awareness uplift, and usability, bounded by surveillance limits and risk-score transparency."*

The existing codebase is a **Flask 3 / Python 3.13 / SQLite backend + React 18 / TypeScript / TailwindCSS v3 frontend** with scikit-learn ML models. It already works. Your job is to **strip what doesn't belong, add what's missing, and produce a clean, thesis-defensible system**.

**Non-negotiable rules:**
- Never add LLM calls (no Gemini, no Ollama, no OpenAI). The title says nothing about generative AI.
- Never rebuild gamification. XP, badges, streaks, leaderboard - all gone.
- Keep every change minimal and reversible. Prefer deleting code over commenting it out.
- Write code a BSc examiner can follow: clear variable names, short functions, inline comments on non-obvious logic.
- All new Python packages must be pip-installable with `--break-system-packages`.

---

## 1. What the Thesis Actually Requires (Mapping)

| Thesis element | What to build/keep |
|---|---|
| "Adaptive dashboard" | Mastery-weighted scenario selection, difficulty auto-progression |
| "Live threat-feed integration" | OSINT pipeline: AlienVault OTX + Phishing.Database + Phishing.Database + Phishing.Database |
| "Behavioural risk scoring" | 8-category scores + composite + risk_level from Attempt telemetry |
| "Random Forest" | RF classifier on 14-feature behavioural vector - keep as-is |
| "Clustering on user telemetry" | KMeans (k=5) with 6 behavioural features - keep as-is |
| "Prediction accuracy" | RF F1, Precision-Recall AUC, Cohen's Kappa vs rule-based baseline |
| "Awareness uplift" | HAIS-Q style pre-test / post-test score delta (7-item questionnaire) |
| "Usability" | 10-item SUS form, score ≥ 68 target |
| "Surveillance limits" | Aggregate-only manager view; employees see their own score only |
| "Risk-score transparency" | SHAP values per user, plain-English feature explanation on dashboard |

---

## 2. The Final Architecture (What to Keep)

### 2.1 Backend - keep these, nothing else

**Flask blueprints to keep:**
- `app/api/auth.py` - login, register, refresh, logout, /me, change-password
- `app/api/training.py` - session start, answer, summary, history, categories
- `app/api/scores.py` - /me, /me/history, /me/cluster, /me/badges (strip badge routes - keep only score + cluster)
- `app/api/manager.py` - dashboard, team list, team profile (aggregate only, no raw attempts)
- `app/api/admin.py` - users CRUD, scenarios CRUD, threats panel, retrain-models, stats
- `app/api/notifications.py` - trimmed to 2 types only (see §4)

**Flask blueprints to DELETE entirely:**
- `app/api/gamification.py` - XP, badges, leaderboard, daily challenge
- `app/api/news.py` / any CyberNews routes
- `app/api/breaches.py` / any FamousBreach routes
- Any invite blueprint (`/invites`)
- Any profile-change-request routes from auth or admin
- Any LLM / AI-generation routes (`/generate-scenarios`, `/ollama/*`, `/ai-generation/*`)

**Services to keep:**
- `adaptive_engine.py` - mastery + difficulty selection (strip Thompson Sampler call, strip gamification calls)
- `risk_scorer.py` - 8-category + composite scores
- `random_forest_model.py` - RF predictor
- `kmeans_clustering.py` - KMeans + archetypes
- `threat_ingestion.py` - OSINT pipeline (4 sources)
- `telemetry_service.py` - UserBehaviorEvent capture (response_time, accuracy)
- `notifications.py` - trimmed

**Services to DELETE entirely:**
- `gamification_engine.py`
- `llm_orchestrator.py`, `gemini_generator.py`, `ollama_fallback.py`
- `answer_evaluator.py` (free-text LLM grader)
- `thompson_sampler.py`
- `peer_signal_service.py`
- `sentiment_analyzer.py` - optionally keep `response_time_ms` signal but remove VADER

**New services to ADD:**
- `shap_explainer.py` - see §5
- `evaluation.py` - HAIS-Q + SUS + RF metrics endpoint - see §6

### 2.2 Data Models - trim from 17 to 10

**Keep these 10 models:**

| Model | Notes |
|---|---|
| `User` | Strip: `coaching_note`, `coaching_hints`, `consent_timestamp`. Keep: `cluster_label`, `job_role`, `department`, `role`. |
| `Organisation` | Keep ONE row only (no multi-tenancy). Remove org_id foreign keys from API responses - keep them internally for DB integrity. |
| `Scenario` | Strip: `model_answer`, `key_points`, `accepted_answers`, `min_words`, `max_words` (free-text rubric fields). Keep question_type but only allow `mcq`, `true_false`, `identify_threat`. |
| `Attempt` | Strip: `answer_text`, `evaluation_score`, `evaluation_label`, `evaluation_feedback`, `sentiment_label`, `vader_compound`. Keep: `is_correct`, `response_time_ms`, `session_id`. |
| `RiskScore` | Keep as-is - 8 category scores + composite + RF prediction. |
| `ThreatFeedEntry` | Keep as-is. |
| `UserCluster` | Keep only the most recent cluster row per user. No history needed. |
| `TokenBlocklist` | Keep - JWT security. |
| `AuditLog` | Keep - required for ethical governance chapter. |
| `Notification` | Keep - trim to 2 types (see §4). |

**DELETE these 7 models entirely:**
- `UserGamification`
- `CyberNews`
- `FamousBreach`
- `ProfileChangeRequest`
- `SystemCounter`
- `Invite`
- `UserBehaviorEvent` - optional: keep if telemetry detail is needed, but it's safe to drop and rely on Attempt.response_time_ms

**Run a new Alembic migration after model changes.** Do not break existing dev SQLite - generate a migration that drops the dead tables cleanly.

### 2.3 Background Jobs - keep 2 of 7

**Keep:**
- `threat_ingestion` - every 6 hours
- `risk_recalc` - every 1 hour

**DELETE from scheduler:**
- `llm_scenario_generation`
- `cyber_news_ingestion`
- `weekly_xp_reset`
- `rf_retrain` → replace with manual admin trigger only (already exists: `POST /admin/retrain-models`)
- `kmeans_recluster` → replace with manual admin trigger (add `POST /admin/recluster` if not present)

### 2.4 Frontend - pages to keep and delete

**Keep these pages:**
- `/login`, `/register` (public)
- `/app/dashboard` (employee) - strip XP bar, streak counter, gamification widgets
- `/app/training` - keep MCQ/true_false/identify_threat only; remove FreeTextInput, EvaluationFeedback
- `/app/my-score` - keep RadarChart, RfPredictionCard, cluster archetype card, 8-week LineChart; REMOVE XP bar, badges section
- `/app/history` - keep as-is
- `/app/profile` - keep; strip "Request change" buttons (profile-change-request UI)
- `/app/manager/dashboard` - keep KPI tiles, RiskHeatmap, ThreatFeed; strip ClusterPie gamification elements
- `/app/manager/team` - keep; strip archetype filter if it depends on gamification
- `/app/admin/*` - keep users, scenarios, threats panels; DELETE ai-generation, invites, profile-change-requests pages
- NEW: `/app/evaluation` (employee) - HAIS-Q pre/post + SUS form - see §6
- NEW: `/app/my-score` addition - SHAP explanation panel - see §5

**DELETE these pages/routes entirely:**
- `/app/badges`
- `/app/leaderboard`
- `/app/my-insights` (peer signal)
- `/app/breach-chronicle`
- `/app/admin/ai-generation`
- `/app/admin/invites`
- `/app/admin/profile-change-requests`
- `/design-system` (can keep locally but not in thesis demo)

**Strip from every remaining page:**
- `<XPBar>` component
- `<LevelUpModal>` component
- `<StreakCounter>` component
- `<NotificationBell>` gamification event types (level_up, badge_earned, streak_milestone)
- Any import of `gamification.ts` API client
- Leaderboard anonymity logic (no longer needed)

---

## 3. Adaptive Engine - What to Simplify

The existing `adaptive_engine.py` calls Thompson Sampler and emits gamification events. Strip both:

```python
# REMOVE this import and all calls to it:
# from app.services.thompson_sampler import ThompsonSampler

# In select_next_session(), replace thompson_sampler.select() with:
# simple weighted selection - lowest mastery categories first
sorted_cats = sorted(mastery.items(), key=lambda x: x[1])
weakest = [c for c, _ in sorted_cats[:3]]

# In process_attempt(), REMOVE these lines:
# add_xp(...)
# check_and_award_badges(...)
# emit_level_up(...)
# emit_badge_earned(...)
# emit_streak_milestone(...)

# KEEP:
# risk_score recalculation
# difficulty promotion/demotion
# emit_risk_escalation() if risk crosses a threshold
```

Difficulty progression stays: promote at ≥80% accuracy, demote at ≤40%, clamp 1-3.

Sentiment analysis: remove VADER entirely. Keep `response_time_ms` in Attempt as a behavioural proxy - it already feeds into the RF feature vector as `avg_response_time`.

---

## 4. Notifications - Trim to 2 Types

In `notifications.py`, keep only:

```python
NOTIFICATION_TYPES = {
    "risk_escalation": "Your risk score has increased - review your training.",
    "training_assigned": "You have been assigned a new training session."
}
```

Delete helpers: `emit_level_up`, `emit_badge_earned`, `emit_streak_milestone`, `emit_announcement`.

Keep: `emit_risk_escalation`, `emit_training_assigned`, `broadcast_to_org`.

In `process_attempt()` in adaptive engine: emit `risk_escalation` when `risk_level` moves from `medium→high` or `high→critical`.

---

## 5. NEW - SHAP Explainability Layer

This is the most important addition. Your proposal explicitly requires it (RQ2 - transparency), and it differentiates AHRIP from opaque tools like KnowBe4.

### 5.1 Install

```bash
pip install shap --break-system-packages
```

### 5.2 Create `backend/app/services/shap_explainer.py`

```python
"""
SHAP explainability for the Random Forest risk classifier.
Produces per-user plain-language feature explanations.
Called after RF prediction; results stored in RiskScore.shap_summary (JSON).
"""
import shap
import numpy as np
import json
from app.services.random_forest_model import load_rf_model

# Human-readable names for each of the 14 RF features (same order as rf_features.json)
FEATURE_LABELS = {
    "avg_response_time":      "How quickly you answer questions",
    "acc_phishing_email":     "Phishing email detection accuracy",
    "acc_smishing":           "SMS phishing detection accuracy",
    "acc_vishing":            "Voice phishing detection accuracy",
    "acc_physical_security":  "Physical security awareness",
    "acc_password_hygiene":   "Password hygiene knowledge",
    "acc_usb_baiting":        "USB baiting awareness",
    "acc_social_engineering": "Social engineering resistance",
    "acc_data_handling":      "Data handling practices",
    "overall_accuracy":       "Overall quiz accuracy",
    "rushed_rate":            "Proportion of rushed answers",
    "overconfident_rate":     "Proportion of overconfident answers",
    "streak_consistency":     "Training consistency",
    "total_sessions":         "Number of training sessions completed",
}


def explain_prediction(feature_vector: np.ndarray, feature_names: list[str]) -> dict:
    """
    Returns a dict with:
      - shap_values: list of {feature, label, value, direction} sorted by |value|
      - top_risk_factors: top 3 plain-English sentences driving the risk score
      - top_protective_factors: top 3 things reducing risk
    """
    rf, _, label_encoder = load_rf_model()
    if rf is None:
        return {"error": "RF model not loaded"}

    explainer = shap.TreeExplainer(rf)
    # feature_vector shape: (1, n_features)
    shap_values = explainer.shap_values(feature_vector)

    # shap_values is list[n_classes] of arrays shape (1, n_features)
    # Use the predicted class index
    predicted_class_idx = rf.predict(feature_vector)[0]
    # map numeric to index
    class_shap = shap_values[predicted_class_idx][0]  # shape (n_features,)

    results = []
    for i, fname in enumerate(feature_names):
        results.append({
            "feature": fname,
            "label": FEATURE_LABELS.get(fname, fname),
            "shap_value": round(float(class_shap[i]), 4),
            "direction": "increases_risk" if class_shap[i] > 0 else "reduces_risk",
        })

    results.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

    risk_factors = [
        f"{r['label']} is contributing to your elevated risk."
        for r in results if r["direction"] == "increases_risk"
    ][:3]

    protective_factors = [
        f"{r['label']} is helping keep your risk low."
        for r in results if r["direction"] == "reduces_risk"
    ][:3]

    return {
        "shap_values": results,
        "top_risk_factors": risk_factors,
        "top_protective_factors": protective_factors,
    }
```

### 5.3 Add `shap_summary` column to RiskScore model

```python
# In backend/app/models/risk_score.py - add one column:
shap_summary = db.Column(db.JSON, nullable=True)
# Stores the output of explain_prediction() as JSON
```

Generate an Alembic migration for this column.

### 5.4 Call SHAP after RF prediction

In `risk_scorer.py`, after writing the RiskScore row, add:

```python
from app.services.shap_explainer import explain_prediction
import numpy as np

feature_vector = np.array([...features...]).reshape(1, -1)
shap_result = explain_prediction(feature_vector, feature_names)
risk_score_row.shap_summary = shap_result
db.session.commit()
```

### 5.5 Expose SHAP via scores API

In `app/api/scores.py`, in the `GET /scores/me` response, add:

```python
"shap_explanation": risk_score.shap_summary  # already a dict
```

### 5.6 Display SHAP on the My Score page (frontend)

Add a new `<ShapExplanationPanel>` component to `/app/my-score`:

```tsx
// frontend/src/components/ShapExplanationPanel.tsx
// Props: { topRiskFactors: string[], topProtectiveFactors: string[] }

// Render two sections:
// 🔴 "What's raising your risk" - list of top_risk_factors
// 🟢 "What's protecting you" - list of top_protective_factors
// Add a small disclaimer: "This explanation is based on your training behaviour only
// and is not used for any employment decision."
```

This panel directly satisfies RQ2 (transparency) and H2 (risk-score opacity harm mitigation).

---

## 6. NEW - Evaluation Module (Thesis Assessment Requirements)

Your three evaluation metrics (prediction accuracy, awareness uplift, SUS) need dedicated endpoints and a UI. Without these, you cannot answer RQ1/H1.

### 6.1 HAIS-Q Style Awareness Questionnaire

Create a 7-item pre/post awareness instrument. Store responses in a new lightweight model:

```python
# backend/app/models/awareness_assessment.py
class AwarenessAssessment(db.Model):
    __tablename__ = "awareness_assessments"
    id = db.Column(UUID, primary_key=True, default=uuid_pk)
    user_id = db.Column(UUID, db.ForeignKey("users.id"), nullable=False)
    phase = db.Column(db.String(10), nullable=False)  # "pre" or "post"
    responses = db.Column(db.JSON, nullable=False)     # {q1: 1-5, q2: 1-5, ...}
    score = db.Column(db.Float, nullable=False)         # mean of 7 items (1-5 scale)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**The 7 questions** (5-point Likert: 1=Strongly Disagree → 5=Strongly Agree):

1. I know how to identify a phishing email.
2. I always check the sender's email address before clicking links.
3. I understand the risks of connecting unknown USB devices.
4. I know what to do if I receive a suspicious phone call asking for my password.
5. I am confident I would report a suspected cyber incident to my manager.
6. I understand why using strong, unique passwords for each account is important.
7. I can recognise signs that a website may be fake or malicious.

**Scoring:** `score = mean(responses) / 5 * 100` → gives 0-100.

### 6.2 SUS Questionnaire

Store SUS responses in a new model:

```python
# backend/app/models/sus_response.py
class SUSResponse(db.Model):
    __tablename__ = "sus_responses"
    id = db.Column(UUID, primary_key=True, default=uuid_pk)
    user_id = db.Column(UUID, db.ForeignKey("users.id"), nullable=False)
    responses = db.Column(db.JSON, nullable=False)  # {q1: 1-5, ..., q10: 1-5}
    sus_score = db.Column(db.Float, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**SUS scoring (standard formula):**
```python
def calculate_sus(responses: dict) -> float:
    # Odd questions (1,3,5,7,9): score - 1
    # Even questions (2,4,6,8,10): 5 - score
    odd = sum(responses[f"q{i}"] - 1 for i in [1, 3, 5, 7, 9])
    even = sum(5 - responses[f"q{i}"] for i in [2, 4, 6, 8, 10])
    return (odd + even) * 2.5  # 0-100
```

**The 10 standard SUS questions** (use verbatim - it's a validated scale):
1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

### 6.3 RF Metrics Endpoint

Add `GET /api/v1/eval/rf-metrics` (admin only):

```python
# Loads rf_features.json + test split, runs RF, returns:
{
  "f1_weighted": 0.87,
  "precision_recall_auc": 0.91,
  "cohens_kappa": 0.82,
  "baseline_f1": 0.61,       # rule-based: high if overall_accuracy < 40%
  "improvement_pp": 26,       # percentage points above baseline
  "n_test_samples": 120,
  "class_distribution": {"low": 60, "medium": 40, "high": 20}
}
```

**Rule-based baseline** for comparison:
```python
def rule_based_predict(features: dict) -> str:
    acc = features["overall_accuracy"]
    if acc < 0.40: return "high"
    elif acc < 0.70: return "medium"
    else: return "low"
```

### 6.4 Awareness Uplift Endpoint

Add `GET /api/v1/eval/awareness-uplift` (admin only):

```python
# Returns per-user pre/post delta and cohort summary:
{
  "n_participants": 28,
  "mean_pre_score": 54.2,
  "mean_post_score": 71.8,
  "mean_delta": 17.6,
  "cohens_d": 0.73,       # effect size (target ≥ 0.5)
  "p_value": 0.003,       # paired t-test
  "participants": [
    {"user_id": "...", "pre": 48, "post": 69, "delta": 21},
    ...
  ]
}
```

Use `scipy.stats.ttest_rel` for the paired t-test.

### 6.5 Evaluation API Blueprint

Create `backend/app/api/evaluation.py`:

```python
from flask import Blueprint
bp = Blueprint("evaluation", __name__, url_prefix="/api/v1/eval")

# POST /eval/awareness - submit pre or post assessment (employee, authenticated)
# GET  /eval/awareness/me - get own assessment status (pre done? post done?)
# POST /eval/sus - submit SUS form (employee, after using the system)
# GET  /eval/rf-metrics - admin only, RF vs baseline stats
# GET  /eval/awareness-uplift - admin only, cohort pre/post summary
# GET  /eval/sus-summary - admin only, mean SUS + grade + distribution
```

### 6.6 Frontend Evaluation Page

Create `/app/evaluation` (employee route):

**Step 1 - Pre-assessment** (shown once, before first training session):
- 7 HAIS-Q style questions on Likert scale
- "Start Training" button appears only after submission

**Step 2 - Post-assessment** (shown after ≥3 training sessions complete):
- Same 7 questions
- Immediately followed by 10 SUS questions

**Step 3 - Confirmation screen:**
- "Thank you. Your responses help evaluate the system's effectiveness."
- Shows own pre/post delta if both are complete

**Admin Evaluation Panel** - add a tab to `/app/admin` dashboard:
- RF Metrics card: F1, PR-AUC, Cohen's Kappa vs baseline, % improvement
- Awareness Uplift card: mean delta, Cohen's d, p-value, participant count
- SUS Summary card: mean score, grade label (Excellent/Good/OK/Poor), bar chart

---

## 7. SHAP + Ethical Transparency - Connecting to RQ2

The thesis RQ2 asks whether technical transparency alone is sufficient, or whether governance is also needed. Your system must demonstrate both:

### 7.1 Technical transparency (already built via §5):
- SHAP panel on My Score page
- Disclaimer text on every risk score display: *"This score reflects your training responses only and is not used for employment or access decisions."*
- Manager dashboard shows only **aggregate** team risk - no individual raw scores visible to managers (only the employee can see their own)

### 7.2 Governance transparency (add to admin panel):
Add a "Transparency Policy" section visible to all users (employee + manager):

```
AHRIP Transparency Notice
- What data is collected: your quiz responses and response times during training sessions
- How risk scores are calculated: a machine learning model trained on quiz performance patterns
- Who can see your score: only you (employees) and anonymised aggregates (managers)
- How to query or dispute your score: contact your administrator
- Data retention: all personal data deleted [X weeks] after the study ends
```

This text should be stored as a config string (not hardcoded) so the admin can update it. Add `GET /api/v1/transparency-policy` (public endpoint, no auth required).

---

## 8. OSINT Sources - Reconcile Proposal vs Existing Build

Your thesis proposal mentions VirusTotal, AbuseIPDB, AlienVault OTX, and GreyNoise. Your existing build has Phishing.Database and AlienVault OTX.

**Decision: keep the existing 4 sources** (they work and are coded). In your thesis writing, explain that:
- Phishing.Database and Phishing.Database serve the same function as VirusTotal's URL-reputation component
- Phishing.Database provides similar signal to GreyNoise (internet-scale threat scanning)
- AlienVault OTX covers the MITRE ATT&CK TTP mapping mentioned in the proposal

Update your proposal's tools section accordingly - or add a footnote. Do not rewrite the entire OSINT pipeline.

If you want to add AbuseIPDB as a 5th source (for IP reputation, which is different from URL phishing), here is the integration pattern to follow in `threat_ingestion.py`:

```python
# AbuseIPDB - IP reputation, not URL phishing
# Use only for enriching existing ThreatFeedEntry records with IP confidence scores
# API: GET https://api.abuseipdb.com/api/v2/check?ipAddress=X
# Header: Key: ABUSEIPDB_API_KEY
# Returns: data.abuseConfidenceScore (0-100)
# Only call this if a ThreatFeedEntry's URL resolves to a known-bad IP
```

---

## 9. SMOTE - Add to Training Pipeline

Your proposal mentions SMOTE for class imbalance. Add it to `train_models.py`:

```bash
pip install imbalanced-learn --break-system-packages
```

```python
# In train_models.py, before fitting the RF:
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42, k_neighbors=min(5, min(class_counts.values()) - 1))
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# Then train on balanced data:
rf.fit(X_train_balanced, y_train_balanced)
```

Log class distribution before and after SMOTE so you can report it in your methodology chapter.

---

## 10. Database Migration Plan

After all model changes, run these steps in order:

```bash
cd backend

# 1. Remove dead model imports from app/__init__.py and any blueprints
# 2. Delete the model files for dropped models
# 3. Generate migration
flask db migrate -m "bsc_scope_downgrade_strip_gamification_llm_invites"

# 4. Review the generated migration - it should:
#    - DROP TABLE user_gamification
#    - DROP TABLE cyber_news
#    - DROP TABLE famous_breaches
#    - DROP TABLE profile_change_requests
#    - DROP TABLE system_counters
#    - DROP TABLE invites
#    - ADD COLUMN risk_scores.shap_summary JSON
#    - DROP COLUMN users.coaching_note
#    - DROP COLUMN users.coaching_hints
#    - DROP COLUMN users.consent_timestamp
#    - DROP COLUMN attempts.answer_text
#    - DROP COLUMN attempts.evaluation_score
#    - DROP COLUMN attempts.evaluation_label
#    - DROP COLUMN attempts.evaluation_feedback
#    - DROP COLUMN attempts.sentiment_label
#    - DROP COLUMN attempts.vader_compound
#    CREATE TABLE awareness_assessments
#    CREATE TABLE sus_responses

# 5. Apply
flask db upgrade

# 6. Re-seed
python seed.py
python seed_ml_data.py
python train_models.py
```

---

## 11. Seed Data for Evaluation Testing

Add a new seed script `seed_eval_data.py` that creates:
- 5 demo employees (receptionist, accountant, hr, it, finance roles)
- Pre-assessment responses for 3 of them (simulate "before training")
- 10+ Attempt records per user (simulate training sessions)
- Post-assessment responses for 3 of them (simulate "after training")
- 2 SUS responses

This lets the admin evaluation panel show real data during your thesis demo.

---

## 12. Updated `bootstrap.sh`

After all changes, update `bootstrap.sh` to:

```bash
#!/bin/bash
set -e
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt --break-system-packages
flask db upgrade
python seed.py
python seed_ml_data.py
python seed_eval_data.py
python train_models.py
echo "AHRIP ready. Run: python wsgi.py"
```

Remove any references to:
- `seed_breaches.py`
- `seed_free_text.py`
- Ollama setup
- Gemini key setup

---

## 13. Acceptance Criteria (How to Know You're Done)

### Backend
- [ ] `pytest` passes with 0 failures on the remaining tests (gamification, LLM, free-text grader tests deleted)
- [ ] `GET /api/v1/scores/me` returns `shap_explanation` with `top_risk_factors` and `top_protective_factors`
- [ ] `GET /api/v1/eval/rf-metrics` returns F1, PR-AUC, Cohen's Kappa, and baseline comparison
- [ ] `GET /api/v1/eval/awareness-uplift` returns mean delta and p-value
- [ ] `GET /api/v1/eval/sus-summary` returns mean SUS score
- [ ] `GET /api/v1/transparency-policy` returns policy text (no auth required)
- [ ] No import of `gamification_engine`, `llm_orchestrator`, `thompson_sampler`, `sentiment_analyzer`, `peer_signal_service` anywhere in the codebase
- [ ] Scheduler runs exactly 2 jobs: `threat_ingestion` and `risk_recalc`

### Frontend
- [ ] No XPBar, LevelUpModal, StreakCounter in any page
- [ ] My Score page shows SHAP explanation panel with plain-English factors
- [ ] Evaluation page shows pre-assessment → training → post-assessment → SUS flow
- [ ] Admin dashboard has Evaluation tab with RF metrics, awareness uplift, SUS summary
- [ ] Manager dashboard shows only aggregate team scores (no individual raw scores)
- [ ] Transparency policy visible on profile page or dedicated `/transparency` route

### Thesis alignment
- [ ] System can produce a screenshot of SHAP explanations → answers RQ2
- [ ] Admin eval panel shows RF vs baseline comparison → answers H1 (prediction accuracy)
- [ ] Admin eval panel shows pre/post delta + p-value → answers H1 (awareness uplift)
- [ ] Admin eval panel shows SUS score ≥ 68 → answers H1 (usability)
- [ ] Transparency notice is visible to employees → answers H2

---

## 14. What NOT to Build (Repeat for Clarity)

If something is not in this document, do not build it. Specifically:

- **No LLM integration** of any kind - not for scenario generation, not for grading, not for feedback
- **No gamification** - XP, badges, levels, streaks, leaderboard are permanently removed
- **No invite system** - seed users directly in `seed.py`
- **No multi-tenancy expansion** - one org, hardcoded in seed, never exposed in UI
- **No cyber news feed** - RSS ingestion is gone
- **No breach chronicle** - `seed_breaches.py` deleted
- **No profile change request workflow** - admin changes user fields directly
- **No SMTP / email** - already absent, keep it that way
- **No Docker setup** - local SQLite is fine for BSc demo; mention containerisation as future work in thesis
- **No peer benchmarking** - peer_signal_service is gone; MyInsights page is gone

---

## 15. Thesis Chapter Mapping

Use this table to explain your system in your dissertation:

| Chapter | System component | Key evidence |
|---|---|---|
| Ch2 Literature | PMT, Prospect Theory, TAM | Proposal §Theories section |
| Ch3 Methodology | Agile sprints, mixed-methods eval | Proposal §Methodology |
| Ch4 System Design | OSINT pipeline → RF → KMeans → SHAP → Dashboard | Architecture diagram |
| Ch4 Technical | RF 14-feature vector, SMOTE, KMeans k=5 | `train_models.py`, `random_forest_model.py` |
| Ch5 Evaluation | RF vs baseline (F1/AUC/Kappa), HAIS-Q pre/post, SUS | Admin eval panel screenshots |
| Ch5 Ethics | SHAP transparency, aggregate-only manager view, policy notice | SHAP panel screenshot + transparency policy text |
| Ch6 Discussion | Awareness uplift effect size, SUS grade, surveillance limits | Cohen's d, p-value, SUS ≥ 68 |
| Ch7 Conclusion | Limitations: single org, synthetic telemetry, BSc-scale sample | Honest acknowledgement |

---

*End of build prompt. Start a fresh session, paste this document, and say: "Begin with Step 1: run the migration plan in §10 and confirm the database schema is clean."*
