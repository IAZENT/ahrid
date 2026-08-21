# Chapter 05 - Random Forest Classifier: From Theory to Code

> This is the **heart** of your ML system. By the end of this chapter, you'll understand every line of the RF code and be able to defend it in your thesis viva.

---

## Part 1: The Theory (Ground Up)

### 1.1 What Is a Decision Tree?

A decision tree is a flowchart-like structure where:
- Each **internal node** tests a feature (e.g., "is overall_accuracy < 0.5?")
- Each **branch** represents the outcome of the test
- Each **leaf node** represents a class prediction (e.g., "high risk")

```
                   overall_accuracy < 0.5?
                        /          \
                      YES           NO
                      /              \
              fast_rate > 0.3?    phishing_acc < 0.7?
                /        \           /          \
              YES        NO        YES          NO
              /           \        /              \
         CRITICAL       HIGH    MEDIUM           LOW
```

**How a tree makes a prediction:**
1. Start at the root
2. At each node, check the condition
3. Go left (True) or right (False)
4. When you reach a leaf, that's your prediction

### 1.2 How Does a Tree Learn?

The tree algorithm uses **Gini Impurity** (by default in scikit-learn) to decide the best split at each node.

**Gini Impurity** measures how "mixed" a set of labels is:

```
Gini(S) = 1 - Σ(pᵢ²)
```

Where `pᵢ` is the proportion of class `i` in set `S`.

**Example:**
- Pure set (all "low"): Gini = 1 - 1² = 0 (perfect!)
- Evenly mixed (25% each): Gini = 1 - (0.25² + 0.25² + 0.25² + 0.25²) = 0.75 (maximum impurity)

The algorithm tries every possible split on every feature and picks the one that **reduces Gini impurity the most**.

### 1.3 Why Not Just Use One Tree?

Single decision trees have problems:
- **Overfitting:** They can memorize the training data (create very deep, specific rules)
- **High variance:** Small changes in data can produce completely different trees
- **Poor generalization:** They don't perform well on unseen data

### 1.4 Random Forest = Many Trees Voting

A Random Forest builds **many** decision trees and lets them **vote**:

```
┌──────────┐  ┌──────────┐  ┌──────────┐       ┌──────────┐
│  Tree 1  │  │  Tree 2  │  │  Tree 3  │  ...  │ Tree 200 │
│  "high"  │  │  "high"  │  │ "medium" │       │  "high"  │
└────┬─────┘  └────┬─────┘  └────┬─────┘       └────┬─────┘
     │             │             │                   │
     └─────────────┴─────────────┴───────────────────┘
                         │
                    Majority vote
                         │
                      "high" ← Final prediction
```

**Two key sources of randomness:**
1. **Bootstrap sampling (Bagging):** Each tree trains on a random subset of the data (sampling with replacement)
2. **Random feature selection:** At each split, only a random subset of features is considered

This randomness makes the trees **diverse** - they make different mistakes, and averaging them out gives a better result.

---

## Part 2: Your Code - Hyperparameters Explained

### The Model Configuration

```python
# In train_models.py
model = RandomForestClassifier(
    n_estimators=200,          # Number of trees
    max_depth=None,            # No limit on tree depth
    random_state=42,           # Reproducibility seed
    n_jobs=-1,                 # Use all CPU cores
    class_weight="balanced",   # Handle class imbalance
)
```

Let's understand each parameter:

### `n_estimators=200`

**What:** Build 200 individual decision trees.

**Why 200?** 
- Too few trees (10-50): predictions are noisy
- Too many (1000+): diminishing returns, slower training
- 200 is a good balance for your dataset size (~1000 samples)

**Rule of thumb:** With `n` samples, `sqrt(n)` to `2*sqrt(n)` trees is often sufficient. For 1056 samples, that's ~32 to ~65, so 200 is generous (more = better, just slower).

### `max_depth=None`

**What:** Trees can grow as deep as needed.

**Why unlimited?** 
- In a Random Forest, individual trees are allowed to overfit because bagging+averaging corrects for it
- Limiting depth (e.g., `max_depth=8`) can prevent overfitting but may underfit
- With `class_weight="balanced"`, unlimited depth works well

**Note:** An earlier version of your code used `max_depth=8`. The current version removed the limit for better performance.

