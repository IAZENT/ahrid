# AHRID Thesis — Requirements Checklist & Word-Count Blueprint
**ST6047CEM Cyber Security Project | Due: 29 Jul 2026 | Marker: Manoj Shrestha**
**Target: 10/10 | Word limit: 10,000 (body) | Reference: cyber_project_sample.html**

---

## MASTER WORD-COUNT PLAN

| # | Section | AHRID Target | Sample Equiv | Status |
|---|---------|-------------|--------------|--------|
| — | Front Matter (Title, Ack, Abstract, Keywords, TOC) | NOT COUNTED | — | ✅ Done |
| 01 | System Architecture & Framework Design | NOT COUNTED | 01 | ✅ Done |
| 02 | Introduction | 562w | 326w | ✅ Done |
| 03 | Problem Context and Motivation | 522w | 184w | ✅ Done |
| 04 | Cybersecurity Theories & Behavioural Factors | 748w | 293w | ✅ Done |
| 05 | Integration of Machine Learning in Cybersecurity | 549w | 249w | ✅ Done |
| 06 | Research Aim | 158w | 105w | ✅ Done |
| 07 | Research Objectives | 231w | 168w | ✅ Done |
| 08 | Contribution and Significance | 390w | 217w | ✅ Done |
| 09 | Justification of the Study | 630w | 403w | ✅ Done |
| 10 | Research Questions | 92w | 79w | ✅ Done |
| 11 | Research Hypotheses | 174w | 116w | ✅ Done |
| S | Scope of the Study | 172w | — (not in sample*) | ✅ Done |
| — | **SUBTOTAL 02–11 + Scope** | **4,228w** | **2,140w** | ✅ |
| 12 | Research Methodology | 814w | 402w | ✅ Done |
| 13 | Ethical Considerations | 720w | 381w | ✅ Done |
| 14 | Literature Review — Overview | 130w | 72w | ❌ TODO |
| 15 | Traditional & ML-Based Security Systems | 300w | 276w | ❌ TODO |
| 16 | Behavioural Economics & Human Factors | 270w | 251w | ❌ TODO |
| 17 | Case Study — CybSafe | 380w | CrowdStrike 358w | ❌ TODO |
| 18 | Case Study — KnowBe4 | 380w | Darktrace 358w | ❌ TODO |
| 19 | Case Study — Hoxhunt | 330w | IBM Watson 308w | ❌ TODO |
| 20 | Case Study — Proofpoint Security Awareness | 320w | FireEye 300w | ❌ TODO |
| 21 | Case Study — SANS Security Awareness | 320w | — (5th case study) | ❌ TODO |
| 22 | Literature Review Synthesis | 270w | 235w | ❌ TODO |
| 23 | Tools and Technologies | 480w | 479w | ❌ TODO |
| 24 | Ethical Reflection in Development | 460w | 451w | ❌ TODO |
| 25 | Findings — RQ1 (Technical) | 450w | 438w | ❌ TODO |
| 26 | Findings — RQ2 (Ethical) | 470w | 483w | ❌ TODO |
| 27 | Discussion, Conclusion & Future Work | 410w | 402w | ❌ TODO |
| — | **SUBTOTAL 12–27** | **5,760w** | **5,423w** | ❌ |
| — | **GRAND TOTAL (body)** | **9,988w** | **7,563w** | TARGET ✅ |
| — | References (50+ APA7) | NOT COUNTED | — | ❌ TODO |
| — | Appendices A–D | NOT COUNTED | — | ❌ TODO |

*Scope: assignment brief requires it; sample omits it. Keep the section — the brief is the marking instrument.

**Budget note:** AHRID's sections 02–11 are already 2,088w richer than the sample equivalent. Sections 12–27 have only 5,760w budget — just 337w more than the sample's 5,423w for those sections. Write tight and to target.

---

## 10 STRUCTURAL RULES FROM SAMPLE GUIDE

These patterns appear across every high-scoring section. Follow them exactly.

