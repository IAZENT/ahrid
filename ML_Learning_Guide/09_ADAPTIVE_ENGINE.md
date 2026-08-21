# Chapter 09 - The Adaptive Engine: Intelligent Tutoring

> This isn't classical ML, but it's arguably the **most intelligent** part of the system - a rule-based adaptive tutoring system inspired by cognitive science.

---

## What Makes It "Adaptive"?

A static quiz gives everyone the same questions. AHRID's adaptive engine:

1. **Tracks mastery** per-category with recency weighting
2. **Applies a forgetting curve** so unused knowledge decays
3. **Selects scenarios** based on weakness, role, and difficulty
4. **Promotes/demotes difficulty** based on performance
5. **Implements spaced repetition** by risk level

---

## Part 1: Mastery Tracking

### Recency-Weighted Accuracy

```python
DECAY_FACTOR = 0.85

def calculate_mastery(attempts):
    """attempts[0] = most recent."""
    if not attempts:
        return 0.0
    weights = [DECAY_FACTOR**i for i in range(len(attempts))]
    weighted = sum(int(a.is_correct) * w for a, w in zip(attempts, weights))
    return weighted / sum(weights)
```

### How the Weights Work

For `DECAY_FACTOR = 0.85`:

```
Attempt 0 (most recent): weight = 0.85⁰ = 1.000
Attempt 1:               weight = 0.85¹ = 0.850
Attempt 2:               weight = 0.85² = 0.723
Attempt 3:               weight = 0.85³ = 0.614
Attempt 4:               weight = 0.85⁴ = 0.522
Attempt 5:               weight = 0.85⁵ = 0.444
...
Attempt 9:               weight = 0.85⁹ = 0.232
```

### Worked Example

```
Attempts (most recent first): [✓, ✗, ✓, ✓, ✗, ✓, ✗, ✓, ✓, ✗]
Correct values:               [1, 0, 1, 1, 0, 1, 0, 1, 1, 0]
Weights:                      [1.00, 0.85, 0.72, 0.61, 0.52, 0.44, 0.37, 0.32, 0.27, 0.23]

Weighted sum:  1×1.00 + 0×0.85 + 1×0.72 + 1×0.61 + 0×0.52 + 1×0.44 + 0×0.37 + 1×0.32 + 1×0.27 + 0×0.23
             = 1.00 + 0 + 0.72 + 0.61 + 0 + 0.44 + 0 + 0.32 + 0.27 + 0
             = 3.36

Weight sum:    1.00 + 0.85 + 0.72 + 0.61 + 0.52 + 0.44 + 0.37 + 0.32 + 0.27 + 0.23
             = 5.33

Mastery = 3.36 / 5.33 = 0.631

Compare with simple accuracy: 6/10 = 0.600
```

The mastery (0.631) is **higher** than simple accuracy (0.600) because the recent attempts (first 4) are mostly correct. The system gives more credit to recent performance.

### Why Use Exponential Decay?

**Cognitive science rationale:** A user who got 3 wrong last month but 5 right this week is improving - their current skill level is better than their historical average. Exponential decay naturally captures this.

**The `0.85` factor** was chosen as a balance:
- Too high (0.99): essentially ignores recency (all attempts equal)
- Too low (0.50): only the last 2-3 attempts matter (too volatile)
- 0.85: the last ~10 attempts are most influential, older ones fade gradually

---

## Part 2: The Forgetting Curve

### Ebbinghaus's Forgetting Curve (1885)

German psychologist Hermann Ebbinghaus discovered that memory decays exponentially over time without reinforcement.

```python
MASTERY_HALFLIFE_DAYS = 21.0
FORGETTING_FLOOR = 0.30

def _apply_forgetting_curve(mastery, last_attempt_at):
    if last_attempt_at is None:
        return mastery
    days_idle = (datetime.utcnow() - last_attempt_at).total_seconds() / 86400
    if days_idle <= 0:
        return mastery
    retained = 0.5 ** (days_idle / MASTERY_HALFLIFE_DAYS)
    return FORGETTING_FLOOR + (mastery - FORGETTING_FLOOR) * retained
```

### The Formula

```
decayed_mastery = FLOOR + (mastery - FLOOR) × 0.5^(days_idle / halflife)
```

### Worked Example

User had phishing mastery = 0.90, last practised 42 days ago:

```
retained = 0.5^(42/21) = 0.5^2 = 0.25
decayed  = 0.30 + (0.90 - 0.30) × 0.25
         = 0.30 + 0.60 × 0.25
         = 0.30 + 0.15
         = 0.45
```

Their phishing mastery dropped from **0.90 → 0.45** after 42 days without practice!

### Decay Over Time

```
Days idle: 0    7    14   21   28   35   42   63   84
Retained:  100% 79%  63%  50%  40%  31%  25%  13%  6%
Mastery:   0.90 0.77 0.68 0.60 0.54 0.49 0.45 0.38 0.34
```

