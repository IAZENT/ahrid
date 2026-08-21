# Figure 6 — AHRID Dual Machine Learning Pipeline: Random Forest Risk Classification and K-Means Behavioural Archetype Discovery

**Thesis placement:** Integration of Machine Learning in Cybersecurity section
**APA7 caption:**
> **Figure 6**
> *AHRID Dual Machine Learning Pipeline: Random Forest Risk Classification and K-Means Behavioural Archetype Discovery*
> Note. SHAP = SHapley Additive exPlanations (Lundberg and Lee, 2017). OSINT = Open-Source Intelligence. RF = Random Forest. The K-Means cluster label is computed first and passed as an input feature to the Random Forest classifier.

---

## Canva Design Spec

### Canvas size
A4 landscape, 1920 x 1080 px. White background.

### Layout: Left-to-right pipeline flow diagram

```
[DATA INPUT]  -->  [K-MEANS]  -->  [RANDOM FOREST]  -->  [SHAP]  -->  [OUTPUT]
```

Full expanded layout:

```
+──────────────+     +──────────────+     +──────────────────+     +──────────+     +──────────────+
|  OSINT FEEDS |     |   K-MEANS    |     |  RANDOM FOREST   |     |   SHAP   |     |  EMPLOYEE    |
|              | --> |  CLUSTERING  | --> |  CLASSIFIER      | --> | EXPLAINER| --> |  DASHBOARD   |
| Phishing.DB  |     |  5 clusters  |     |  200 estimators  |     |          |     |              |
| AlienVault   |     |  Silhouette  |     |  SMOTE balanced  |     | Plain    |     | Risk badge   |
| OTX          |     |  0.268       |     |  Accuracy 91.4%  |     | language |     | Low/Med/High |
+──────────────+     +──────────────+     +──────────────────+     +──────────+     +──────────────+
                            |                      ^
                            |   cluster label      |
                            +---------- as feature-+
                     +──────────────+     +──────────────────+
                     |  USER BEHAV- |     |  14 FEATURES     |
                     |  IOUR LOG    | --> |  scenario scores,|
                     |              |     |  response time,  |
                     |  PostgreSQL  |     |  category perf,  |
                     |  Supabase    |     |  streak count... |
                     +──────────────+     +──────────────────+
```

### Detailed design instructions

**Overall flow:** Horizontal pipeline, left to right. Use rounded rectangles for each stage. Large directional arrows between stages.

**Stage 1 — Data Sources (leftmost, 2 boxes stacked):**
Top box: "OSINT FEEDS"
- Background: #FEF9E7 (light amber)
- Border: #F39C12 (amber) 2px
- Content lines:
  - "Phishing.Database" (icon: shield)
  - "AlienVault OTX"
  - "Read-only feeds"
  - "Refreshed every 6 hours"

Bottom box: "USER BEHAVIOUR LOG"
- Background: #EBF5FB (light blue)
- Border: #3498DB (blue) 2px
- Content:
  - "PostgreSQL / Supabase"
  - "Scenario responses"
  - "Timestamps & streaks"

**Stage 2 — K-Means Clustering:**
Box background: #EAFAF1 (light green)
Border: #27AE60 (green) 2px
Header: "K-MEANS CLUSTERING" Montserrat Bold
Content:
- "5 behavioural archetypes"
- "Silhouette: 0.268"
- Archetype list (small font, 10pt):
  - Overconfident Clicker
  - Cautious Learner
  - Inconsistent Performer
  - Resilient Defender
  - Disengaged Completer

**Key arrow between K-Means and RF:**
Dashed red arrow labelled "cluster label as input feature"
This is the KEY architectural novelty — make it visually prominent.

**Stage 3 — Feature Vector:**
Narrow box: "14-FEATURE BEHAVIOURAL VECTOR"
Background: #F8F9FA (very light grey)
Content (small text): "Scenario accuracy, response time, category performance (8 categories), attempt count, streak, cluster label"

**Stage 4 — Random Forest:**
Largest box — this is the core model.
Background: #EBF5FB (light blue)
Border: #2980B9 (dark blue) 2px
Header: "RANDOM FOREST CLASSIFIER" Montserrat Bold
Content:
- "200 decision trees"
- "SMOTE class balancing"
- "3 risk tiers: Low / Medium / High"
- Metrics box (light background inside):
  - Accuracy: 91.4%
  - Macro F1: 0.8878
  - PR-AUC: 0.9166
  - Cohen's Kappa: 0.8751
  - Baseline F1: 0.3653
  - Improvement: +52.24pp

**Stage 5 — SHAP TreeExplainer:**
Box background: #F5EEF8 (light purple)
Border: #8E44AD (purple) 2px
Header: "SHAP TreeExplainer"
Content:
- "Per-prediction attribution"
- "Plain-language output"
- "Non-technical users"
- "(Lundberg and Lee, 2017)"

**Stage 6 — Output (rightmost):**
Box background: #1B2A4A (dark navy)
Text: white
Header: "EMPLOYEE DASHBOARD"
Content:
- Risk badge: Low / Medium / High (coloured pill)
- "Personalised scenario queue"
- "SHAP explanation card"
- "Manager risk overview (RBAC)"

**Arrows:**
- Main flow arrows: solid, dark navy #1B2A4A, 3px
- K-Means to RF dashed: #C0392B (red), 2px dashed, label "cluster label"
- User log to K-Means and Feature vector: #3498DB solid

### Colour palette
- OSINT/amber: #F39C12 / #FEF9E7
- User log/blue: #3498DB / #EBF5FB
- K-Means/green: #27AE60 / #EAFAF1
- Feature/grey: #95A5A6 / #F8F9FA
- RF/dark blue: #2980B9 / #EBF5FB
- SHAP/purple: #8E44AD / #F5EEF8
- Output/navy: #1B2A4A
- Key arrow: #C0392B
