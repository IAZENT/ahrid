# Chapter 14 - Non-ML Intelligent Systems

> Not everything "smart" in AHRID is ML. This chapter covers the rule-based, heuristic, and algorithmic intelligence that supports the ML components.

---

## 1. OSINT Threat Feed Pipeline

### What It Does
Periodically fetches real phishing URLs from public threat intelligence feeds and converts them into training scenarios.

### Sources
- **PhishTank** - Community-verified phishing URL database
- **Phishing.Database** - Automated phishing URL feed
- **URLhaus** - Malware/phishing URL tracker

### Pipeline

```
Fetch URLs (every 6h via scheduler)
       │
       ▼
Deduplicate (by URL hash)
       │
       ▼
Classify (lure type, difficulty, category - Chapter 10)
       │
       ▼
Sanitise (strip tracking params, defang URL)
       │
       ▼
Generate scenario template
       │
       ▼
Store in Scenario table (marked as threat-feed sourced)
```

### URL Sanitisation

```python
def defang_url(url):
    """Make URL safe to display without being clickable."""
    return (url
        .replace("http://", "hxxp://")
        .replace("https://", "hxxps://")
        .replace(".", "[.]"))

# Example:
# "https://paypa1.com/login" → "hxxps://paypa1[.]com/login"
```

---

## 2. Risk Escalation & Notifications

When a user's risk level **worsens**, the system emits an alert:

```python
def _check_and_emit_risk_change(user_id, previous_level, new_level):
    if new_level in ("medium", "high", "critical"):
        if _level_rank(new_level) > _level_rank(previous_level):
            # Create notification for the user's manager
            Notification.create(
                user_id=manager_id,
                type="risk_escalation",
                message=f"{user.full_name} has escalated to {new_level} risk.",
                severity=new_level,
            )
```

### Risk Level Ranking

```python
LEVEL_RANK = {"unknown": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
```

An escalation from "low" → "high" triggers a notification. A de-escalation ("high" → "medium") does **not** - to avoid notification fatigue.

---

## 3. Role-Based Scenario Targeting

Each scenario can specify which job roles it's most relevant for:

```python
scenario.target_roles = ["accountant", "finance"]
```

The adaptive engine prioritises these scenarios for matching roles:

```python
# In scenario selection:
if user.job_role in scenario.target_roles:
    priority_boost = 1.5  # 50% more likely to be selected
```

This means an accountant sees more invoice fraud scenarios than a receptionist, while both still get general phishing training.

---

## 4. Scheduler (APScheduler)

Background tasks run on a schedule:

| Task | Interval | Purpose |
|------|----------|---------|
| Threat feed fetch | 6 hours | Ingest new phishing URLs |
| Cluster reassignment | Daily | Re-cluster users with new data |
| Inactive user check | Daily | Flag users who haven't trained in 30+ days |
| Metric aggregation | Daily | Pre-compute dashboard analytics |

---

## 5. Privacy-Preserving Dashboard

The manager dashboard implements **aggregate-only** visibility:

- **Managers see:** Team-level statistics (average risk, cluster distribution, completion rates)
- **Managers DON'T see:** Individual user answers, response times, or SHAP explanations
- **Users see:** Their own detailed risk breakdown, SHAP factors, and category performance
- **Users DON'T see:** Other users' data or their ranking

This privacy boundary is a design choice for ethical AI deployment in the workplace.

---

## 🔬 Exercise

1. **Privacy design:** If a manager sees a team average risk of 72 (high), but they can't see individual scores, how would they identify who needs help? (Hint: look at cluster distributions)

2. **Threat feed latency:** If a new phishing campaign launches at 9 AM and your feed fetches every 6 hours, what's the worst-case delay before it appears as a training scenario?

---

> **Next:** [Chapter 15 - Glossary & Quick Reference →](./15_GLOSSARY.md)
