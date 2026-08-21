# Chapter 02 - The Data Foundation

> *"Garbage in, garbage out"* - Every ML model is only as good as its data.

Before we touch any algorithms, we need to understand **what data exists**, **how it's structured**, and **how it flows** through the system.

---

## The Core Data Model: Attempts

The **Attempt** is the fundamental unit of data in AHRID. Every time a user answers a training question, one `Attempt` row is created.

### Schema (`backend/app/models/attempt.py`)

```python
class Attempt(db.Model):
    id            = uuid_pk()                    # Unique identifier
    user_id       = uuid_fk("users.id")          # Who answered
    scenario_id   = uuid_fk("scenarios.id")      # Which question
    answer_given  = db.Column(db.String(1))       # "A", "B", "C", or "D"
    is_correct    = db.Column(db.Boolean)         # Did they get it right?
    response_time_ms = db.Column(db.Integer)      # How fast they answered (ms)
    category      = db.Column(db.String(50))      # e.g., "phishing_email"
    difficulty    = db.Column(db.Integer)          # 1 (easy), 2 (medium), 3 (hard)
    session_id    = db.Column(Uuid)               # Groups attempts into sessions
    is_synthetic  = db.Column(db.Boolean)          # True = ML training data only
    created_at    = db.Column(db.DateTime)         # When it happened
```

### What Each Field Means for ML

| Field | ML Significance | Used By |
|-------|----------------|---------|
| `is_correct` | The most important signal - accuracy is the basis of risk scoring | Risk Scorer, RF, KMeans |
| `response_time_ms` | Behavioural proxy: fast + wrong = overconfident, fast + right = competent | RF, KMeans |
| `category` | Allows per-category accuracy calculation (8 categories) | RF (5 of 14 features), Risk Scorer |
| `difficulty` | Not directly used in ML features, but drives adaptive engine | Adaptive Engine |
| `session_id` | Groups attempts into sessions - used for session_consistency feature | RF, KMeans |
| `is_synthetic` | **Critical flag** - synthetic data trains ML but is excluded from risk scoring | Training pipeline |
| `created_at` | Time-based features: days_since_last_session, recency weighting | RF, Adaptive Engine |

---

## The 8 Security Categories

Every scenario (question) belongs to exactly one of these 8 categories:

```python
CATEGORIES = [
    "phishing_email",       # Recognising fraudulent emails
    "smishing",             # SMS-based phishing
    "vishing",              # Voice-based phishing
    "physical_security",    # Tailgating, clean desk, etc.
    "password_hygiene",     # Strong passwords, reuse, etc.
    "usb_baiting",          # Unknown USB drives
    "social_engineering",   # Pretexting, elicitation, etc.
    "data_handling",        # Data classification, sharing rules
]
```

**Why 8?** These map to the most common attack vectors against non-technical staff (per NIST/SANS frameworks). Your thesis specifically scopes to SME staff in Kathmandu Valley.

---

## Real Data vs. Synthetic Data

### The Problem
ML models need **lots** of labelled data to train well. A Random Forest with 4 classes (low/medium/high/critical) needs at minimum ~50-100 samples per class. But in a real deployment, you might only have 10-20 real users.

### The Solution: Synthetic Data

`seed_synthetic_ml_data.py` generates **1,050 synthetic users** across 5 risk profiles:

```python
PROFILES = [
    # (label,       base_accuracy, rt_correct_range, rt_wrong_range, n_users, attempts_range)
    ("critical",    0.15,          (1500, 3500),     (1200, 3000),   200,     (20, 35)),
    ("high",        0.35,          (2000, 5000),     (1500, 4000),   200,     (18, 30)),
    ("medium",      0.60,          (2500, 6000),     (3000, 7000),   250,     (15, 25)),
    ("low",         0.82,          (3000, 7000),     (4000, 10000),  250,     (15, 30)),
    ("very_low",    0.92,          (2500, 5500),     (5000, 12000),  150,     (20, 40)),
]
```

### How Synthetic Profiles Work

Let's trace through the `"critical"` profile:

1. **Base accuracy = 0.15** → These simulated users only get 15% of questions right
2. **Response time (correct): 1500-3500ms** → They answer fast even when right (guessing)
3. **Response time (wrong): 1200-3000ms** → They answer even faster when wrong (clicking without thinking)
4. **200 users** → Enough samples for the RF to learn this pattern
5. **20-35 attempts each** → Enough history to compute meaningful features

### Realism Mechanisms

The synthetic data isn't just random - it has realistic properties:

```python
# Per-user jitter: users within a tier aren't clones
PER_USER_ACCURACY_JITTER = 0.07  # ±7% accuracy variation

# Difficulty modifier: harder questions → lower accuracy
diff_modifier = {1: 0.10, 2: 0.0, 3: -0.15}.get(sc.difficulty, 0)

# Category variation: Gaussian noise per question
category_modifier = random.gauss(0, 0.08)

# Occasional overconfident fast answers
if not is_correct and random.random() < 0.15:
    rt = random.randint(1000, 2500)  # Very fast but wrong
```

