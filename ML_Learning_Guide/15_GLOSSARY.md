# Chapter 15 - Glossary & Quick Reference

> Every term, formula, hyperparameter, and constant in one place.

---

## A - Algorithms & Techniques

| Term | Definition | Where Used |
|------|-----------|------------|
| **Random Forest** | Ensemble of decision trees using bagging + random feature subsets | Risk prediction |
| **K-Means** | Centroid-based clustering using iterative assignment + update | User archetypes |
| **SMOTE** | Synthetic Minority Over-sampling Technique - interpolates minority class samples | Training pipeline |
| **SHAP** | SHapley Additive exPlanations - game-theory-based feature attribution | Explainability |
| **TreeExplainer** | Polynomial-time exact SHAP for tree ensembles | SHAP on RF |
| **StandardScaler** | Transforms features to mean=0, std=1 | KMeans preprocessing |
| **Winsorization** | Clipping extreme values at a percentile | Response time outliers |
| **Gini Impurity** | Measures class mixture at tree nodes; 0=pure, 0.75=max(4-class) | Decision tree splits |
| **Exponential Decay** | `weight = λⁱ` for recency weighting | Mastery tracking |
| **Ebbinghaus Curve** | `retained = 0.5^(days/halflife)` for memory decay | Forgetting curve |

---

## B - Feature Vectors

### Random Forest (14 features)

| # | Feature | Type | Range | Computation |
|---|---------|------|-------|-------------|
| 1 | `avg_response_time_ms` | Continuous | 0-20000+ | Mean of all response times |
| 2 | `phishing_accuracy` | Ratio | 0.0-1.0 | Correct/total for phishing_email |
| 3 | `smishing_accuracy` | Ratio | 0.0-1.0 | Correct/total for smishing |
| 4 | `social_engineering_accuracy` | Ratio | 0.0-1.0 | Correct/total for social_engineering |
| 5 | `password_hygiene_accuracy` | Ratio | 0.0-1.0 | Correct/total for password_hygiene |
| 6 | `physical_security_accuracy` | Ratio | 0.0-1.0 | Correct/total for physical_security |
| 7 | `overall_accuracy` | Ratio | 0.0-1.0 | Correct/total across all categories |
| 8 | `fast_attempt_rate` | Ratio | 0.0-1.0 | Attempts < 4000ms / total |
| 9 | `overconfident_rate` | Ratio | 0.0-1.0 | (< 2000ms ∧ wrong) / total |
| 10 | `session_consistency` | Ratio | 0.0-1.0 | Modal session size / total sessions |
| 11 | `job_role_encoded` | Ordinal | 0-7 | receptionist=0 ... other=7 |
| 12 | `total_sessions` | Count | 0-∞ | Distinct session_id count |
| 13 | `days_since_last_session` | Count | 0-∞ | (now - last_attempt).days |
| 14 | `attempts_count` | Count | 0-∞ | Total attempts for user |

### K-Means (6 features)

| # | Feature | Scaling | Note |
|---|---------|---------|------|
| 1 | `avg_response_time_ms` | StandardScaler + Winsorize(P95) | Clipped before scaling |
| 2 | `overall_accuracy` | StandardScaler | - |
| 3 | `accuracy_variance` | StandardScaler | std() of per-category accuracies |
| 4 | `fast_attempt_rate` | StandardScaler | - |
| 5 | `total_sessions` | StandardScaler | - |
| 6 | `session_consistency` | StandardScaler | - |

---

## C - Constants & Hyperparameters

| Constant | Value | File | Purpose |
|----------|-------|------|---------|
| `n_estimators` | 200 | train_models.py | Number of RF trees |
| `random_state` | 42 | Multiple | Reproducibility seed |
| `class_weight` | "balanced" | train_models.py | Auto-adjust for imbalanced classes |
| `n_init` | 10 | kmeans_clustering.py | KMeans initialisations |
| `N_CLUSTERS_DEFAULT` | 5 | kmeans_clustering.py | Target cluster count |
| `FAST_RESPONSE_MS` | 4000 | random_forest_model.py | Threshold for "fast" answers |
| `OVERCONFIDENT_MS` | 2000 | random_forest_model.py | Threshold for "very fast" answers |
| `DECAY_FACTOR` | 0.85 | adaptive_engine.py | Recency weight per attempt |
| `MASTERY_HALFLIFE_DAYS` | 21 | adaptive_engine.py | Forgetting half-life |
| `FORGETTING_FLOOR` | 0.30 | adaptive_engine.py | Minimum decayed mastery |
| `PROMOTION_THRESHOLD` | 0.80 | adaptive_engine.py | Mastery to increase difficulty |
| `DEMOTION_THRESHOLD` | 0.40 | adaptive_engine.py | Mastery to decrease difficulty |
| `MIN_ATTEMPTS_FOR_PREDICT` | 10 | random_forest_model.py | Minimum data for RF |
| `MIN_ATTEMPTS_FOR_CLUSTER` | 5 | kmeans_clustering.py | Minimum data for KMeans |
| `RT_CLIP_PERCENTILE` | 95 | kmeans_clustering.py | Winsorization percentile |