### `random_state=42`

**What:** Sets the random number generator seed so results are reproducible.

**Why 42?** It's a convention (from *The Hitchhiker's Guide to the Galaxy*). Any integer works - the point is that running the code twice gives the same result.

### `n_jobs=-1`

**What:** Use all available CPU cores for parallel tree construction.

**Why:** Each tree is independent, so they can be built simultaneously. This makes training ~4-8x faster on a multi-core machine.

### `class_weight="balanced"`

**What:** Automatically adjust sample weights inversely proportional to class frequency.

**How it works:**
```
weight_i = n_samples / (n_classes * n_samples_class_i)
```

For your data:
```json
{
    "0": 568,  // low risk - weight = 1056 / (4 * 568) = 0.465
    "1": 167,  // medium   - weight = 1056 / (4 * 167) = 1.581
    "2": 185,  // high     - weight = 1056 / (4 * 185) = 1.427
    "3": 136   // critical - weight = 1056 / (4 * 136) = 1.941
}
```

This means each "critical" sample is weighted ~4x more than each "low" sample during training. Without this, the model would just predict "low" for everything (since it's the majority class) and still get decent accuracy.

---

## Part 3: The Training Pipeline

### Step 1: Prepare Training Data

```python
def prepare_training_data():
    # Find all users with ≥10 attempts
    user_ids = [
        uid for (uid,) in (
            db.session.query(Attempt.user_id)
            .group_by(Attempt.user_id)
            .having(func.count(Attempt.id) >= MIN_ATTEMPTS_FOR_USER)
            .all()
        )
    ]
    
    rows = []
    labels = []
    for uid in user_ids:
        # Compute label from accuracy (rule-based)
        risk_level = _compute_risk_from_attempts(uid)
        if risk_level not in RISK_LEVEL_ENCODING:
            continue
        
        # Build 14-feature vector
        vec = build_feature_vector_for_user(uid)
        if vec is None:
            continue
        
        rows.append(vec)
        labels.append(RISK_LEVEL_ENCODING[risk_level])
    
    return np.vstack(rows), np.array(labels)
```

**Key insight:** The training **labels** come from the rule-based scorer. So the RF is learning to replicate (and improve on) the rule-based system - it can capture non-linear patterns that simple accuracy-based rules miss.

### Step 2: Train-Test Split

```python
can_stratify = min_class_count >= 2 and len(class_dist) >= 2

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2,           # 80% train, 20% test
    random_state=42,          # Reproducible
    stratify=y if can_stratify else None,  # Maintain class proportions
)
```

**Stratified split** ensures each class appears in both train and test sets in the same proportion:

```
Original:    low=53.8%, medium=15.8%, high=17.5%, critical=12.9%
Train (80%): low≈53.8%, medium≈15.8%, high≈17.5%, critical≈12.9%
Test (20%):  low≈53.8%, medium≈15.8%, high≈17.5%, critical≈12.9%
```

Without stratification, the test set might randomly have 0 "critical" samples, making evaluation meaningless for that class.

### Step 3: SMOTE (see Chapter 06)

### Step 4: Fit the Model

```python
model.fit(X_train, y_train)
```

Under the hood, this:
1. Creates 200 bootstrap samples of `X_train`
2. Builds a decision tree on each sample
3. At each node, considers `sqrt(14) ≈ 3-4` random features for splitting
4. Grows each tree until leaves are pure or no further improvement is possible

### Step 5: Evaluate

```python
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, output_dict=True)
```

---

## Part 4: How Prediction Works (Inference)

```python
class RiskForestPredictor:
    def predict(self, user_id):
        if not self.is_ready:
            return None
        
        vec = self.build_feature_vector(user_id)
        if vec is None:
            return None
        
        x = vec.reshape(1, -1)                    # Shape: (1, 14)
        proba = self.model.predict_proba(x)[0]     # Shape: (4,)
        cls_idx = int(np.argmax(proba))            # Index of highest probability
        cls = int(self.model.classes_[cls_idx])     # Actual class label
        confidence = float(proba[cls_idx])          # How sure the model is
        
        return {
            "predicted_risk_level": RISK_LEVEL_DECODING.get(cls, "unknown"),
            "confidence": round(confidence, 4),
            "feature_importances": self._top_importances(),
        }
```

### Understanding `predict_proba`

Each tree votes, and the probabilities are the **fraction of trees** that voted for each class:

```
Example: 200 trees
  - 12 voted "low"      → proba[0] = 12/200 = 0.06
  - 28 voted "medium"   → proba[1] = 28/200 = 0.14
  - 145 voted "high"    → proba[2] = 145/200 = 0.725
  - 15 voted "critical" → proba[3] = 15/200 = 0.075

Prediction: "high" (class 2) with confidence 72.5%
```

### Feature Importances

```python
def _top_importances(self, k=3):
    importances = self.model.feature_importances_
    names = self.feature_names
    ranked = sorted(zip(names, importances), key=lambda p: -p[1])[:k]
    return {name: round(float(weight), 4) for name, weight in ranked}
```

Feature importances are calculated as the **mean decrease in Gini impurity** across all trees and all splits that use that feature. Higher = more important.

---

## Part 5: Cross-Validation

```python
cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring="f1_macro")
```

### What Is Cross-Validation?

Instead of a single train/test split (which might be lucky or unlucky), k-fold CV:

1. Divides data into k equal parts (folds)
2. Trains on k-1 folds, tests on the remaining 1
3. Repeats k times, rotating the test fold
4. Averages the scores

```
Fold 1: [TEST] [train] [train]  → F1 = 0.854
Fold 2: [train] [TEST] [train]  → F1 = 0.772
Fold 3: [train] [train] [TEST]  → F1 = 0.819
                                   Mean = 0.815 ± 0.034
```

Your results show **F1_macro = 0.815 ± 0.034**, which means the model consistently performs well across different data splits. The small standard deviation (0.034) indicates **stable** performance.

---

## Part 6: Your Actual Results

From `rf_metrics.json`:

```
Accuracy:         88.7%
Macro F1:         85.0%
Cross-val F1:     81.5% ± 3.4%

Per-class performance:
                 Precision  Recall   F1
  low (0):        0.956     0.947   0.952
  medium (1):     0.743     0.765   0.754
  high (2):       0.816     0.838   0.827
  critical (3):   0.885     0.852   0.868
```

### Interpreting These Numbers

- **Low risk** is easiest to predict (F1 = 0.95) because it's the most common class and has clear signals (high accuracy, slow careful responses)
- **Medium risk** is hardest (F1 = 0.75) because it's the "in between" class - features overlap with both low and high
- **Critical risk** does well (F1 = 0.87) because critical users have extreme behaviours (very fast, very wrong)

---

## Part 7: Model Serialisation

```python
import joblib

# Save
joblib.dump(model, model_path)  # → risk_rf_model.pkl (5.9 MB)

# Load
model = joblib.load(model_path)
```

**Why joblib instead of pickle?** `joblib` is optimised for large numpy arrays (which Random Forest models contain internally) and is faster for ML models.

### The Full Artifact Suite

| File | Contains | Size |
|------|----------|------|
| `risk_rf_model.pkl` | The trained Random Forest (200 trees) | ~6 MB |
| `rf_features.json` | List of 14 feature names | 325 bytes |
| `rf_label_encoder.pkl` | Label encoding map | 57 bytes |
| `rf_metrics.json` | Training metrics + SMOTE info + CV | 2 KB |

---

## 🔬 Exercise

1. **Explain this prediction:** If the model predicts "high risk" with 72.5% confidence, what does that confidence value literally mean? (Hint: think about tree voting)

2. **Threshold experiment:** If you changed the risk level thresholds in `_compute_risk_from_attempts()` to different values (say 30/50/70 instead of 40/60/80), how would this affect the training labels and therefore the model?

3. **Feature importance:** The `_top_importances()` method returns the 3 most important features globally. But SHAP (Chapter 08) gives *per-user* importances. Why might the global and per-user importances differ?

4. **Viva question:** "Why did you choose Random Forest over Logistic Regression?" Good answer: RF handles non-linear relationships (e.g., fast answers are risky only when combined with low accuracy), requires no feature scaling, and provides feature importances natively.

---

> **Next:** [Chapter 06 - SMOTE: Handling Class Imbalance →](./06_SMOTE.md)
