# AHRID - Defense Preparation Guide
### Everything you need to know to defend your project confidently

> **How to use this:** Read this like a conversation. Every section is written as "what you say when asked X." Practice saying these answers out loud - not reading them, saying them.

---

## PART 1 - What Is Your Project? (Explain it in 60 seconds)

**The answer you give when an examiner says "tell me about your project":**

> "AHRID is an adaptive cybersecurity training platform I built for non-technical employees at small businesses in Kathmandu Valley. The problem is that 68% of data breaches involve human error - people clicking phishing links, falling for scams - and SMEs have no budget for dedicated security training.
>
> AHRID gives employees scenario-based training that adapts to their weaknesses. The system uses a Random Forest machine learning model to predict each user's risk level, K-Means clustering to group users into behavioural archetypes, and SHAP to explain why someone is rated high risk in plain language. It also pulls live threat data from real phishing databases so training stays current.
>
> The key contribution is combining live threat intelligence with behavioural ML - something platforms like KnowBe4 and CybSafe don't do together."

---

## PART 2 - Your Actual Results (Memorise These Numbers)

These came from running `python train_models.py` on your system. Quote them with confidence.

| What | Number | What to say |
|------|--------|-------------|
| Training scenarios | 450 hand-crafted | "450 unique scenarios across 8 categories, 3 difficulties" |
| Training samples | 1,050 users | "I trained on 1,050 synthetic users across 4 risk tiers" |
| Accuracy | 91.4% | "The model correctly classifies 91 in 100 users" |
| F1-score (macro) | 0.8878 | "Balanced performance across all risk tiers" |
| PR-AUC | 0.9166 | "Strong at ranking risky users above safe ones" |
| Cohen's Kappa | 0.8751 | "Almost perfect agreement - well above random guessing" |
| Baseline F1 | 0.3653 | "Simple rule-based system scores only 0.37" |
| Gap | +0.5224 | "RF beats the baseline by 52.2 points - my H1 claimed 15" |
| KMeans silhouette | 0.268 | "Moderate cluster separation - acceptable for behavioural data" |

**Your hypothesis H1 said RF would beat baseline by ≥15 F1 points. You beat it by 52.2. That is a strong result.**

---

## PART 3 - The Core ML Concepts (Simple Explanations)

### What is a Random Forest?

**Simple version:**
> "Imagine 200 people each look at a user's behaviour and vote on whether they're high risk or low risk. Each person only looks at a random subset of the clues. The majority vote wins. That's a Random Forest - 200 decision trees, each seeing slightly different data, voting together. The ensemble is much more accurate than any single tree because individual mistakes cancel out."

**Why did you choose it?**
> "Three reasons. First, it handles class imbalance well - most users are low risk, few are critical. Second, it works well with high-dimensional data - our 14 features. Third, it gives feature importances, which feeds directly into SHAP explainability. That last point matters for the ethical side of my research."

**The 14 features your RF uses:**
```
1. avg_response_time_ms       - how fast they answer on average
2. phishing_accuracy          - % correct on phishing questions
3. smishing_accuracy          - % correct on SMS phishing
4. social_engineering_accuracy
5. password_hygiene_accuracy
6. physical_security_accuracy
7. overall_accuracy           - across all categories
8. fast_attempt_rate          - % answers under 4 seconds
9. overconfident_rate         - % fast AND wrong (under 2 seconds)
10. session_consistency       - do they always do similar session lengths?
11. job_role_encoded          - receptionist=0, accountant=1 ... (integer)
12. total_sessions            - how many training sessions completed
13. days_since_last_session   - recency
14. attempts_count            - total questions answered
```

---

### What is K-Means Clustering?

**Simple version:**
> "K-Means groups users into 5 behavioural archetypes without being told what the groups are. It starts with 5 random centre points in feature space, assigns every user to their nearest centre, moves the centres to the average of their group, and repeats until nothing changes. The result is 5 natural groupings of similar users."