### Rule 1 — Introduction: 4-move structure
BROAD (global stat) → NARROW (Nepal/SME numbers) → GAP (one sentence) → SOLUTION (AHRID + mechanisms + key metric)

### Rule 2 — Every theory must end with a design-decision link
> "AHRID operationalises this by..." OR "This directly informed the design decision to..."
Never describe a theory without connecting it to a concrete AHRID architecture choice.

### Rule 3 — Case study: 5-move structure
BACKGROUND → TECHNICAL APPROACH → STRENGTH → LIMITATION (be critical) → LESSON: "For the AHRID framework, [Platform] demonstrates..."

### Rule 4 — Findings: always state baseline vs result
> "X improved from Y% [baseline] to Z% [AHRID], representing a [N]pp improvement"
Never state a metric in isolation.

### Rule 5 — Ethical Reflection must embed real design-decision statistics
Sample uses "94% required confidence scores" and "82% required explanation." AHRID must embed equivalent specific facts.

### Rule 6 — Methodology must end with a limitations paragraph
> "Nonetheless, the methodology is not without its limitations..."

### Rule 7 — Literature Synthesis: all case studies → themes → AHRID lessons
Close: "The AHRID framework directly incorporates these lessons: [lesson per platform in parenthetical]."

### Rule 8 — Conclusion: re-confirm both hypotheses by name, list all metrics, give 4 future directions

### Rule 9 — Research Questions: no preamble, just the two questions

### Rule 10 — Macro skeleton of every paragraph: PROBLEM → EVIDENCE → DESIGN RESPONSE

---

## SECTION-BY-SECTION CONTENT CHECKLIST

### FRONT MATTER ✅

- [x] Title Page: full project title, Rupesh Kumar Thakur, College ID 230548, CU ID 14806490, Batch 35'C, ST6047CEM, Manoj Shrestha, Softwarica × Coventry
- [x] System Architecture: Fig 1 (AHRID pipeline actual image) + Fig 2 (Sprint Cycle actual image)
- [x] Acknowledgement: supervisor + institution + volunteers + family
- [x] Abstract: 223w — platform, DSR, Nepal stats, ML pipeline, all 5 key metrics, both RQs, IPA 2075
- [x] Keywords: 16 relevant terms

---

### SECTIONS 02–11 + SCOPE ✅ (4,228w total)

**02 Introduction** ✅ (562w | 6 citations)
- [x] Global: USD 10.5T damages (Statista 2025)
- [x] SME: 88% ransomware incidents (Verizon 2025 DBIR)
- [x] Nepal: 18,926 incidents FY2024–25 (Nepal Police 2025)
- [x] Human element: 68% (Verizon 2025)
- [x] Generic training: 6-week retention failure (Lain et al. 2022)
- [x] Contextual relevance gap (Siponen 2000)
- [x] Enterprise platform exclusion (Kritzinger & von Solms 2010)
- [x] Explicit problem statement sentence
- [x] AHRID: K-Means + RF + SHAP + OSINT + 15-sprint Agile + DSR
- [x] Metrics: 91.4%, F1=0.8878, +52.24pp over baseline F1=0.3653

**03 Problem Context and Motivation** ✅ (522w | 5 citations)
- [x] Three structural deficiencies: budget / personnel / literacy
- [x] Platform cost: USD 15–40/user evidence
- [x] Hadlington 2017, Kabanda et al. 2018, IJMIR 2025
- [x] Workman 2008, Ahmad 2018, Buczak & Guven 2016
- [x] Interdisciplinary convergence (CS + psychology + org risk)
- [x] Figure 4 placeholder

