# 🧠 AHRID in Plain English - Every Feature Explained Simply

> **Who is this for?** You - when you need to explain a concept in 60 seconds, or when you're reading a chapter and want the "so what?" answer without re-reading 10 pages.

---

## How to Use This

Each section follows the same pattern:
1. **What it is** - one sentence
2. **Relatable analogy** - a real-world situation most people recognise
3. **How it applies to AHRID** - the concrete connection

---

## 🌲 1. Random Forest (Risk Prediction)

**What:** A machine learning model that predicts each user's risk level (low/medium/high/critical) by looking at 14 behavioural features.

**Analogy - Job Interview Panel:**
> Imagine 200 interviewers each ask a slightly different set of questions. At the end, they vote on whether the candidate is a good fit. One interviewer might be wrong, but 200 voting together rarely are. That's exactly what a Random Forest does - 200 decision trees each vote on "what risk level is this user?", and the majority wins.

**In AHRID:** Every time a user has completed ≥10 quiz attempts, the 200-tree forest votes on whether they're Low / Medium / High / Critical risk. The result is shown on their profile and drives how SHAP explains the score.

---

## 🌳 1a. Decision Tree (Building Block of Random Forest)

**What:** A flowchart that makes a prediction by asking a series of yes/no questions.

**Analogy - Doctor's Diagnosis Checklist:**
> *"Is your accuracy below 50%?"* → Yes → *"Are you also answering in under 3 seconds?"* → Yes → **HIGH RISK**. A doctor uses exactly this kind of branching logic to narrow down a diagnosis. A decision tree is just that logic, learned automatically from data.

**In AHRID:** Each of the 200 trees in the forest is a different version of this checklist, trained on a slightly different slice of the data.

---

## 🌱 1b. Gini Impurity (How Trees Learn)

**What:** A measure of how "mixed up" a set of labels is. Lower is better.

**Analogy - Sorting a Fruit Bowl:**
> A bowl with 100 apples has Gini = 0 (perfectly pure - easy to label). A bowl with 25 apples, 25 oranges, 25 bananas, 25 grapes has Gini = 0.75 (maximally mixed). When the tree is learning, it tries every possible split and picks whichever one results in the least-mixed groups on each side.

**In AHRID:** The tree might ask "does the user's overall accuracy exceed 0.6?" - it picks that threshold because it splits users into mostly-low-risk and mostly-high-risk groups better than any other question it could ask.

---

## 🔄 2. K-Means Clustering (Behavioural Archetypes)

**What:** An unsupervised algorithm that groups users into 5 behavioural types without needing pre-set labels.

**Analogy - Grouping Students in a Library:**
> A librarian looks at 1,000 students studying in the library. Without reading their IDs, she notices some are always in a rush (slam books, leave quickly), some are deliberate (highlight everything, double check), some come once a year. She naturally groups them into "speedrunners", "careful scholars", "binge-studiers", etc. She didn't *know* these categories upfront - the patterns emerged from the data. That's K-Means.

**In AHRID:** After looking at each user's speed, accuracy, and consistency, the algorithm discovers 5 natural groups and we name them:
- 🔴 **Overconfident Clicker** - Fast and wrong
- 🟢 **Cautious Learner** - Slow and right, improving
- 🟡 **Inconsistent Performer** - Great at phishing, terrible at USB baiting
- 🔵 **Resilient Defender** - Fast, accurate, and consistent
- 🟣 **Disengaged Completer** - Just ticking the compliance box

---

## 📏 2a. StandardScaler (Feature Normalization)

**What:** Rescales all features to the same range so one feature doesn't dominate the others.

**Analogy - Comparing Exam Scores and Heights:**
> Imagine trying to cluster students using "exam score (0-100)" and "height in cm (150-190)". The height numbers are much larger, so the clustering algorithm would essentially ignore exam scores. You'd rescale both to the same range (like z-scores). That's StandardScaler.

**In AHRID:** `avg_response_time_ms` goes up to 20,000. `overall_accuracy` is 0-1. Without scaling, response time would completely swamp accuracy in the distance calculation. StandardScaler makes them equal partners.

---

## 🎯 2b. Silhouette Score (Clustering Quality)

**What:** A number from −1 to +1 measuring how well-separated the clusters are.

**Analogy - Sorting M&Ms by Color:**
> If you separate M&Ms perfectly (all reds together, all blues together), silhouette = +1. If a red one ends up deep in the blue pile, silhouette goes negative. If they're just touching the boundary - silhouette ≈ 0.