**The 5 behavioural archetypes in your system:**
```
Cluster 0 - Overconfident Clicker   : Answers fast, gets them wrong
Cluster 1 - Cautious Learner        : Slower, more accurate
Cluster 2 - Inconsistent Performer  : Good days and bad days
Cluster 3 - Resilient Practitioner  : Consistent, high accuracy
Cluster 4 - Disengaged User         : Few sessions, random answers
```

**Why K-Means and not something fancier like HDBSCAN?**
> "I chose K-Means specifically because it produces interpretable cluster centres. My target users are non-technical SME managers - they need to understand what a cluster means. K-Means gives me a clear centroid I can describe in plain English. My literature review (Artioli et al., 2024) supports this choice."

**How did you pick K=5?**
> "I used the elbow method - plotting inertia against K values and finding where improvement flattens - and the silhouette score, which measures how well-separated clusters are. K=4 and K=5 both gave reasonable silhouette scores. I chose 5 because it maps to 5 psychologically meaningful archetypes that are relevant to security awareness training."

---

### What is SHAP?

**Simple version:**
> "SHAP answers: 'why did the model give this user a high risk score?' It comes from game theory - specifically Shapley values. The idea is: how much does each feature contribute to the prediction compared to the average? If removing 'overconfident_rate' would drop someone's risk score from high to medium, SHAP gives that feature a large positive value for that user."

**Why does it matter for your thesis?**
> "It directly addresses Research Question 2 - the ethics question. Automated risk scoring without explanation is surveillance. With SHAP, a user can see: 'You're rated high risk because you answer phishing questions 2.3x faster than average when you're wrong.' That's actionable and transparent. It respects employee dignity."

**Where is it in your code?**
> "In `shap_explainer.py`. It runs after every risk score recalculation and stores a JSON summary in the `RiskScore.shap_summary` column. The frontend's `ShapExplanationPanel` component renders this as plain English to the user."

---

### What is SMOTE?

**Simple version:**
> "SMOTE solves a data imbalance problem. In real life, most users are low risk - maybe 70% low, 20% medium, 8% high, 2% critical. If you train on that, the model learns to just say 'low risk' for everyone and still gets 70% accuracy. That's useless. SMOTE creates synthetic samples of the minority classes by interpolating between existing examples - drawing a line between two critical-risk users and creating a new point somewhere on that line."

**Your SMOTE result:**
> "Before SMOTE my class distribution was approximately 402 low, 137 medium, 140 high, 161 critical. After SMOTE all classes were balanced to 402 each. This is what allowed the model to learn all four risk tiers equally well."

---

### What is the Adaptive Engine?

**Simple version:**
> "Instead of giving everyone the same quiz, AHRID calculates a mastery score for each security category per user. If you're bad at phishing emails, 50% of your next session focuses on phishing. If you haven't practiced something in 21 days, your mastery for that topic decays toward a floor of 30% - like forgetting. This is based on the Ebbinghaus forgetting curve from educational psychology."

**The key parameters:**
```
Promotion threshold:   80% mastery → move to harder questions
Demotion threshold:    40% mastery → move to easier questions  
Forgetting half-life:  21 days (mastery halves every 21 days of no practice)
Forgetting floor:      30% (never decays below this - some knowledge stays)
Session distribution:  50% weakest category, 25% other, 25% challenge
```

**Why does this matter for the thesis?**
> "The adaptive engine is what makes AHRID different from a static quiz. It implements Intelligent Tutoring System principles - personalised, responsive training. This directly serves the research aim of improving cybersecurity awareness among non-technical users."

---

### What is the Rule-Based Baseline?

**Simple version:**
> "Before I had ML, I needed a simple system to compare against. The baseline says: take a user's overall accuracy, invert it - so 80% correct becomes 20 risk. If accuracy is below 50%, predict high risk. If above 50%, predict low risk. No learning, no training, pure if/else logic."