**04 Cybersecurity Theories** ✅ (748w | 9 sources)
- [x] Framed as design constraints not background — "Theory is not decoration here"
- [x] PMT (Rogers 1975/1983 + Floyd et al. 2000) → SHAP + scenario design
- [x] Prospect Theory (Kahneman & Tversky 1979) → 3 biases → OSINT + adaptive sequencing
- [x] TAM (Davis 1989 + Venkatesh et al. 2003) → SHAP as usefulness mechanism
- [x] Compliance budget (Beautement et al. 2008) → low-burden design
- [x] Wogalter et al. 1999 → warnings understood = acted upon
- [x] Workman 2008 + Boss et al. 2015 → non-punitive governance
- [x] Siponen 2000 → alternative frameworks rejected
- [x] Typo fixed: "specific AHRID" | PMT duplication removed
- [x] Figure 5 placeholder

**05 ML Integration** ✅ (549w | 6 citations)
- [x] Cross-domain: finance (Dal Pozzolo 2018), healthcare, manufacturing
- [x] SIEM/EDR fragmentation gap
- [x] Novel dual-pipeline: K-Means cluster label → RF input feature
- [x] RF (Breiman 2001), SMOTE (Chawla 2002), K-Means (Artioli 2024)
- [x] scikit-learn 1.4 (Pedregosa 2011), SHAP (Lundberg & Lee 2017)
- [x] Figure 6 placeholder

**06 Research Aim** ✅ (158w)
- [x] One aim sentence + 5 sub-components

**07 Research Objectives** ✅ (231w)
- [x] Table 1: 5 objectives × Type (L&U / D&D / F&S) × Section mapping

**08 Contribution and Significance** ✅ (390w | 3 citations)
- [x] Technical: novel dual-component + all metrics
- [x] Interdisciplinary: theory → engineering
- [x] Practical: open OSINT, no subscription, SME-accessible
- [x] Ethical: IPA 2075, non-punitiveness, Jobin et al. 2019

**09 Justification of the Study** ✅ (630w | 6 citations)
- [x] Nepal: 18,926 / 52/day / 40.8% financial fraud (Nepal Police 2025)
- [x] Underreporting acknowledged + "true incidence is higher"
- [x] Verizon 2025: personalisation argument
- [x] Academic gap: Buczak & Guven 2016, IJMIR 2025, Kabanda 2018
- [x] Practical: Kemp 2025, Ahmad 2018
- [x] Realistic expectations stated
- [x] Figure 7 placeholder

**10 Research Questions** ✅ (92w | 0 citations — correct per Rule 9)
- [x] RQ1 "How can an adaptive ML platform..." (Technical)
- [x] RQ2 "What ethical obligations arise..." (Ethical)
- [x] No preamble

**11 Research Hypotheses** ✅ (174w)
- [x] H1: K-Means + RF + SHAP → statistically significant improvement
- [x] H2: "While X can Y, without Z, W occurs" — conditional warning

**Scope of the Study** ✅ (172w)
- [x] Geographic: Kathmandu Valley only
- [x] Organisational: non-technical roles (not IT staff)
- [x] Technical: synthetic data, IPA 2075 compliant, no real user data
- [x] Methodological: desk-based, no longitudinal deployment
- [x] OSINT: read-only feeds, no offensive operations

---

### SECTIONS 12–27 ❌ (5,760w to write)

**12 Research Methodology** ✅ — 814w (includes Table 2 Risk Register)
- [ ] Open: "desk-based Design Science Research methodology" (Hevner et al. 2004)
- [ ] DSR justification: artefact-building suits cybersecurity platform research
- [ ] Agile rationale: 5-phase, 15-sprint; why Agile suits evolving threat landscapes
- [ ] Multi-phase overview: Requirements → Literature → ML Dev → Integration → Evaluation
- [ ] Data: synthetic behavioural data calibrated to KV SME patterns; OSINT read-only
- [ ] ML development: train/test split, SMOTE, 5-fold cross-validation
- [ ] Ethics embedded at each sprint (not post-hoc)
- [ ] **LIMITATIONS paragraph** ← required by Rule 6
- [ ] Figure 8: 15-Sprint Project Plan placeholder
- [ ] Table 2: Risk Register (5 risks × likelihood × impact × mitigation × owner)
- [ ] Citations: Hevner et al. 2004, March & Smith 1995, Peffers et al. 2007

