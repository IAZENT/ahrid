---
tags: [exam, ST6047CEM, AHRID, numbers, cheat-sheet]
---

# Numbers Cheat Sheet

Related: [[00 - Exam Prep Hub]] | [[01 - Section A Short Answer]]

> [!warning] If you memorise nothing else before Sunday, memorise this page.

## ML Performance
| Metric | Value |
|---|---|
| Accuracy | **90.95%** |
| Macro F1-score | **0.889** (0.8890) |
| PR-AUC | **0.9399** |
| Cohen's Kappa (κ) | **0.8684** — almost perfect agreement |
| Rule-based baseline F1 | **0.3868** |
| Improvement over baseline | **+50.21 percentage points** |
| 3-fold CV mean F1 | **0.8604** |
| 3-fold CV std dev | **0.0094** (low → stable, not overfitting) |
| Low Risk precision | **1.000** (perfect — no false escalations) |
| Critical Risk recall | **0.943** (catches almost all genuine threats) |
| Medium Risk precision | **0.784** (weakest — expected class overlap) |

## Dataset & Model Configuration
| Item | Value |
|---|---|
| Synthetic profiles | **1,050** |
| Behavioural features (RF input) | **18** (17 + cluster label) |
| Behavioural features (K-Means input) | **6** standardised features |
| Risk classes | **4** (Low / Medium / High / Critical) |
| Train/test split | **80:20** stratified |
| Cross-validation | **3-fold** stratified |
| K-Means clusters (k) | **5** |
| Silhouette score | **≈0.2645** (moderate) |
| SMOTE result | balanced to **409/class** (~1,636 total) |
| Random Forest trees | **200** |

## K-Means Archetypes
| Cluster | Name | % | Risk |
|---|---|---|---|
| C0 | Overconfident Clicker | 22.7% | High |
| C1 | Cautious Learner | 25.3% | Low |
| C2 | Inconsistent Performer | 20.6% | Medium |
| C3 | Resilient Defender | 17.6% | Low |
| C4 | Disengaged Completer | 13.8% | Critical |

## Project & Methodology
| Item | Value |
|---|---|
| Methodology | Design Science Research (Peffers et al., 2007) |
| DSR phases | **6** |
| Project stages | **5** |
| Agile sprints | **15** |
| Development window | January–July 2026 (per thesis) |
| OSINT sources | **2** — Phishing.Database, AlienVault OTX |
| JWT access token life | **15 minutes** |
| JWT refresh token life | **30 days** |
| Bcrypt salting rounds | **12** |

## Nepal Context (Justification)
| Item | Value |
|---|---|
| Cybercrime incidents FY2020–21 | **3,906** |
| Cybercrime incidents FY2024–25 | **18,926** |
| Financial fraud share of cases | **40.82%** |
| Source | Nepal Police Cyber Bureau (2025) |

## Bibliography & Documentation
| Item | Value |
|---|---|
| Total references | **100** (verified, real DOIs, 0 fabricated) |
| Appendices | **A–L** (current order: A SWOT, B Roles & Responsibilities, C Budget, D Code Explanation File, E Ethical Form, F Gantt Chart, G ML Model Performance, H OSINT Pipeline, then API Reference / Glossary / GUI / DB Schema) |