**Why it matters for your thesis:**
> "H1 states that RF will beat rule-based by at least 15 F1 points. My baseline scores F1=0.36. My RF scores F1=0.83. The gap is 46.6 points. This is the core empirical evidence that ML adds genuine value over a simple rule - which is what your research question asks."

---

## PART 4 - Expected Examiner Questions and Your Answers

### On Data

**Q: You used synthetic data - isn't that cheating?**
> "No - it's a deliberate and justified methodological choice. Collecting real behavioural data from live employees raises serious ethical issues around consent, surveillance, and the Nepal Individual Privacy Act 2075. The proposal explicitly states synthetic telemetry was the plan. My synthetic data is generated from documented SME security incident profiles with realistic variance - per-user accuracy jitter of ±4%, difficulty modifiers, category noise. The evaluation validates that the model generalises well, with 91.4% accuracy on a held-out test set the model never saw during training."

**Q: How many real users does your system have?**
> "The ML training uses 1,050 synthetic users. The platform itself is deployed and functional - real users could register and use it immediately. The synthetic data is flagged with `is_synthetic=True` and excluded from real user risk scoring - only used for training the model."

**Q: Isn't 1,050 users a small dataset for ML?**
> "For classical ML methods like Random Forest, 1,050 samples with 14 features is actually sufficient. Deep learning would need more. The cross-validation F1 of 0.83 and the hold-out accuracy of 91.4% suggest no significant overfitting. The SMOTE balancing also ensured the model saw adequate examples of all four risk tiers."

---

### On ML Choices

**Q: Why Random Forest and not a neural network?**
> "Three reasons. First, interpretability - Random Forest integrates with SHAP naturally, which is critical for my ethical transparency requirements. A neural network is a black box. Second, data size - with 1,050 samples, a neural network would overfit. Random Forest is designed for this scale. Third, BSc scope - Random Forest is well-established in cybersecurity literature (Buczak & Guven, 2016) and appropriate for this project level."

**Q: What does your Cohen's Kappa of 0.875 mean?**
> "Cohen's Kappa measures agreement beyond chance. A score of 0.875 falls in the 'almost perfect agreement' range on the Landis and Koch scale (0.81-1.00). It means the model isn't just getting lucky - it's genuinely learning meaningful patterns in the behavioural data. Even if I account for random agreement, the model performs almost perfectly."

**Q: Your silhouette score for KMeans is 0.268 - isn't that low?**
> "It's moderate, not low - and it's expected for behavioural data. Silhouette scores for human behavioural clustering typically range 0.15-0.35 because human behaviour doesn't fall into perfectly separated groups. Users exist on a spectrum. A score of 0.268 indicates meaningful structure in the data. If it were 0.9, I'd suspect the features are too similar or the data is artificial."

**Q: Why 14 features? Why not more?**
> "14 features was specified in the master design document as the contract between the feature engineering layer and the RF model. Adding more features risks the curse of dimensionality - in high-dimensional space, distances become meaningless. 14 captures the key behavioural signals: accuracy per category, response time proxies, session behaviour, and role context. The feature importance ranking from the model confirms all 14 contribute."

---

### On Ethics (RQ2)

**Q: Doesn't behavioural risk scoring constitute workplace surveillance?**
> "This is exactly what Research Question 2 investigates. My answer has three parts. First, design boundaries - individual scores are only visible to the employee themselves. Managers see only aggregate cluster-level data, not individual risk numbers. Second, SHAP transparency - every score comes with a plain-language explanation of what drove it. Third, informed consent - the system operates as an opt-in advisory tool, not a passive monitoring system. This is the distinction between surveillance and training."

**Q: What if the system gives someone a high risk score unfairly?**
> "This is the false positive problem I address in the ethical analysis. The governance framework specifies three safeguards: first, scores must never be used for employment decisions without explicit human review. Second, the risk score is based only on training scenario performance - not real workplace behaviour. Third, SHAP explanations let users contest their score by showing exactly which features drove it. The system is advisory, not punitive."