**In AHRID:** AHRID's silhouette score is **0.23** - moderate. This is expected for human behaviour (people don't fall neatly into boxes). The clusters are useful but overlapping, which is honest and realistic.

---

## ⚖️ 3. SMOTE (Handling Class Imbalance)

**What:** A technique that creates *new synthetic training examples* for underrepresented risk classes.

**Analogy - Practising for Rare Events in Medical Training:**
> Medical students train on thousands of common cases but might only see 5 examples of a rare disease. Instead of just repeating those 5 cases, a simulation creates realistic new scenarios *based* on those 5 cases, so students get adequate practice. SMOTE does exactly this for ML data.

**In AHRID:** You had 568 "low risk" users but only 136 "critical" users. Without fixing this, the model would learn to mostly predict "low risk" (and miss dangerous users). SMOTE created new synthetic "critical" users by interpolating between real critical users, until all 4 classes had equal training representation (454 each).

---

## 🔵 3a. Why Imbalance is Dangerous (Security Context)

**Analogy - Airport Security That Only Flags Tourists:**
> If 90% of travellers are tourists and 10% are businesspeople, an airport security system that always says "tourist" would be 90% accurate but would never catch a suspicious businessperson. In security, missing the rare dangerous case is a catastrophic failure - not a rounding error.

**In AHRID:** Missing a "critical risk" user (who would click a real phishing link) is far worse than incorrectly flagging a "low risk" user. SMOTE + `class_weight="balanced"` ensures the model pays special attention to dangerous but rare cases.

---

## 🔍 4. SHAP (Explainability)

**What:** A mathematical technique (from game theory) that tells you *exactly how much* each feature contributed to a specific prediction.

**Analogy - Splitting a Restaurant Bill Fairly:**
> Four friends share a dinner. Alice had wine (expensive), Bob had water, Claire had dessert, Dave had both. The final bill is £120. How much did each person contribute? SHAP solves this exact "fair credit attribution" problem - for ML predictions instead of restaurant bills. It guarantees the individual contributions sum to the total difference from the average.

**In AHRID:** If a user is predicted "high risk", SHAP breaks it down:
- *"Your low SMS phishing accuracy is pushing your risk up (+0.18)"*
- *"Your fast answering habit adds risk (+0.09)"*
- *"But your strong phishing email detection protects you (−0.16)"*

This makes the AI transparent and actionable - not just a black-box verdict.

---

## 🚀 4a. TreeExplainer (Fast SHAP for Random Forests)

**What:** A specialised SHAP algorithm that computes exact explanations for tree-based models in polynomial time (not exponentially slow).

**Analogy - Express Checkout vs. Regular Queue:**
> Computing all possible combinations of features to find fair attribution would take an exponentially long time (like waiting in every possible queue). TreeExplainer knows the structure of the decision tree and skips directly to the relevant paths - the express checkout.

**In AHRID:** Instead of testing all 2^14 subsets of 14 features (16,384 combinations) per user, TreeExplainer traces each tree's decision path in milliseconds.

---

## 🧮 5. Risk Scoring - The Rule-Based Baseline

**What:** A simple formula (`risk = (1 - accuracy) × 100`) that always gives a score, even before any ML is trained.

**Analogy - A Simple Driving Test Score:**
> Before self-driving cars existed, driving ability was just "how many errors did you make?" (100 − errors = score). It's blunt but reliable. The ML is the upgrade that additionally considers *how you made errors* (e.g., were you overconfident?) - but the simple score always works.

**In AHRID:** The rule-based score is Layer 1. It's always available. The Random Forest (Layer 2) improves on it once enough data is collected (≥10 attempts). If the RF isn't trained yet, users still get a score.

---

## 📚 6. Feature Engineering

**What:** The process of transforming raw data (individual quiz answers) into a compact set of meaningful numbers that ML can work with.

**Analogy - Making a Student Report Card:**
> A school doesn't feed 1,000 raw homework assignments to a university. It computes a GPA (overall accuracy), a subject breakdown (category accuracies), and attendance record (engagement) - a compact summary that carries the important signals. Feature engineering is building that report card for the ML model.

**In AHRID:**
- **Raw data**: 20,000+ individual attempt rows
- **RF features (14)**: avg response time, per-category accuracy (×5), fast attempt rate, overconfident rate, session consistency, job role, session count, days since last session, total attempts
- **KMeans features (6)**: response time, overall accuracy, accuracy variance, fast attempt rate, session count, consistency

---

## 📊 6a. Fast Attempt Rate