---

## D - Evaluation Metrics

| Metric | Formula | Range | Your Value | Interpretation |
|--------|---------|-------|-----------|----------------|
| Accuracy | correct/total | 0-1 | 0.887 | 88.7% predictions correct |
| F1 (macro) | harmonic mean of P & R, avg over classes | 0-1 | 0.850 | Good balance of precision/recall |
| Cohen's κ | (observed-chance)/(1-chance) | -1 to 1 | ~0.82 | Almost perfect agreement |
| Silhouette | (b-a)/max(a,b) avg | -1 to 1 | 0.230 | Moderate cluster separation |
| Cohen's d | (μ_post-μ_pre)/σ_pooled | -∞ to ∞ | TBD | Effect size of training |
| SUS | Standardised questionnaire | 0-100 | TBD | Usability score |

---

## E - File Quick Reference

| File | Purpose | Key Functions |
|------|---------|--------------|
| `random_forest_model.py` | RF inference + feature vectors | `build_feature_vector_for_user()`, `predict()` |
| `kmeans_clustering.py` | KMeans inference + training | `predict_cluster()`, `train_kmeans()` |
| `shap_explainer.py` | SHAP explanations | `explain_prediction()` |
| `risk_scorer.py` | Rule-based risk scoring | `recalculate_for_user()` |
| `adaptive_engine.py` | Mastery + scenario selection | `start_session()`, `process_attempt()` |
| `scenario_classifier.py` | URL classification | `classify_url()` |
| `behavioral_profiler.py` | Mistake pattern analysis | `cluster_user_mistakes()` |
| `telemetry_service.py` | Engagement scoring | `get_category_engagement_scores()` |
| `train_models.py` | Training pipeline | `main()`, `train_random_forest()` |
| `seed_synthetic_ml_data.py` | Synthetic data generation | `main()` |

---

## F - Five Archetypes

| ID | Name | Colour | Key Signal | Intervention |
|----|------|--------|-----------|--------------|
| 0 | Overconfident Clicker | 🔴 Red | Fast + wrong | Slow-down exercises |
| 1 | Cautious Learner | 🟢 Green | Slow + accurate | Challenge scenarios |
| 2 | Inconsistent Performer | 🟡 Amber | High accuracy variance | Targeted weak-area training |
| 3 | Resilient Defender | 🔵 Blue | Fast + accurate | Peer mentoring role |
| 4 | Disengaged Completer | 🟣 Purple | Low sessions + erratic | Gamified micro-sessions |

---

## G - Risk Levels

| Level | Score Range | Colour | Label Encoding |
|-------|-----------|--------|---------------|
| Low | 0-39.9 | Green | 0 |
| Medium | 40-59.9 | Yellow | 1 |
| High | 60-79.9 | Orange | 2 |
| Critical | 80-100 | Red | 3 |

---

## H - Key Formulas Cheat Sheet

```
Risk Score          = (1 - accuracy) × 100
Gini Impurity       = 1 - Σ(pᵢ²)
SMOTE Interpolation = x + λ(x_nn - x),  λ ∈ [0,1]
StandardScaler      = (x - μ) / σ
Euclidean Distance  = √(Σ(aᵢ - bᵢ)²)
Silhouette          = (b - a) / max(a, b)
Shapley Value       = Sum to (prediction - average)
Mastery (weighted)  = Σ(correct_i × λⁱ) / Σ(λⁱ)
Forgetting Curve    = floor + (mastery - floor) × 0.5^(days/halflife)
Cohen's d           = (μ_post - μ_pre) / σ_pooled
Cohen's κ           = (p_o - p_e) / (1 - p_e)
SUS Score           = (Σ odd(v-1) + Σ even(5-v)) × 2.5
F1 Score            = 2 × (P × R) / (P + R)
```

---

## I - Common Viva Questions & Answers

| Question | Key Points |
|----------|------------|
| "Why Random Forest over Neural Networks?" | Interpretable, works well with tabular data, no GPU needed, feature importances built-in |
| "Why not deep learning?" | Small dataset (~1000 samples), tabular features (not images/text), explainability requirement |
| "How do you handle class imbalance?" | Dual approach: SMOTE + class_weight="balanced" |
| "Why SHAP over LIME?" | TreeExplainer gives exact values for tree models; consistent; additive |
| "Is the silhouette score good enough?" | 0.23 is moderate - expected for behavioural data; clusters are interpretable despite overlap |
| "Why 5 clusters?" | Maps to 5 actionable intervention strategies; domain-driven not data-driven |
| "How do you prevent data leakage?" | SMOTE after split; synthetic data flagged; separate train/test sets |
| "What if a user has very few attempts?" | Guard rails: MIN_ATTEMPTS thresholds + graceful fallback to rule-based |
| "Is this system ethical?" | SHAP transparency, aggregate-only manager view, no GenAI, user controls own data |

---

> **🎓 Congratulations!** You've completed the full ML Learning Guide. You now understand every algorithm, feature, and design decision in your AHRID project. Go ace that thesis defence! 🚀
