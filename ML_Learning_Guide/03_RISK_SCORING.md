# Chapter 03 - Risk Scoring: The Rule-Based Baseline

> Before ML predicts anything, AHRID needs a **deterministic, explainable** risk score. This is the foundation that everything else builds on.

---

## Why a Rule-Based Baseline?

Every good ML system needs a **baseline** to compare against. If your Random Forest only achieves 60% accuracy and a simple rule-based system achieves 58%, the ML isn't adding much value. Your thesis evaluates the RF against this baseline using Cohen's Kappa.

The risk scorer is also the **fallback** - when the RF model hasn't been trained yet (e.g., fresh deployment with no data), users still get meaningful risk scores.

---

## The Core Idea: Risk = Inverse of Accuracy

The fundamental equation is simple:

```
risk_score = (1.0 - accuracy) × 100
```

If a user gets 80% of phishing questions right:
```
phishing_risk = (1.0 - 0.80) × 100 = 20.0  (low risk)
```

If they get 30% right:
```
phishing_risk = (1.0 - 0.30) × 100 = 70.0  (high risk)
```

### Why This Makes Sense
- A user who **always answers correctly** has 0 risk (they recognise every threat)
- A user who **always answers wrong** has 100 risk (they fall for every attack)
- The midpoint (50% accuracy) gives risk = 50 (moderate risk)

---

## Per-Category Scoring

The scorer computes **8 independent category scores** plus a **composite**:

```python
# From risk_scorer.py
def _category_score(attempts):
    """Return risk for one category in [0, 100]"""
    attempts = list(attempts)
    if not attempts:
        return 0.0  # no signal → no risk recorded yet
    accuracy = sum(1 for a in attempts if a.is_correct) / len(attempts)
    return round((1.0 - accuracy) * 100.0, 2)
```

### Worked Example

Suppose user "Sita" has these attempt histories:

| Category | Correct | Wrong | Accuracy | Risk Score |
|----------|---------|-------|----------|------------|
| phishing_email | 8 | 2 | 80% | 20.0 |
| smishing | 3 | 7 | 30% | 70.0 |
| vishing | 0 | 0 | - | 0.0 (no data) |
| physical_security | 5 | 5 | 50% | 50.0 |
| password_hygiene | 9 | 1 | 90% | 10.0 |
| usb_baiting | 0 | 0 | - | 0.0 (no data) |
| social_engineering | 4 | 6 | 40% | 60.0 |
| data_handling | 7 | 3 | 70% | 30.0 |

**Composite Score** = average of *seen* categories only:
```
composite = (20.0 + 70.0 + 50.0 + 10.0 + 60.0 + 30.0) / 6 = 40.0
```

Note: vishing and usb_baiting are excluded because Sita has no attempts there. This prevents unfairly lowering the composite.

---

## Risk Level Bucketing

The composite score maps to a human-readable risk level:

```python
LEVEL_THRESHOLDS = (
    (80.0, "critical"),    # composite >= 80 → critical
    (60.0, "high"),        # composite >= 60 → high
    (40.0, "medium"),      # composite >= 40 → medium
    (0.0,  "low"),         # composite >= 0  → low
)

def _level_for(score, attempts_count):
    if attempts_count == 0:
        return "unknown"
    for threshold, label in LEVEL_THRESHOLDS:
        if score >= threshold:
            return label
    return "low"
```

### Sita's Result
```
composite = 40.0 → "medium" risk level
```

**Visual representation:**
```
 0          20          40          60          80          100
 ├──────────┼──────────┼──────────┼──────────┼──────────┤
 │   LOW    │   LOW    │  MEDIUM  │   HIGH   │ CRITICAL │
                       ▲
                    Sita (40.0)
```

---

## The Recalculation Trigger

Risk scores are recalculated **synchronously after every attempt**:

```python
# In adaptive_engine.py → process_attempt():
attempt = Attempt(...)           # 1. Save the attempt
db.session.flush()
new_score = recalculate_for_user(user_id)  # 2. Immediately recompute

# Risk escalation check
if new_level > prev_level and new_level in ("medium", "high", "critical"):
    emit_risk_escalation(user_id, ...)     # 3. Alert if worsened
```

This means the risk score is **always up-to-date** - there's no lag between answering a question and seeing its impact.

---

## The Recalculation Function - Line by Line

