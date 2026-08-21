# Chapter 08 - SHAP Explainability: Why the Model Decided

> *"A prediction without an explanation is just a magic number."* - This chapter covers the most academically interesting part of your project: making AI transparent.

---

## Why Explainability Matters

Your thesis title explicitly mentions **"risk-score transparency"**. In security awareness training, telling someone "you're high risk" without explaining *why* is:

1. **Not actionable** - They don't know what to improve
2. **Not trustworthy** - "The AI said so" isn't convincing
3. **Ethically questionable** - Opaque risk scores can feel like surveillance
4. **Academically required** - RQ2 of your thesis is about transparency

---

## What Is SHAP?

**SHAP** = **SH**apley **A**dditive ex**P**lanations

It comes from **cooperative game theory** (specifically, Shapley values from 1953). The core idea:

> *"How much did each feature contribute to pushing the prediction away from the average?"*

### The Shapley Value Concept

Imagine a game where 3 players (features) work together to produce a prediction. How do we fairly distribute credit?

```
Features: A (accuracy), B (fast_rate), C (overconfident_rate)

Model prediction for this user: "high risk" (score = 0.75)
Average prediction across all users: "medium" (score = 0.45)

Difference to explain: 0.75 - 0.45 = 0.30

SHAP distribution:
  Feature A (low accuracy):        +0.20  (biggest contributor)
  Feature B (high fast_rate):      +0.15  (also contributing)
  Feature C (low overconfident):   -0.05  (slightly protective)
                                   ──────
  Sum of SHAP values:              +0.30  ← Exactly the difference!
```

**Key property: SHAP values always sum to the difference between the prediction and the average.** This is mathematically guaranteed.

---

## TreeExplainer: Fast SHAP for Random Forests

Computing exact Shapley values is exponentially expensive (2^n subsets for n features). But for tree-based models, there's a **fast exact algorithm** called `TreeExplainer`:

```python
import shap

explainer = shap.TreeExplainer(predictor.model)
shap_values = explainer.shap_values(x, check_additivity=False)
```

`TreeExplainer` exploits the tree structure to compute exact SHAP values in polynomial time (not exponential). For a Random Forest with 200 trees, it traces each tree's decision path and attributes importance to each feature along the way.

### How TreeExplainer Works (Simplified)

For each tree in the forest:
1. Start at the root
2. At each split node, compute the expected prediction if this feature were removed
3. The difference between "with" and "without" is this feature's contribution
4. Average across all 200 trees

---

## Your Implementation

### The `explain_prediction` Function

```python
def explain_prediction(feature_vector, feature_names):
    try:
        # 1. Load the trained model
        predictor = RiskForestPredictor()
        if not predictor.is_ready:
            return {"error": "rf_not_ready"}
        
        # 2. Create the SHAP explainer
        explainer = shap.TreeExplainer(predictor.model)
        
        # 3. Compute SHAP values
        x = np.asarray(feature_vector).reshape(1, -1)
        raw = explainer.shap_values(x, check_additivity=False)
        
        # 4. Get the predicted class
        predicted_class_idx = int(predictor.model.predict(x)[0])
        
        # 5. Extract SHAP values for the predicted class
        if isinstance(raw, list):
            class_shap = np.asarray(raw[predicted_class_idx])[0]
        else:
            arr = np.asarray(raw)
            if arr.ndim == 3:
                class_shap = arr[0, :, predicted_class_idx]
            elif arr.ndim == 2:
                class_shap = arr[0]
            else:
                class_shap = arr.reshape(-1)
```

### Why the Shape Handling?

Different versions of scikit-learn and SHAP return values in different shapes:

| SHAP Version | Output Shape | Meaning |
|-------------|-------------|---------|
| Older | `list[np.ndarray]` | One array per class |
| Newer | `(1, 14, 4)` | (samples, features, classes) |
| Binary | `(1, 14)` | Single array (binary classifier) |

Your code handles all three cases - this is a robustness concern, not an ML one.

### Building the Result

```python
results = []
for i, fname in enumerate(feature_names):
    val = float(class_shap[i])
    results.append({
        "feature": fname,
        "label": FEATURE_LABELS.get(fname, fname),  # Human-readable name
        "shap_value": round(val, 4),
        "direction": "increases_risk" if val > 0 else "reduces_risk",
    })

# Sort by absolute value (most impactful first)
results.sort(key=lambda r: abs(r["shap_value"]), reverse=True)

# Top 3 risk factors (positive SHAP values)
risk_factors = [
    f"{r['label']} is contributing to your elevated risk."
    for r in results 
    if r["direction"] == "increases_risk" and abs(r["shap_value"]) > 1e-4
][:3]

# Top 3 protective factors (negative SHAP values)
protective_factors = [
    f"{r['label']} is helping keep your risk low."
    for r in results 
    if r["direction"] == "reduces_risk" and abs(r["shap_value"]) > 1e-4
][:3]
```

---

## Understanding SHAP Direction

```
SHAP value > 0  →  This feature INCREASES the user's risk prediction
SHAP value < 0  →  This feature DECREASES (protects against) risk
SHAP value ≈ 0  →  This feature has little impact on this prediction
```

