# Chapter 06 - SMOTE: Handling Class Imbalance

> Your dataset has 568 "low risk" users but only 136 "critical" users. This chapter explains why that's a problem and how SMOTE fixes it.

---

## The Class Imbalance Problem

### Your Data Distribution (Before SMOTE)

```
Class 0 (low):      ████████████████████████████████████████████████  568 (53.8%)
Class 1 (medium):   ██████████████                                    167 (15.8%)
Class 2 (high):     ████████████████                                  185 (17.5%)
Class 3 (critical): ███████████                                       136 (12.9%)
```

### Why This Is a Problem

Imagine you built a "classifier" that **always predicts "low risk"** regardless of input:

```
Accuracy = 568 / 1056 = 53.8% - Not bad?
```

This naive classifier:
- ✅ Gets every "low" user right (568/568 = 100% recall for class 0)
- ❌ Gets every "medium", "high", and "critical" user wrong (0% recall for classes 1-3)
- ❌ **Misses every dangerous user** - catastrophic in a security system!

A model trained on imbalanced data tends to **optimise for the majority class** because that's how it gets the highest accuracy.

---

## Two Lines of Defence

Your project uses **two complementary strategies** to handle imbalance:

### 1. `class_weight="balanced"` (in the RF itself)

This makes the RF pay more attention to minority classes by weighting their samples higher during tree construction.

```python
# Weight formula: n_total / (n_classes * n_class)
low_weight      = 1056 / (4 * 568) = 0.465  ← downweighted
medium_weight   = 1056 / (4 * 167) = 1.581  ← upweighted
high_weight     = 1056 / (4 * 185) = 1.427  ← upweighted
critical_weight = 1056 / (4 * 136) = 1.941  ← most upweighted
```

### 2. SMOTE (before training)

SMOTE physically creates new synthetic training samples for minority classes.

---

## What Is SMOTE?

**SMOTE** = **S**ynthetic **M**inority **O**ver-sampling **TE**chnique

Instead of just duplicating existing minority samples (which would cause overfitting), SMOTE creates **new, plausible** data points by interpolating between existing ones.

### The Algorithm (Step by Step)

1. For each minority class sample `x`:
2. Find its `k` nearest neighbours (in feature space) **within the same class**
3. Randomly pick one of those neighbours `x_nn`
4. Create a new sample by interpolating:

```
x_new = x + λ × (x_nn - x)

where λ is random ∈ [0, 1]
```

### Visual Example (2D for simplicity)

Imagine two features: `overall_accuracy` and `fast_attempt_rate`

```
                    fast_attempt_rate
                    │
              0.8   │         × (critical user C)
                    │        ╱
              0.6   │       ★ (NEW synthetic point!)
                    │      ╱
              0.4   │     × (critical user A)
                    │
              0.2   │
                    │
              0.0   └──────────────────────────
                    0.0   0.2   0.4   0.6   0.8
                          overall_accuracy
```

The star (★) is a SMOTE-generated point between users A and C. It has realistic feature values because it's an interpolation of two real users.

---

## Your SMOTE Implementation

```python
# From train_models.py

# Check if SMOTE is feasible
pre_dist = dict(Counter(int(v) for v in y_train))
smallest = min(pre_dist.values()) if pre_dist else 0

if smallest >= 2 and len(pre_dist) >= 2:
    from imblearn.over_sampling import SMOTE
    
    # Adaptive k_neighbors: can't be >= smallest class size
    k = max(1, min(5, smallest - 1))
    
    smote = SMOTE(random_state=42, k_neighbors=k)
    X_train, y_train = smote.fit_resample(X_train, y_train)
```

### Understanding `k_neighbors`

The `k` parameter controls how many nearest neighbours SMOTE considers when creating each synthetic sample.

```python
k = max(1, min(5, smallest - 1))
```

**Why adaptive k?**
- Default k = 5, which means SMOTE looks at the 5 nearest neighbours
- But if a class has only 3 samples, you can't have 5 neighbours!
- `smallest - 1` ensures k is never larger than the smallest class minus one
- `max(1, ...)` ensures k is at least 1

