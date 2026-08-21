# AHRIP - Adaptive Human Risk Intelligence Platform

## Complete System Report

---

## 1. System Overview

AHRIP is a full-stack web application that assesses and improves cybersecurity awareness within organisations. It combines a transparent, rule-based risk scorer with machine learning to predict risk levels, cluster users into behavioural archetypes, and explain every prediction in plain language.

### What It Does

1. **Trains employees** on cybersecurity through adaptive multiple-choice scenarios across 8 categories
2. **Scores risk** per user using a deterministic rule-based scorer (the system of record for live risk levels)
3. **Predicts risk** using a trained Random Forest classifier (14 behavioural features) as a secondary, explainable ML signal
4. **Clusters users** into 5 behavioural archetypes using K-Means (6 features)
5. **Explains predictions** using SHAP (TreeExplainer) so every ML output is human-readable
6. **Ingests real threats** from OSINT sources and auto-generates training scenarios from them
7. **Evaluates effectiveness** via pre/post awareness assessments (HAIS-Q) and System Usability Scale (SUS) surveys
8. **Decays mastery over time** so categories a user hasn't practised in weeks resurface for a refresher, instead of keeping a stale "mastered" badge forever

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Framer Motion, Zustand |
| Backend | Flask 3.1, SQLAlchemy 2.0, Flask-JWT-Extended, Flask-Bcrypt, Flask-Migrate (Alembic) |
| ML | scikit-learn (RandomForestClassifier, KMeans), SHAP, imbalanced-learn (SMOTE) |
| Database | PostgreSQL (Supabase, production) / SQLite (local dev) |
| Auth | JWT (15-min access, 30-day refresh), bcrypt (12 rounds) |
| Background | APScheduler (threat ingestion every 6h) |
| Hosting | Render (backend, free tier), Vercel (frontend), Supabase (managed Postgres, free tier) |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (Vercel)                │
│  Dashboard │ Training │ My Score │ Eval │ Admin │ Mgr     │
└───────────┬─────────────────────────────────────────────┘
            │ REST API (JSON, JWT bearer)
