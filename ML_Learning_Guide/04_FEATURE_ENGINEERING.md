# Chapter 04 - Feature Engineering Deep-Dive

> *"Features are more important than algorithms."* - Every ML practitioner, ever.
>
> This chapter is the **most important** for understanding your project's ML.

---

## What Is Feature Engineering?

Feature engineering is the process of transforming raw data (individual attempt rows) into **meaningful numerical signals** that an ML model can learn from.

Think of it like this: the raw data says *"User X answered question Y with 'B' in 3200ms"*. Feature engineering transforms that into *"User X has 72% accuracy in phishing, responds in an average of 4100ms, and answers too fast 23% of the time."*

---

## Random Forest Features (14 Total)

The RF classifier uses **14 features** per user. Let's go through every single one.

### Feature Vector Construction (`random_forest_model.py`)

```python
FEATURE_NAMES = [
    "avg_response_time_ms",           # 1
    "phishing_accuracy",              # 2
    "smishing_accuracy",              # 3
    "social_engineering_accuracy",    # 4
    "password_hygiene_accuracy",      # 5
    "physical_security_accuracy",     # 6
    "overall_accuracy",               # 7
    "fast_attempt_rate",              # 8
    "overconfident_rate",             # 9
    "session_consistency",            # 10
    "job_role_encoded",               # 11
    "total_sessions",                 # 12
    "days_since_last_session",        # 13
    "attempts_count",                 # 14
]
```

---

### Feature 1: `avg_response_time_ms`

**What it measures:** How quickly the user responds to questions, on average.

```python
response_times = [a.response_time_ms for a in attempts if a.response_time_ms]
avg_rt = float(np.mean(response_times)) if response_times else 0.0
```

**Why it matters:**
- Very fast answers (< 2s) suggest guessing or not reading the question
- Very slow answers (> 15s) suggest uncertainty or distraction
- Moderate times (4-8s) suggest careful reading

**Range:** 0 to ~20,000ms typically

---

### Features 2-6: Per-Category Accuracies

Five of the eight categories are explicitly tracked as features:

```python
def _category_accuracy(attempts, category):
    cat = [a for a in attempts if a.category == category]
    if not cat:
        return 0.0
    return sum(1 for a in cat if a.is_correct) / len(cat)
```

| Feature | Category | What Low Values Mean |
|---------|----------|---------------------|
| `phishing_accuracy` | phishing_email | Can't recognise fraudulent emails |
| `smishing_accuracy` | smishing | Falls for SMS scams |
| `social_engineering_accuracy` | social_engineering | Susceptible to manipulation |
| `password_hygiene_accuracy` | password_hygiene | Poor password practices |
| `physical_security_accuracy` | physical_security | Doesn't notice physical threats |

**Range:** 0.0 (always wrong) to 1.0 (always right)

**Why only 5 of 8?** The remaining 3 categories (vishing, usb_baiting, data_handling) are covered by `overall_accuracy`. Including all 8 would create redundancy (multicollinearity), and these 5 were chosen as the most discriminative.

---

### Feature 7: `overall_accuracy`

```python
overall_acc = sum(1 for a in attempts if a.is_correct) / len(attempts)
```

**What it measures:** The user's accuracy across ALL categories combined.

**Why include both overall AND per-category?** 
- Per-category tells the model *where* the user struggles
- Overall tells the model the *general competence level*
- A user might have 90% phishing accuracy but 20% physical security - the overall score (55%) captures the mix

---

### Feature 8: `fast_attempt_rate` 🔑

This is a **behavioural proxy** - a creative way to extract meaningful signals from response time.

```python
FAST_RESPONSE_MS = 4000  # Under 4 seconds = "fast"

fast_rate = (
    sum(1 for a in attempts 
        if a.response_time_ms and a.response_time_ms < FAST_RESPONSE_MS)
    / len(attempts)
)
```

**What it measures:** The proportion of questions answered in under 4 seconds.

**Why it matters:** Security awareness questions require reading a scenario (often a fake email). Answering in < 4s means the user likely didn't read it carefully. In real life, this translates to clicking phishing links without checking.

**Range:** 0.0 (never rushes) to 1.0 (always rushes)

**Example:**
- User with 40 attempts, 15 answered in < 4s → fast_rate = 15/40 = 0.375
- This means 37.5% of their answers are rushed

---

### Feature 9: `overconfident_rate` 🔑

This is the most **novel** behavioural feature in your system.

```python
OVERCONFIDENT_MS = 2000  # Under 2 seconds = "very fast"

overconfident_rate = (
    sum(1 for a in attempts
        if a.response_time_ms 
        and a.response_time_ms < OVERCONFIDENT_MS 
        and not a.is_correct)          # Fast AND wrong
    / len(attempts)
)
```

**What it measures:** How often the user answers **very quickly** but gets it **wrong**.