**Your data:**
```
smallest class (critical, after 80/20 split) ≈ 109 samples
k = min(5, 109 - 1) = 5  ← standard k works fine
```

### The Result

```python
# Before SMOTE (training set only, after 80/20 split):
{"0": 454, "1": 133, "2": 148, "3": 109}

# After SMOTE:
{"0": 454, "1": 454, "2": 454, "3": 454}
```

```
Before SMOTE:                              After SMOTE:
Class 0: ████████████████████████ 454      ████████████████████████ 454 (unchanged)
Class 1: ███████        133                ████████████████████████ 454 (+321 synthetic)
Class 2: ████████       148                ████████████████████████ 454 (+306 synthetic)
Class 3: ██████         109                ████████████████████████ 454 (+345 synthetic)
```

Every class is now perfectly balanced at 454 samples each.

---

## Why SMOTE Over Other Methods?

| Method | How | Pros | Cons |
|--------|-----|------|------|
| **Random oversampling** | Duplicate existing minority samples | Simple | Overfitting (model memorises duplicates) |
| **Random undersampling** | Remove majority samples | Simple | Loses information (throwing away data!) |
| **SMOTE** | Create new synthetic minority samples | Adds diversity without losing data | Can create noisy samples in overlapping regions |
| **class_weight** | Weight samples differently | No data modification needed | Doesn't add information |

Your project uses **SMOTE + class_weight** together - this is a common best practice called "belt and suspenders."

---

## The Logging (Important for Thesis)

```python
smote_status = {
    "applied": True, 
    "k_neighbors": k,
    "before": pre_dist,    # Original class distribution
    "after": post_dist,    # After SMOTE
}
```

This is saved in `rf_metrics.json` under the `"smote"` key. Your thesis methodology chapter should report these exact numbers to show:

1. There **was** class imbalance (pre-SMOTE distribution)
2. SMOTE was applied with what parameters
3. The result was a balanced training set

---

## When SMOTE Is Skipped

```python
if smallest >= 2 and len(pre_dist) >= 2:
    # Apply SMOTE
else:
    print(f"SMOTE skipped: smallest class={smallest} (need >= 2).")
```

SMOTE requires:
- At least 2 classes present
- At least 2 samples per class (to have at least 1 neighbour)

If these conditions aren't met (e.g., early deployment with very little data), training continues without SMOTE - the `class_weight="balanced"` parameter in the RF still helps.

---

## Potential Pitfall: Data Leakage

SMOTE is applied **after** the train-test split, not before:

```python
# CORRECT ORDER (what your code does):
X_train, X_test, y_train, y_test = train_test_split(...)  # Split first
X_train, y_train = smote.fit_resample(X_train, y_train)     # SMOTE on train only
```

If SMOTE were applied **before** splitting, synthetic samples derived from what would become test data could leak information into the training set, inflating the evaluation metrics. Your code does this correctly.

---

## 🔬 Exercise

1. **Why not oversample to 1000 each?** SMOTE balances to the size of the largest class (454). What would happen if you forced it to generate 1000 samples per class? (Hint: think about the ratio of real to synthetic data)

2. **Manual SMOTE:** Take two data points:
   - Point A: `[3000, 0.70, 0.40, 0.85, 0.60, 0.50, 0.65, 0.20, 0.05, 0.80, 2, 6, 5, 30]`
   - Point B: `[4500, 0.55, 0.30, 0.60, 0.50, 0.40, 0.50, 0.35, 0.10, 0.60, 2, 4, 8, 25]`
   - λ = 0.3
   
   Calculate the SMOTE-generated point using `x_new = A + 0.3 × (B - A)`.

3. **Impact analysis:** Looking at the "Before" and "After" distributions in your `rf_metrics.json`, what was the imbalance ratio before SMOTE (ratio of largest to smallest class)? After SMOTE?

---

> **Next:** [Chapter 07 - K-Means Clustering: Behavioural Archetypes →](./07_KMEANS_CLUSTERING.md)