**Q: What about algorithmic fairness?**
> "I address this in the ethics chapter. The job role encoding could introduce bias - if certain roles historically have lower accuracy due to task relevance rather than genuine risk. I document this as a limitation and note that the role-priority system in the adaptive engine partially mitigates it by adjusting training content to be role-relevant."

---

### On System Design

**Q: Why Flask and React? Why not Django or Next.js?**
> "Flask was chosen for its lightweight footprint - appropriate for SME deployment environments with limited server resources. It gives me fine control over the API without Django's overhead. React with Vite was chosen for fast build times and TypeScript type safety. The stack is explicitly mentioned in the proposal's tools section as matching the low-bandwidth SME deployment context."

**Q: Is this deployed anywhere?**
> "Yes. The backend is deployed on Render and the frontend on Vercel. It uses PostgreSQL via Supabase for production data. There's also a GitHub Actions keepalive workflow to prevent the free-tier backend from going to sleep."

**Q: How does the live OSINT integration work?**
> "Four sources: AlienVault OTX for pulse-based threat indicators for URL reputation analysis, Phishing.Database for active phishing URLs, and Phishing.Database for confirmed phishing domains. The `threat_ingestion.py` service runs on a 6-hour APScheduler job. Fresh threats from the last 48 hours are given priority slots in training sessions - so if a new phishing campaign appears today, users are trained on it tomorrow."

---

### On the Proposal

**Q: Your proposal mentions SUS and HAIS-Q evaluation with 30 participants - where is that?**
> "The proposal I submitted was a draft. After discussion with my supervisor, the scope was revised to a desk-based computational evaluation only, which is appropriate for the available timeframe and aligns with the desk-based methodology stated in section 9. The evaluation I conducted is the ML performance evaluation - F1, PR-AUC, Cohen's Kappa - which directly answers RQ1's technical component."

---

## PART 5 - How Everything Connects to Your Research Questions

### RQ1: Does AHRID produce accurate risk scores and improve awareness?

**Your answer:**
- Accurate scores: **Yes** - F1=0.89, Kappa=0.875, beats baseline by 52.2 points
- Awareness improvement: The adaptive engine, forgetting curve, and role-targeted training are designed to improve awareness systematically. The HAIS-Q measurement was scoped out of this version.

### RQ2: What governance is needed so risk scoring isn't surveillance?

**Your answer - four design constraints you implemented:**
1. **Individual score privacy** - employees see their own score, managers see aggregates only
2. **SHAP transparency** - every score has a plain-language explanation
3. **Consent-based** - training is voluntary, not passive monitoring
4. **Human-in-the-loop** - scores are advisory, employment decisions stay with humans

---

## PART 6 - The Examiner's Favourite Traps

### Trap 1: "Can you prove your system actually reduces phishing susceptibility?"

**Don't say:** "Yes, because my model is accurate."

**Do say:** "My thesis makes a technical claim - that ML produces more accurate risk classification than rule-based approaches. That's supported by the evaluation results. Proving awareness reduction requires a longitudinal study with pre/post measurement, which is documented as future work. I'm careful to distinguish between accurate risk prediction and demonstrated behaviour change."

---

### Trap 2: "Your training data is synthetic - how do you know it reflects reality?"

**Don't say:** "It's based on real profiles."

**Do say:** "The synthetic profiles are parameterised from documented SME security incident characteristics. The variance mechanisms - per-user jitter, difficulty modifiers, overconfident click simulation - model known behavioural patterns from the security awareness literature. Hadlington (2017) specifically documents the fast-click overconfident pattern I simulate in the critical-risk profile. The model generalises well on the held-out 20%, which suggests the patterns are coherent."

---

### Trap 3: "Why should I trust a model trained on fake data?"

**Don't say:** "Because it's 85% accurate."