### Example Output for User "Sita"

```json
{
  "shap_values": [
    {"feature": "smishing_accuracy", "label": "SMS phishing detection accuracy",
     "shap_value": 0.1823, "direction": "increases_risk"},
    {"feature": "overall_accuracy", "label": "Overall quiz accuracy",
     "shap_value": 0.1245, "direction": "increases_risk"},
    {"feature": "fast_attempt_rate", "label": "Proportion of rushed answers",
     "shap_value": 0.0892, "direction": "increases_risk"},
    {"feature": "phishing_accuracy", "label": "Phishing email detection accuracy",
     "shap_value": -0.1567, "direction": "reduces_risk"},
    {"feature": "password_hygiene_accuracy", "label": "Password hygiene knowledge",
     "shap_value": -0.0934, "direction": "reduces_risk"},
    ...
  ],
  "top_risk_factors": [
    "SMS phishing detection accuracy is contributing to your elevated risk.",
    "Overall quiz accuracy is contributing to your elevated risk.",
    "Proportion of rushed answers is contributing to your elevated risk."
  ],
  "top_protective_factors": [
    "Phishing email detection accuracy is helping keep your risk low.",
    "Password hygiene knowledge is helping keep your risk low.",
    ...
  ]
}
```

### What This Tells Sita

- Her **SMS phishing weakness** is the #1 contributor to her risk score
- She **rushes too many answers**, which the model learned is dangerous
- But her **phishing email skills** are protecting her - she's good at email threats
- Her **password hygiene** knowledge is also a strength

This is **actionable**: she knows to focus on SMS phishing training and slow down when answering.

---

## Human-Readable Feature Labels

```python
FEATURE_LABELS = {
    "avg_response_time_ms":        "How quickly you answer questions",
    "phishing_accuracy":           "Phishing email detection accuracy",
    "smishing_accuracy":           "SMS phishing detection accuracy",
    "social_engineering_accuracy": "Social engineering resistance",
    "password_hygiene_accuracy":   "Password hygiene knowledge",
    "physical_security_accuracy":  "Physical security awareness",
    "overall_accuracy":            "Overall quiz accuracy",
    "fast_attempt_rate":           "Proportion of rushed answers",
    "overconfident_rate":          "Proportion of overconfident answers",
    "session_consistency":         "Consistency across training sessions",
    "job_role_encoded":            "Job role",
    "total_sessions":              "Total training sessions completed",
    "days_since_last_session":     "Days since you last trained",
    "attempts_count":              "Total training attempts",
}
```

These translations turn opaque feature names into messages that non-technical SME staff can understand. This is a key part of your thesis's transparency objective.

---

## Graceful Degradation

```python
except Exception as exc:
    LOG.exception("SHAP explanation failed")
    return {"error": f"{type(exc).__name__}: {exc}"}
```

SHAP explanation is **best-effort** - if it fails for any reason:
1. The error is logged
2. A structured error dict is returned
3. The risk score is still computed and saved
4. The UI shows the score without the explanation panel

This is critical for production reliability - SHAP should never crash the main risk scoring pipeline.

---

## SHAP vs. Feature Importances

| Aspect | RF Feature Importances | SHAP Values |
|--------|----------------------|-------------|
| **Scope** | Global (same for all users) | Per-user (different for each person) |
| **Method** | Mean decrease in Gini impurity | Game-theoretic attribution |
| **Additivity** | Don't sum to anything meaningful | Sum to prediction - average |
| **Direction** | Only magnitude (no sign) | Signed (+risk / -risk) |
| **Speed** | Instant (computed during training) | Slower (computed per prediction) |

Your system uses BOTH:
- Feature importances for the `_top_importances()` method (global)
- SHAP for the per-user explanation panel (local)

---

## Where SHAP Appears in the UI

The frontend renders the SHAP explanation in `ShapExplanationPanel`:

1. **Risk Factors** (red cards): Features pushing the user toward higher risk
2. **Protective Factors** (green cards): Features keeping the user's risk low
3. **Transparency Disclaimer**: Explaining that the score is ML-generated

---

## 🔬 Exercise

1. **Interpretation:** If a user has SHAP value of -0.25 for `days_since_last_session`, what does this mean? Is it good or bad for the user?

2. **Additivity check:** If the average prediction across all users is "low" (class 0) with probability 0.54, and a user's prediction is "high" (class 2) with probability 0.73, the SHAP values for this user should sum to approximately what value?

3. **Ethics question:** Should SHAP explanations for `job_role_encoded` be shown to users? If their job role increases their risk, is that "fair"? What should the UI do differently?

4. **Viva question:** "Why SHAP instead of LIME?" Good answer: SHAP provides **consistent** (same result regardless of reference point), **locally accurate** explanations, and `TreeExplainer` gives exact values in polynomial time for tree-based models. LIME approximates locally with a simpler model, which can be inconsistent.

---

> **Next:** [Chapter 09 - The Adaptive Engine: Intelligent Tutoring →](./09_ADAPTIVE_ENGINE.md)