```python
def recalculate_for_user(user_id) -> RiskScore:
    # Step 1: Get all REAL attempts (exclude synthetic)
    cat_attempts = {c: [] for c in CATEGORIES}
    rows = Attempt.query.filter_by(user_id=user_id, is_synthetic=False) \
                        .order_by(Attempt.created_at.desc()).all()
    
    # Step 2: Group by category
    for a in rows:
        if a.category in cat_attempts:
            cat_attempts[a.category].append(a)
    
    # Step 3: Compute per-category scores
    cat_scores = {c: _category_score(cat_attempts[c]) for c in CATEGORIES}
    
    # Step 4: Compute composite (only from seen categories)
    seen_categories = [c for c, atts in cat_attempts.items() if atts]
    composite = sum(cat_scores[c] for c in seen_categories) / len(seen_categories)
    
    # Step 5: Determine risk level
    risk_level = _level_for(composite, len(rows))
    
    # Step 6: Upsert the RiskScore row (create or update)
    risk = RiskScore.query.filter_by(user_id=user_id).first()
    if risk is None:
        risk = RiskScore(user_id=user_id)
        db.session.add(risk)
    
    # Step 7: Update all fields
    risk.composite_score = composite
    risk.phishing_email_score = cat_scores["phishing_email"]
    # ... (all 8 categories)
    risk.risk_level = risk_level
    risk.attempts_count = len(rows)
    
    # Step 8: Best-effort SHAP explanation
    try:
        if RiskForestPredictor().is_ready:
            vec = build_feature_vector_for_user(user_id)
            if vec is not None:
                risk.shap_summary = explain_prediction(vec, FEATURE_NAMES)
    except Exception:
        risk.shap_summary = None  # Never block the score
    
    db.session.flush()
    return risk
```

---

## Why "Rule-Based" Matters for Your Thesis

Your thesis research question compares the **RF classifier** against this **rule-based baseline**:

| Method | How It Decides | Strengths | Weaknesses |
|--------|---------------|-----------|------------|
| Rule-based | `risk = (1 - accuracy) × 100` | Transparent, deterministic, always works | Can't capture complex patterns |
| Random Forest | Learns from 14 behavioural features | Captures non-linear relationships (e.g., fast+wrong = risky) | Needs training data, less transparent |

The evaluation endpoint `GET /eval/rf-metrics` computes **Cohen's Kappa** to measure how much the RF's predictions agree with the rule-based labels *beyond what chance would predict*.

### Cohen's Kappa Interpretation

| κ Value | Interpretation |
|---------|---------------|
| < 0 | Less agreement than chance |
| 0.0 - 0.20 | Slight agreement |
| 0.21 - 0.40 | Fair agreement |
| 0.41 - 0.60 | Moderate agreement |
| 0.61 - 0.80 | Substantial agreement |
| 0.81 - 1.00 | Almost perfect agreement |

If your RF gets κ ≈ 0.85 against the baseline, that's evidence it's learned meaningful patterns.

---

## Key Design Decision: No Recency Weighting Here

Notice that `risk_scorer.py` treats **all attempts equally** - a question answered 3 months ago counts the same as one answered today. This is deliberate:

- The **risk scorer** gives a stable, complete picture
- The **adaptive engine** (Chapter 09) uses recency-weighted mastery for training decisions
- The **RF model** (Chapter 05) can implicitly capture recency via `days_since_last_session`

This separation of concerns means each component has one clear job.

---

## The RiskScore Data Model

The result is persisted in a single row per user:

```python
class RiskScore(db.Model):
    composite_score        # 0.0 to 100.0
    phishing_email_score   # 8 per-category scores
    smishing_score
    vishing_score
    physical_security_score
    password_hygiene_score
    usb_baiting_score
    social_engineering_score
    data_handling_score
    risk_level             # "low" | "medium" | "high" | "critical" | "unknown"
    shap_summary           # JSON blob from SHAP explainer (Chapter 08)
    attempts_count         # Total real attempts used in computation
```

---

## 🔬 Exercise

1. **Manual calculation:** If a user has these attempts:
   - Phishing: 6 correct, 4 wrong
   - Smishing: 2 correct, 8 wrong
   - Password: 9 correct, 1 wrong
   
   Calculate each category risk score and the composite. What risk level would they get?

2. **Edge case thinking:** What happens if a user has only 1 attempt in 1 category? Is the score meaningful? What could you do to handle this better?

3. **Threshold analysis:** The current thresholds are 0/40/60/80. If you changed them to 0/30/50/70, how would it affect the risk distribution? Would more or fewer users be "critical"?

---

> **Next:** [Chapter 04 - Feature Engineering Deep-Dive →](./04_FEATURE_ENGINEERING.md)
