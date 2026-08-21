# Chapter 12 - Model Training Pipeline End-to-End

> This chapter traces the **complete workflow** from zero data to production-ready ML models.

---

## The Full Pipeline

```
Step 1: Seed Scenarios      → ~500+ training questions created
Step 2: Seed Users           → Demo users + synthetic profiles
Step 3: Seed Synthetic Data  → 1050 users × 15-40 attempts each
Step 4: Train Models         → RF + KMeans fitted and saved
Step 5: Deploy               → Models loaded lazily on first request
```

---

## Step-by-Step Walkthrough

### Step 1: Seed the Scenario Catalogue

```bash
python seed_scenarios.py           # 24 hand-crafted scenarios
python seed_more_scenarios.py      # ~500 templated scenarios
```

These are **idempotent** - re-running skips existing scenarios (matched by title).

### Step 2: Seed Users

```bash
python seed_users.py               # 5 demo users (admin, manager, employees)
```

### Step 3: Generate Synthetic ML Data

```bash
python seed_synthetic_ml_data.py
```

This creates **1,050 synthetic users** across 5 risk profiles (see Chapter 02). The key output:

```
  critical:  200 users, accuracy=15%
  high:      200 users, accuracy=35%
  medium:    250 users, accuracy=60%
  low:       250 users, accuracy=82%
  very_low:  150 users, accuracy=92%

Created 1050 synthetic users with ~25,000 attempts
Generated 2100 awareness assessments and 1050 SUS responses
```

### Step 4: Train Models

```bash
python train_models.py
```

This runs the `main()` function:

```python
def main():
    app = create_app()
    with app.app_context():
        # --- Random Forest ---
        X, y = prepare_training_data()
        if X is not None and len(set(y.tolist())) >= 2:
            train_random_forest(X, y, rf_path)
        
        # --- K-Means ---
        kmeans_result = train_kmeans()
        if kmeans_result is not None:
            n = reassign_all_users()
            print(f"KMeans: trained + assigned {n} users")
```

### The Training Output

```
SMOTE: {0: 454, 1: 133, 2: 148, 3: 109} → {0: 454, 1: 454, 2: 454, 3: 454} (k=5)
RF trained on 1056 samples → accuracy=0.887
KMeans: trained + assigned 1057 users (inertia=2547.035)
```

### Artifacts Produced

```
ml_models/
├── risk_rf_model.pkl       ← 5.9 MB (200-tree Random Forest)
├── rf_features.json        ← Feature name list
├── rf_label_encoder.pkl    ← Risk level encoding
├── rf_metrics.json         ← Training metrics + SMOTE info
├── user_clusters.pkl       ← KMeans bundle (scaler + model)
├── kmeans_features.json    ← Feature name list
└── kmeans_metrics.json     ← Clustering metrics
```

---

## Admin-Triggered Retrain

In production, retraining is triggered via the admin panel:

```
POST /api/v1/admin/retrain-models
```

This runs both RF and KMeans independently in a background job. Progress is polled via:

```
GET /api/v1/admin/retrain-status
```

The admin dashboard shows model status cards with:
- Last trained timestamp
- Number of samples used
- Accuracy / silhouette score
- Current job status (idle / running / completed)

---

## Model Loading (Lazy Initialisation)

Models are loaded **lazily** - not at app boot time:

```python
class RiskForestPredictor:
    def __init__(self):
        self.model = None
        self.load_model()  # Tries to load from disk
    
    def load_model(self):
        try:
            self.model = joblib.load(self.model_path)
        except FileNotFoundError:
            self.model = None  # Pass-through mode
    
    @property
    def is_ready(self):
        return self.model is not None
```

If the `.pkl` file doesn't exist, the predictor works in "pass-through mode" - `predict()` returns `None`, and the system falls back to rule-based scoring.

---

## 🔬 Exercise

1. **Run the pipeline yourself:**
   ```bash
   cd backend
   source .venv/bin/activate
   python seed_synthetic_ml_data.py
   python train_models.py
   ```
   Check the output - how many samples? What accuracy?

2. **Inspect the metrics:**
   ```bash
   cat ml_models/rf_metrics.json | python -m json.tool
   cat ml_models/kmeans_metrics.json | python -m json.tool
   ```

3. **Experiment:** What happens if you delete `ml_models/risk_rf_model.pkl` and restart the Flask app? Does the app crash? (It shouldn't - test it!)

---

> **Next:** [Chapter 13 - Evaluation & Thesis Metrics →](./13_EVALUATION_METRICS.md)