┌───────────▼─────────────────────────────────────────────┐
│                 Flask Backend (Render)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
│  │   Auth   │  │ Training │  │  Scores  │  │  Admin  │  │
│  │ (JWT)    │  │ (Adaptive│  │ (Risk +  │  │ (Users, │  │
│  │          │  │  Engine) │  │  SHAP)   │  │  Scenarios)│
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
│  │ Manager  │  │  Eval    │  │  Health  │  │ Notifs  │  │
│  │ (Team,   │  │ (HAIS-Q, │  │          │  │         │  │
│  │  Reports)│  │  SUS)    │  │          │  │         │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────────┐
│  │              ML Services Layer                          │
│  │  ┌────────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │  │ Risk Scorer│  │ RF Model │  │ KMeans Clusterer │    │
│  │  │ (Rule-based,│ │ (14 feat,│  │ (6 features,     │    │
│  │  │  source of │  │  200 est)│  │  5 clusters)     │    │
│  │  │  truth)    │  │          │  │                  │    │
│  │  └────────────┘  └──────────┘  └──────────────────┘    │
│  │  ┌────────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │  │ Adaptive   │  │ SHAP     │  │ Behavioral       │    │
│  │  │ Engine     │  │ Explainer│  │ Profiler         │    │
│  │  │ (+forgetting│ │          │  │                  │    │
│  │  │  curve)    │  │          │  │                  │    │
│  │  └────────────┘  └──────────┘  └──────────────────┘    │
│  └────────────────────────────────────────────────────────┘
│                                                            │
│  ┌────────────────────────────────────────────────────────┐
│  │              Data Pipeline                               │
│  │  Threat Ingestion → Classifier → Scenario Generator      │
│  └────────────────────────────────────────────────────────┘
└──────────────────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────┐
│           PostgreSQL (Supabase, production)                │
│  users │ scenarios │ attempts │ risk_scores │ clusters     │
│  awareness_assessments │ sus_responses │ threats           │
└─────────────────────────────────────────────────────────┘
```

**Why this split (rule-based scorer as source of truth, ML as a parallel signal):** a thesis/demo system needs every risk decision to be defensible and auditable. The composite risk score that drives notifications and dashboards comes from a deterministic formula (§3.4) - anyone can recompute it by hand from raw attempt data. The Random Forest and SHAP layers sit alongside it to demonstrate predictive ML and explainability, not to silently override a number nobody can audit.

---

## 3. ML Models - What, Why, How, Drawbacks, Future Work

### 3.1 Random Forest Classifier (Risk Prediction)

**What it is:** A `RandomForestClassifier` that predicts a user's risk level (`low` / `medium` / `high` / `critical`) from 14 behavioural features derived from their training history.

**Why a Random Forest specifically (vs. logistic regression, gradient boosting, neural nets, etc.):**
- The feature set mixes continuous (response time), ratio (per-category accuracy), count (sessions, attempts), and categorical (job role) data - trees split on raw values, so no scaling/normalisation is needed and mixed types aren't a problem.
- An ensemble of 200 trees averages out the noise of any single user's small attempt history, which matters when many users only have 10-40 attempts.
- `feature_importances_` and SHAP TreeExplainer give exact, fast explanations - this was a hard requirement, since an opaque score with no justification is not acceptable for a tool that flags employees as "high risk."
- `class_weight="balanced"` plus SMOTE oversampling (below) handle the fact that most users are *not* critical risk, so naive accuracy would be misleading without this.
- Trees are robust to outliers in the response-time feature (an accidental 5-minute idle tab doesn't blow up the whole model the way it would for a distance-based or gradient method).

**Model configuration:**
```python
RandomForestClassifier(
    n_estimators=200,       # 200 decision trees
    max_depth=None,         # unlimited depth
    random_state=42,        # reproducibility
    n_jobs=-1,              # parallel across all cores
    class_weight="balanced" # auto-weights by class frequency
)
```

**The 14 features:**

| # | Feature | What It Measures | Why It Matters |
|---|---------|-----------------|----------------|
| 1 | `avg_response_time_ms` | Mean time to answer | Slow = uncertain, fast = overconfident |
| 2 | `phishing_accuracy` | Accuracy on phishing_email category | Core phishing resilience |
| 3 | `smishing_accuracy` | Accuracy on smishing category | SMS phishing resistance |
| 4 | `social_engineering_accuracy` | Accuracy on social_engineering | Resistance to manipulation |
| 5 | `password_hygiene_accuracy` | Accuracy on password_hygiene | Password security knowledge |
| 6 | `physical_security_accuracy` | Accuracy on physical_security | Physical security awareness |
| 7 | `overall_accuracy` | Total correct / total attempts | General competence |
| 8 | `fast_attempt_rate` | Fraction answered in <4 seconds | Rushed/impulsive behaviour |
| 9 | `overconfident_rate` | Fraction fast (<2s) AND wrong | Overconfidence signal |
| 10 | `session_consistency` | Fraction of sessions matching modal length | Engagement consistency |
| 11 | `job_role_encoded` | Numeric encoding of job role (0-7) | Role-based risk differences |
| 12 | `total_sessions` | Count of distinct training sessions | Experience level |
| 13 | `days_since_last_session` | Days since most recent attempt | Recency / engagement decay |
| 14 | `attempts_count` | Total number of attempts | Sample size for scoring |

**Training pipeline:**
1. Eligible users: ≥10 attempts in the database
2. Labels come from the rule-based scorer, not from human annotation: composite score ≥80 → critical, ≥60 → high, ≥40 → medium, else low (this is intentional - the RF is trained to *approximate and generalise* the deterministic rule, not replace it)
3. 80/20 stratified train/test split
4. SMOTE oversampling on the training set only (never on test data, to avoid leakage) - balances all 4 classes to equal counts before fitting
5. 3-fold cross-validation with F1-macro scoring (macro, not weighted, because under-represented classes like "critical" matter most and weighted F1 would hide poor performance on them)
6. Metrics saved to `ml_models/rf_metrics.json` for the admin transparency page

**Inference:**
- Builds the same 14-feature vector for the requesting user
- Calls `model.predict_proba()` for class probabilities
- Returns predicted risk level + confidence + the top-3 SHAP risk factors and top-3 protective factors
- Minimum 10 attempts required, otherwise the RF prediction is withheld (avoids confidently wrong predictions on near-empty histories)

**Current model performance** (trained 2026-06-28, on 1,050 users - synthetic, see §4.3):

| Metric | Value |
|---|---|
| Test accuracy | 91.4% |
| F1-macro | 0.8878 |
| PR-AUC (macro) | 0.9166 |
| Cohen's Kappa | 0.8751 |
| Baseline F1 | 0.3653 |
| Gap over baseline | +0.5224 |
| CV F1-macro | 0.829 ± 0.010 |
| Training samples | 1,050 (840 train / 210 test) |
| SMOTE: classes balanced to | 402 each |
| Training scenarios | 450 hand-crafted, length-balanced |

The medium-risk class remains the hardest to separate - it sits between "clearly fine" (low) and "clearly bad" (high), so the model confuses it with both neighbours more than it confuses low with critical. This is expected and visible in the confusion matrix in the admin Evaluation page.

**Drawbacks of this approach:**
- **Labels are circular.** The RF is trained on labels produced by the rule-based scorer it's meant to complement, so it can never outperform the rule it was trained to imitate - it can only generalise it to noisier/incomplete histories. It cannot discover a genuinely new definition of "risk" the rule-based formula misses.
- **Synthetic-data dominance.** All 25,000+ attempts used for training/eval are synthetic, generated from hand-picked accuracy/response-time distributions (§4.3). The model has not seen real human behavioural noise (distractions, multi-tasking, genuine guessing patterns, language barriers, etc.).
- **No temporal validation.** The 80/20 split is random, not time-based - in production, you'd want to train on older data and test on newer data to catch concept drift (e.g., users getting better at recognising the *specific* phishing templates in this dataset rather than phishing in general).
- **Static job-role encoding.** `job_role_encoded` is a fixed integer mapping with no inherent ordering - tree splits on it are somewhat arbitrary; a one-hot or learned-embedding encoding might generalise better with more data.
- **No model versioning/rollback.** Retraining overwrites the previous `.pkl` artifact in place; there's no A/B comparison or automatic rollback if a retrain regresses.
- **No drift monitoring.** Nothing currently re-checks accuracy against newly labelled real attempts after deployment; degradation would only be caught manually.

**Future improvements:**
1. Collect a real-attempt-only holdout set once enough genuine users have trained, and report RF performance separately on synthetic vs. real data - this is the single most valuable next step for credibility.
2. Add time-based (not random) train/test splitting to detect concept drift.
3. Try gradient boosting (XGBoost/LightGBM) as a comparison model - likely modest accuracy gains, at the cost of needing SHAP's `TreeExplainer` (still compatible) but losing some of RF's built-in robustness to small data.
4. Automate retraining on a schedule (e.g., weekly via the existing APScheduler) once real-attempt volume justifies it, with metric-gated promotion (only swap the model if the new one's CV F1 doesn't regress).
5. Add calibration (e.g., `CalibratedClassifierCV`) so `predict_proba` outputs are trustworthy probabilities, not just ranking scores - useful if confidence is ever shown to end users as a literal percentage.

### 3.2 K-Means Clustering (User Archetypes)

**What it is:** A `KMeans` clustering algorithm that groups users into 5 behavioural archetypes based on a 6-feature behavioural vector, independent of any risk label.

**Why K-Means specifically:**
- The goal is descriptive segmentation for managers ("here are your 5 types of trainee"), not a precise predictive task - K-Means' simple, interpretable centroids fit that better than a denser model like DBSCAN or Gaussian Mixture, which would be harder to narrate as "archetypes" in a manager-facing UI.
- Fast, deterministic (fixed `random_state`), and cheap enough to re-run per training cycle on every user without a background job queue.
- 5 clusters maps cleanly onto a pre-defined taxonomy of trainee behaviour the UI already needed (Overconfident Clicker, Cautious Learner, etc.) - K-Means' requirement to pick `k` upfront is a non-issue here because we wanted a fixed, named set of archetypes anyway.

**Model configuration:**
```python
KMeans(
    n_clusters=min(5, max(2, n_users // 2)),  # adaptive for small cohorts
    random_state=42,
    n_init=10  # run 10 times, keep best inertia
)
```

**The 6 features:**

| # | Feature | What It Measures |
|---|---------|-----------------|
| 1 | `avg_response_time_ms` | Mean response time (winsorized - see below) |
| 2 | `overall_accuracy` | Correct / total attempts |
| 3 | `accuracy_variance` | Std dev of per-category accuracies (inconsistency) |
| 4 | `fast_attempt_rate` | Fraction with response_time < 4000ms |
| 5 | `total_sessions` | Distinct session count |
| 6 | `session_consistency` | Fraction of sessions matching modal length |

**Preprocessing:**
1. **Winsorization (95th-percentile clip) on `avg_response_time_ms` only**, applied identically at train time and inference time. This was added after discovering that K-Means (a distance-based algorithm) is extremely sensitive to outliers: a single real user with an extreme average response time (multiple minutes, likely from leaving a tab idle mid-question) was pulling an entire cluster centroid toward itself and creating a degenerate one-user cluster. Clipping the *clustering input* to the 95th percentile (while still storing and displaying the user's true, unclipped response time elsewhere in the UI) fixed this without discarding any user's real data.
2. **StandardScaler** (z-score normalisation) applied after the clip, so no single feature's raw scale (milliseconds vs. a 0-1 accuracy ratio) dominates the Euclidean distance K-Means uses internally.

**The 5 archetypes:**

| Cluster | Archetype | Behaviour | Intervention |
|---------|-----------|-----------|-------------|
| 0 | **Overconfident Clicker** | Fast but wrong, impulsive answers | Slowed-down practice, red-flag training |
| 1 | **Cautious Learner** | Takes time, mostly correct | Challenge scenarios |
| 2 | **Inconsistent Performer** | Mixed results, blind spots | Targeted category training |
| 3 | **Resilient Defender** | Fast, accurate, consistent | Advanced threats, peer mentoring |
| 4 | **Disengaged Completer** | Slow, inconsistent, few sessions | Shorter gamified sessions, manager check-in |

**Current model** (trained 2026-06-20, on 1,057 users with ≥5 attempts):

| Metric | Value |
|---|---|
| Users clustered | 1,057 |
| Silhouette score | 0.230 |
| Inertia | 2,547.0 |
| Cluster sizes | {0: 245, 1: 220, 2: 173, 3: 184, 4: 235} |

**Drawbacks:**
- **Silhouette score of 0.23 is weak-to-moderate** (0 = overlapping clusters, 1 = perfectly separated) - the 5 archetypes are a useful narrative, but the underlying behavioural data doesn't cleanly separate into 5 distinct groups; in reality, trainee behaviour is more of a continuum than discrete types.
- **`k=5` is fixed by product design, not chosen by the data** (e.g. via elbow method or silhouette sweep). A data-driven `k` might be 3 or 4 and fit better, at the cost of not matching the pre-written archetype copy in the UI.
- **Same synthetic-data dominance issue as the RF** - archetypes are defined almost entirely by synthetic behavioural profiles, not observed real trainees.
- **Cluster *labels* (which cluster ID = "Overconfident Clicker") are assigned by inspecting centroids once after training, not algorithmically** - if a retrain shuffles which cluster ID ends up with which centroid shape, the hardcoded ID→archetype mapping in the UI could silently mislabel users until someone notices and re-maps it.
- **No silhouette-per-user**, only a global average - a manager can't currently tell whether a specific user is a confident or borderline member of their assigned archetype.

**Future improvements:**
1. Run a silhouette/elbow sweep over `k=2..8` on real (not synthetic) data once volume allows, to validate whether 5 is still the right number of archetypes.
2. Assign archetype labels programmatically by centroid characteristics (e.g. "highest avg accuracy + lowest response time" → Resilient Defender) instead of a hand-maintained ID mapping, so relabelling survives a retrain automatically.
3. Surface per-user distance-to-centroid in the UI as a soft "archetype confidence," especially useful for users near a cluster boundary.
4. Consider Gaussian Mixture Models for soft/probabilistic cluster membership instead of K-Means' hard assignment, if "this user is 60% Cautious Learner, 40% Resilient Defender" turns out to be more actionable for managers than a single label.

### 3.3 SHAP Explainer (Model Transparency)

**What it is:** Uses `shap.TreeExplainer` to explain individual Random Forest predictions feature-by-feature.

**Why SHAP specifically (vs. simpler approaches like raw feature importances):**
- Global `feature_importances_` tell you what matters *on average across all users* - they cannot tell an individual user *why their specific prediction* came out the way it did. SHAP can.
- It's game-theoretically grounded (Shapley values): each feature's contribution is fairly attributed such that they sum exactly to the difference between the prediction and the average prediction - not an approximation, for tree ensembles specifically (`TreeExplainer` computes exact values in polynomial time, unlike model-agnostic SHAP which samples).
- It naturally separates risk-increasing factors from risk-reducing (protective) factors per user, which maps directly onto the "top 3 concerns / top 3 strengths" UI pattern used in the My Score page.
- This was treated as close to a requirement: a tool that tells an employee or manager "you are high risk" with zero justification is not something people will trust or act on.

**How it works:**
1. Takes the same 14-feature vector used by the RF for that user
2. Creates `TreeExplainer(model)` once (cached, reused across requests)
3. Calls `explainer.shap_values(x, check_additivity=False)`
4. Each feature gets a signed SHAP value: positive = pushes risk up, negative = pushes risk down
5. Returns the top 3 risk-increasing and top 3 risk-reducing features, mapped to human-readable labels (table below)

**Human-readable labels:**

| Feature | Label shown to user |
|---------|---------|
| `avg_response_time_ms` | "How quickly you answer questions" |
| `phishing_accuracy` | "Phishing email detection accuracy" |
| `smishing_accuracy` | "SMS phishing detection accuracy" |
| `social_engineering_accuracy` | "Social engineering resistance" |
| `password_hygiene_accuracy` | "Password hygiene knowledge" |
| `physical_security_accuracy` | "Physical security awareness" |
| `overall_accuracy` | "Overall quiz accuracy" |
| `fast_attempt_rate` | "Proportion of rushed answers" |
| `overconfident_rate` | "Proportion of overconfident answers" |
| `session_consistency` | "Consistency across training sessions" |
| `job_role_encoded` | "Job role" |
| `total_sessions` | "Total training sessions completed" |
| `days_since_last_session` | "Days since you last trained" |
| `attempts_count` | "Total training attempts" |

**Drawbacks:**
- SHAP explains the *Random Forest's* prediction, not the rule-based scorer that actually drives notifications/escalations - a sharp user could notice the two numbers (RF risk level vs. rule-based risk level) occasionally disagree, since they're separate computations on overlapping but not identical inputs.
- `check_additivity=False` is set to avoid floating-point assertion errors with SMOTE-trained forests - this silences a *correctness check*, not just a warning; in rare edge cases the displayed SHAP values could fail to sum exactly to the prediction delta without anyone noticing.
- SHAP values are computed fresh per-request (not cached), which is the dominant per-request CPU cost in the My Score page - fine at current scale, but would need caching if usage grew substantially.

**Future improvements:**
1. Cache SHAP explanations per user, invalidated only when the user's underlying attempt data or the model itself changes - would meaningfully speed up the My Score endpoint.
2. Surface a SHAP *waterfall* (cumulative contribution chart) instead of just top-3/top-3 lists, for users who want the full picture.
3. Periodically verify additivity offline (outside the request path) to catch the edge case above without paying its cost on every request.

### 3.4 Rule-Based Risk Scorer (Source of Truth)

**What it is:** The deterministic mechanism that computes the composite and per-category risk scores actually used for risk levels, notifications, and escalations everywhere in the product.

**How it works:**
1. Fetches all *non-synthetic* attempts for the user (synthetic attempts never affect a real user's live score)
2. Groups them by the 8 cybersecurity categories
3. Per-category risk: `(1 - accuracy) × 100` - 0 means always correct, 100 means always wrong
4. Composite score: mean of category scores for categories the user has actually attempted (categories with zero attempts don't drag the average down)
5. Risk level thresholds: ≥80 critical, ≥60 high, ≥40 medium, else low

**Why rule-based + ML, not just one or the other:**
- The rule is fully auditable - any stakeholder can verify a user's risk level by hand from raw attempt data, with no model in the loop. This matters enormously for trust and for a thesis evaluation.
- ML alone, with no rule, would mean the "ground truth" risk label is whatever the model says, with no independent way to check whether the model is *right* - there's no oracle to validate against.
- Used together: the rule provides the trustworthy number; the RF + SHAP layer demonstrates that a learned model can approximate that number from raw behavioural signals and explain itself - i.e., the ML proves *predictability and explainability*, while the rule provides *ground truth and auditability*.

### 3.5 Adaptive Engine (Session Selection + Forgetting Curve)

**What it is:** Selects which training scenarios a user sees next, based on per-category mastery, recency, spaced repetition, and (as of this update) a time-based forgetting curve.

**Why adaptive, not random/fixed scenario order:**
- Maximises learning efficiency by spending more session time on weak categories
- Avoids boredom by not over-serving already-mastered content
- Spaced repetition reinforces learning at intervals tied to how risky the user currently is
- Difficulty auto-adjusts so neither bored experts nor overwhelmed beginners get a flat, one-size session

**How mastery is computed:**
```python
def calculate_mastery(attempts):  # attempts[0] = most recent
    weights = [DECAY_FACTOR**i for i in range(len(attempts))]
    weighted = sum(int(a.is_correct) * w for a, w in zip(attempts, weights))
    return weighted / sum(weights)
```
This is a recency-weighted accuracy: the most recent attempt counts full weight, and each attempt further back counts `0.85ˣ` as much. This means a user's mastery score reflects *how they've been doing lately*, not a flat lifetime average - get 3 wrong in a row after a long correct streak, and mastery drops quickly rather than being diluted by history.

**The gap this update fixes - time-based forgetting:**

The recency-weighted formula above only re-weights *existing* attempts; it does nothing if a user simply stops practising a category. A user who scored 90% mastery in `password_hygiene` two months ago and never touched it again would still show 90% mastery forever, because there are no new attempts to push the old ones down the decay curve. The adaptive engine would then never resurface that category (the "weakest category gets 50% of the session" rule only looks at the *lowest current mastery score*, and a frozen 90% looks fine even though the user has almost certainly forgotten some of it).

**Fix - `_apply_forgetting_curve` in `app/services/adaptive_engine.py`:**
```python
MASTERY_HALFLIFE_DAYS = 21.0   # ~3 weeks: knowledge halfway decayed
FORGETTING_FLOOR = 0.30        # decays toward "needs a refresher," not toward 0.5

def _apply_forgetting_curve(mastery, last_attempt_at):
    if last_attempt_at is None:
        return mastery
    days_idle = (datetime.utcnow() - last_attempt_at).total_seconds() / 86400
    if days_idle <= 0:
        return mastery
    retained = 0.5 ** (days_idle / MASTERY_HALFLIFE_DAYS)
    return FORGETTING_FLOOR + (mastery - FORGETTING_FLOOR) * retained
```
This decays mastery exponentially toward a floor of 0.30 (not toward a neutral 0.5), because unpracticed security awareness *erodes* - it doesn't drift to "uncertain," it drifts toward "needs review." A category sitting at 0.90 mastery decays to ~0.60 after one half-life (21 days idle) and approaches the 0.30 floor after long neglect; a category that was already weak (e.g. 0.20) barely moves, since it's already near the floor - neglect doesn't artificially *improve* a weak score. The category dict returned by `get_user_profile()` also now reports `days_since_practice`, so the staleness reason is visible, not just its effect.

Because `weakest_category` selection (and therefore 50% of every session) is computed directly from this decayed mastery value, a long-neglected category naturally rises back to the top of what a user is served next - with zero changes needed to the selection logic itself.

**Session composition (unchanged by this update):**
1. Compute per-category mastery (with the forgetting curve applied)
2. Identify weakest and strongest categories
3. Session distribution: 50% weakest category, 25% other categories, 25% challenge (one difficulty level up)
4. Spaced repetition: correctly answered scenarios are excluded for 12-72 hours, scaled by the user's current risk level (the riskier the user, the sooner a correct answer can reappear, to reinforce learning faster)
5. Difficulty progression: mastery ≥80% → promote one level, ≤40% → demote one level
6. One slot reserved for a recent threat-feed-derived scenario (ingested in the last 48 hours), when available

**Constants:**
- `PROMOTION_THRESHOLD = 0.80`, `DEMOTION_THRESHOLD = 0.40`
- `MIN_ATTEMPTS_FOR_DECISION = 5`, `RECENCY_WINDOW = 10`, `DECAY_FACTOR = 0.85`
- `MASTERY_HALFLIFE_DAYS = 21.0`, `FORGETTING_FLOOR = 0.30` *(new)*
- `SESSION_SIZE = 20` (default)

**Drawbacks of the adaptive engine overall:**
- `MASTERY_HALFLIFE_DAYS = 21` and `FORGETTING_FLOOR = 0.30` are reasonable defaults, not empirically validated against this user base's actual retention curve - real spaced-repetition research (e.g. SuperMemo/Anki) tunes half-life per item difficulty and per individual, which this simplified single-constant model doesn't attempt.
- The forgetting curve currently only feeds the *backend* selection logic; it isn't yet surfaced as a "needs refresher" indicator anywhere in the frontend UI, so users have no direct visibility into *why* an old topic reappeared.
- Spaced-repetition exclusion windows (12-72h) and the forgetting half-life (21 days) are independent constants tuned by intuition, not jointly optimised - they could in principle work against each other for an edge-case user.

**Future improvements:**
1. Surface `days_since_practice` and a "refresher due" badge per category in the employee dashboard/My Score page, so the *reason* a topic reappears is visible to the user, not just its effect.
2. Replace the single global half-life with a per-category (or per-user) half-life learned from actual re-test performance, once enough real longitudinal data exists.
3. A/B test `MASTERY_HALFLIFE_DAYS` values against measured retention (re-test accuracy after N days) instead of using a literature-informed guess.

---

## 4. Data Pipeline

### 4.1 Threat Ingestion

**Sources:** PhishStats, AlienVault OTX

**Pipeline stages:**
1. **FETCH** - Pull raw URLs from the 4 sources
2. **VALIDATE** - Structural URL checks (regex + hostname)
3. **DEDUPLICATE** - Collapse against the current batch and the last 48h of DB rows
4. **CLASSIFY** - Detect lure type (credential_harvest, invoice_fraud, delivery_notification, it_support, ceo_impersonation, prize_scam) and map it to an AHRIP training category
5. **SANITISE** - Defang URLs before they're ever displayed to a trainee (so the scenario itself can't be clicked as a live link)
6. **GENERATE** - Template-based MCQ scenario creation from the classified threat
7. **PERSIST** - Bulk insert `ThreatFeedEntry` + `Scenario` rows (max 20 per run)

Runs every 6 hours via APScheduler in production, or can be manually triggered from the admin Threats page.

### 4.2 Scenario Generation

- 6 lure-type templates, each with title, prompt, correct answer, 3 distractors, explanation, and red flags
- Correct answer is placed in a uniformly random slot (A/B/C/D) to defeat "the longest/most-detailed option is usually right" guessing bias
- Option-length balancing pads short distractors so answer length alone isn't a tell
- HMAC-signed presentation tokens prevent a user from learning "position 3 is always correct" across repeated attempts at the same scenario

### 4.3 Synthetic Data Generation

**1,050 synthetic users** across 5 risk profiles, each with per-user accuracy jitter (`±0.07` Gaussian) so users within a tier aren't identical clones of the profile mean:

| Profile | Users | Base Accuracy | Attempts/User |
|---------|-------|--------------|---------------|
| Critical | 200 | 15% | 20-35 |
| High | 200 | 35% | 18-30 |
| Medium | 250 | 60% | 15-25 |
| Low | 250 | 82% | 15-30 |
| Very Low | 150 | 92% | 20-40 |

All synthetic attempts are marked `is_synthetic=True` and are **excluded from live rule-based risk scoring** (§3.4) - they exist purely to bootstrap ML training (§3.1, §3.2) with enough volume and class diversity to produce a stable model. Each synthetic user also gets a generated pre/post HAIS-Q assessment and SUS response, so the admin Evaluation page has meaningful demo data.

**Why synthetic data was necessary, and why that's also the system's biggest current weakness:** a brand-new platform has no real user history to train on, and a Random Forest needs hundreds of labelled examples per class to be stable - the system genuinely cannot bootstrap from a handful of real users. The honest trade-off is that the RF and KMeans models currently describe *synthetic, hand-specified* behavioural profiles extremely well (88.7% accuracy, §3.1) rather than necessarily describing real human behaviour - that gap only closes as real usage accumulates and the synthetic:real ratio shifts.

---

## 5. Database Schema

### Core Tables (live production counts, Supabase)

| Table | Rows | Purpose |
|-------|------|---------|
| `users` | 1,062 | User accounts (1 admin, 1 manager, ~10 demo employees, 1,050 synthetic) |
| `scenarios` | 501 | Training scenarios across 8 categories |
| `attempts` | 25,494 | User answers (79 real, 25,415 synthetic) |
| `risk_scores` | 6 | One per real user with scored attempts, composite + 8 category scores |
| `awareness_assessments` | 2,108 | Pre+post HAIS-Q assessments |
| `sus_responses` | 1,052 | System Usability Scale responses |
| `threat_feed_entries` | 0 (live) | Ingested phishing URLs (populates once scheduler/admin trigger runs in prod) |
| `user_clusters` | 0 (live) | Cluster assignment history (populated by clustering job, not yet run in prod) |
| `notifications` | 4 | Training assignments + risk escalations |
| `audit_logs` | 0 (live) | Admin action audit trail |

Scenario distribution by category: phishing_email 70, social_engineering 63, password_hygiene 63, usb_baiting 62, physical_security 61, data_handling 61, vishing 61, smishing 60.

Note: the RF/KMeans models themselves were trained locally against a snapshot of 1,056-1,057 synthetic users (§3.1, §3.2) before the artifacts were committed and shipped with the deploy - production's live `users`/`attempts` counts (above) reflect the same synthetic seed run, but `user_clusters` is empty because the clustering *assignment* job (which writes that table) hasn't been triggered against production yet, distinct from training the KMeans model itself.

### Key Relationships

```
User (1) ──→ (N) Attempt
User (1) ──→ (1) RiskScore
User (1) ──→ (N) UserCluster
User (1) ──→ (N) AwarenessAssessment
User (1) ──→ (N) SUSResponse
Scenario (1) ──→ (N) Attempt
Scenario (1) ──→ (1) ThreatFeedEntry
```

---

## 6. API Design

### Endpoints Summary

| Blueprint | Prefix | Endpoints | Purpose |
|-----------|--------|-----------|---------|
| auth | `/api/v1/auth` | 10 | Registration, login, JWT, password reset |
| training | `/api/v1/training` | 10 | Adaptive sessions, history, categories, config |
| scores | `/api/v1/scores` | 3 | Risk scores, history, cluster archetype |
| manager | `/api/v1/manager` | 6 | Team dashboard, member profiles, training assignment |
| admin | `/api/v1/admin` | 16 | User/scenario/threat CRUD, stats, background jobs |
| evaluation | `/api/v1/eval` | 9 | HAIS-Q awareness, SUS, RF metrics, transparency |
| notifications | `/api/v1/notifications` | 5 | CRUD with unread polling |
| health | `/api/v1` | 1 | DB + ML model health check |

**Total: 60 endpoints**

### Authentication

- JWT access tokens (15-minute expiry), refresh tokens (30-day expiry)
- Token blocklist for logout
- Account lockout: 5 failed attempts → 15-minute lock
- Role-based access: employee, manager, admin

### Security Features

- bcrypt password hashing (12 rounds)
- HMAC-signed presentation tokens for MCQ shuffling
- Rate limiting (200/minute default, stricter on sensitive endpoints)
- Input sanitisation (bleach for HTML, Marshmallow for validation)
- CORS restricted to the deployed frontend origin (exact-match - see §9, this caused a real production incident from a trailing-slash mismatch)
- No account enumeration on forgot-password

---

## 7. Frontend Design

### Pages (18 total)

**Auth (4):** Login, Register, Forgot Password, Reset Password

**Employee (6):** Dashboard, Training (adaptive session flow), My Score (risk profile, SHAP, RF prediction, archetype, 8-week trend), History, Profile, Evaluation (HAIS-Q + SUS)

**Manager (4):** Dashboard, Team, Clusters (5 archetype cards), Reports (CSV export)

**Admin (6):** Dashboard, Users, Scenarios, Threats, Password Resets, Evaluation (RF metrics, awareness uplift, SUS summary)

### Design Principles

- Dark-only theme via CSS custom properties
- Role-aware sidebar navigation
- Responsive: mobile hamburger menu, desktop persistent sidebar
- 5-step keyboard-navigable onboarding tour for first-time users
- Real-time notification polling (60-second interval)
- Zustand state management with localStorage persistence

---

## 8. Evaluation Framework

### HAIS-Q Awareness Assessment

- 7-item Likert scale (1-5) measuring cybersecurity awareness
- Pre-training and post-training phases
- Score: mean of 7 responses / 5 × 100
- Uplift measured via paired t-test and Cohen's d

### SUS (System Usability Scale)

- Standard 10-question SUS questionnaire, 0-100 score using the standard SUS formula
- Grading: ≥85 Excellent, ≥72 Good, ≥52 OK, ≥38 Poor, else Awful

### ML Model Evaluation

- Random Forest: accuracy, F1 (macro/weighted), 3-fold CV, full confusion matrix, class distribution
- KMeans: silhouette score, inertia, cluster sizes
- Baseline comparison available in the admin Evaluation page: rule-based scorer vs. RF agreement rate

### Current Live Data Snapshot

| Metric | Value |
|--------|-------|
| Total users | 1,062 |
| Total attempts | 25,494 (79 real, 25,415 synthetic) |
| Total scenarios | 501 |
| Awareness assessments | 2,108 |
| SUS responses | 1,052 |
| RF test accuracy | 88.7% |
| RF CV F1-macro | 0.815 ± 0.034 |
| RF critical-class recall | 0.852 |
| KMeans silhouette | 0.230 |
| KMeans clusters | 5 |

---

## 9. Deployment

| Component | Host | Notes |
|---|---|---|
| Backend | Render (free tier) | Flask + gunicorn, auto-deploys on push to `main`, runs `flask db upgrade` on every boot before starting workers |
| Frontend | Vercel | Static SPA build, rewrites all routes to `index.html` |
| Database | Supabase (Postgres, free tier, `ap-south-1`) | Connection pooled via PgBouncer on port 6543 |
| Keep-warm | GitHub Actions (`*/10 * * * *` cron) | Pings the Render root endpoint every ~10 minutes so the free-tier instance doesn't spin down after 15 minutes idle (cold starts otherwise add 30-60s+ to the first request) |

**Notable production incidents resolved during deployment** (kept here because they're instructive, not just historical trivia):
- **Empty schema in production:** `backend/migrations/versions/` had no actual migration files committed, so `flask db upgrade` only ever created the bookkeeping `alembic_version` table - no application tables existed, causing every DB-touching endpoint to 500. Fixed by generating a genuine initial migration (`flask db migrate` run against the actually-empty production DB, since the local dev SQLite already had all tables via the dev-only `db.create_all()` fallback and produced "no changes detected") and committing it.
- **CORS "Network Error" with a working backend:** the browser reported a generic network error even though the backend was reachable and returning `200`. Root cause: `ALLOWED_ORIGINS` on Render was set to `https://ahrid.vercel.app/` (trailing slash) while the browser's `Origin` header sends `https://ahrid.vercel.app` (no trailing slash) - Flask-CORS does an exact string match, so the preflight silently came back with no `Access-Control-Allow-Origin` header at all.
- **Stale deploy referencing a migration revision that doesn't exist:** a Render auto-deploy ran against a commit that predated the migration file being pushed, producing `Can't locate revision identified by '<hash>'` and crash-looping before gunicorn ever bound a port (manifesting as the whole app being unreachable, not a clean error page). Fixed with a manual "Deploy latest commit."

---

## 10. Current State

### What Works

- Complete adaptive training pipeline across 501 scenarios in 8 categories, with time-based forgetting curve for mastery
- Rule-based risk scoring with per-category breakdown, fully auditable
- Random Forest classifier trained on 1,056 users (88.7% accuracy, 0.815 CV F1-macro)
- K-Means clustering with 5 behavioural archetypes (0.230 silhouette)
- SHAP explainability for every RF risk prediction
- Threat ingestion from OSINT sources, every 6 hours
- HAIS-Q pre/post awareness assessments and SUS usability surveys
- Admin panel with live ML model metrics and transparency page
- Manager dashboard with team oversight
- Role-based access control (employee/manager/admin), JWT auth with refresh
- Live production deployment (Render + Vercel + Supabase) with automated keep-warm

### Known Limitations

- Synthetic data dominates the training/eval set (99.7% of attempts) - real-world validation at scale is still pending
- RF labels are derived from the same rule-based scorer it's meant to complement, so it cannot exceed that rule's definition of "risk," only generalise it
- KMeans silhouette (0.230) indicates the 5 archetypes don't cleanly separate in the underlying data - useful narrative, imperfect statistical grounding
- No automated retraining pipeline or model versioning/rollback - retrains overwrite the previous artifact in place
- No drift monitoring against real attempts post-deployment
- Mastery forgetting curve constants (`21`-day half-life, `0.30` floor) are reasoned defaults, not empirically validated against this user base's actual retention
- Forgetting-curve staleness (`days_since_practice`) is computed and used by the selection engine but not yet surfaced in the frontend UI
- `user_clusters` and `threat_feed_entries` tables are empty in production - the model artifacts are trained and shipped, but the corresponding assignment/ingestion jobs haven't been run against the live database yet

### Recommended Next Steps (Priority Order)

1. Surface mastery staleness ("refresher due") in the employee UI - lowest effort, directly improves training relevance
2. Trigger the clustering-assignment and threat-ingestion jobs against production so `user_clusters`/`threat_feed_entries` aren't empty
3. Once real-attempt volume grows, evaluate RF/KMeans performance on real-only data and report it separately from the synthetic-blended numbers above
4. Add scheduled, metric-gated model retraining
5. Add time-based train/test splitting for the RF to catch concept drift before it does for real

---

## 11. File Structure Summary

```
AHRIP/
├── backend/
│   ├── app/
│   │   ├── api/          # 8 blueprint files (60 endpoints)
│   │   ├── models/       # 13 ORM models
│   │   ├── services/     # 12 service modules
│   │   ├── utils/        # security, validators, decorators
│   │   ├── config.py
│   │   ├── extensions.py
│   │   └── __init__.py
│   ├── migrations/       # Alembic migration scripts
│   ├── ml_models/        # Persisted model artifacts + metrics JSON
│   ├── train_models.py   # Training orchestrator
│   ├── seed_*.py         # Data seeding scripts
│   ├── requirements.txt
│   └── wsgi.py
├── frontend/
│   ├── src/
│   │   ├── api/          # 8 API modules
│   │   ├── components/   # 25+ components (layout, shared, ui, training)
│   │   ├── pages/        # 18 pages (auth, employee, manager, admin)
│   │   ├── hooks/        # 5 custom hooks
│   │   ├── store/        # Zustand auth store
│   │   ├── lib/          # categories, utils, routing
│   │   ├── types/        # TypeScript interfaces
│   │   ├── App.tsx       # Root routing
│   │   └── index.css     # Tailwind + dark theme
│   ├── package.json
│   └── vite.config.ts
├── .github/workflows/    # Render keep-warm cron
└── REPORT.md             # This file
```