**What:** The fraction of attempts answered in under 4,000ms (4 seconds).

**Analogy - Multiple Choice Exam Guessing:**
> There's always that student who circles answers without reading the question - finishing a 60-minute exam in 15 minutes. A high "fast attempt rate" is the digital equivalent: answering security questions before reading them. Speed + accuracy = competence. Speed + errors = dangerous recklessness.

**In AHRID:** `fast_attempt_rate > 0.30` is a flag. The model learned that rushing through security training strongly predicts real-world vulnerability.

---

## 📊 6b. Overconfident Rate

**What:** The fraction of fast *wrong* answers - answering quickly but incorrectly.

**Analogy - That Friend Who Answers Every Pub Quiz Question Confidently Wrong:**
> They shout "NAPOLEON!" before you've finished asking. 100% wrong, 0% self-doubt. An "overconfident clicker" is the security-training equivalent - they think they know what a phishing email looks like, so they don't bother reading carefully, and they miss the red flags.

**In AHRID:** `overconfident_rate = fast_wrong / total_attempts`. It's one of the 14 RF features because it's a powerful predictor of real-world phishing susceptibility.

---

## 🎓 7. The Adaptive Engine (Intelligent Tutoring)

**What:** A rule-based system that personalises which quiz questions each user sees, based on their weaknesses, role, and time since last practice.

**Analogy - A Personal Gym Trainer:**
> A good trainer doesn't give the same workout to everyone. They target your weak spots (if your legs are weak, more squats), they progress difficulty as you improve (add weight when 80% reps are perfect), and they remind you to train if you've been away too long. AHRID's adaptive engine is the digital gym trainer for security awareness.

