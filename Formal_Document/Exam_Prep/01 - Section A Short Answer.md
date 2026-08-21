---
tags: [exam, ST6047CEM, AHRID, short-answer]
---

# Section A — Short Answer Question Bank

Related: [[00 - Exam Prep Hub]] | [[04 - Numbers Cheat Sheet]]

> [!question] Q1. State your two research questions.
> > [!success]- Answer
> > **RQ1 (Technical):** How can an adaptive cybersecurity awareness platform integrate behavioural machine learning, live OSINT threat intelligence, and explainable AI to deliver personalised, context-aware security awareness training for non-technical SME employees in Kathmandu Valley?
> > **RQ2 (Ethical):** How can automated behavioural risk assessment be implemented to protect employee privacy, promote transparency, support non-punitive learning, and comply with Nepal's IPA 2075, while maintaining organisational trust?

> [!question] Q2. State your two hypotheses and whether they were confirmed.
> > [!success]- Answer
> > **H1 (Technical):** Integrating behavioural clustering, supervised ML, XAI, and OSINT will significantly improve risk classification accuracy vs. a rule-based baseline. **Confirmed** — macro F1 = 0.889 vs baseline 0.3868 (+50.21pp), κ = 0.8684.
> > **H2 (Ethical):** Privacy-by-design, XAI, RBAC, and non-punitive governance will satisfy IPA 2075 without processing real personal data. **Confirmed** — full IPA 2075 compliance matrix, zero PII in the ML pipeline.

> [!question] Q3. Name the three stages of the ML pipeline in order and one output each.
> > [!success]- Answer
> > 1. **K-Means clustering** → 5 behavioural archetypes (cluster label)
> > 2. **Random Forest classification** → 4-tier risk prediction (Low/Medium/High/Critical) using 18 features including the cluster label
> > 3. **SHAP TreeExplainer** → plain-language, per-feature explanation for every prediction

> [!question] Q4. Give the exact values for accuracy, macro F1, PR-AUC, and Cohen's Kappa.
> > [!success]- Answer
> > Accuracy = **90.95%**, macro F1 = **0.889** (0.8890), PR-AUC = **0.9399**, Cohen's κ = **0.8684** (almost perfect agreement, Landis & Koch 1977 scale).

> [!question] Q5. What two OSINT sources does AHRID ingest, and what does each provide?
> > [!success]- Answer
> > **Phishing.Database** (GitHub-hosted, community-maintained, daily-refreshed phishing URL list) and **AlienVault OTX** (Open Threat Exchange — crowd-sourced Indicators of Compromise via API).

> [!question] Q6. Name the four IPA 2075 principles addressed and one technical control per principle.
> > [!success]- Answer
> > - **Purpose limitation** → behavioural scores architecturally isolated from PII, never sent to third parties
> > - **Data minimisation** → exactly 18 behavioural features, zero biometric/financial/identity data
> > - **Right to information** → SHAP explanation generated for every prediction
> > - **Informed consent** → consent-first onboarding with withdrawal support

> [!question] Q7. List the five behavioural archetypes with approximate percentages and risk level.
> > [!success]- Answer
> > - **C0 Overconfident Clicker** — 22.7% — High risk
> > - **C1 Cautious Learner** — 25.3% — Low risk
> > - **C2 Inconsistent Performer** — 20.6% — Medium risk
> > - **C3 Resilient Defender** — 17.6% — Low risk
> > - **C4 Disengaged Completer** — 13.8% — Critical risk

> [!question] Q8. How many behavioural features feed the Random Forest, and what are the top 2 by importance?
> > [!success]- Answer
> > **18 features** (17 behavioural + K-Means cluster label). Top 2 by MDI: **overall_accuracy** (~0.31) and **avg_response_time_ms** (~0.11–0.17 depending on version cited).

> [!question] Q9. What are the three JWT/security mechanisms protecting the API?
> > [!success]- Answer
> > **JWT access tokens (15 min)** + **refresh tokens (30 days)** via Flask-JWT-Extended with server-side revocation; **bcrypt password hashing** (12 salting rounds); **Flask-Limiter** rate limiting against credential stuffing; plus RBAC (Employee/Manager/Admin) and Bleach input sanitisation against XSS.

> [!question] Q10. What methodology did you follow, and how many phases/sprints?
> > [!success]- Answer
> > **Design Science Research** (Peffers et al., 2007) — 6 phases (problem identification, objectives, design & development, demonstration, evaluation, communication) — translated into **5 practical project stages** delivered across **15 Agile sprints**.

> [!question] Q11. What class imbalance technique did you use and what was the before/after distribution?
> > [!success]- Answer
> > **SMOTE** (Synthetic Minority Over-sampling Technique). Balanced from an imbalanced set (e.g. ~840 total across 4 skewed classes) up to **409 samples per class** (or ~1,636 total), via k=5 nearest-neighbour interpolation.

> [!question] Q12. What evaluation split and cross-validation did you use?
> > [!success]- Answer
> > **80:20 stratified train/test split**, plus **3-fold stratified cross-validation** giving mean F1 = 0.8604 with std = 0.0094 (low variance → not overfitting).

> [!question] Q13. What is the silhouette score for your K-Means clustering, and is that good?
> > [!success]- Answer
> > **≈0.2645** — a moderate score. Honestly framed as reflecting the natural overlap in real behavioural data rather than a flaw; validity is judged by whether archetypes are *behaviourally meaningful* (they are), not purely by geometric separation.

> [!question] Q14. What tech stack did you use for frontend, backend, and database?
> > [!success]- Answer
> > **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS (SPA), deployed on Vercel.
> > **Backend:** Flask 3.1, Flask-JWT-Extended, Flask-Limiter, Flask-CORS, Gunicorn, deployed on Render.
> > **Database:** PostgreSQL (production) / SQLite (development) via SQLAlchemy ORM + Flask-Migrate.