**13 Ethical Considerations** ✅ — 720w
- [ ] Open: "profound ethical implications beyond technical performance"
- [ ] Privacy: IPA 2075, data minimisation, no PII in dataset
- [ ] Algorithmic bias: SMOTE, feature audit for identity-attribute proxies
- [ ] Transparency: SHAP as accountability mechanism
- [ ] Non-punitiveness: elevated tier triggers learning, not sanction
- [ ] Human oversight: employees can contest; managers see aggregate only
- [ ] Close: "ethics not an afterthought — built into every sprint"
- [ ] Citations: Jobin et al. 2019, Nepal IPA 2075, ICO 2021

**14 Literature Review — Overview** ❌ — target 130w
- [ ] 1 opening sentence on ML in cybersecurity acceleration
- [ ] Preview bullet points: evolution / behavioural economics / 5 case studies / synthesis
- [ ] Name the 5 AHRID case studies: CybSafe, KnowBe4, Hoxhunt, Proofpoint, SANS

**15 Traditional & ML-Based Security Systems** ❌ — target 300w
- [ ] Historical progression: generic SAT → phishing simulators → adaptive platforms
- [ ] Limitation at each stage (static → click-rate only → no explainability)
- [ ] ML advances in awareness training (behavioural classifiers, personalisation)
- [ ] The gap: "platforms target infrastructure; none address human behavioural trajectory in SME contexts"
- [ ] Citations: Sasse et al. 2001, Hadnagy 2011, Lain et al. 2022

**16 Behavioural Economics & Human Factors** ❌ — target 270w
- [ ] Expected Utility Theory: normative rational model
- [ ] Prospect Theory (Kahneman & Tversky): loss aversion, availability heuristic in security
- [ ] Cognitive load: alert fatigue degrades security decision quality
- [ ] Design insight: automated systems mitigate bias through consistent analysis
- [ ] AHRID link: OSINT → availability heuristic fix; adaptive sequencing → confirmation bias fix
- [ ] Citations: Kahneman & Tversky 1979, Hadlington 2017, Beautement et al. 2008

**17 Case Study — CybSafe** ❌ — target 380w (Rule 3: 5 moves)
- [ ] Background: founded 2012, UK, behavioural science, SebDB behavioural database
- [ ] Technical: phishing simulation + behavioural risk scoring + culture analytics
- [ ] Strength: most scientifically grounded human-risk platform; longitudinal behaviour tracking
- [ ] Limitation: enterprise per-seat pricing; English-only; no OSINT; no SHAP explainability
- [ ] Lesson: "For AHRID, CybSafe demonstrates behavioural science grounding is essential. However, pricing exclusion and opacity motivate AHRID's open-OSINT design and SHAP layer"
- [ ] Table 3: CybSafe at a Glance

**18 Case Study — KnowBe4** ❌ — target 380w (Rule 3: 5 moves)
- [ ] Background: founded 2010, Stu Sjouwerman, 65,000+ customers, largest phishing simulation library
- [ ] Technical: phishing templates + LMS + SecurityCoach real-time coaching + risk scoring by click-rate
- [ ] Strength: largest library; strong enterprise adoption; broad content coverage
- [ ] Limitation: punitive design (shaming poor performers) violates PMT coping appraisal; no adaptive personalisation; USD 24–48/user/year
- [ ] Lesson: "KnowBe4 validates phishing simulation efficacy. Its punitive framing directly violates PMT — AHRID's non-punitive governance is a direct design response"
- [ ] Table 4: KnowBe4 at a Glance

**19 Case Study — Hoxhunt** ❌ — target 330w (Rule 3: 5 moves)
- [ ] Background: founded 2016, Helsinki, gamified adaptive phishing simulation
- [ ] Technical: adaptive difficulty engine, gamification (points, badges), employee feedback loop
- [ ] Strength: adaptive difficulty improves engagement; tracks individual progress
- [ ] Limitation: historical scenario templates (no live OSINT); no SHAP explainability; SME pricing barrier
- [ ] Lesson: "Hoxhunt validates adaptive difficulty. Without live feeds, training reflects historical threats — AHRID's OSINT pipeline addresses this directly"
- [ ] Table 5: Hoxhunt at a Glance

