---
tags: [exam, ST6047CEM, AHRID, justification]
---

# Section B — Design Justification Question Bank

Related: [[00 - Exam Prep Hub]] | [[03 - Section C Critical Ethical]]

> [!tip] Format every answer here as: **claim → evidence → why the alternative was worse for *this* project specifically.**

> [!question] B1. Why Random Forest over XGBoost, SVM, or deep neural networks?
> > [!success]- Answer
> > - **XAI compatibility:** SHAP TreeExplainer computes *exact* Shapley values for tree ensembles; deep learning would need approximated, less trustworthy explanations for non-technical employees.
> > - **Data scale:** 1,050 synthetic profiles is far too small for a deep neural network to generalise well without severe overfitting risk.
> > - **Robustness with SMOTE-balanced, moderately-sized tabular data:** RF handles mixed feature types and class imbalance well after SMOTE, without extensive hyperparameter tuning like XGBoost/SVM require.
> > - **Result:** macro F1 = 0.889, PR-AUC = 0.9399 — strong performance without the complexity cost.

> [!question] B2. Your K-Means silhouette score is "moderate." Defend including clustering despite this weakness.
> > [!success]- Answer
> > - The silhouette score measures **geometric separation**, not **behavioural validity**. The five archetypes (Overconfident Clicker, Cautious Learner, etc.) map coherently onto established theory (Hadlington 2017's phishing-susceptibility-under-time-pressure findings; Protection Motivation Theory; the compliance-budget model).
> > - The cluster label is included as **one of 18 features**, not the sole risk determinant — its MDI contribution is deliberately modest, so a moderate silhouette doesn't propagate as a dominant source of error into the Random Forest.
> > - It's explicitly flagged as a **limitation**, not hidden — this is what "honest scientific reporting" looks like, and the RF's strong performance (F1=0.889) shows the overall pipeline is robust even with this known softness in one component.

> [!question] B3. Why SMOTE instead of just collecting more real minority-class data?
> > [!success]- Answer
> > - Collecting more **real** data was out of scope — the entire project uses synthetic data specifically to avoid processing real employee PII under IPA 2075.
> > - Generating more synthetic minority samples directly (rather than SMOTE) risks just duplicating statistical patterns already present, adding no new signal.
> > - SMOTE interpolates *between* existing minority points in feature space, creating plausible new examples rather than exact duplicates, which better trains the classifier's decision boundary near the minority classes.
> > - **Risk introduced:** SMOTE can create synthetic points that don't correspond to real behavioural patterns. **Mitigation:** applied only on the *training* set (test set stays real/untouched), k=5 neighbours keeps interpolation local/plausible, and 3-fold CV (F1 std = 0.0094) confirms the model isn't just overfitting to synthetic artefacts.

> [!question] B4. Your evaluation is entirely synthetic data. Justify why this doesn't invalidate RQ1's findings.
> > [!success]- Answer
> > - RQ1 asks whether the **architecture** (clustering + RF + XAI + OSINT) can outperform a rule-based baseline — this is a claim about the *pipeline's technical capability*, which is fully testable on any properly-calibrated dataset, synthetic or real.
> > - The synthetic data was **statistically calibrated** against real-world sources (Nepal Police Cyber Bureau cybercrime statistics, international breach reports), so it isn't arbitrary — it approximates plausible SME behavioural distributions.
> > - What synthetic data does **not** let you claim: that real Kathmandu Valley employees will show a 50-point F1 improvement, or that real-world deployment will replicate these exact numbers.
> > - **What would need to change for real-world claims:** IRB/ethics approval, informed consent from a real partner SME, live behavioural data collection, and re-training/re-validating the model on that real data before repeating the RQ1 evaluation.

> [!question] B5. Explain the *mechanism* by which AHRID enforces non-punitive governance (not just the policy).
> > [!success]- Answer
> > - **RBAC boundary:** managers can query aggregate team-level risk trends via the manager API scope, but individual SHAP explanations and per-user behavioural detail are **not exposed** to the manager role — only to the employee themselves and admins for audit purposes.
> > - **Workflow trigger:** an elevated risk classification triggers the adaptive engine to surface *additional training scenarios* to that employee — it does not write to any HR/performance-review-adjacent table or notify a manager of "low performance."
> > - **Audit design:** actions are logged for accountability (who accessed what), not for surveillance of employee behaviour patterns beyond the training context.
> > - This is a **technical control**, not just a written policy — a malicious admin *could* still misuse the system, which is why organisational governance (documented as a limitation) must sit alongside the technical safeguard.

> [!question] B6. Why Flask instead of Django or FastAPI?
> > [!success]- Answer
> > - AHRID's complexity lives in the **service and ML layers**, not framework-specific scaffolding — Flask's minimalism avoids Django's heavier ORM/admin conventions that add nothing here.
> > - Flask's extension model (Flask-JWT-Extended, Flask-Limiter, Flask-CORS) let each cross-cutting concern (auth, rate limiting, CORS) be added independently and modularly.
> > - FastAPI's async-first design targets I/O-bound concurrency; AHRID's bottleneck is CPU-bound ML inference (RF prediction, SHAP computation), where async offers little benefit over Flask + Gunicorn's multi-worker model.

> [!question] B7. Why K-Means and not DBSCAN/HDBSCAN for clustering?
> > [!success]- Answer
> > - K-Means is simple, computationally efficient, and interpretable at this dataset scale (1,050 profiles) — appropriate for a BSc-scope desk-based project.
> > - DBSCAN/HDBSCAN don't require pre-specifying k, but can label points as "noise," which is undesirable here — **every employee should be assigned to a training archetype**, not excluded.
> > - k=5 was chosen via elbow method + silhouette analysis, and produced 5 archetypes that are independently interpretable against behavioural theory.
> > - **HDBSCAN is explicitly listed as future work** — a genuine limitation acknowledged, not ignored.

> [!question] B8. Why did you choose the specific Random Forest hyperparameters (200 trees, appropriate depth)?
> > [!success]- Answer
> > - **n_estimators=200:** enough trees for stable, low-variance ensemble predictions without excessive training time on a modest dataset.
> > - **Depth/leaf constraints + SMOTE balancing:** prevent overfitting to the training set — validated by the small CV/test performance gap (CV mean F1 0.8604 vs test performance ~0.889, std only 0.0094).
> > - Alternative: exhaustive grid search / Bayesian hyperparameter optimisation would likely yield marginal gains but wasn't prioritised given time constraints across 15 sprints and the fact that current performance already exceeds the H1 threshold (F1 > 0.85).

> [!question] B9. Why did you choose to embed SHAP explanations rather than a simpler feature-importance display?
> > [!success]- Answer
> > - Global feature importance (e.g. MDI) tells you what matters *on average across all predictions* — it can't tell an individual employee *why their specific score* was High Risk.
> > - SHAP gives **per-prediction, per-feature attribution**, which is what "right to information" under IPA 2075 actually requires — a personally meaningful explanation, not a generic model summary.
> > - TreeExplainer specifically is *exact* for tree ensembles (not sampling-approximated like KernelSHAP), so the explanation is mathematically faithful to what the Random Forest actually did.

> [!question] B10. Why did you scope this to Kathmandu Valley SMEs specifically rather than a broader population?
> > [!success]- Answer
> > - Nepal Police Cyber Bureau data shows cybercrime rising sharply (3,906 → 18,926 incidents FY2020–21 to FY2024–25, 40.82% financial fraud) — establishing urgency in this specific context.
> > - Existing platforms (KnowBe4, CybSafe, Proofpoint) assume large-enterprise budgets, English-first workforces, and mature security governance — assumptions that don't hold for resource-constrained Nepali SMEs.
> > - Narrowing scope kept the desk-based, single-researcher, 15-sprint project *feasible* — a broader claim (e.g. "all developing-economy SMEs") would be unsupportable given the calibration data used.
