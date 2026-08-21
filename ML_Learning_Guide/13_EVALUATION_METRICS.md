# Chapter 13 - Evaluation & Thesis Metrics

> This chapter covers the metrics that go into your thesis results chapter.

---

## Evaluation Framework

AHRID's evaluation endpoints (`/api/v1/eval/*`) compute four types of metrics:

```
1. ML Model Performance (RQ1: "How accurately does the model predict risk?")
2. Awareness Uplift      (RQ2: "Does training actually improve security awareness?")
3. Usability Scoring      (RQ3: "Is the system usable for non-technical staff?")
4. Engagement Metrics     (Supporting: "Are users completing training?")
```

---

## 1. ML Model Performance

### Random Forest Metrics

```python
# From eval endpoint
y_true = [rule_based_label for each user]
y_pred = [rf_predicted_label for each user]

metrics = {
    "accuracy": accuracy_score(y_true, y_pred),
    "f1_macro": f1_score(y_true, y_pred, average="macro"),
    "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
    "cohens_kappa": cohen_kappa_score(y_true, y_pred),
    "classification_report": classification_report(y_true, y_pred),
    "confusion_matrix": confusion_matrix(y_true, y_pred),
    "precision_recall_auc": average_precision_score(y_true_bin, y_proba),
}
```

### Understanding Each Metric

#### Accuracy
```
accuracy = correct_predictions / total_predictions
```
Simple but can be misleading with imbalanced classes.

#### F1 Score (Macro)
```
F1 = 2 × (precision × recall) / (precision + recall)

Macro F1 = average F1 across all classes (treats each class equally)
```

- **Precision:** Of all users predicted "high risk", how many actually are?
- **Recall:** Of all actual "high risk" users, how many did we catch?
- **F1:** Harmonic mean of precision and recall

#### Cohen's Kappa (κ)
```
κ = (observed_agreement - chance_agreement) / (1 - chance_agreement)
```

This is your **key metric for thesis RQ1** - it measures how much better the RF is compared to random chance, adjusted for the class distribution.

#### Confusion Matrix (How to Read)

```
                   Predicted
              low  med  high  crit
Actual low  │ 108   2    1     0  │
Actual med  │   5  24    3     1  │
Actual high │   2   4   30     1  │
Actual crit │   0   2    2    23  │
```

- **Diagonal:** Correct predictions (good!)
- **Off-diagonal:** Errors
- **Bottom-left off-diagonal:** Under-predictions (predicted low, actually high - dangerous!)
- **Top-right off-diagonal:** Over-predictions (predicted high, actually low - annoying but safe)

### K-Means Metrics

```python
{
    "silhouette_score": silhouette_score(X_scaled, labels),
    "inertia": model.inertia_,           # Sum of squared distances to centroids
    "cluster_sizes": {0: 180, 1: 210, ...},
    "archetype_distribution": {...},
}
```

---

## 2. Awareness Uplift

### Pre/Post Assessment Design

```python
class AwarenessAssessment(db.Model):
    user_id     = uuid_fk("users.id")
    phase       = db.Column(db.String(10))  # "pre" or "post"
    score       = db.Column(db.Float)       # 0.0 to 100.0
    category    = db.Column(db.String(50))
    created_at  = db.Column(db.DateTime)
```

For each category, the system records scores **before** and **after** training.

### Cohen's d (Effect Size)

```python
from scipy import stats

pre_scores  = [a.score for a in assessments if a.phase == "pre"]
post_scores = [a.score for a in assessments if a.phase == "post"]

mean_diff = np.mean(post_scores) - np.mean(pre_scores)
pooled_std = np.sqrt(
    (np.std(pre_scores, ddof=1)**2 + np.std(post_scores, ddof=1)**2) / 2
)
cohens_d = mean_diff / pooled_std
```

### Interpreting Cohen's d