**20 Case Study — Proofpoint Security Awareness Training** ❌ — target 320w (Rule 3: 5 moves)
- [ ] Background: enterprise email security company, acquired Wombat Security 2018
- [ ] Technical: threat-aware content from email intelligence, CISO dashboards, real phishing templates
- [ ] Strength: most current threat content available commercially
- [ ] Limitation: requires Proofpoint email subscription (vendor lock-in); closed OSINT; SME cost barrier; no individual explainability
- [ ] Lesson: "Proofpoint validates threat-aware training content. Proprietary lock-in — AHRID achieves same currency via open OSINT (Phishing.Database + AlienVault OTX)"
- [ ] Table 6: Proofpoint at a Glance

**21 Case Study — SANS Security Awareness** ❌ — target 320w (Rule 3: 5 moves)
- [ ] Background: SANS Institute, Securing the Human programme, academic/research credibility
- [ ] Technical: annual curriculum, role-based modules, security culture maturity model
- [ ] Strength: research-backed content; maturity framework; most trusted academic brand
- [ ] Limitation: static annual curriculum; no ML personalisation; no live threats; English-only; expensive; no local context
- [ ] Lesson: "SANS validates security culture maturity as measurable. Annual static curriculum cannot match AHRID's daily OSINT-driven scenario refresh"
- [ ] Table 7: SANS at a Glance

**22 Literature Review Synthesis** ❌ — target 270w
- [ ] Open: connect all 5 case studies by lesson theme (pricing / adaptability / explainability / live content / local context)
- [ ] Common gaps across all 5: SME pricing exclusion / no open OSINT / no explainability / no local context / English-only
- [ ] Table 8: Five Platforms vs AHRID Feature Matrix (rows: 6 platforms; cols: adaptive ML / live feeds / explainability / SME pricing / local context / open-source)
- [ ] Close: "The AHRID framework directly incorporates these lessons: interpretable scoring (CybSafe), non-punitive design (KnowBe4), live OSINT (Hoxhunt), open feeds (Proofpoint), dynamic curriculum (SANS)"

**23 Tools and Technologies** ❌ — target 480w
- [ ] Python 3.11 — ecosystem justification
- [ ] FastAPI — async backend, REST API
- [ ] React — frontend dashboard
- [ ] PostgreSQL — relational storage for user/scenario data
- [ ] scikit-learn 1.4 — RF + K-Means + SMOTE (cite Pedregosa 2011)
- [ ] SHAP — explainability layer (cite Lundberg & Lee 2017)
- [ ] pandas + NumPy — data processing
- [ ] Phishing.Database + AlienVault OTX — OSINT ingestion (read-only)
- [ ] Docker — containerised deployment (Render free tier)
- [ ] GitHub Actions — CI/CD and keep-warm cron job
- [ ] Justify EACH technology choice explicitly (not just list)
- [ ] Table 9: Technology Stack (Component | Technology | Version | Justification)
- [ ] Figure 11: AHRID Technical Architecture layer diagram placeholder

**24 Ethical Reflection in Development** ❌ — target 460w
- [ ] Open: "not an afterthought — a parallel inquiry integrated into every sprint"
- [ ] Privacy: IPA 2075 compliance; synthetic data only; no PII; 14 features are behavioural, not identity-based
- [ ] Bias: feature audit conducted; SMOTE prevents class dominance; no demographic proxies
- [ ] Transparency: SHAP provides plain-language per-prediction attribution; all scores contestable
- [ ] Automation boundary: score triggers learning, not sanction; no automated consequence
- [ ] Role-based access: employees see own score; managers see team aggregate only
- [ ] Embed at least 2 specific design-decision facts (counts/percentages)
- [ ] Close: epistemic responsibility — "employees must understand basis for scores, not delegate judgment blindly"

