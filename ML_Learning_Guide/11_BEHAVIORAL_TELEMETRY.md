# Chapter 11 - Behavioural Telemetry & Profiling

> Beyond correctness, AHRID tracks *how* users interact - dwell times, answer changes, and engagement patterns.

---

## Telemetry Events

The `UserBehaviorEvent` model captures granular interaction data:

| Event Type | When Recorded | Payload |
|-----------|--------------|---------|
| `answer_submitted` | User submits an answer | `{total_dwell_ms, answer_changes}` |
| `read_time_recorded` | User reads a scenario | `{dwell_ms}` |
| `hint_requested` | User asks for a hint | `{}` |

### Engagement Scoring

```python
def get_category_engagement_scores(user_id) -> dict[str, float]:
    """Per-category struggle score (0-1). Higher = user struggles more."""
    summary = get_user_telemetry_summary(user_id, days=30)
    dwell = summary["avg_dwell_ms_per_category"]
    
    max_dwell = max(dwell.values())
    min_dwell = min(dwell.values())
    span = (max_dwell - min_dwell) or 1
    
    for cat, ms in dwell.items():
        dwell_score = (ms - min_dwell) / span               # 0-1 normalised
        score = 0.6 * dwell_score + 0.4 * answer_changes    # Weighted blend
```

**Interpretation:** High dwell time + many answer changes = user is **struggling** with that category.

---

## Mistake Clustering

```python
def cluster_user_mistakes(user_id, limit=50):
    """Group recent wrong answers by (category, difficulty)."""
    rows = Attempt.query.filter_by(user_id=user_id, is_correct=False) \
                        .order_by(Attempt.created_at.desc()).limit(limit).all()
    
    counter = Counter()
    for a in rows:
        counter[(a.category, a.difficulty)] += 1
    
    return {
        "dominant_category": ...,     # Where they fail most
        "dominant_difficulty": ...,   # At which difficulty level
        "clusters": [...],            # Top (category, difficulty) pairs
        "signature": "phishing_email|2",  # Concise pattern identifier
    }
```

This helps identify patterns like: *"User X consistently fails phishing questions at difficulty 2"* - more specific than just "weak at phishing."

---

## 🔬 Exercise

1. If a user has avg_dwell = 8000ms for smishing but only 2000ms for phishing, what does that suggest about their relative comfort with each category?

---

> **Next:** [Chapter 12 - Model Training Pipeline End-to-End →](./12_TRAINING_PIPELINE.md)