| d | Effect Size | Meaning for Your Thesis |
|---|-------------|------------------------|
| 0.2 | Small | Training had minimal impact |
| 0.5 | Medium | Training meaningfully improved awareness |
| 0.8 | Large | Training substantially improved awareness |
| > 1.0 | Very large | Exceptional improvement |

### Statistical Significance (Paired t-test)

```python
t_stat, p_value = stats.ttest_rel(post_scores, pre_scores)
```

A p-value < 0.05 means the improvement is statistically significant (not due to chance).

---

## 3. Usability - System Usability Scale (SUS)

### What Is SUS?

SUS is a standardised 10-question usability questionnaire (Brooke, 1996). Each question is answered on a 1-5 Likert scale.

```python
SUS_QUESTIONS = [
    "I think that I would like to use this system frequently.",               # Positive
    "I found the system unnecessarily complex.",                               # Negative
    "I thought the system was easy to use.",                                   # Positive
    "I think that I would need the support of a technical person...",          # Negative
    "I found the various functions in this system were well integrated.",      # Positive
    "I thought there was too much inconsistency in this system.",             # Negative
    "I would imagine that most people would learn to use this system...",     # Positive
    "I found the system very cumbersome to use.",                             # Negative
    "I felt very confident using the system.",                                # Positive
    "I needed to learn a lot of things before I could get going...",          # Negative
]
```

### SUS Scoring Algorithm

```python
def compute_sus_score(responses):
    score = 0
    for i, val in enumerate(responses):
        if (i + 1) % 2 == 1:  # Odd items (positive)
            score += val - 1   # Subtract 1
        else:                  # Even items (negative)
            score += 5 - val   # Invert: 5 - response
    return score * 2.5         # Scale to 0-100
```

### SUS Score Interpretation

| Score | Adjective | Grade |
|-------|-----------|-------|
| 0-25 | Worst Imaginable | F |
| 25-39 | Poor | D |
| 39-52 | OK | C |
| 52-73 | Good | B |
| 73-85 | Excellent | A |
| 85-100 | Best Imaginable | A+ |

**Industry average:** 68. Scoring above 68 means your system is **above average usability**.

---

## 4. Engagement Metrics

```python
engagement_metrics = {
    "total_users": count,
    "active_users_30d": ...,              # Users with attempts in last 30 days
    "avg_sessions_per_user": ...,
    "avg_attempts_per_session": ...,
    "completion_rate": ...,               # Sessions fully completed
    "session_duration_avg_min": ...,
    "return_rate_7d": ...,                # Users who came back within 7 days
}
```

---

## Your Thesis Results Structure

```
Results Chapter
├── 5.1 ML Prediction Performance
│   ├── RF accuracy, F1, κ
│   ├── Confusion matrix analysis
│   ├── SMOTE impact (before vs after)
│   └── Cross-validation stability
│
├── 5.2 Clustering Quality
│   ├── Silhouette score
│   ├── Cluster distribution
│   └── Archetype interpretability
│
├── 5.3 Awareness Uplift
│   ├── Pre vs post scores per category
│   ├── Cohen's d effect sizes
│   └── Statistical significance (p-values)
│
├── 5.4 Usability
│   ├── SUS scores (mean, distribution)
│   └── Comparison to industry benchmark (68)
│
└── 5.5 Engagement
    ├── Active user rates
    ├── Session completion
    └── Return rates
```

---

## 🔬 Exercise

1. **Compute Cohen's d:** If pre-training mean = 42.5, post = 65.8, pre-std = 15.2, post-std = 12.8, what is Cohen's d? Is the effect small, medium, or large?

2. **SUS scoring:** Given responses `[4, 2, 5, 1, 4, 2, 5, 1, 4, 1]`, compute the SUS score.

3. **Confusion matrix analysis:** In the example matrix above, which class has the most errors? What type of error is most common (over-prediction or under-prediction)?

---

> **Next:** [Chapter 14 - Non-ML Intelligent Systems →](./14_NON_ML_SYSTEMS.md)