**Do say:** "The model is trained to recognise behavioural patterns, not to memorise specific users. The patterns - response time, category accuracy variance, session consistency - are theoretically grounded. The held-out evaluation shows these patterns generalise. In a real deployment, the model would be retrained on real user data as it accumulates. The synthetic training is the bootstrapping phase."

---

### Trap 4: "What is the single biggest limitation of your project?"

**Don't say:** "Nothing, it's complete."

**Do say:** "The clearest limitation is that the ML model is trained entirely on synthetic data. This is a principled choice - real behavioural monitoring raises significant ethical concerns - but it means I cannot claim the model will achieve the same performance on genuinely novel real users without retraining. A second limitation is that awareness improvement is claimed theoretically via the adaptive engine design but not empirically measured in this version. Both are documented in the limitations chapter."

---

## PART 7 - 90-Second Project Summary (For When You're Nervous)

Read this once a day until you could say it in your sleep:

> "My project is called AHRID - Adaptive Human Risk Intelligence Dashboard. It's for non-technical SME employees in Kathmandu Valley who are the most common targets of phishing and social engineering attacks but have no dedicated security training.
>
> I built a full-stack platform - Flask backend, React frontend, deployed on Render and Vercel - that gives employees adaptive scenario-based security training. The system has three ML components: a Random Forest classifier that predicts each user's risk level from 14 behavioural features, K-Means clustering that groups users into 5 behavioural archetypes, and SHAP explainability that tells users why they've been rated high risk.
>
> The platform also ingests live threat data from four OSINT sources - AlienVault OTX, and Phishing Database - so training scenarios reflect current real-world threats.
>
> My evaluation shows the Random Forest achieves F1=0.89 and Cohen's Kappa=0.875 on a held-out test set, and beats a rule-based baseline by 52.2 F1 points - well above my hypothesis target of 15 points.
>
> The system addresses both a technical research question - can ML accurately classify user risk - and an ethical one - how do you do this without it becoming workplace surveillance. My answer to the second question is: SHAP transparency, individual score privacy, and human-in-the-loop governance."

---

## PART 8 - Quick Revision Cheatsheet

```
AHRID = Adaptive Human Risk Intelligence Dashboard
Target = Non-technical SME staff, Kathmandu Valley
Problem = 68% breaches = human error, SMEs have no security training

ML Stack:
  Random Forest  → predicts risk level (low/medium/high/critical)
  K-Means        → groups users into 5 behavioural archetypes
  SHAP           → explains WHY a user is high risk
  Rule-based     → baseline to compare RF against

Your Numbers:
  Scenarios = 450 hand-crafted, length-balanced
  Accuracy  = 91.4%
  F1        = 0.89
  PR-AUC    = 0.92
  Kappa     = 0.875  ("almost perfect agreement")
  Gap       = +0.52  (RF vs baseline, hypothesis needed 0.15)

Adaptive Engine:
  Mastery threshold = 80% to promote, 40% to demote
  Forgetting curve  = 21-day half-life, 30% floor
  Session split     = 50% weakest / 25% other / 25% challenge

OSINT Sources: OTX, Phishing.Database

Theories:
  PMT   = Protection Motivation Theory (threat + coping appraisal)
  TAM   = Technology Acceptance Model (ease of use → adoption)
  Prospect Theory = loss-framing increases compliance

Key Papers:
  Breiman (2001)         → Random Forests
  Lundberg & Lee (2017)  → SHAP
  Hadlington (2017)      → cognitive failures in cybersecurity
  Parsons et al. (2017)  → HAIS-Q instrument
  Buczak & Guven (2016)  → ML in cybersecurity

Ethics:
  Individual score privacy
  SHAP transparency
  Consent-based (not passive monitoring)
  Human-in-the-loop (scores are advisory only)
  Nepal Individual Privacy Act 2075
```

---

> Keep this file open during revision. For deeper understanding of any topic, go to the numbered chapter files (01-16). This file is for DEFENSE - what you say, not just what you know.
