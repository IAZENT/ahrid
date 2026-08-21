# AHRID Thesis Defence Preparation Guide

**Candidate:** Rupesh Kumar Thakur (CUID: 230548)
**Programme:** BSc (Hons) Cybersecurity
**Title:** Adaptive Human-Risk Intelligence Dashboard (AHRID): An ML-Driven Cybersecurity Awareness Platform for SMEs in Nepal
**Methodology:** Design Science Research (Peffers et al., 2007) + Agile (15 sprints)
**Date prepared:** 15 July 2026

---

## Table of Contents

1. [Opening & General Questions](#1-opening--general-questions)
2. [Motivation & Problem Statement](#2-motivation--problem-statement)
3. [Research Questions & Hypotheses](#3-research-questions--hypotheses)
4. [Literature & Theoretical Foundations](#4-literature--theoretical-foundations)
5. [Research Methodology (DSR)](#5-research-methodology-dsr)
6. [Technical Architecture & Implementation](#6-technical-architecture--implementation)
7. [Machine Learning Pipeline](#7-machine-learning-pipeline)
8. [SHAP & Explainability (Deep Dive)](#8-shap--explainability-deep-dive)
9. [K-Means Clustering (Deep Dive)](#9-k-means-clustering-deep-dive)
10. [OSINT & Threat Intelligence](#10-osint--threat-intelligence)
11. [Ethical, Privacy & Legal Considerations](#11-ethical-privacy--legal-considerations)
12. [Evaluation & Results](#12-evaluation--results)
13. [Limitations, Validity & Generalisability](#13-limitations-validity--generalisability)
14. [Future Work & Continuation](#14-future-work--continuation)
15. [Nasty / Curveball Questions](#15-nasty--curveball-questions)
16. [Contribution to Knowledge](#16-contribution-to-knowledge)
17. [Personal Reflection & Process](#17-personal-reflection--process)
18. [Viva Soft-Skills & Strategy](#18-viva-soft-skills--strategy)
19. [Essential Reading List](#19-essential-reading-list)
20. [Quick-Reference Numbers to Memorise](#20-quick-reference-numbers-to-memorise)

---

## 1. Opening & General Questions

### Q1.1: Can you summarise your thesis in 3 minutes?

"My thesis addresses the cybersecurity awareness gap in Kathmandu Valley SMEs. These organisations face rising phishing threats but can't afford enterprise-grade Security Awareness Training platforms like KnowBe4 or Proofpoint. I designed and built AHRID — an Adaptive Human-Risk Intelligence Dashboard — using Design Science Research methodology. AHRID integrates four components: K-Means behavioural clustering to identify employee archetypes, a Random Forest classifier for risk prediction, SHAP for explainable AI so employees understand their scores, and a live OSINT pipeline that transforms real phishing intelligence into training scenarios. The system achieved a macro F1-score of 0.889 and Cohen's κ of 0.8684, significantly outperforming a rule-based baseline by over 50 percentage points. Ethically, the platform complies with Nepal's Individual Privacy Act 2075 through privacy-by-design — no PII enters the ML pipeline, and elevated risk triggers additional training, not disciplinary action. The key contribution is demonstrating that adaptive, explainable, privacy-preserving cybersecurity awareness training is technically feasible and affordable for developing-economy SMEs."

### Q1.2: Now summarise it in one sentence.

"AHRID is an adaptive cybersecurity awareness platform that uses behavioural clustering, Random Forest classification, SHAP explainability, and live OSINT threat feeds to deliver personalised, privacy-preserving phishing training for Nepali SMEs, achieving macro F1 of 0.889 against a 0.387 baseline."

### Q1.3: What is the single idea that binds your thesis together?

The unifying idea is **adaptive personalisation through explainable machine learning**. Every component — clustering, classification, SHAP, OSINT, the adaptive engine — serves the goal of giving each employee a tailored, transparent, continuously evolving security training experience rather than a generic one-size-fits-all approach.

### Q1.4: What are the strongest parts of your work?

1. **The ML pipeline integration** — clustering → RF → SHAP → adaptive engine is end-to-end and fully functional
2. **Explainability** — SHAP provides genuine per-prediction transparency, not just a black-box score
3. **Ethical rigour** — privacy-by-design is architectural, not bolted on; non-punitive governance is embedded
4. **OSINT automation** — real-world threat intelligence is automatically transformed into training content
5. **Strong quantitative results** — F1=0.889, κ=0.8684, PR-AUC=0.9399

### Q1.5: What are the weakest parts of your work?

1. **Synthetic data** — all evaluation uses generated profiles, not real employee behaviour
2. **No user testing** — the platform hasn't been deployed with real SME employees
3. **Moderate silhouette coefficient** — cluster separation is limited (inherent to behavioural data)
4. **No longitudinal evaluation** — can't assess whether behavioural improvement persists over time
5. **English-only** — limits accessibility for Nepali-speaking employees

### Q1.6: What is original about your work? Where is the novelty?

Three novel contributions: (1) combining K-Means + RF + SHAP + live OSINT in a single adaptive SAT platform — no existing platform integrates all four; (2) designing for Nepal's IPA 2075 compliance specifically, addressing a regulatory context no prior SAT research has covered; (3) the non-punitive, explainable governance model that gives employees agency over their risk classification.

### Q1.7: Where did you go wrong?

I would have started the ethics approval process earlier if I were planning real-user deployment. I also underestimated the complexity of OSINT feed normalisation — different sources have different schemas and reliability levels. Finally, the synthetic data generation could have been more sophisticated using agent-based modelling instead of statistical distributions.

---

## 2. Motivation & Problem Statement

### Q2.1: Why did you choose this topic?

Nepal has over 80% internet penetration (Kemp, 2025) but cybersecurity awareness lags far behind. The Nepal Police Cyber Bureau reports rising phishing and social engineering attacks annually, yet most Kathmandu Valley SMEs lack dedicated security teams. Existing commercial SAT platforms (KnowBe4, Proofpoint) are expensive, one-size-fits-all, English-only, and designed for Western enterprises. I wanted to build something that addresses the actual needs of Nepali SMEs — adaptive, affordable, explainable, and privacy-respecting.

### Q2.2: Why focus on SMEs specifically?

SMEs represent the vast majority of businesses in Kathmandu Valley. They typically have fewer than 50 employees, no CISO, and minimal security budgets. Research (Kabanda, 2018; Beautement et al., 2008) shows that SMEs suffer disproportionately from phishing because they can't afford enterprise SAT licenses or dedicated security training staff. AHRID targets this gap.

### Q2.3: Why Nepal? Isn't this a global problem?

While the human risk problem is global, Nepal's context is unique: (1) IPA 2075 is a relatively new privacy law with limited AI governance guidance; (2) the threat landscape is shaped by rapid digitisation without corresponding security maturity; (3) no SAT platform currently caters to Nepali SME constraints (language, cost, compliance). I scoped to Kathmandu Valley to keep the study feasible — generalisability beyond this region is explicitly a limitation and future work direction.

### Q2.4: What gap does your work fill that existing research doesn't?

The literature review identified three gaps: (1) most SAT platforms use static, rule-based risk scoring rather than ML-driven adaptive assessment; (2) few integrate real-time OSINT threat feeds into training content; (3) almost none provide explainable AI so employees understand *why* they were classified at a given risk level. AHRID combines all three with privacy-by-design in a developing-country context.

### Q2.5: Who is the target user?

Non-technical employees in Kathmandu Valley SMEs — people who handle email, click links, and interact with web services daily but lack security training. Three roles: Employee (trains and views dashboard), Manager (team risk overview), Admin (user/scenario/OSINT management).

### Q2.6: What is the real-world impact of the problem you're addressing?

Verizon's 2023 DBIR reports that 74% of data breaches involve the human element. For SMEs without security budgets, a single successful phishing attack can mean credential theft, financial loss, or business closure. Nepal Police Cyber Bureau data shows rising cybercrime year-on-year, but there's no locally adapted training platform to address this.

### Q2.7: Is this problem already solved by commercial tools?

Partially, but not for this context. KnowBe4, Proofpoint, and Cofense address enterprise needs with proprietary, expensive, opaque scoring. They don't provide XAI, don't integrate live OSINT into adaptive training, and don't address IPA 2075. For a 20-person Nepali SME, they're neither affordable nor suitable.

---

## 3. Research Questions & Hypotheses

### Q3.1: State your research questions.

**RQ1 (Technical):** To what extent can an integrated approach combining behavioural clustering (K-Means), supervised classification (Random Forest), explainable AI (SHAP), and live OSINT threat feeds improve the accuracy and adaptiveness of cybersecurity risk assessment compared with a conventional rule-based baseline?

**RQ2 (Ethical):** How can privacy-by-design, explainable AI, and non-punitive governance be embedded into an adaptive cybersecurity awareness platform to ensure compliance with Nepal's Individual Privacy Act 2075 and promote ethical organisational deployment?

### Q3.2: State your hypotheses.

**H1 (Technical):** Integrating clustering, supervised ML, XAI, and OSINT within a single platform will achieve macro F1-score > 0.85 and substantial Cohen's κ agreement.

**H2 (Ethical):** Embedding privacy-by-design, XAI, RBAC, data minimisation, and non-punitive governance will improve acceptance and support ethical deployment consistent with IPA 2075.

### Q3.3: How did your research questions emerge?

They emerged from the gap analysis in the literature review. RQ1 was driven by the observation that existing SAT platforms lack adaptive, ML-driven assessment. RQ2 was driven by ethical concerns around employee behavioural monitoring, particularly in a jurisdiction (Nepal) with a new but under-explored privacy law.

### Q3.4: How do RQ1 and RQ2 relate?

They represent the dual evaluation axes — technical effectiveness and responsible deployment. A system that's accurate but opaque, or transparent but inaccurate, fails. Both must be satisfied simultaneously. This mirrors the AI4People framework (Floridi et al., 2018) which argues that beneficial AI requires both capability and ethical governance.

### Q3.5: Did you confirm or reject your hypotheses?

**H1 — Confirmed:** Macro F1 = 0.889 (exceeds 0.85), Cohen's κ = 0.8684 (almost perfect per Landis & Koch, 1977). PR-AUC = 0.9399. CV mean = 0.8604 ± 0.0094.

**H2 — Supported:** No PII in the pipeline. All 18 features are behavioural. SHAP provides per-prediction explanations. Non-punitive governance embedded. Full IPA 2075 alignment demonstrated. Note: H2 is "supported" rather than "confirmed" because full validation requires real organisational deployment.

### Q3.6: Why macro F1 and not accuracy?

The dataset has class imbalance. Accuracy can be misleadingly high if the model favours the majority class. Macro F1 gives equal weight to all four risk classes (Low, Medium, High, Critical), penalising models that neglect minority classes. PR-AUC is also reported because it is more informative than ROC-AUC for imbalanced problems.

### Q3.7: Why did you set the F1 threshold at 0.85?

0.85 represents "good" classification performance in the literature — above this threshold, the model is considered reliable enough for decision support. It's also above what conventional approaches (rule-based baselines) can achieve, making it a meaningful improvement target rather than an arbitrary number.

### Q3.8: Could you have had a null hypothesis?

Yes — H0 would be "the integrated ML approach does not significantly improve classification over the rule-based baseline." The 50.21 percentage-point improvement in macro F1 (0.387 → 0.889) and near-perfect κ effectively reject this null hypothesis, though formal statistical hypothesis testing (e.g., McNemar's test) was not performed. This is acknowledged.

---

## 4. Literature & Theoretical Foundations

### Q4.1: What theories underpin your work?

Four key theories:

1. **Protection Motivation Theory (PMT)** — Rogers, 1975, 1983. Security behaviour depends on threat appraisal (perceived severity + vulnerability) and coping appraisal (self-efficacy + response efficacy). AHRID uses PMT to frame scenarios — showing *why* a URL is dangerous (threat) and *how* to identify it (coping).

2. **Technology Acceptance Model (TAM)** — Davis, 1989. Perceived usefulness and ease of use determine adoption. AHRID targets TAM via SHAP explanations (usefulness — users understand their score) and a clean dashboard (ease of use).

3. **Prospect Theory** — Kahneman & Tversky, 1979. People are loss-averse — they respond more strongly to potential losses than equivalent gains. AHRID frames phishing outcomes in terms of what could be *lost* (data breach, credential theft) rather than abstract risk scores.

4. **Ebbinghaus Forgetting Curve** — Ebbinghaus, 1885. Knowledge retention decays exponentially without reinforcement. AHRID's adaptive engine implements spaced repetition — revisiting scenarios the employee previously failed.

### Q4.2: How does Protection Motivation Theory specifically influence your design?

PMT has two appraisal pathways. **Threat appraisal**: AHRID's scenarios show real phishing URLs (sanitised) so employees perceive genuine severity and personal vulnerability. **Coping appraisal**: SHAP explanations and progressive difficulty levels build self-efficacy ("I can spot phishing") and response efficacy ("checking the URL domain works"). If either appraisal pathway fails, the employee won't change behaviour — AHRID addresses both.

### Q4.3: How does Prospect Theory influence scenario design?

Scenario framing emphasises losses: "If you click this link, your credentials could be stolen" rather than "If you avoid this link, you stay safe." Loss framing produces stronger behavioural responses per Kahneman & Tversky. The lure types (Urgency, Fear, Authority) exploit the same psychological mechanisms that real phishing uses, teaching employees to recognise them.

### Q4.4: How does your literature review structure support your arguments?

Seven subsections building toward the gap: (1) evolving cyber threat landscape → establishes the problem exists; (2) human factors in cybersecurity → establishes people are the vulnerability; (3) current SAT limitations → establishes existing solutions fail; (4) ML in cybersecurity → establishes ML can help; (5) XAI in security → establishes transparency matters; (6) privacy/ethics → establishes governance is critical; (7) Nepal-specific context → establishes the specific gap AHRID fills.

### Q4.5: How did you decide which sources to include in your literature review?

Selection criteria: (1) peer-reviewed publications from reputable journals/conferences (ACM, IEEE, Springer, MDPI); (2) recency — prioritised 2018–2026 sources, with seminal works (Rogers 1975, Kahneman & Tversky 1979) included for theoretical foundations; (3) relevance to cybersecurity awareness, ML-based risk assessment, or XAI; (4) Nepal-specific data from official government sources (Nepal Police Cyber Bureau, Nepal Law Commission).

### Q4.6: What are the key case studies you reference?

- **KnowBe4** — market-leading SAT but proprietary scoring, no XAI, enterprise pricing
- **Proofpoint Security Awareness** — similar limitations, no OSINT integration
- **PhishMe/Cofense** — phishing simulation focus but uses live phishing (ethical concerns)
- **Nepal Police Cyber Bureau reports** — local threat statistics for synthetic data calibration
- **Verizon DBIR 2023** — "74% of breaches involve human element"

### Q4.7: Which are the three most important papers that relate to your thesis?

1. **Lundberg & Lee (2017)** — SHAP. Without this, the XAI component wouldn't exist. It provides the mathematical foundation for feature-level explanations.
2. **Peffers et al. (2007)** — DSRM. This defines the entire research methodology — every phase of my project maps to their six-phase model.
3. **Floridi et al. (2018)** — AI4People. This frames the ethical argument — AI systems must be beneficial, non-maleficent, autonomous, just, and explicable.

### Q4.8: What published work is closest to yours? How is yours different?

The closest work is commercial SAT platforms (KnowBe4, Proofpoint) and academic ML-based phishing detection systems. My work differs in three ways: (1) it's a complete *training* platform, not just a detector; (2) it integrates XAI at the employee-facing level, not just for analysts; (3) it's designed for developing-country SME constraints (cost, privacy law, language).

### Q4.9: What are the most recent major developments in your area?

- Growing integration of LLMs into phishing generation and detection (2024–2026)
- Increased regulatory attention to AI governance (EU AI Act 2024, Nepal's evolving data protection landscape)
- Rise of XAI requirements in enterprise security tools
- Cloud-based phishing-as-a-service making attacks more accessible to low-skill attackers

### Q4.10: Who has had the strongest influence on your subject area?

In theory: **Rogers** (PMT), **Kahneman & Tversky** (behavioural economics). In ML: **Breiman** (RF), **Lundberg** (SHAP). In DSR: **Hevner** and **Peffers**. In AI ethics: **Floridi**. In cybersecurity human factors: **Sasse** and **Beautement** (compliance budget concept).

---

## 5. Research Methodology (DSR)

### Q5.1: Why Design Science Research and not another methodology?

DSR was chosen because the objective is to *create and evaluate an artefact* (AHRID), not observe an existing phenomenon. Alternatives and why rejected:

| Methodology | Why Rejected |
|-------------|-------------|
| Experimental research | Requires real participants, ethics approval, long deployment — infeasible for BSc |
| Survey/interview | Answers "what do SMEs need?" but doesn't build or evaluate a solution |
| Case study | Studies existing platform, doesn't create a new one |
| Action research | Requires iterative deployment with an organisation; no partner available |
| Grounded theory | Generates theory from data; not appropriate for artefact creation |

### Q5.2: What are Hevner's 7 DSR guidelines and how do you meet them?

1. **Design as artefact** — AHRID is the artefact (software platform)
2. **Problem relevance** — addresses real SME cybersecurity awareness gap in Nepal
3. **Design evaluation** — RF metrics, baseline comparison, OSINT functional testing
4. **Research contributions** — novel integration of clustering + RF + SHAP + OSINT for SAT
5. **Research rigour** — formal ML evaluation (F1, κ, PR-AUC, CV), structured DSRM phases
6. **Design as search process** — iterative Agile sprints refined the artefact over 15 iterations
7. **Communication of research** — thesis document + deployed prototype

### Q5.3: Explain the six DSRM phases and how you followed them.

1. **Problem identification** — literature review revealed SAT limitations for developing-country SMEs
2. **Objectives** — defined RQ1/RQ2 and H1/H2 with measurable thresholds
3. **Design & development** — built AHRID (Flask + React + ML pipeline) over 15 Agile sprints
4. **Demonstration** — deployed prototype with synthetic data, functional OSINT pipeline
5. **Evaluation** — quantitative ML metrics (F1, κ, PR-AUC) + ethical compliance analysis
6. **Communication** — this thesis document

### Q5.4: How does Agile complement DSR?

DSR provides the overarching research framework; Agile provides the development process. DSR's iterative "design-evaluate" cycle maps naturally to Agile sprints. Each sprint delivered a functional increment (e.g., Sprint 3 = K-Means clustering, Sprint 7 = SHAP integration), and each DSR phase comprised multiple sprints. This combination is well-established in IS research.

### Q5.5: Why desk-based? Why not deploy with real users?

Three reasons: (1) **Ethics** — processing real employee behavioural data requires institutional ethics approval and organisational consent, exceeding BSc scope; (2) **Feasibility** — deploying in a live SME requires months of organisational buy-in, training, monitoring; (3) **Privacy** — IPA 2075 compliance is simpler to demonstrate with synthetic data where no PII exists. Real-user validation is the #1 future work priority.

### Q5.6: How were your synthetic datasets generated?

1,050 behavioural profiles generated using controlled random distributions calibrated against: (a) Nepal Police Cyber Bureau cybercrime statistics, (b) Verizon DBIR breach distributions, (c) peer-reviewed behavioural cybersecurity literature. Each profile has 18 behavioural features. Distributions designed to produce realistic class imbalance.

### Q5.7: How do you justify 1,050 profiles?

Provides ~210 test samples (20% split) — sufficient for per-class evaluation across 4 risk categories. Three-fold CV on training set assesses generalisation. The number balances statistical power with computational feasibility. Larger synthetic datasets wouldn't add validity since the data is already synthetic.

### Q5.8: Why 80:20 split and 3-fold CV?

80:20 is standard for this dataset size. Three-fold (not 5 or 10) chosen because stratified post-SMOTE split provides sufficient samples per fold. CV mean = 0.8604 ± 0.0094 shows low variance, confirming the model isn't overfitting to a particular split.

### Q5.9: How did you manage project risks?

Formal risk register (Table 4) identified 6 risks with likelihood/impact/mitigation: synthetic data validity (Medium/High), OSINT availability (Low/Medium), ML overfitting (Medium/Medium), privacy compliance (Low/High), schedule management (Medium/Medium), deployment infrastructure (Low/Low). Each reviewed per sprint.

### Q5.10: What were the crucial research decisions you made?

1. Using synthetic data instead of attempting real-user deployment
2. Choosing Random Forest over deep learning (interpretability trade-off)
3. Integrating OSINT as automated pipeline rather than manual curation
4. Designing for IPA 2075 specifically rather than GDPR
5. Using non-punitive governance as an architectural principle, not just policy

### Q5.11: How did you evaluate your artefact? Is this evaluation rigorous enough?

Evaluation was both quantitative (ML metrics: accuracy, F1, κ, PR-AUC, CV) and qualitative (ethical compliance analysis against IPA 2075, architectural review of privacy-by-design). For a BSc-level DSR project, this represents a thorough desk-based evaluation. The limitation is the absence of real-world deployment evaluation, which is explicitly acknowledged.

---

## 6. Technical Architecture & Implementation

### Q6.1: Describe your tech stack and justify each choice.

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Backend | Flask 3.1 (Python) | Lightweight, ML-ecosystem native (scikit-learn, SHAP, joblib) |
| Frontend | React 18 + TypeScript + Vite | Type safety, component architecture, fast HMR |
| Styling | Tailwind CSS | Utility-first, rapid UI development, small bundle |
| Database | PostgreSQL | ACID compliance, JSON support, production-grade, free |
| ORM | SQLAlchemy | Declarative models, Alembic migrations |
| ML | scikit-learn, SHAP, joblib | Industry-standard, well-documented |
| Auth | Flask-JWT-Extended | JWT access (15 min) + refresh (30 days) + server-side blocklist |
| Deployment | Render (backend) + Vercel (frontend) | Free-tier, CI/CD, HTTPS by default |

### Q6.2: How many API endpoints and how are they organised?

61 REST API endpoints across 8 Flask blueprints:
- **auth** (10): register, login, logout, refresh, profile, password change/reset
- **training** (9): scenarios, sessions, progress, adaptive recommendations
- **scores** (3): risk score retrieval and history
- **notifications** (5): CRUD + mark-read
- **manager** (6): team overview, risk aggregation, training assignment
- **eval** (9): awareness survey, SUS questionnaire, uplift calculations
- **admin** (18): user management, scenario CRUD, OSINT controls, system stats
- **health** (1): healthcheck

### Q6.3: How does authentication work?

JWT-based with three layers: (1) Access token (15-minute expiry) for API requests; (2) Refresh token (30-day expiry) for obtaining new access tokens; (3) Server-side blocklist (`token_blocklist` table) — on logout, the token's JTI is stored so it can't be reused even if not expired. RBAC enforced via decorators. Passwords bcrypt-hashed.

### Q6.4: Describe your database schema.

10 PostgreSQL tables (8 core models + 2 evaluation): `users`, `scenarios`, `threat_feed_entries`, `training_sessions`, `risk_scores`, `notifications`, `token_blocklist`, `awareness_responses`, `sus_responses`, `password_reset_requests`. 10 foreign keys enforced at DB level. CASCADE on user deletion, SET NULL on scenario/threat deletion.

### Q6.5: Why Flask and not Django or FastAPI?

Flask is lightweight and doesn't impose structure — ideal for a research prototype with custom ML pipeline integration. Django's ORM and admin panel add unnecessary overhead. FastAPI's async model isn't needed since ML inference is CPU-bound. Flask's ecosystem provides exactly what's needed without bloat.

### Q6.6: Why PostgreSQL and not MongoDB or MySQL?

PostgreSQL offers ACID compliance (essential for financial/audit data), JSONB support (useful for storing SHAP explanations and OSINT metadata), robust foreign key enforcement, and is free and production-grade. MongoDB's schema-less nature would sacrifice data integrity. MySQL lacks PostgreSQL's advanced features (JSONB, window functions).

### Q6.7: Why React and not Vue, Angular, or server-rendered templates?

React's component model maps well to the dashboard's modular structure (employee view, manager view, admin panels). TypeScript adds type safety for a large frontend codebase. Vite provides instant HMR for rapid development. Angular would be overweight for this project. Vue would be acceptable but React has a larger ecosystem.

### Q6.8: How does the system handle concurrent users? Does it scale?

Current architecture: Flask with Gunicorn workers behind Render's load balancer. PostgreSQL handles concurrent DB access. ML inference is per-request (joblib-loaded model in memory). For a 20–50 person SME, this scales easily. For larger deployments, you'd add Redis caching, async task queues (Celery), and model serving via a dedicated endpoint.

### Q6.9: What security measures are in place beyond authentication?

- CORS configuration restricting allowed origins
- Input validation on all API endpoints
- SQL injection prevention via SQLAlchemy parameterised queries
- XSS prevention via React's default escaping
- Rate limiting potential (not yet implemented — noted as future work)
- HTTPS enforced by Render/Vercel
- No secrets in code — environment variable configuration (12-factor)

### Q6.10: How would you deploy this in a real SME?

Two options: (1) **Cloud** — current Render + Vercel setup, SME accesses via web browser; (2) **On-premises** — Docker Compose with PostgreSQL, Flask, and Nginx on a local server. For privacy-sensitive SMEs, on-premises keeps all data within the organisation. Either way, HTTPS and database encryption at rest should be configured.

---

## 7. Machine Learning Pipeline

### Q7.1: Walk me through the ML pipeline end to end.

1. **Data ingestion** — 1,050 synthetic behavioural profiles with 18 features
2. **SMOTE** — balances classes from {Low:409, Med:125, High:165, Crit:141} → 409/class (k=5)
3. **K-Means clustering** (k=5) — identifies 5 behavioural archetypes; cluster label appended as 19th feature
4. **80:20 stratified split** — preserves class distribution
5. **Random Forest training** — 200 trees, max_depth=12, min_samples_split=5, min_samples_leaf=2
6. **3-fold cross-validation** — mean accuracy 0.8604 ± 0.0094
7. **SHAP TreeExplainer** — computes per-prediction feature contributions
8. **Prediction** — employee behavioural vector → RF → risk class + SHAP explanation

### Q7.2: Why Random Forest and not deep learning, SVM, or XGBoost?

- **Interpretability** — RF provides native feature importance (MDI) aligning with XAI requirement
- **SHAP compatibility** — TreeExplainer is exact for tree ensembles (no approximation needed)
- **Robustness** — handles mixed feature types, resistant to overfitting with proper hyperparameters
- **Tabular data** — Deep learning typically underperforms RF/XGBoost on structured tabular data of this size
- **XGBoost** — valid alternative but adds hyperparameter complexity (learning rate, regularisation) without clear benefit at this scale
- **SVM** — no native probability calibration, harder to explain, poor scaling to multi-class

### Q7.3: What is a Random Forest? Explain like I'm not a data scientist.

A Random Forest is an ensemble of decision trees. Each tree sees a random subset of the data and features, makes its own prediction, and the forest takes a majority vote. This "wisdom of crowds" approach reduces the risk of any single tree's mistakes dominating the result. It's like asking 200 independent experts and going with the consensus.

### Q7.4: Explain your RF hyperparameters and why you chose them.

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| n_estimators | 200 | Sufficient for convergence; diminishing returns beyond ~150 |
| max_depth | 12 | Prevents overfitting while allowing complex decision boundaries |
| min_samples_split | 5 | Prevents splitting on too few samples |
| min_samples_leaf | 2 | Ensures leaf nodes are statistically meaningful |
| class_weight | None | SMOTE already handles imbalance |
| random_state | 42 | Reproducibility |

### Q7.5: Did you do hyperparameter tuning?

The hyperparameters were selected based on established best practices and validated via cross-validation. A full grid search or Bayesian optimisation wasn't performed but could further optimise performance. Given that CV std is only ±0.0094, the current parameters are robust. This is a valid area for future refinement.

### Q7.6: What are your top features by importance?

Top 5 by MDI (Mean Decrease Impurity):
1. `overall_accuracy` — 0.3096
2. `avg_response_time` — 0.1086
3. `scenario_completion_rate` — 0.1024
4. `phishing_accuracy` — 0.0758
5. `sessions_completed` — 0.0663

Bottom: `cluster_label` — 0.0085.

### Q7.7: The cluster label has very low importance. Why include it?

The cluster label provides contextual information about the employee's behavioural archetype. While its MDI is low (0.0085), it adds marginal but consistent improvement. More importantly, the cluster label drives the *adaptive engine's* scenario selection — it's architecturally essential even if its direct contribution to RF classification is small.

### Q7.8: What does SMOTE do and why is it necessary?

SMOTE (Synthetic Minority Over-sampling Technique) generates synthetic samples for minority classes by interpolating between existing samples and their k-nearest neighbours. Before: {Low:409, Med:125, High:165, Crit:141}. After: 409/class. Without SMOTE, RF would be biased toward Low-risk predictions. k=5 neighbours used for interpolation.

### Q7.9: Could SMOTE introduce unrealistic samples?

Valid concern. SMOTE interpolates *within* the feature space between real samples, so synthetic points lie on the line connecting existing data points. For behavioural features (accuracy, response time), this produces plausible intermediate values. It's less risky than for image data where interpolation can create unrealistic images. Future work should validate with real data.

### Q7.10: Why not use other oversampling techniques like ADASYN or random oversampling?

SMOTE is the most established technique (Chawla et al., 2002, 16,000+ citations). Random oversampling duplicates existing points, risking overfitting. ADASYN would be a valid alternative that generates more synthetic data near decision boundaries. For this project, SMOTE's simplicity and extensive validation in the literature made it the appropriate choice.

### Q7.11: How do you prevent overfitting?

Five mechanisms: (1) SMOTE on training set only (test set untouched); (2) max_depth=12 limits tree complexity; (3) min_samples_split/leaf prevents splitting on noise; (4) 200 trees with bagging reduces variance; (5) 3-fold CV confirms generalisation (CV mean 0.86 vs test accuracy 0.91 — gap is small and expected).

### Q7.12: The CV accuracy (0.86) is lower than test accuracy (0.91). Why?

This is expected. CV uses only the training set (80% of data), so each fold trains on ~67% of the total data. The test accuracy uses the full training set. The small gap (0.05) and low CV variance (±0.0094) confirm the model generalises well — there's no overfitting.

### Q7.13: What is bagging and how does Random Forest use it?

Bagging (Bootstrap Aggregating) trains each tree on a random bootstrap sample (with replacement) of the training data. Each tree also considers a random subset of features at each split. This decorrelates the trees, reducing variance. The final prediction is the majority vote across all 200 trees.

### Q7.14: What is Mean Decrease Impurity (MDI)?

MDI measures how much each feature reduces impurity (Gini index) across all splits in all trees. A feature that frequently produces high-impurity-reduction splits is more important. It's fast to compute but biased toward high-cardinality features. SHAP provides a complementary, more rigorous feature importance measure.

### Q7.15: How do you handle new employees with no training history?

New employees start with default feature values (zeros for accuracy, completion rate, etc.) and are assigned the default training path. After their first few training sessions, the model has enough data to make a meaningful prediction. The adaptive engine prioritises Level 1 (easy) scenarios for new employees.

---

## 8. SHAP & Explainability (Deep Dive)

### Q8.1: What is SHAP? Explain it simply.

SHAP uses game theory to answer: "How much did each feature contribute to this specific prediction?" Imagine 18 players (features) in a cooperative game. SHAP calculates each player's fair contribution to the outcome (the predicted risk level) by considering all possible combinations of players. The result: a number per feature showing how much it pushed the prediction higher or lower.

### Q8.2: What are the mathematical properties of SHAP?

SHAP satisfies four axioms from Shapley values:
1. **Efficiency** — SHAP values sum to the difference between prediction and average prediction
2. **Symmetry** — features with identical contributions get identical SHAP values
3. **Dummy** — features with no impact get zero SHAP value
4. **Additivity** — for ensemble models, SHAP values are additive across base models

Plus three additional properties: **local accuracy** (explanations sum to the prediction), **missingness** (absent features get zero), **consistency** (increasing a feature's contribution never decreases its SHAP value).

### Q8.3: What is TreeSHAP and why use it over KernelSHAP?

TreeSHAP exploits the tree structure of Random Forest to compute *exact* Shapley values in polynomial time — O(TLD²) where T=trees, L=leaves, D=depth. KernelSHAP uses weighted regression on sampled coalitions and is much slower and approximate. Since we're using RF, TreeSHAP is both faster and more accurate.

### Q8.4: What are the limitations of SHAP?

1. **Feature dependence** — SHAP can attribute importance to correlated but unused features
2. **Misinterpretation risk** — non-technical users may misunderstand SHAP values
3. **Computational cost** — even TreeSHAP adds overhead per prediction
4. **No causal claims** — SHAP shows correlation-based contribution, not causation
5. **Manipulation risk** — in adversarial settings, SHAP can be gamed to obscure biases

In AHRID, these are mitigated by: translating SHAP values into plain-language explanations (not raw numbers), using TreeSHAP for efficiency, and clearly framing explanations as behavioural correlations.

### Q8.5: How do you present SHAP explanations to non-technical employees?

Employees don't see raw SHAP values. Instead, AHRID translates them into plain English: "Your risk level is HIGH. Main factors: your phishing accuracy is 42% (contributing toward higher risk), and your average response time is 3.2 seconds (very fast clicks suggest insufficient scrutiny)." This maps to the TAM principle — perceived usefulness requires understandable output.

### Q8.6: Why not use LIME instead of SHAP?

LIME (Local Interpretable Model-agnostic Explanations) approximates locally with a linear model. Problems: (1) LIME is unstable — different runs can produce different explanations for the same prediction; (2) LIME doesn't guarantee the mathematical properties SHAP does (efficiency, consistency); (3) TreeSHAP is *exact* for tree ensembles, making it strictly superior here.

### Q8.7: Could SHAP explanations reveal sensitive information?

In AHRID, SHAP only explains behavioural features (accuracy, response time, completion rate) — never demographic or identity data. Since no PII enters the pipeline, SHAP cannot reveal sensitive information. Employees see their own explanations; managers see aggregate metrics only.

### Q8.8: How does SHAP support the right to explanation?

IPA 2075 and GDPR (Article 22) suggest that individuals should be able to understand automated decisions affecting them. SHAP directly enables this — every risk classification is accompanied by a feature-level explanation. Employees can understand, question, and act on their risk assessment.

---

## 9. K-Means Clustering (Deep Dive)

### Q9.1: Why cluster employees at all?

Clustering identifies behavioural archetypes — groups of employees with similar risk patterns. This enables: (1) tailored training paths per archetype (not per individual, which would be noisy); (2) richer context for the RF classifier (cluster label as additional feature); (3) manager-level insights ("you have 5 Overconfident Clickers on your team").

### Q9.2: Why K-Means and not DBSCAN, HDBSCAN, or Gaussian Mixture Models?

K-Means is simple, interpretable, computationally efficient, and well-suited to this dataset size. DBSCAN/HDBSCAN don't require predefined k (advantage) but produce variable cluster counts and can label points as noise (disadvantage — every employee should belong to an archetype). GMMs assume Gaussian distributions which may not hold. HDBSCAN is recommended for future work.

### Q9.3: How did you determine k=5?

Elbow method (plotting inertia vs k, looking for the "bend") and silhouette analysis (measuring cluster cohesion vs separation). k=5 balanced mathematical optimality with behavioural interpretability — the resulting 5 archetypes are meaningfully distinct and actionable.

### Q9.4: Describe the 5 behavioural archetypes.

| Cluster | Archetype | n | Behaviour Pattern |
|---------|-----------|---|-------------------|
| C0 | Overconfident Clicker | 239 | High engagement, poor accuracy — clicks everything quickly |
| C1 | Cautious Learner | 266 | Moderate engagement, improving accuracy — actively learning |
| C2 | Inconsistent Performer | 216 | Variable results — good one session, poor the next |
| C3 | Resilient Defender | 185 | Consistently high accuracy — security-aware |
| C4 | Disengaged Completer | 145 | Completes minimum training — does bare minimum |

### Q9.5: What is the silhouette coefficient and is yours acceptable?

Silhouette measures cluster cohesion vs separation (-1 to +1). Behavioural data inherently has overlapping boundaries — employees don't fall into perfectly distinct groups. Moderate silhouette scores are expected and documented in the thesis. The archetypes' behavioural validity (do they make sense?) matters more than geometric separation.

### Q9.6: How do the clusters evolve as an employee trains?

As an employee completes more training and their behavioural features change (accuracy improves, response time adjusts), they can move between clusters during periodic re-clustering. An Overconfident Clicker who learns to slow down and improve accuracy might migrate to Cautious Learner or even Resilient Defender. This is the "adaptive" part of AHRID.

### Q9.7: Did you normalise features before clustering?

Yes. K-Means is distance-based, so features on different scales (e.g., accuracy 0–1 vs response time 1–60 seconds) would bias the clustering toward high-magnitude features. Standard scaling (z-score normalisation) was applied before clustering to give all features equal influence.

---

## 10. OSINT & Threat Intelligence

### Q10.1: What OSINT sources do you use?

Two publicly available feeds:
1. **Phishing.Database** — community-maintained phishing URL list (GitHub, updated daily)
2. **AlienVault OTX** — crowd-sourced threat intelligence with IoCs

No network scanning, penetration testing, or offensive security activities performed.

### Q10.2: Describe the 7-stage OSINT pipeline.

1. **Acquisition** — fetch raw URLs from feeds via HTTP/API
2. **Validation** — check URL format, liveness, content type
3. **Deduplication** — hash-based dedup against existing DB entries
4. **Classification** — categorise by attack type using URL structural analysis
5. **Sanitisation** — defang URLs (`hxxps://`), strip tracking parameters
6. **Scenario generation** — transform into MCQ training scenarios with difficulty classification
7. **Database persistence** — store in `threat_feed_entries` and `scenarios` tables

### Q10.3: How do you classify URL difficulty?

Three levels using structural heuristics (first-match wins, priority order):
- **Level 1 (Obvious, 10 XP)** — non-HTTPS, free-hosting TLDs (.tk/.ml/.ga/.cf/.gq), typosquats (paypa1, g00gle), free platforms (blogspot, weebly)
- **Level 3 (Advanced, 25 XP)** — cloud infra abuse (amazonaws, vercel, azurewebsites, netlify), subdomain-brand attacks, IDN homograph encoding
- **Level 2 (Subtle, 15 XP)** — brand in path/query/subdomain, or default fallback

Level 1 checked before Level 3 → URL with both free TLD and cloud hosting is conservatively classified Level 1.

### Q10.4: Why is the difficulty classification deterministic and not ML-based?

Deterministic heuristics ensure: (1) reproducibility — same URL always gets same difficulty; (2) transparency — the rule that triggered is documented; (3) simplicity — URL structural features are well-defined. An ML-based classifier would require labelled training data for URL difficulty, which doesn't exist. The heuristics are informed by phishing taxonomy literature.

### Q10.5: What are the 8 scenario categories?

Credential Harvesting, Malware Delivery, CEO Fraud/BEC, Technical Support Scam, Invoice Fraud, Account Verification Phish, Social Media Impersonation, General Phishing.

### Q10.6: What are the 6 lure types?

Urgency, Authority, Curiosity, Fear, Reward, Social Proof. Mapped to Cialdini's principles of persuasion and Prospect Theory loss-aversion.

### Q10.7: How does the adaptive engine select scenarios for an employee?

The engine considers: (1) employee's cluster archetype, (2) weak categories (low accuracy), (3) current difficulty level (mastery-based progression), (4) spaced repetition timing (Ebbinghaus curve — revisit failed scenarios after appropriate intervals). This ensures personalised, progressively challenging training.

### Q10.8: What happens if an OSINT feed goes down?

The system has cached scenario repository. Scenarios already generated remain in the database regardless of feed availability. The pipeline logs feed failures and retries. Training continues from the existing scenario pool. This resilience is documented in the risk register.

### Q10.9: Could the OSINT pipeline ingest malicious content that harms the platform?

URLs are sanitised (defanged) before storage — users never interact with live phishing infrastructure. Content is stored as text metadata, not rendered HTML. Input validation on all ingested data prevents SQL injection or XSS via feed content. The pipeline is consume-only — no outbound actions against ingested URLs.

---

## 11. Ethical, Privacy & Legal Considerations

### Q11.1: How does AHRID comply with IPA 2075?

Nepal's Individual Privacy Act 2075 (2018) and Article 28 of the Constitution recognise privacy as a fundamental right. Compliance through:

1. **Data minimisation** — only 18 behavioural features; no PII in ML pipeline
2. **Purpose limitation** — data used solely for risk assessment and training personalisation
3. **Synthetic data** — all model development used synthetic profiles
4. **Consent** — platform design includes consent workflows for future deployment
5. **Right to explanation** — SHAP provides per-prediction explanations

### Q11.2: How is IPA 2075 different from GDPR?

IPA 2075 is broader in scope but less specific in AI governance: (1) it recognises privacy as a constitutional right (Article 28) but lacks GDPR's specific provisions for automated decision-making (Article 22); (2) it doesn't define "data controller" or "data processor" as explicitly; (3) enforcement mechanisms are less developed. AHRID's privacy-by-design approach exceeds IPA 2075's requirements to anticipate future regulatory development.

### Q11.3: How do you ensure algorithmic fairness?

Three safeguards: (1) **Feature audit** — all 18 features examined; no direct or proxy variables for protected characteristics; (2) **SMOTE** — prevents classifier from favouring majority class; (3) **SHAP transparency** — biased predictions can be inspected and challenged. However, synthetic data cannot guarantee fairness across real demographic groups — this requires post-deployment monitoring.

### Q11.4: What about the ethics of monitoring employee behaviour?

AHRID adopts a **non-punitive governance model**: elevated risk triggers training, not discipline. Key safeguards: (1) managers see aggregate team metrics, not individual SHAP explanations; (2) employees see their own explanations and can self-improve; (3) the system is developmental, not surveillant. However, technical controls alone are insufficient — organisational governance policies must accompany deployment.

### Q11.5: Why not use real phishing simulations?

Ethical concerns: (1) live phishing exposes employees to malicious infrastructure; (2) it creates adversarial employer-employee dynamics; (3) it may violate IPA 2075 if employees aren't informed. AHRID generates locally rendered scenarios from sanitised OSINT — employees never interact with live phishing URLs.

### Q11.6: Is synthetic data ethically problematic?

Synthetic data eliminates privacy risk but introduces validity risk. The ethical trade-off is transparent: no PII compromised, but results can't directly generalise. For a BSc project, this is the ethically responsible choice — real employee data would require ethics board approval, organisational consent, and data protection measures exceeding project scope.

### Q11.7: What happens to an employee's data if they leave?

CASCADE deletion: removing a user from `users` automatically deletes all associated records. No orphaned personal data remains. Enforced at PostgreSQL level, not just application code.

### Q11.8: How do you handle the "right to be forgotten"?

CASCADE deletion satisfies this. Admin deletes user account → all data irrecoverably removed. No external backups containing PII in current architecture.

### Q11.9: Could AHRID be misused for employee surveillance?

Risk acknowledged. Mitigation: (1) RBAC — employees only see own data; (2) managers see aggregates only; (3) non-punitive principle documented; (4) future work includes policy templates. A determined malicious admin could still misuse the system — organisational governance is the ultimate safeguard.

### Q11.10: How did you deal with the ethical implications of your work?

Ethics was a design requirement, not a post-hoc compliance exercise. The ethical framework (Floridi et al., 2018; Jobin et al., 2019) was incorporated from the earliest design phase. Every development sprint included an ethical review checkpoint. RQ2 specifically evaluates ethical outcomes alongside technical ones.

### Q11.11: What ethical framework did you follow?

Primarily AI4People (Floridi et al., 2018): beneficence (help employees improve), non-maleficence (no punitive use), autonomy (employees understand and control their data), justice (fairness across employee groups), explicability (SHAP explanations). Supplemented by Jobin et al.'s (2019) global AI ethics landscape review.

### Q11.12: Is informed consent meaningful if an employer mandates the platform?

Critical question. If an employer mandates AHRID, consent isn't truly voluntary. Mitigation: (1) the non-punitive principle ensures no adverse consequences from risk classification; (2) SHAP explanations ensure employees understand what the system does; (3) future work should explore opt-out mechanisms and data portability. This tension between organisational mandates and individual consent is acknowledged as an ethical limitation.

### Q11.13: What about bias in the synthetic data itself?

If the statistical distributions used to generate synthetic data embed biases (e.g., calibrated against historical cybercrime data that reflects enforcement bias), the model could reproduce those biases. This is mitigated by using behavioural features only (not demographic) and by the SMOTE class-balancing step. Post-deployment bias auditing is essential — listed as future work.

---

## 12. Evaluation & Results

### Q12.1: Summarise your key results.

| Metric | Value | Threshold/Benchmark |
|--------|-------|-----------------------|
| Overall accuracy | 90.95% | — |
| Macro F1-score | 0.889 | > 0.85 (H1) ✅ |
| Cohen's κ | 0.8684 | > 0.61 (substantial) ✅ |
| PR-AUC | 0.9399 | — |
| CV mean accuracy | 0.8604 ± 0.0094 | — |
| Rule-based baseline F1 | 0.3868 | — |
| Improvement | +50.21 pp | — |

### Q12.2: What does the confusion matrix show?

- **Low Risk** — perfect precision (1.000): genuinely safe employees never escalated
- **Critical Risk** — highest recall (0.943): almost all dangerous patterns caught
- **Medium Risk** — lower precision (0.784): expected overlap with neighbouring classes
- No systematic misclassification between non-adjacent classes

### Q12.3: How did you construct the rule-based baseline?

Simple threshold rules on individual features: "if accuracy < 40% → Critical, if accuracy > 80% → Low." Achieved macro F1 = 0.3868. Demonstrates that single-feature rules can't capture multi-dimensional behavioural patterns.

### Q12.4: Why is PR-AUC better than ROC-AUC here?

ROC-AUC can be misleadingly high with class imbalance (inflated by true negatives). PR-AUC focuses on precision and recall — the metrics that matter for identifying at-risk employees. PR-AUC 0.9399 confirms strong performance regardless of threshold.

### Q12.5: What is Cohen's Kappa and why report it?

κ measures agreement between predicted and actual labels, correcting for chance. Landis & Koch (1977): 0.61–0.80 = substantial, 0.81–1.00 = almost perfect. AHRID achieves κ = 0.8684 (almost perfect). More informative than accuracy for multi-class problems.

### Q12.6: How do you evaluate the OSINT pipeline?

Functional evaluation: (1) correct 7-stage processing, (2) reproducible classification across runs, (3) balanced scenario distribution across categories, (4) continuous operation without platform interruption. No quantitative OSINT precision metrics — acknowledged as a limitation.

### Q12.7: Were there any findings that surprised you?

1. `overall_accuracy` dominating feature importance (0.31) — expected but the margin was larger than anticipated
2. `cluster_label` having very low MDI (0.0085) despite being architecturally important
3. The baseline performing so poorly (F1=0.387) — highlights how inadequate rule-based approaches are
4. Perfect precision on Low Risk — no false positives for safe employees

### Q12.8: How do your findings relate to existing literature?

The F1 and κ results are consistent with other RF-based behavioural classification studies in cybersecurity (typically reporting F1 0.80–0.92). The baseline comparison (rule-based vs ML) mirrors findings from fraud detection literature (Dal Pozzolo, 2018) showing ML consistently outperforms threshold rules. The SHAP integration extends existing XAI work into the SAT domain.

### Q12.9: How do you know your findings are correct?

Multiple validation layers: (1) 3-fold CV with low variance confirms stable performance; (2) multiple complementary metrics (F1, κ, PR-AUC) tell a consistent story; (3) confusion matrix analysis shows no pathological failure modes; (4) baseline comparison provides meaningful reference point. Limitation: all validation is on synthetic data.

### Q12.10: Could you have used statistical hypothesis testing?

Yes — McNemar's test could formally compare the RF vs baseline. Paired t-test on CV folds could test whether performance is significantly above 0.85. These weren't performed but would strengthen the evaluation. The magnitude of improvement (50+ percentage points) makes formal testing somewhat unnecessary — the difference is clearly not due to chance.

---

## 13. Limitations, Validity & Generalisability

### Q13.1: What are the main limitations?

1. **Synthetic data** — cannot fully reproduce real organisational behaviour
2. **No real-user validation** — controlled experimental, not operational
3. **Kathmandu Valley scope** — may not generalise to other regions
4. **No longitudinal study** — can't measure sustained behavioural change
5. **English-only** — limits accessibility
6. **Moderate silhouette** — clusters overlap (inherent to behavioural data)
7. **No OSINT classification evaluation** — heuristics not validated against ground truth
8. **No formal usability testing** — SUS questionnaire designed but not administered
9. **Single classifier comparison** — only compared RF vs rule-based, not vs XGBoost/SVM
10. **No adversarial robustness testing** — model not tested against adversarial inputs

### Q13.2: How generalisable are your findings?

Limited generalisability, by design. The platform is scoped to Kathmandu Valley SMEs with non-technical employees. The synthetic data distributions reflect this context. Extending to larger enterprises, different regions, or different cultural contexts would require re-calibration and real-user validation. This is explicitly a future work item.

### Q13.3: What biases may exist in your research?

1. **Synthetic data bias** — distributions calibrated against available (potentially biased) cybercrime statistics
2. **Feature selection bias** — the 18 features chosen reflect the researcher's assumptions about what drives risk
3. **Evaluation bias** — desk-based evaluation lacks the ecological validity of real-world deployment
4. **Cultural bias** — scenario content (English, Western brand names) may not resonate with Nepali employees
5. **Confirmation bias** — researcher designed both the system and the evaluation

### Q13.4: How would your system cope with bigger datasets? Does it scale?

Computationally: RF training is O(n·m·k·log(n)) — scales well to much larger datasets. SHAP TreeExplainer is O(TLD²) per prediction — also efficient. K-Means is O(n·k·i·d) — linear in dataset size. The architecture would need infrastructure scaling (database, API servers) before algorithmic scaling becomes an issue. 10,000+ employees would need Redis caching and async processing.

### Q13.5: What threats to validity exist?

- **Internal validity** — synthetic data may not capture real behavioural complexity; SMOTE may generate unrealistic samples
- **External validity** — results specific to synthetic Kathmandu Valley SME profiles; no cross-context validation
- **Construct validity** — "cybersecurity risk" operationalised through 18 behavioural features may miss important dimensions
- **Conclusion validity** — no formal statistical hypothesis testing performed

### Q13.6: If someone tried to replicate your study, could they?

Yes — the thesis documents: (1) exact hyperparameters and random seed (42); (2) synthetic data generation methodology; (3) the complete tech stack and architecture; (4) OSINT sources and pipeline stages. The codebase is on GitHub. The main reproducibility risk is OSINT feed content changing over time.

---

## 14. Future Work & Continuation

### Q14.1: What are your recommendations for future work?

1. **Real-world deployment** — pilot with consenting employees in Kathmandu Valley SMEs
2. **Longitudinal study** — 12+ months to measure sustained behavioural change
3. **Nepali localisation** — translate scenarios, SHAP explanations, consent workflows
4. **HDBSCAN** — density-based clustering without predefined k
5. **Thompson Sampling / contextual bandits** — explore-exploit balance for scenario selection
6. **Regional expansion** — test across Nepal and South Asian SME contexts
7. **Formal usability testing** — administer SUS questionnaire to real users
8. **Multi-classifier comparison** — benchmark RF against XGBoost, LightGBM, neural networks
9. **Adversarial robustness** — test model against intentional gaming of behavioural features

### Q14.2: If you had 6 more months, what would you do first?

Deploy with one real Kathmandu Valley SME (10–30 employees), collect real behavioural data with informed consent, retrain the model, and compare performance with synthetic-data results. This addresses the most critical validity limitation.

### Q14.3: How would you start the real-user deployment?

1. Partner with a Kathmandu Valley SME willing to participate
2. Obtain institutional ethics approval
3. Design informed consent process (Nepali and English)
4. Deploy on-premises for data sovereignty
5. Run for 3–6 months collecting behavioural data
6. Retrain models on real data and compare metrics

### Q14.4: How would you address the synthetic data limitation?

Three approaches: (1) deploy and collect real data; (2) transfer learning — pre-train on synthetic, fine-tune on small real dataset; (3) validate synthetic distributions against real organisational audit data (anonymised email click rates from a partner SME).

### Q14.5: You mention HDBSCAN. What advantage would it have?

HDBSCAN doesn't require specifying k in advance, can identify clusters of varying density, and labels outlier points as noise rather than forcing them into a cluster. For behavioural data, this could reveal more nuanced archetypes and identify genuinely anomalous employees who don't fit any pattern.

### Q14.6: What about using LLMs for scenario generation?

A future direction. LLMs could generate more realistic phishing email templates from OSINT indicators, including context-aware social engineering content. However, this raises ethical concerns — generating realistic phishing content could be misused. Appropriate safeguards (output filtering, access controls) would be essential.

### Q14.7: How long-term are your contributions?

The technical contribution (specific ML metrics) will be superseded as models improve. The architectural contribution (clustering + ML + XAI + OSINT integration pattern) is more durable — it's a framework others can build on. The ethical contribution (non-punitive, explainable governance model for SAT) is the most enduring — it addresses a fundamental design principle.

---

## 15. Nasty / Curveball Questions

### Q15.1: "You trained and tested on synthetic data. This is meaningless."

It's not meaningless — it validates the *architecture and methodology*. The ML pipeline, evaluation framework, and ethical design are all demonstrated to work. What it doesn't validate is operational performance with real humans. This is clearly stated as a limitation. DSR evaluates artefacts, and the artefact is the platform — the synthetic data evaluation demonstrates it functions correctly. Real-world validation is future work.

### Q15.2: "Why not just use KnowBe4?"

Cost (enterprise pricing vs free), customisation (one-size-fits-all vs adaptive), XAI (opaque vs SHAP-transparent), privacy (cloud-stored vs privacy-by-design), compliance (GDPR-focused vs IPA 2075), OSINT integration (none documented vs automated pipeline), accessibility (English enterprise vs developing-economy SME context).

### Q15.3: "Your work is just a web app with some ML. What's the research contribution?"

The contribution is not the code — it's the integration pattern and evaluation. No prior work combines K-Means + RF + SHAP + OSINT in an adaptive SAT platform evaluated against a developing-country privacy framework. The DSR methodology ensures this is research, not just engineering. The thesis answers specific research questions with measurable outcomes.

### Q15.4: "90.95% accuracy means 1 in 10 employees is misclassified. Is that acceptable?"

First, accuracy isn't the primary metric — macro F1 (0.889) and κ (0.8684) are. Second, misclassification here means assigning someone to an adjacent risk category (Medium instead of High), not missing a critical threat entirely. The confusion matrix shows no Low↔Critical misclassifications. Third, the misclassified employees still receive training — the consequence is suboptimal (not wrong) training path selection.

### Q15.5: "What if an employee deliberately games the system?"

Adversarial robustness wasn't tested — this is a limitation. An employee could intentionally slow down their response time or change behaviour to manipulate their score. Mitigation strategies for future work: anomaly detection for sudden behavioural shifts, temporal consistency checks, and ensemble of multiple assessment methods beyond the training platform.

### Q15.6: "Your model doesn't use any demographic features. Doesn't that make it less accurate?"

Deliberately so. Including demographics would improve accuracy marginally but create fairness and privacy violations. A model that predicts risk based on age or gender, even as a proxy, is discriminatory. The 18 behavioural features capture *actions*, not *identity* — this is a feature, not a limitation.

### Q15.7: "Is your field going in the right direction?"

Yes — the trend toward adaptive, explainable, privacy-preserving security training is the right trajectory. The risk is that the field prioritises detection metrics over ethical governance. AHRID argues that both must advance together. The emerging regulatory landscape (EU AI Act, evolving IPA 2075) will increasingly require this dual focus.

### Q15.8: "Why didn't you compare with other ML models?"

Time and scope constraints. The thesis compared RF vs rule-based baseline (the most meaningful comparison — ML vs non-ML). Comparing RF vs XGBoost, SVM, or neural networks would add rigour but wouldn't change the core contribution (architecture + ethics). Listed as future work.

### Q15.9: "How do you know 18 features are the right features?"

Feature selection was informed by behavioural cybersecurity literature and the available interaction data from the platform. MDI and SHAP analysis confirm that the top features are behaviourally meaningful. However, real-world deployment might reveal additional important features (device type, time of day, organisational role) not captured in the current set.

### Q15.10: "What if IPA 2075 changes?"

AHRID's privacy-by-design exceeds current IPA 2075 requirements, providing a buffer against regulatory tightening. The architecture is modular — consent workflows, data retention policies, and RBAC can be adjusted without rebuilding the ML pipeline. Future regulatory monitoring is recommended.

### Q15.11: "You haven't cited [specific paper X]. Are you aware of it?"

If you genuinely haven't read it: "I'm not familiar with that specific paper. Could you tell me the key argument? I'd be happy to discuss how it relates to my work." Never pretend you've read something you haven't.

### Q15.12: "What would happen if you used your model on a real company tomorrow?"

Performance would likely decrease because: (1) real behaviour is noisier than synthetic data; (2) the feature distributions may differ from my calibrated synthetics; (3) real employees have context (organisational culture, workload, stress) that synthetic profiles don't capture. I'd expect a 5–15% performance drop initially, with improvement after retraining on real data.

---

## 16. Contribution to Knowledge

### Q16.1: What are the contributions to knowledge of your thesis?

1. **Technical contribution** — demonstrated that K-Means + RF + SHAP + OSINT can be integrated into a single adaptive SAT platform achieving F1=0.889
2. **Methodological contribution** — applied DSR with Agile to cybersecurity awareness in a developing-country context
3. **Ethical contribution** — designed a non-punitive, explainable governance model for employee behavioural monitoring aligned with IPA 2075
4. **Practical contribution** — created a free, deployable platform prototype addressing an unmet need for Nepali SMEs

### Q16.2: Who will be most interested in your work?

1. **Nepali SME managers/CISOs** — the target users of the platform
2. **Cybersecurity awareness researchers** — the adaptive ML + XAI integration pattern
3. **AI ethics researchers** — the non-punitive governance model for workplace AI
4. **Developing-country policy makers** — evidence that privacy-by-design can work within IPA 2075
5. **SAT platform developers** — the OSINT-to-training automation pipeline

### Q16.3: What is the relevance to practitioners?

AHRID demonstrates that adaptive, explainable cybersecurity training is technically feasible without enterprise budgets. The architecture could be replicated or adapted by SMEs, NGOs, or government agencies in developing countries facing similar constraints.

### Q16.4: What have you done that merits a BSc (Hons)?

Designed, built, and evaluated a full-stack adaptive cybersecurity platform using DSR methodology. The work integrates four ML/AI techniques (clustering, RF, SHAP, OSINT), achieves strong quantitative results (F1=0.889, κ=0.8684), addresses a genuine gap in developing-country cybersecurity, and demonstrates ethical rigour through privacy-by-design. The thesis satisfies both technical and ethical research questions with measurable outcomes.

---

## 17. Personal Reflection & Process

### Q17.1: What have you learned from the process?

1. **ML is the easy part** — getting the model to work took weeks; building the full platform took months
2. **Ethical design is harder than technical design** — privacy-by-design requires thinking about consequences at every layer
3. **Synthetic data is a double-edged sword** — it enables rapid iteration but limits validity claims
4. **DSR is an excellent methodology for applied CS** — it gives structure to "build and evaluate" projects
5. **Scope management is critical** — I had to constantly resist feature creep to stay within BSc timescale

### Q17.2: Looking back, what might you have done differently?

1. Started ethics board conversations earlier (even if not required for desk-based study)
2. Used a more sophisticated synthetic data generation method (agent-based modelling)
3. Compared more ML classifiers (XGBoost, LightGBM)
4. Built the Nepali localisation from the start rather than deferring
5. Included formal usability testing in the evaluation design

### Q17.3: What was the most challenging aspect?

Integrating the OSINT pipeline with the ML pipeline. Real-world threat feeds are messy — inconsistent schemas, varying reliability, duplicate entries. Building a robust 7-stage pipeline that handles all edge cases while maintaining training scenario quality was the most complex engineering challenge.

### Q17.4: How has your view of cybersecurity awareness changed?

Before: "just teach people not to click phishing links." After: I understand it as a complex behavioural problem requiring adaptive, personalised intervention informed by behavioural economics (PMT, Prospect Theory), sustained through spaced repetition (Ebbinghaus), and governed ethically. One-off training doesn't work — continuous, explainable, non-punitive engagement does.

### Q17.5: What advice would you give to someone starting a similar project?

1. Choose DSR if you're building something — it legitimises "build and evaluate" as research
2. Start with the ethical framework before writing any code
3. Use synthetic data to move fast, but be honest about its limitations
4. Integrate XAI from day one — bolting it on later is painful
5. Keep scope narrow — better to do one thing well than five things poorly

### Q17.6: If you were to continue this as a Master's thesis, what would it look like?

Year 1: real-world deployment with 3–5 Kathmandu Valley SMEs, ethics approval, Nepali localisation. Year 2: longitudinal study (12+ months), real-data model retraining, formal comparison of clustering algorithms (HDBSCAN) and classifiers (XGBoost, neural networks), Thompson Sampling for scenario selection. The Master's would validate the architecture that the BSc designed.

---

## 18. Viva Soft-Skills & Strategy

### General Tips

- **Listen carefully** — answer what they asked, not what you think they asked
- **"I don't know, but I would investigate by..."** is always better than bluffing
- **Defend design decisions** — state alternatives considered and why rejected
- **Acknowledge limitations honestly** — examiners respect intellectual honesty
- **Keep answers concise** — 1–2 minutes unless asked to elaborate
- **Reference your thesis** — "As discussed in Section 4.2..."
- **Pause before answering** — 3 seconds of thought looks confident, not hesitant

### 3-Minute Elevator Pitch (Practice This)

"Kathmandu Valley SMEs face rising phishing threats but can't afford enterprise security training. I built AHRID — an adaptive platform using K-Means clustering, Random Forest classification, SHAP explainability, and live OSINT threat feeds. Employees get personalised training based on their behavioural archetype, and every risk score comes with a plain-English explanation. The system achieved macro F1 of 0.889 and Cohen's κ of 0.869, outperforming a rule-based baseline by 50 percentage points. Ethically, it complies with Nepal's privacy law through zero-PII design and non-punitive governance. The key contribution: adaptive, explainable, privacy-preserving cybersecurity training is feasible and affordable for developing-economy SMEs."

### Common Opening Patterns

Examiners typically start with one of:
1. "Summarise your thesis" (practice the 3-minute version)
2. "What motivated this work?" (personal connection + gap analysis)
3. "What's original about your contribution?" (three novel contributions)
4. "Walk us through your methodology" (DSR → Agile → ML pipeline)

### Handling "I Don't Know" Questions

Template: "That's a really interesting question. I didn't explore [X] in this study because [scope/time/feasibility reason], but my approach would be to [next investigative step]. I think the answer likely relates to [educated hypothesis]."

### Red Flags to Avoid

- Don't get defensive about limitations — own them confidently
- Don't claim your work is "novel" without specifying exactly what aspect is novel
- Don't use jargon without being able to explain it simply
- Don't blame tools, data, or external factors for shortcomings
- Don't over-promise about future work — be realistic

---

## 19. Essential Reading List

### Core References (Must Re-Read Before Defence)

| Reference | Why It Matters | URL |
|-----------|----------------|-----|
| Peffers et al. (2007) — DSRM | Your methodology | https://doi.org/10.2753/MIS0742-1222240302 |
| Hevner et al. (2004) — DSR in IS | 7 DSR guidelines | https://doi.org/10.2307/25148625 |
| Breiman (2001) — Random Forests | Core ML algorithm | https://doi.org/10.1023/A:1010933404324 |
| Lundberg & Lee (2017) — SHAP | XAI method | https://proceedings.neurips.cc/paper_files/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf |
| Chawla et al. (2002) — SMOTE | Class imbalance | https://doi.org/10.1613/jair.953 |
| Rogers (1975) — PMT | Behavioural theory | https://doi.org/10.1016/S0065-2601(08)60220-1 |
| Kahneman & Tversky (1979) — Prospect Theory | Loss-aversion | https://doi.org/10.2307/1914185 |
| Davis (1989) — TAM | Acceptance theory | https://doi.org/10.2307/249008 |
| Floridi et al. (2018) — AI4People | Ethical framework | https://doi.org/10.1007/s11023-018-9482-5 |
| IPA 2075 | Nepal privacy law | https://lawcommission.gov.np/content/12261/12261-the-privacy-act-2075/ |
| Christoph Molnar — Interpretable ML Book (SHAP chapter) | Deep SHAP understanding | https://christophm.github.io/interpretable-ml-book/shap.html |

### Supplementary Reading

| Reference | Topic | URL |
|-----------|-------|-----|
| Jobin et al. (2019) — AI ethics landscape | Global AI ethics | https://doi.org/10.1038/s42256-019-0088-2 |
| Kabanda (2018) — SME cybersecurity | Developing countries | https://aisel.aisnet.org/ecis2018_rp/15 |
| Hadlington (2017) — Human factors | Behavioural risk | https://doi.org/10.1016/j.heliyon.2017.e00346 |
| Boss et al. (2009) — Mandatoriness | Compliance vs motivation | https://doi.org/10.1057/ejis.2009.8 |
| Beautement et al. (2008) — Compliance budget | Training fatigue | https://doi.org/10.1145/1595676.1595684 |
| March & Smith (1995) — Design science | DSR theoretical basis | (university library) |
| Kemp (2025) — Digital Nepal | Internet stats | https://datareportal.com/reports/digital-2025-nepal |
| Nepal Police Cyber Bureau (2025) | Cybercrime statistics | https://cib.nepalpolice.gov.np |
| Verizon (2023) — DBIR | 74% human element | https://www.verizon.com/business/resources/reports/dbir/ |
| Landis & Koch (1977) — Kappa | κ interpretation | https://doi.org/10.2307/2529310 |
| Pedregosa et al. (2011) — scikit-learn | ML library | https://doi.org/10.48550/arXiv.1201.0490 |
| Dal Pozzolo (2018) — Adaptive ML | Fraud detection baseline comparison | https://dipot.ulb.ac.be/dspace/bitstream/2013/271162/3/dalpozzolo_thesis.pdf |

### Defence Preparation Resources

| Resource | What It Covers | URL |
|----------|----------------|-----|
| GradCoach — Preparing for Viva | 13 common questions with strategy | https://gradcoach.com/dissertation-thesis-defence/ |
| VivaCoach — 50 Common Questions | Comprehensive question list | https://vivacoach.ai/blog/50-common-viva-questions-and-how-to-answer-them |
| EloquentScience — 40 Viva Questions | Categorised question bank | https://eloquentscience.com/2024/06/top-40-potential-questions-to-be-asked-in-a-phd-viva-or-defense/ |
| Calgary — Nasty Viva Questions | Hardest curveball questions | https://pages.cpsc.ucalgary.ca/~saul/wiki/uploads/Chapter1/NastyPhDQuestions.html |

---

## 20. Quick-Reference Numbers to Memorise

### ML Performance
- **90.95%** accuracy · **0.889** macro F1 · **0.8684** κ · **0.9399** PR-AUC
- **0.8604 ± 0.0094** CV mean
- **0.3868** baseline F1 → **+50.21 pp** improvement
- **1.000** precision (Low Risk) · **0.943** recall (Critical Risk) · **0.784** precision (Medium Risk)

### Dataset & Model
- **1,050** synthetic profiles · **18** features · **4** risk classes · **19th** feature = cluster label
- Before SMOTE: **{409, 125, 165, 141}** → After: **409/class**
- **5** K-Means clusters · **200** RF trees · max_depth **12** · random_state **42**
- Top feature: `overall_accuracy` = **0.3096** MDI

### Architecture
- **61** API endpoints · **8** blueprints · **10** DB tables · **10** foreign keys
- JWT: **15 min** access · **30 day** refresh · server-side blocklist
- **15** Agile sprints · January–July **2026**

### OSINT & Training
- **7** pipeline stages · **6** lure types · **8** scenario categories · **3** difficulty levels
- Level 1 = **10 XP** · Level 2 = **15 XP** · Level 3 = **25 XP**
- **2** OSINT sources: Phishing.Database + AlienVault OTX

### Legal & Ethics
- **IPA 2075** + Article **28** of Nepal Constitution
- **0** PII features in ML pipeline · **18** behavioural-only features
- **AI4People** (Floridi et al., 2018) — 5 principles: beneficence, non-maleficence, autonomy, justice, explicability
- **Hevner's 7** DSR guidelines · **Peffers' 6** DSRM phases

### Key Archetype Sizes
- C0 Overconfident Clicker: **239** · C1 Cautious Learner: **266** · C2 Inconsistent Performer: **216** · C3 Resilient Defender: **185** · C4 Disengaged Completer: **145**

---

*Good luck, Rupesh. You built something meaningful — now go defend it with confidence.*