**25 Findings — RQ1 (Technical)** ❌ — target 450w
- [ ] Accuracy: 91.4% — state what baseline this compares to
- [ ] F1 macro: 0.8878 vs baseline 0.3653 → +52.24pp (Rule 4: baseline vs result)
- [ ] PR-AUC: 0.9166 | Cohen's Kappa: 0.8751
- [ ] K-Means Silhouette: 0.268 at k=5; tested k=2–8 (k=5 selected)
- [ ] 5 archetypes named: Overconfident Clicker, Cautious Learner, Inconsistent Performer, Resilient Defender, Disengaged Completer
- [ ] Cluster label contribution: evidence it improved RF F1 vs RF without cluster label
- [ ] OSINT pipeline: feeds active, scenario generation functional across 8 categories
- [ ] Figure 12: Confusion Matrix (actual model output)
- [ ] Figure 13: Silhouette Plot k=2–8 (actual model output)
- [ ] Table 11: Training Dataset Feature Summary (14 features × description × type)
- [ ] Table 12: RF Performance Metrics vs Baseline (all 5 metrics side by side)
- [ ] Limitations paragraph: synthetic data, no live user study
- [ ] Close: "These findings confirm H1..."

**26 Findings — RQ2 (Ethical)** ❌ — target 470w
- [ ] Privacy: IPA 2075 compliance confirmed; no PII; data minimisation
- [ ] Bias: 14 features audited — no identity-attribute proxies; SMOTE for class balance
- [ ] Transparency: SHAP explanations for all predictions; plain-language format validated
- [ ] Non-punitive governance: elevated tier → learning pathway, not sanction
- [ ] Role-based access: design confirmed — three distinct roles (employee / manager / HR)
- [ ] Table 10: Ethics as Design Constraint Matrix (rows: each principle; cols: obligation, design decision, implementation, validation)
- [ ] Figure 14: Ethics Design Decision Map placeholder
- [ ] Close: "These findings confirm H2: AHRID improves outcomes; without embedded governance framework, privacy and trust risks would remain unmitigated"

**27 Discussion, Conclusion & Future Work** ❌ — target 410w
- [ ] Open: "This research has successfully demonstrated..."
- [ ] Confirm H1 and H2 explicitly by name (Rule 8)
- [ ] Restate ALL metrics: 91.4%, F1=0.8878, +52.24pp, Kappa=0.8751, Silhouette=0.268
- [ ] Ethical contributions: governance framework, IPA 2075 compliance model
- [ ] Interdisciplinary: PMT + PT + TAM → design decisions → measurable outcomes
- [ ] Implications: AHRID as model for non-Western SME security awareness platforms
- [ ] Limitations: synthetic data / desk-based / English UI / no longitudinal study
- [ ] 4 future directions (Rule 8):
  1. Live deployment study with real Kathmandu Valley SMEs
  2. Federated learning across SMEs without data sharing
  3. Nepali-language UI development
  4. Integration with Nepal's evolving regulatory framework
- [ ] Closing statement of contribution to the field

---

## FIGURE INVENTORY