```
1.0 ┤
    │ ──                                   
0.9 ┤   ──                                 Original mastery
    │      ──                              
0.8 ┤        ──                            
    │          ───                          
0.7 ┤             ───                      
    │                ───                    
0.6 ┤                   ───                Half-life (21 days)
    │                      ────            
0.5 ┤                          ────        
    │                              ─────   
0.4 ┤                                  ────────
    │                                          ─────── Floor (0.30)
0.3 ┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
    └──────────────────────────────────────
     0    14   28   42   56   70   84  days
```

### Why a Floor of 0.30?

> *"Unpracticed security awareness erodes rather than becoming merely uncertain."*

Without a floor, mastery would decay toward 0.0 (complete ignorance). But a user who once scored 90% in phishing hasn't truly forgotten everything - they retain some base knowledge. The floor of 0.30 means:

- Mastery can never drop below 30% due to time alone
- The system will still resurface the category for practice (since 30% is below the promotion threshold)
- But it won't catastrophically reset a user's entire history

---

## Part 3: Difficulty Progression

```python
PROMOTION_THRESHOLD = 0.80
DEMOTION_THRESHOLD = 0.40
MIN_ATTEMPTS_FOR_DECISION = 5

def _next_difficulty(current, mastery, total_attempts):
    if total_attempts < MIN_ATTEMPTS_FOR_DECISION:
        return MIN_DIFFICULTY   # Not enough data yet
    if mastery >= PROMOTION_THRESHOLD:
        return min(current + 1, MAX_DIFFICULTY)  # Promote
    if mastery <= DEMOTION_THRESHOLD:
        return max(current - 1, MIN_DIFFICULTY)  # Demote
    return current  # Stay
```

```
                    Difficulty Progression
                    
Mastery  0.0   0.2   0.4   0.6   0.8   1.0
          │     │     │     │     │     │
          │ DEMOTE   │  HOLD │  PROMOTE│
          │◄────────►│◄──────►│◄───────►│
          │  ≤ 0.40  │       │ ≥ 0.80  │
```

### Example Flow

```
Session 1: Difficulty 1, Mastery 0.65 → HOLD at 1
Session 2: Difficulty 1, Mastery 0.75 → HOLD at 1
Session 3: Difficulty 1, Mastery 0.85 → PROMOTE to 2 ↑
Session 4: Difficulty 2, Mastery 0.55 → HOLD at 2
Session 5: Difficulty 2, Mastery 0.35 → DEMOTE to 1 ↓
Session 6: Difficulty 1, Mastery 0.82 → PROMOTE to 2 ↑
Session 7: Difficulty 2, Mastery 0.83 → PROMOTE to 3 ↑
Session 8: Difficulty 3, Mastery 0.88 → MAXED OUT (stay at 3)
```

---

## Part 4: Smart Scenario Selection

### The Distribution Ratio

```python
SCENARIO_SELECTION_RATIO = {
    "weakest_category": 0.50,   # Half the session targets weak areas
    "other_categories": 0.25,   # Quarter for breadth
    "challenge": 0.25,          # Quarter for stretching
}
```

For a 20-question session:
- 10 questions from the user's **weakest category**
- 5 questions from **other categories** (breadth)
- 5 questions at **higher difficulty** (stretch)

### Additional Selection Logic

1. **Threat feed slot:** If a real phishing URL was ingested in the last 48 hours, one question is swapped for a scenario based on that URL

2. **Role targeting:** Scenarios have `target_roles` - an accountant gets more invoice fraud scenarios

3. **Prefer unseen:** Scenarios the user hasn't seen are prioritised, then old-but-seen, then recently-seen

4. **Spaced repetition:** Correctly answered questions are suppressed for a time window based on risk level:

```python
RISK_LEVEL_TO_SPACING_HOURS = {
    "critical": 12,   # See correct answers again sooner (they need practice)
    "high":     24,
    "medium":   48,
    "low":      72,    # Can wait longer between revisits
    "unknown":  24,
}
```

5. **Session guarantee:** If all filters leave too few questions, the engine relaxes spacing to ensure a full session.

---

## Part 5: Transparency Metadata

```python
reasons = {}  # scenario.id → explanation string

# For weakest-category picks:
reasons[s.id] = (
    f"Targets your weakest area: {cat_display}. "
    f"Priority for {role_label} role."
)

# For challenge picks:
reasons[s.id] = (
    f"Challenge: {s_cat_display} at higher difficulty to stretch your skills."
)

# For threat-feed picks:
reasons[s.id] = "Based on a real phishing threat detected in the last 48 hours."
```

Each question in a session comes with an explanation of **why** it was selected - another transparency feature for your thesis.

---

## 🔬 Exercise

1. **Calculate mastery:** Given attempts (most recent first): `[✓, ✓, ✗, ✓, ✗, ✗, ✓]` with `λ = 0.85`, compute the recency-weighted mastery.

2. **Forgetting curve:** A user had mastery = 0.75 in "usb_baiting" and hasn't practised for exactly 21 days (one half-life). What's their decayed mastery?

3. **Session design:** If a user's weakest category is "smishing" at difficulty 2, and they have "medium" risk level, design a 10-question session. How many smishing questions? How many challenges? What's the spacing window?

---

> **Next:** [Chapter 10 - Scenario Classification: URL Intelligence →](./10_SCENARIO_CLASSIFIER.md)