### The `is_synthetic` Flag

This is **crucial** for data integrity:

```python
# In risk_scorer.py - real scoring EXCLUDES synthetic data:
rows = Attempt.query.filter_by(user_id=user_id, is_synthetic=False).all()

# In train_models.py - ML training INCLUDES all data (including synthetic):
rows = Attempt.query.filter_by(user_id=user_id).all()  # No is_synthetic filter
```

**Why?** The rule-based risk scorer shows a user their *real* performance. But the RF needs enough training data, so it uses everything.

---

## Data Flow: From Answer to Feature

```
User clicks "B"
        │
        ▼
┌─ Attempt Row ──────────────────────────────────────────┐
│ user_id:  abc-123                                       │
│ answer:   "B"                                           │
│ correct:  True  (scenario.correct_answer == "B")        │
│ time:     3200ms                                        │
│ category: "phishing_email"                              │
│ session:  sess-789                                      │
└─────────────────────────────────────────────────────────┘
        │
        ├──► Risk Scorer uses this to update
        │    phishing_email_score for user abc-123
        │
        ├──► When RF predicts, this attempt contributes to:
        │    - phishing_accuracy feature
        │    - overall_accuracy feature
        │    - avg_response_time_ms feature
        │    - fast_attempt_rate (3200ms > 4000ms threshold? No)
        │
        └──► When KMeans assigns, this attempt contributes to:
             - overall_accuracy feature
             - avg_response_time_ms feature
             - fast_attempt_rate feature
             - session_consistency (via session_id grouping)
```

---

## Understanding the User Model

The `User` model has ML-relevant fields:

```python
class User(db.Model):
    job_role = db.Column(db.String(50))          # Encoded as integer for RF
    cluster_label = db.Column(db.String(100))    # Updated by KMeans
    cluster_assigned_at = db.Column(db.DateTime)  # When cluster was assigned
```

### Job Role Encoding

The RF treats `job_role` as a categorical feature, encoded as integers:

```python
JOB_ROLE_ENCODING = {
    "receptionist": 0, "accountant": 1, "hr": 2, "it": 3,
    "finance": 4, "sales": 5, "management": 6, "other": 7,
}
```

**Why encode as integers?** Decision trees in Random Forests can split on numerical values (e.g., `job_role_encoded < 3.5`), which implicitly groups related roles. This is a simplified approach - more advanced methods use one-hot encoding, but for 8 categories with an ensemble model, ordinal encoding works well enough.

---

## Minimum Data Requirements

The system has several "guard rails" that prevent ML from running on insufficient data:

| Threshold | Value | Where | Why |
|-----------|-------|-------|-----|
| `MIN_ATTEMPTS_FOR_PREDICT` | 10 | RF prediction | Can't compute meaningful accuracy from <10 answers |
| `MIN_ATTEMPTS_FOR_CLUSTER` | 5 | KMeans assignment | Need some behaviour data for features |
| `MIN_ATTEMPTS_FOR_USER` | 10 | RF training | Each user in training set needs ≥10 attempts |
| `MIN_USERS_FOR_CLUSTERING` | 3 | KMeans training | Can't form 5 clusters from <3 data points |
| `MIN_TRAINING_SAMPLES` | 20 | Config | Overall minimum to even attempt training |
| `min_class_count >= 2` | 2 | SMOTE | SMOTE needs ≥2 samples per class |

These guard rails ensure the system **degrades gracefully** - if there's not enough data, it falls back to rule-based scoring instead of crashing.

---

## 🔬 Exercise

1. **Count your data:** Run this SQL against your SQLite database:
   ```sql
   SELECT COUNT(*) as total_attempts,
          COUNT(DISTINCT user_id) as unique_users,
          SUM(CASE WHEN is_synthetic = 1 THEN 1 ELSE 0 END) as synthetic,
          SUM(CASE WHEN is_synthetic = 0 THEN 1 ELSE 0 END) as real
   FROM attempts;
   ```

2. **Understand the distribution:** 
   ```sql
   SELECT category, 
          COUNT(*) as attempts,
          ROUND(AVG(is_correct) * 100, 1) as accuracy_pct,
          ROUND(AVG(response_time_ms)) as avg_rt_ms
   FROM attempts 
   WHERE is_synthetic = 0
   GROUP BY category;
   ```

3. **Think about it:** Why does the synthetic data generator use `random.seed(42)`? What would happen if it didn't?

---

> **Next:** [Chapter 03 - Risk Scoring: The Rule-Based Baseline →](./03_RISK_SCORING.md)