| # | Description | Section | Status |
|---|-------------|---------|--------|
| 1 | AHRID System Architecture: End-to-End Pipeline | 01 | ✅ ACTUAL IMAGE |
| 2 | Agile Research Methodology Sprint Cycle | 01 | ✅ ACTUAL IMAGE |
| 3 | Nepal Cybercrime Incident Trends FY2023–2025 | 02 | ❌ PLACEHOLDER — Canva needed |
| 4 | Structural Mismatch: Platforms vs SME Needs | 03 | ❌ PLACEHOLDER — Canva needed |
| 5 | Integrated Theoretical Framework (PMT+PT+TAM) | 04 | ❌ PLACEHOLDER — Canva needed |
| 6 | AHRID Dual ML Pipeline (RF+K-Means+SHAP) | 05 | ❌ PLACEHOLDER — Canva needed |
| 7 | Five-Angle Justification Framework | 09 | ❌ PLACEHOLDER — Canva needed |
| 8 | 15-Sprint Project Plan (Jan–Jul 2026) | 12 | ❌ TO ADD |
| 9 | Evolution of Security Awareness (2000–2025) | 15 | ❌ TO ADD |
| 10 | Why Employees Fail: Three Cognitive Biases | 16 | ❌ TO ADD |
| 11 | AHRID Technical Architecture (Layer Diagram) | 23 | ❌ TO ADD |
| 12 | Random Forest Confusion Matrix (actual output) | 25 | ❌ EXPORT FROM MODEL |
| 13 | K-Means Silhouette Plot k=2–8 (actual output) | 25 | ❌ EXPORT FROM MODEL |
| 14 | Ethics Design Decision Map (flowchart) | 26 | ❌ TO ADD |

**Canva priority:** Fig 3 → Fig 6 → Fig 5 → Fig 7 → Fig 4

---

## TABLE INVENTORY

| # | Description | Section | Status |
|---|-------------|---------|--------|
| 1 | Research Objectives (5 rows × 3 cols) | 07 | ✅ IN DOCX |
| 2 | Risk Register (5 risks × 5 cols) | 12 | ❌ TODO |
| 3 | CybSafe at a Glance | 17 | ❌ TODO |
| 4 | KnowBe4 at a Glance | 18 | ❌ TODO |
| 5 | Hoxhunt at a Glance | 19 | ❌ TODO |
| 6 | Proofpoint at a Glance | 20 | ❌ TODO |
| 7 | SANS at a Glance | 21 | ❌ TODO |
| 8 | Five Platforms vs AHRID Feature Matrix | 22 | ❌ TODO |
| 9 | Technology Stack (4 cols) | 23 | ❌ TODO |
| 10 | Ethics as Design Constraint Matrix | 26 | ❌ TODO |
| 11 | Training Dataset Feature Summary (14 features) | 25 | ❌ TODO |
| 12 | RF Performance Metrics vs Baseline | 25 | ❌ TODO |

---

## CITATION TARGETS

| Section | Current | Target | Sources still needed |
|---------|---------|--------|---------------------|
| 02 Introduction | 6 | 6 | ✅ |
| 03 Problem Context | 5 | 5 | ✅ |
| 04 Theories | 9 sources | 8+ | ✅ |
| 05 ML Integration | 6 | 6 | ✅ |
| 08 Contribution | 3 | 3 | ✅ |
| 09 Justification | 6 | 6 | ✅ |
| 12 Methodology | 0 | 3+ | Hevner 2004, Peffers 2007, March & Smith 1995 |
| 13 Ethics | 0 | 3+ | Jobin 2019, Nepal IPA 2075, ICO 2021 |
| 15 Traditional ML | 0 | 3+ | Sasse 2001, Hadnagy 2011, Lain 2022 |
| 16 Behavioural Econ | 0 | 3+ | Kahneman 1979, Hadlington 2017, Beautement 2008 |
| 17–21 Case Studies | 0 | 2+ each | Platform white papers/annual reports |
| 23 Tools | 0 | 5+ | Pedregosa 2011, Lundberg 2017, Breiman 2001 + others |
| 24 Ethical Reflection | 0 | 3+ | Jobin 2019, IPA 2075, Floridi 2019 |
| 25 Findings RQ1 | 0 | 4+ | Breiman 2001, Chawla 2002, Lundberg 2017, Artioli 2024 |
| 26 Findings RQ2 | 0 | 3+ | Jobin 2019, IPA 2075, Workman 2008 |
| 27 Conclusion | 0 | 2+ | Hevner 2004 + key finding citations |
| **Body total** | **~27** | **50+ in References** | Need ~23+ more unique sources |

---

## REFERENCES SECTION REQUIREMENTS