**The psychology:** An overconfident person thinks they know the answer immediately. They don't pause to verify. In cybersecurity, this is the "I know what I'm doing" person who clicks the phishing link because they're confident it's safe.

```
                    Speed
                Fast (<2s)    Slow (>2s)
              ┌────────────┬────────────┐
    Correct   │ Competent  │ Careful    │
              │ (good)     │ (good)     │
              ├────────────┼────────────┤
    Wrong     │ OVER-      │ Struggling │
              │ CONFIDENT  │ (expected) │
              │ (dangerous)│            │
              └────────────┴────────────┘
```

**Range:** 0.0 to 1.0 (typically < 0.3)

---

### Feature 10: `session_consistency`

```python
if total_sessions:
    rows = (
        db.session.query(Attempt.session_id, func.count(Attempt.id))
        .filter(Attempt.user_id == user_id)
        .group_by(Attempt.session_id)
        .all()
    )
    sizes = [int(c) for _, c in rows]
    modal = max(set(sizes), key=sizes.count)
    same = sum(1 for s in sizes if s == modal)
    session_consistency = same / len(sizes) if sizes else 0.0
```

**What it measures:** How consistently the user completes sessions of the same length.

**How it works:**
1. Group all attempts by `session_id`
2. Count how many attempts in each session
3. Find the **mode** (most common session size)
4. Calculate what fraction of sessions match the mode

**Example:**
- Sessions: [5, 5, 5, 3, 5, 5] → mode = 5, 5 out of 6 match → consistency = 5/6 = 0.833
- Sessions: [3, 7, 2, 5, 1, 4] → mode = varies, low match → consistency ≈ 0.167

**Why it matters:** Consistent session completion suggests engaged, disciplined training. Wildly varying session lengths suggest distraction or disengagement.

**Range:** 0.0 (every session is different length) to 1.0 (all sessions identical length)

---

### Feature 11: `job_role_encoded`

```python
JOB_ROLE_ENCODING = {
    "receptionist": 0, "accountant": 1, "hr": 2, "it": 3,
    "finance": 4, "sales": 5, "management": 6, "other": 7,
}

job_role_encoded = float(JOB_ROLE_ENCODING.get(job_role, 7))
```

**What it measures:** The user's job function, encoded as an integer.

**Why include it?** Different roles face different threats:
- Receptionists are targeted by physical social engineering
- Accountants face invoice fraud
- IT staff face credential harvesting

The RF can learn that certain roles are naturally higher-risk for certain attack types.

---

### Feature 12: `total_sessions`

```python
total_sessions = (
    db.session.query(func.count(func.distinct(Attempt.session_id)))
    .filter(Attempt.user_id == user_id)
    .scalar() or 0
)
```

**What it measures:** How many training sessions the user has completed.

