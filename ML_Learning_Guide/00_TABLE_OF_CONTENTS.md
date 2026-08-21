# 🧠 AHRID ML & System Architecture - Complete Learning Guide

> **From Zero to Thesis-Ready: A Deep-Dive into Every ML and Intelligent System Component in Your AHRID Project**

---

## Who Is This For?

You built AHRID (Adaptive Human Risk Intelligence Dashboard) with Claude's help. This guide walks you through **every** ML technique, algorithm, and intelligent-system design choice in the project - from first principles - so you can:

1. **Understand** what each piece of code does and *why* it was chosen
2. **Explain** every algorithm in your thesis viva/defence
3. **Reproduce** the work from scratch if asked
4. **Extend** the system confidently in the future

---

## Table of Contents

| # | Chapter | File | What You'll Learn |
|---|---------|------|-------------------|
| 01 | [Project Overview & ML Architecture](./01_PROJECT_OVERVIEW.md) | - | The big picture: how all ML pieces fit together |
| 02 | [The Data Foundation](./02_DATA_FOUNDATION.md) | `models/attempt.py`, `seed_*.py` | Feature engineering starts here - understanding your data |
| 03 | [Risk Scoring - The Rule-Based Baseline](./03_RISK_SCORING.md) | `risk_scorer.py` | Inverse-accuracy scoring, composite risk, level bucketing |
| 04 | [Feature Engineering Deep-Dive](./04_FEATURE_ENGINEERING.md) | `random_forest_model.py`, `kmeans_clustering.py` | How raw attempts become 14 RF features and 6 KMeans features |
| 05 | [Random Forest Classifier - From Theory to Code](./05_RANDOM_FOREST.md) | `random_forest_model.py`, `train_models.py` | Decision trees → ensemble → your 14-feature risk predictor |
| 06 | [SMOTE - Handling Class Imbalance](./06_SMOTE.md) | `train_models.py` | Why balanced classes matter and how SMOTE synthesises samples |
| 07 | [K-Means Clustering - Behavioural Archetypes](./07_KMEANS_CLUSTERING.md) | `kmeans_clustering.py` | Unsupervised grouping → 5 human archetypes |
| 08 | [SHAP Explainability - Why the Model Decided](./08_SHAP_EXPLAINABILITY.md) | `shap_explainer.py` | Game-theory-based feature attribution for transparency |
| 09 | [The Adaptive Engine - Intelligent Tutoring](./09_ADAPTIVE_ENGINE.md) | `adaptive_engine.py` | Mastery tracking, forgetting curves, spaced repetition |
| 10 | [Scenario Classification - URL Intelligence](./10_SCENARIO_CLASSIFIER.md) | `scenario_classifier.py` | Heuristic pattern matching for threat categorisation |
| 11 | [Behavioural Telemetry & Profiling](./11_BEHAVIORAL_TELEMETRY.md) | `telemetry_service.py`, `behavioral_profiler.py` | Dwell time, answer changes, engagement scoring |
| 12 | [Model Training Pipeline End-to-End](./12_TRAINING_PIPELINE.md) | `train_models.py`, `seed_synthetic_ml_data.py` | The complete workflow from raw data to pickled models |
| 13 | [Evaluation & Thesis Metrics](./13_EVALUATION_METRICS.md) | `eval` endpoints | F1, Cohen's Kappa, Cohen's d, SUS scoring |
| 14 | [Non-ML Intelligent Systems](./14_NON_ML_SYSTEMS.md) | Various | OSINT pipeline, sanitisation, scheduler, notifications |
| 15 | [Glossary & Quick Reference](./15_GLOSSARY.md) | - | Every term, formula, and hyperparameter in one place |
| 16 | [Combinatorial Scenario Generation](./16_COMBINATORIAL_GENERATION.md) | `seed_scenarios.py` | Scaling quality content dynamically using combinatorics |
| 17 | [Simple Explainer - Every Feature in Plain English](./17_SIMPLE_EXPLAINER.md) | - | All ML concepts with relatable analogies and one-line viva answers |
| 18 | [Viva Q&A - Complete Defense Guide](./18_VIVA_QA.md) | - | 33 full questions, 4 examiner traps, lightning round, paper references |

---

## How to Read This Guide

- **If preparing for defense/viva:** Start with [00_DEFENSE_PREP.md](./00_DEFENSE_PREP.md) - Q&A format, your actual results, what to say out loud.
- **If you're in a rush:** Read Chapters 01, 05, 07, 08 - they cover the core ML.
- **If preparing for viva:** Read everything in order - each chapter builds on the previous.
- **If you want hands-on:** Each chapter includes 🔬 **Exercises** to try on your own data.

| 00 | [**DEFENSE PREP** ← Start Here](./00_DEFENSE_PREP.md) | - | Q&A format, your results, what to say in the viva |

---

## Your ML Stack at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                    AHRID ML Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Raw Data (Attempts)                                           │
│       │                                                         │
│       ├──► Risk Scorer (rule-based baseline)                    │
│       │       └──► Composite score + 8 category scores          │
│       │                                                         │
│       ├──► Feature Engineering (14 features)                    │
│       │       └──► Random Forest Classifier (supervised)        │
│       │               ├──► Risk level prediction                │
│       │               └──► SHAP explainability                  │
│       │                                                         │
│       ├──► Feature Engineering (6 features)                     │
│       │       └──► K-Means Clustering (unsupervised)            │
│       │               └──► 5 behavioural archetypes             │
│       │                                                         │
│       └──► Adaptive Engine                                      │
│               ├──► Mastery tracking (recency-weighted)          │
│               ├──► Forgetting curve (exponential decay)         │
│               ├──► Difficulty progression (promote/demote)      │
│               └──► Smart scenario selection                     │
│                                                                 │
│   OSINT Feeds ──► Scenario Classifier (heuristic)               │
│                       └──► Lure type + difficulty + category    │
│                                                                 │
│   Training Pipeline                                             │
│       ├──► SMOTE (class balancing)                              │
│       ├──► Cross-validation (3-fold)                            │
│       └──► Metrics (F1, accuracy, silhouette, Cohen's κ)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

> **Next:** [Chapter 01 - Project Overview & ML Architecture →](./01_PROJECT_OVERVIEW.md)