- [ ] 50+ sources, APA7 format, alphabetical by first author surname
- [ ] All 27 currently cited body sources included
- [ ] 23+ additional sources for sections 12–27
- [ ] Source mix required:
  - Academic journals: minimum 20
  - Books/textbooks: minimum 5
  - Government/policy: Nepal Police 2025, Nepal IPA 2075 text
  - Industry reports: Verizon DBIR 2025, Statista 2025, DataReportal/Kemp 2025
  - Platform sources: CybSafe white papers, KnowBe4 State of Phishing, Verizon DBIR

---

## APPENDICES REQUIREMENTS

**A — Technical Specifications**
- [ ] Hardware/deployment environment (Render backend, Vercel frontend)
- [ ] Software versions: Python 3.11, scikit-learn 1.4, FastAPI, React, PostgreSQL
- [ ] GitHub Actions keep-warm configuration

**B — Code Snippets (5 excerpts)**
- [ ] B1: RF Training Pipeline (backend/train_models.py)
- [ ] B2: SMOTE Balancing Block (backend/seed_synthetic_ml_data.py)
- [ ] B3: SHAP TreeExplainer Attribution Generator
- [ ] B4: OSINT Ingestion Pipeline (backend/app/services/threat_ingestion.py)
- [ ] B5: Adaptive Engine Scenario Selection (backend/app/services/adaptive_engine.py)

**C — SWOT Analysis**
- [ ] Strengths: novel dual-pipeline / SHAP / open OSINT / SME-accessible / free tier
- [ ] Weaknesses: synthetic data only / English UI / desk-based / no longitudinal
- [ ] Opportunities: Nepal digital growth / regulatory push / SME market gap
- [ ] Threats: enterprise platforms dropping prices / evolving phishing / adversarial ML

**D — Glossary (15+ terms)**
- [ ] AHRID, OSINT, PMT, SHAP, K-Means, RF, SMOTE, Silhouette, F1 macro, PR-AUC, Cohen's Kappa, TAM, DSR, SME, IPA 2075, Phishing, Vishing, Behavioural archetype, DBIR

---

## WRITING QUALITY STANDARDS (FIRST CLASS CRITERIA)

- [ ] British English: colour, analyse, programme, behaviour, organisation, recognise
- [ ] No em dashes in text — restructure with semicolons
- [ ] APA7 in-text citations: (Author, Year) — never footnotes
- [ ] Sentence variety: 8–12 word punchy + 20–30 word analytical sentences mixed
- [ ] Every theory → design decision link (Rule 2)
- [ ] Every case study → AHRID lesson (Rule 3)
- [ ] No vague filler: "robust", "leverage", "state-of-the-art" used sparingly if at all
- [ ] Figure captions APA7: **Figure N**\n *italic title*\n *Note.* Source statement.
- [ ] Table captions APA7: **Table N**\n *title above the table*\n *Note.* below the table

---

## AHRID METRICS QUICK REFERENCE

| Metric | Value |
|--------|-------|
| Accuracy | 91.4% |
| F1 macro | 0.8878 |
| Baseline F1 | 0.3653 |
| F1 improvement | +52.24 percentage points |
| PR-AUC | 0.9166 |
| Cohen's Kappa | 0.8751 |
| Silhouette (k=5) | 0.268 |
| K-Means clusters | 5 |
| RF features | 14 |
| RF estimators | 200 |
| Agile sprints | 15 |
| Agile phases | 5 |
| Nepal incidents FY24–25 | 18,926 |
| Human element in breaches | 68% (Verizon 2025) |
| SME ransomware share | 88% (Verizon 2025) |
| Nepal mobile penetration | 76.4% (Kemp 2025) |
| Global cybercrime damages | USD 10.5T annually (Statista 2025) |
| Projected 2029 damages | USD 15.63T (Statista 2025) |
| Nepal financial fraud share | 40.8% of incidents (Nepal Police 2025) |

---

*Last updated: 2026-07-05*
*Sections 02–11 + Scope: DONE (4,228w) | Sections 12–27: TODO (5,760w target)*