**Why it matters:** More sessions = more practice = generally lower risk. But the RF can also learn exceptions (e.g., lots of sessions but still high risk = the training isn't working).

---

### Feature 13: `days_since_last_session`

```python
last_session_at = max(a.created_at for a in attempts)
days_since = max(0, (datetime.utcnow() - last_session_at).days)
```

**What it measures:** How many days ago the user last trained.

**Why it matters:** Security awareness decays over time. A user who trained 90 days ago is rustier than one who trained yesterday. This captures the **recency** dimension.

---

### Feature 14: `attempts_count`

```python
attempts_count = float(len(attempts))
```

**What it measures:** Total number of questions ever answered.

**Why it matters:** Combined with accuracy, this tells the model about **confidence** in the estimate. 95% accuracy over 100 questions is more reliable than 95% over 10 questions.

---

## K-Means Features (6 Total)

The clustering model uses a **different, smaller** feature set:

```python
FEATURE_NAMES = [
    "avg_response_time_ms",   # Same as RF
    "overall_accuracy",       # Same as RF
    "accuracy_variance",      # NEW - unique to KMeans
    "fast_attempt_rate",      # Same as RF
    "total_sessions",         # Same as RF
    "session_consistency",    # Same as RF
]
```

### Why Different Features?

| Concern | RF (14 features) | KMeans (6 features) |
|---------|-----------------|-------------------|
| **Goal** | Predict a specific label | Discover natural groups |
| **Per-category accuracy** | Yes (5 categories) | No - uses variance instead |
| **Job role** | Yes | No - grouping should be behavioural, not demographic |
| **Days since last** | Yes | No - clustering captures behaviour patterns, not recency |
| **Feature count** | More features = more discriminative power | Fewer features = cleaner clusters (curse of dimensionality) |

### The Unique KMeans Feature: `accuracy_variance`

```python
def _per_category_accuracy(attempts):
    by_cat = {}
    for a in attempts:
        by_cat.setdefault(a.category, []).append(bool(a.is_correct))
    return [sum(vals) / len(vals) for vals in by_cat.values() if vals]

per_cat = _per_category_accuracy(attempts)
accuracy_variance = float(np.std(per_cat)) if len(per_cat) > 1 else 0.0
```

**What it measures:** How much a user's accuracy varies **between** categories.

**Example:**
- User A: phishing=90%, smishing=85%, social_eng=80% → variance ≈ 0.04 (consistent)
- User B: phishing=95%, smishing=20%, social_eng=60% → variance ≈ 0.31 (inconsistent)

**Why it matters for clustering:** This single feature captures the "Inconsistent Performer" archetype - someone who's strong in some areas but dangerously weak in others.

---

## Feature Scaling

### RF: No Scaling Needed ✅

Random Forests are **scale-invariant** - they split on thresholds within each feature independently, so a feature in milliseconds (0-20000) and one in percentages (0-1) don't interfere with each other.

### KMeans: StandardScaler Required ⚠️

K-Means uses **Euclidean distance** to measure similarity between data points. Without scaling, a feature in milliseconds would dominate the distance calculation over a feature in the 0-1 range.

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

`StandardScaler` transforms each feature to have **mean = 0** and **standard deviation = 1**:

```
scaled_value = (original_value - mean) / std_dev
```

**Example for avg_response_time_ms:**
- Mean = 5000ms, StdDev = 2000ms
- A user with 3000ms → scaled = (3000 - 5000) / 2000 = -1.0 (1 std below average)
- A user with 9000ms → scaled = (9000 - 5000) / 2000 = +2.0 (2 std above average)

The scaler is **saved with the model** so the same transformation is applied during prediction:

```python
bundle = {
    "scaler": scaler,      # Saved!
    "model": kmeans,
    "rt_clip": rt_clip,     # Winsorization threshold
}
joblib.dump(bundle, out_path)
```

---

## Winsorization (Response Time Clipping)

A special pre-processing step for KMeans:

```python
RESPONSE_TIME_CLIP_PERCENTILE = 95

rt_clip = float(np.percentile(X[:, 0], RESPONSE_TIME_CLIP_PERCENTILE))
X_clustering = X.copy()
X_clustering[:, 0] = np.clip(X_clustering[:, 0], None, rt_clip)
```

**What this does:** Caps the response time at the 95th percentile before clustering.

**Why:** If one user has avg_response_time = 120,000ms (2 minutes - they went AFK), that extreme value would pull them into their own cluster, wasting one of the 5 available clusters on a single outlier.

**Example:**
- 95th percentile = 12,000ms
- User with 120,000ms → clipped to 12,000ms for clustering purposes
- The display value stays at 120,000ms - only the clustering input is modified

---

## Putting It All Together

Here's the complete feature vector for a hypothetical user:

```
User: Sita, receptionist, 45 attempts across 8 sessions

RF Feature Vector (14 features):
┌─────────────────────────────┬──────────┐
│ avg_response_time_ms        │  4,200.0 │  ← Takes time to read
│ phishing_accuracy           │    0.85  │  ← Good at phishing
│ smishing_accuracy           │    0.42  │  ← Weak at SMS scams
│ social_engineering_accuracy │    0.60  │  ← Moderate
│ password_hygiene_accuracy   │    0.90  │  ← Strong
│ physical_security_accuracy  │    0.75  │  ← Good
│ overall_accuracy            │    0.70  │  ← Blended
│ fast_attempt_rate           │    0.22  │  ← Sometimes rushes
│ overconfident_rate          │    0.09  │  ← Rarely overconfident
│ session_consistency         │    0.75  │  ← Fairly consistent
│ job_role_encoded            │    0.00  │  ← receptionist = 0
│ total_sessions              │    8.00  │  ← 8 sessions done
│ days_since_last_session     │    3.00  │  ← Trained 3 days ago
│ attempts_count              │   45.00  │  ← 45 total questions
└─────────────────────────────┴──────────┘

KMeans Feature Vector (6 features):
┌─────────────────────────────┬──────────┐
│ avg_response_time_ms        │  4,200.0 │
│ overall_accuracy            │    0.70  │
│ accuracy_variance           │    0.17  │  ← Some category spread
│ fast_attempt_rate           │    0.22  │
│ total_sessions              │    8.00  │
│ session_consistency         │    0.75  │
└─────────────────────────────┴──────────┘
```

---

## 🔬 Exercise

1. **Feature importance hypothesis:** Before looking at the actual RF feature importances, rank the 14 features by how important you *think* they'd be for predicting risk. Then check `rf_metrics.json` or the `_top_importances()` method.

2. **Edge case analysis:** What happens to `accuracy_variance` if a user has only attempted questions in one category? The code returns `0.0` - is this correct? Could it be misleading?

3. **Design your own feature:** If you could add a 15th feature to the RF, what would it be? Think about what behavioural signals the current 14 might miss.

---

> **Next:** [Chapter 05 - Random Forest Classifier: From Theory to Code →](./05_RANDOM_FOREST.md)