**In AHRID:**
- 50% of each session targets your **weakest category**
- 25% maintains **breadth** (categories you haven't seen recently)
- 25% is a **stretch** (higher difficulty to push you)

---

## 📉 7a. Recency-Weighted Mastery

**What:** An accuracy calculation where recent quiz answers count more than old ones.

**Analogy - Netflix Recommendations vs. Your 2007 Watch History:**
> Netflix cares far more about what you watched last week than what you watched 10 years ago. If you used to love action films but now prefer documentaries, your recommendations should reflect the current you. Same principle here - a user who got 8/10 wrong last month but 9/10 right this week is genuinely improving, and their current mastery should reflect that.

**In AHRID:** Mastery is computed with exponential decay (factor 0.85). The most recent answer counts as `1.0`, the answer before it counts as `0.85`, the one before as `0.72`, and so on. Old errors fade; recent wins matter most.

---

## 📉 7b. Forgetting Curve (Ebbinghaus)

**What:** A mathematical model of how human memory decays exponentially without practice, then stabilises at a minimum floor.

**Analogy - Learning a Foreign Language on Duolingo:**
> After 3 months of daily Spanish, you're fluent. Then life gets busy and you stop for 6 months. You haven't forgotten *everything*, but you've definitely regressed. The more time passes, the faster the initial drop - but then it plateaus. Duolingo knows this, which is why it reminds you every day.

**In AHRID:** Half-life = 21 days. Mastery floor = 30%. A user with phishing mastery of 0.90 who doesn't train for 42 days (2 half-lives) drops to 0.45. The system will resurface phishing scenarios before they forget completely. `decayed = 0.30 + (0.90 − 0.30) × 0.5^(42/21)` = **0.45**

---

## 🎯 7c. Difficulty Progression (Promote/Demote)

**What:** Automatically increasing or decreasing question difficulty based on recent mastery.

**Analogy - Video Game Difficulty Scaling:**
> In Dark Souls, if you keep dying to a boss, the game doesn't make it harder. In rhythm games, once you 5-star a song on Hard, you unlock Expert. AHRID works like a well-designed game - pass 80% on Level 2 questions? You're on Level 3. Drop below 40%? Back to Level 2 to rebuild confidence.

**In AHRID:**
- Mastery ≥ 0.80 → Promote to next difficulty (max 3)
- Mastery ≤ 0.40 → Demote to easier difficulty (min 1)
- Between → Stay at current difficulty

---

## 🕵️ 8. Scenario Classification (URL Intelligence)

**What:** A heuristic (rule-based) system that automatically classifies an incoming phishing URL into a threat type, training category, and difficulty level.

**Analogy - Spam Filter Rules:**
> Before AI spam filters, email clients used rules: "If subject contains 'FREE MONEY' → spam." These rules are simple but effective for obvious cases. The scenario classifier is the same - it scores a URL against keyword patterns and structural features to decide what kind of threat it is.

**In AHRID:**
- URL `http://paypa1.com/login` → Difficulty 1 (obvious: typosquat + HTTP), lure type: `credential_harvest`
- URL `https://paypal.login.evil.com` → Difficulty 3 (brand in subdomain, legit-looking), lure type: `credential_harvest`
- Lure type then maps deterministically to a training category (e.g., `smishing`, `social_engineering`) using a URL hash to ensure variety

---

## 📡 9. OSINT Threat Feed Pipeline

**What:** An automated pipeline that fetches real-world phishing URLs from public threat databases every 6 hours and converts them into training scenarios.

**Analogy - A Breaking News Feed for Security Training:**
> Imagine a cybersecurity textbook that automatically updates overnight with last week's actual phishing campaigns. Your trainees face scenarios based on real threats, not hypothetical 5-year-old examples. That's what the OSINT pipeline does.

**In AHRID:** Sources: PhishTank, URLhaus → deduplicate → classify → sanitise (`https://evil.com` → `hxxps://evil[.]com`) → generate scenario → inject into training. One question per session can be a real threat from the last 48 hours.

---

## 📈 10. Evaluation Metrics

### F1 Score

**What:** A single number balancing both "of predicted highs, how many were right" (precision) and "of all real highs, how many did we catch" (recall).

**Analogy - Security Guard Performance:**
> A guard who stops every single person (never misses a threat) has perfect Recall but terrible Precision - they're also stopping legitimate employees all day. A guard who only stops someone when 100% certain has perfect Precision but may miss real threats (low Recall). F1 score is the one number that penalises both extremes. **AHRID's RF: F1-macro = 0.85**

---

### Cohen's Kappa (κ)

**What:** How much better is the model than random chance, adjusted for class distribution?

**Analogy - Coin Flip vs. Expert Diagnosis:**
> If a doctor correctly identifies a disease 70% of the time, but the disease affects 70% of the population - the doctor is no better than flipping a coin! Cohen's Kappa measures the *extra* skill beyond chance. κ > 0.6 is considered substantial agreement.

**In AHRID:** Used in the evaluation endpoint to prove the RF isn't just predicting the majority class (low risk) by default.

---

### Cohen's d (Awareness Uplift Effect Size)

**What:** How large is the improvement from pre-training to post-training, measured in standard deviations?

**Analogy - Blood Pressure Drug Study:**
> In a clinical trial, you don't just ask "did blood pressure drop?" - you ask "how much?" Cohen's d tells you whether the change is meaningful in practical terms: 0.2 = small, 0.5 = medium, 0.8 = large. Same idea for AHRID - did security awareness *actually* improve, and by how much?

**In AHRID:** The eval endpoint computes Cohen's d between pre-assessment and post-assessment scores per category.

---

### SUS Score (Usability)

**What:** A standardised 10-question survey scoring usability from 0 to 100.

**Analogy - Product Reviews, Standardised:**
> Instead of "was it good?", ask 10 specific questions about ease, complexity, confidence, and consistency - then convert to a 0-100 scale that every researcher understands. Industry average = 68. Above 73 = "Excellent".

**In AHRID:** Administered to real users (SME staff) to answer RQ3: "Is AHRID usable for non-technical users?"

---

## 🔄 11. Cross-Validation

**What:** Training and testing the model on multiple different data splits to get a stable, unbiased estimate of performance.

**Analogy - Taking an Exam Multiple Times:**
> If you only take one version of a standardised test, you might get lucky (easy questions) or unlucky (hard day). If you take it 3 different times and average the results, you get a fairer measure of your actual ability. 3-fold cross-validation does this for your ML model - it trains/tests 3 different ways and reports the average.

**In AHRID:** `cv=3`, `scoring="f1_macro"` → Result: **F1 = 0.815 ± 0.034**. The small ±0.034 means the model performs *consistently* across different data splits - not just getting lucky on one particular test set.

---

## 🧩 12. Stratified Train-Test Split

**What:** When dividing data into train (80%) and test (20%), ensure each risk class is proportionally represented in both sets.

**Analogy - Demographic Sampling in a Survey:**
> A fair opinion poll doesn't only call people in one city. It ensures each region is proportionally represented. Similarly, if 13% of users are "critical risk", then 13% of the training *and* test set should be critical risk - not 0% in test by accident.

**In AHRID:** Without stratification, you might end up with zero "critical" users in the test set, making evaluation of that class meaningless. `stratify=y` in `train_test_split()` prevents this.

---

## 💾 13. joblib (Model Serialisation)

**What:** A library for saving trained ML models to disk so they don't need to be retrained every time.

**Analogy - Saving a Video Game:**
> You don't replay the entire game every time you open it. You save at a checkpoint and pick up where you left off. `joblib.dump(model, "model.pkl")` is the save button for a trained Random Forest. `joblib.load()` is loading that save.

**In AHRID:** `risk_rf_model.pkl` (~6MB) is the saved Random Forest. The Flask API loads it once at startup and uses it for every prediction without retraining.

---

## 📊 14. Behavioural Telemetry

**What:** Tracking how users interact with training - not just right/wrong, but timing, session length, answer changes, and dwell time.

**Analogy - Eye-Tracking in UX Research:**
> Product designers don't just ask "did you find the button?" - they track where your eyes went, how long you hesitated, and whether you changed your mind. Telemetry is the same idea applied to quiz-taking behaviour.

**In AHRID:** `telemetry_service.py` captures dwell time (time spent reading before answering), answer changes (changing A→B), and session engagement scores. These feed into the "overconfident rate" and "response time" features.

---

## 🏷️ 15. Label Encoding (Job Roles)

**What:** Converting categorical text values (like job titles) into numbers so ML can process them.

**Analogy - Airline Seat Class Numbers:**
> An airline's booking system might store seat class as "Economy"/"Business"/"First" internally, but the pricing algorithm needs numbers (1/2/3). Label encoding does this conversion.

**In AHRID:** `{"receptionist": 0, "accountant": 1, "hr": 2, "it": 3, "finance": 4, "sales": 5, "management": 6, "other": 7}`. The Random Forest can then learn: "IT staff (3) tend to score higher on phishing detection than receptionists (0)" without needing separate columns for each role.

---

## 🔒 16. Synthetic Data (`is_synthetic` Flag)

**What:** Artificially generated user data used to train ML models when real user data is scarce.

**Analogy - Flight Simulator for Pilot Training:**
> Before a pilot flies a real plane with passengers, they train on a simulator. The simulated scenarios are artificial, but they teach real skills. Synthetic data is the simulator - the model trains on realistic fake users, then applies what it learned to real ones.

**In AHRID:** 1,050 synthetic users across 5 risk profiles were generated. Crucially, `is_synthetic=True` is flagged on these records so they're *included* in ML training but *excluded* from real user risk scoring. A real user's score is never contaminated by synthetic patterns.

---

## 📋 Quick Reference: Decision Flowchart

```
User completes an attempt
         │
         ▼
   ≥10 real attempts?
    /            \
  YES             NO
   │               │
   ▼               ▼
Build 14      Rule-based
features      score only
   │         (simple accuracy)
   ▼
Random Forest predicts risk level
   │
   ▼
SHAP explains why
   │
   ▼
Adaptive Engine picks next session
   │
   ├── Weakest category (50%)
   ├── Breadth (25%)
   └── Challenge/stretch (25%)
         │
         ▼
   Forgetting curve applied
   (decay mastery if inactive)
         │
         ▼
   K-Means assigns archetype
   (runs on retrain trigger)
```

---

## 🗣️ One-Line Viva Answers

| Concept | Say This Out Loud |
|---------|-------------------|
| **Random Forest** | "200 decision trees each vote on a user's risk; the majority wins - averaging out individual tree errors." |
| **K-Means** | "Groups users into 5 natural behavioural archetypes without needing pre-set labels - the patterns emerge from the data." |
| **SMOTE** | "Creates new realistic minority-class training samples by interpolating between existing ones - so critical-risk users aren't ignored." |
| **SHAP** | "Mathematically attributes each prediction to its contributing features, so users know *why* they're rated risky, not just *that* they are." |
| **Adaptive Engine** | "A cognitive-science-inspired tutoring system that targets your weakest areas, promotes difficulty when you succeed, and models memory decay." |
| **Forgetting Curve** | "Based on Ebbinghaus (1885): memory decays exponentially without practice, with a half-life of 21 days and a retention floor of 30%." |
| **Silhouette 0.23** | "Moderate but meaningful clustering - human behaviour naturally overlaps between categories, so perfect separation would actually be suspicious." |
| **Cohen's d** | "Measures the practical size of awareness improvement, not just statistical significance - small (0.2), medium (0.5), large (0.8)." |

---

> **Next:** Return to the chapter for the technical details, or see [00_DEFENSE_PREP.md](./00_DEFENSE_PREP.md) for full viva Q&A.
