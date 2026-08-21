# 🎓 AHRID Viva Q&A - Complete Defense Guide

> **How to use this:** Every question here has been asked in real ML thesis vivas. Read the answer out loud - not in your head. The goal is to be able to say it naturally, not recite it. Questions are grouped by topic. The 🔴 ones are the hardest.

---

## HOW EXAMINERS THINK

Before reading the questions, understand what examiners are testing:

| What they ask | What they're really checking |
|---|---|
| "Explain Random Forest" | Do you understand it, or did you just run sklearn? |
| "Why did you choose this?" | Did you make informed decisions or just copy code? |
| "What are the limitations?" | Are you honest and academically mature? |
| "What would you do differently?" | Can you critically reflect on your own work? |
| "Why not use X instead?" | Do you know the alternatives? |

**Golden rule:** Never say "I don't know" and stop. Say "That's an interesting point - my understanding is..." and give your best answer. Examiners reward intellectual honesty + reasoning far more than perfect recall.

---

## PART 1 - RANDOM FOREST

---

### Q1: What is a Random Forest? Explain it simply.

**The answer:**
> "A Random Forest is an ensemble model - it builds many decision trees and lets them vote. Each tree is trained on a slightly different random sample of the data and uses a random subset of features at each split. The majority vote across all trees gives the final prediction.
>
> Think of it like asking 200 people to look at a suspicious email and vote on whether it's phishing. Each person focuses on different clues - some look at the sender, some at the link, some at the urgency. No single person is always right, but 200 votes together are far more reliable. That's the ensemble principle."

---

### Q2: Why did you choose Random Forest over other models?

**The answer:**
> "Three specific reasons for my project:
>
> First, **interpretability** - Random Forest integrates cleanly with SHAP, which was a requirement for my ethical transparency goal. A neural network is a black box; RF gives me native feature importances that feed directly into SHAP explanations.
>
> Second, **data scale** - I have 1,050 training samples with 14 features. Random Forest is designed for this range. A neural network with this little data would overfit badly.
>
> Third, **robustness to imbalance** - with `class_weight='balanced'`, RF handles skewed class distributions without needing architectural changes. My data has 4× more low-risk users than critical-risk users.
>
> The literature supports this too - Buczak & Guven (2016) document RF as a strong baseline for behavioural classification in cybersecurity contexts."

---

### Q3: What is a Decision Tree and how does it learn?

**The answer:**
> "A decision tree is a flowchart. At each internal node, it asks a yes/no question about a feature - like 'is overall accuracy below 0.5?' It splits the data based on the answer, going left or right, until it reaches a leaf node which gives the prediction.
>
> The tree learns by finding the *best* split at each node - the one that reduces impurity the most. It tries every possible threshold for every feature and picks whichever creates the most homogeneous groups on each side.
>
> The measure of homogeneity is called Gini Impurity. A pure group - say, all high-risk users - has Gini = 0. A perfectly mixed group has Gini = 0.75 for four classes. The algorithm greedily minimises Gini at each split."

---

### Q4: What is Gini Impurity? Why not use Entropy?

**The answer:**
> "Gini Impurity measures how likely a randomly chosen element from a set would be incorrectly labelled if labelled randomly according to the class distribution. Mathematically: `Gini = 1 - Σ(pᵢ²)` where pᵢ is the proportion of class i.
>
> Entropy is an alternative - it measures information content using logarithms: `Entropy = -Σ(pᵢ × log₂(pᵢ))`.
>
> In practice, both produce very similar trees. scikit-learn defaults to Gini because it's computationally cheaper - no logarithm calculation needed. For my dataset size, this is a minor concern, but I used the default since there was no specific reason to switch."

---

### Q5: Why do you use 200 trees? Why not 50 or 500?

**The answer:**
> "200 is a balance between performance and compute. The general rule of thumb is that accuracy improves rapidly up to around 50-100 trees, then flattens. Beyond 300-400, you're spending training time for marginal gains.
>
> With my dataset of about 1,050 samples and 14 features, 200 trees gives stable predictions - individual tree variance cancels out, and I get consistent probability estimates from `predict_proba`. I could have used 100 and likely seen similar results. 500 would have been wasteful with no accuracy benefit.
>
> The key insight is that more trees never *hurts* accuracy - it just reaches diminishing returns on compute."

---

### Q6: 🔴 Can a single decision tree in your forest overfit? If yes, doesn't that undermine the whole model?

**The answer:**
> "Yes, individual trees in a Random Forest are intentionally allowed to overfit - they grow until leaves are pure, with `max_depth=None`. This seems counterintuitive.
>
> But the ensemble corrects for it through two mechanisms. First, **bootstrap sampling** - each tree trains on a different random 63% subset of the data (sampling with replacement), so they overfit to *different* noise. Second, **feature randomness** - each split only considers √14 ≈ 4 random features, which de-correlates the trees further.
>
> When 200 such trees vote, their individual overfitting errors cancel out because they're not correlated. This is the mathematical basis of bagging - variance reduction without bias increase. It's why Random Forests consistently outperform single deep trees."

---

### Q7: What is Bootstrap Sampling (Bagging)?

**The answer:**
> "Bagging stands for Bootstrap AGGregating. For each of the 200 trees, instead of training on all 1,050 samples, the algorithm randomly samples 1,050 rows *with replacement* - meaning some rows appear multiple times, others not at all.
>
> On average, each tree sees about 63% of the unique training data. The remaining ~37% - called the Out-of-Bag (OOB) samples - can be used to estimate the model's error without needing a separate validation set.
>
> The key effect: every tree is trained on a slightly different dataset, making them diverse. Diverse errors cancel when you average the votes."

---

### Q8: What are Feature Importances and how does RF compute them?

**The answer:**
> "Feature importances measure how much each feature contributes to reducing impurity across all trees. Specifically, at every split that uses a feature, you measure the weighted reduction in Gini impurity. These reductions are averaged across all trees and all nodes that use that feature.
>
> A feature used frequently and at high-level nodes (close to the root) will have high importance because it affects many predictions.
>
> In AHRID, `overall_accuracy` and `avg_response_time_ms` tend to rank highest - they're the strongest predictors of risk level. I use this both as a sanity check (if `job_role` were the top feature, something would be wrong) and as input to SHAP for per-user explanations."

---

### Q9: 🔴 Why not use Gradient Boosting (XGBoost) instead? It's usually more accurate.

**The answer:**
> "Gradient Boosting is often more accurate on structured tabular data - that's true. But it introduces two trade-offs that matter for my project.
>
> First, **explainability** - while SHAP does support XGBoost, the sequential boosting process makes the SHAP values harder to interpret intuitively. With Random Forest, each tree's independent vote maps cleanly to the ensemble probability. My thesis has a specific ethical requirement for transparent explanations, and I prioritised that.
>
> Second, **overfitting risk** - Gradient Boosting is more prone to overfitting on small datasets if not carefully tuned. With 1,050 samples, Random Forest's bagging approach gives me built-in regularisation without needing hyperparameter tuning.
>
> That said, XGBoost is a valid direction for future work - I'd compare them properly with cross-validated performance before switching."

---

### Q10: What does `predict_proba` return and what does it mean?

**The answer:**
> "Instead of just predicting a class label, `predict_proba` returns a probability array - one value per class, all summing to 1.0. For my four classes (low, medium, high, critical), it returns something like `[0.06, 0.14, 0.725, 0.075]`.
>
> These probabilities literally represent the fraction of the 200 trees that voted for each class. In this example, 145 out of 200 trees voted 'high risk' - so the confidence is 72.5%.
>
> This is valuable for two reasons. First, it gives a confidence score - a prediction with 99% confidence is more actionable than one with 51%. Second, it enables SHAP to compute per-class explanations, not just for the winning class."

---

---

## PART 2 - SMOTE (CLASS IMBALANCE)

---

### Q11: What is SMOTE and why did you need it?

**The answer:**
> "My training data had a class imbalance problem - roughly 54% of users were 'low risk' and only 13% were 'critical risk'. If I trained on that directly, the model would find it easy to just predict 'low risk' for everyone and still get 54% accuracy. But it would miss every high-risk and critical user, which is the worst possible outcome for a security system.
>
> SMOTE - Synthetic Minority Over-sampling Technique - fixes this by creating *new, realistic* training examples for the minority classes. It doesn't just duplicate existing samples, which would cause overfitting. Instead it interpolates between two existing minority-class users to create a plausible new one.
>
> After SMOTE, all four classes had equal representation - 454 samples each - and the model could learn all risk tiers equally well."

---

### Q12: How exactly does SMOTE create new samples?

**The answer:**
> "For each minority-class sample - say a 'critical risk' user - SMOTE finds its k nearest neighbours within the same class (I used k=5). It randomly picks one of those neighbours, then creates a new point by interpolating between the original and the neighbour:
>
> `x_new = x_original + λ × (x_neighbour - x_original)`
>
> where λ is a random number between 0 and 1. So the new sample sits somewhere on the line segment between two real critical-risk users. It's realistic because it's between real examples, but it's not a copy of either.
>
> This is fundamentally different from just duplicating minority samples - duplication would cause the model to memorise those specific examples. SMOTE adds diversity."

---

### Q13: 🔴 Does SMOTE introduce data leakage? How did you prevent it?

**The answer:**
> "This is a really important question - yes, SMOTE can introduce data leakage if applied incorrectly, and I was careful to avoid that.
>
> The problem: if you apply SMOTE before splitting into train/test sets, some synthetic samples are created from data that will end up in the test set. The test set has effectively 'leaked' into training, which artificially inflates your metrics.
>
> My code applies SMOTE *after* the 80/20 train-test split - only to the training portion. The test set contains only real, original samples the model has never seen. This is the correct order:
> 1. Split data into train/test
> 2. Apply SMOTE to train only
> 3. Train model on SMOTE-augmented train set
> 4. Evaluate on untouched test set"

---

### Q14: You also used `class_weight='balanced'` - isn't SMOTE enough on its own?

**The answer:**
> "Good catch. I use both, and they work at different levels.
>
> SMOTE operates at the *data* level - it physically adds new samples before training begins, balancing the class counts.
>
> `class_weight='balanced'` operates at the *algorithm* level - during tree construction, it tells the RF to weight each sample by the inverse of its class frequency. Rare classes (critical risk) get higher weight, so mistakes on them cost more during the split quality calculation.
>
> Using both is called 'belt and suspenders' - two independent mechanisms protecting against the same problem. SMOTE gives the model more examples to learn from; `class_weight` ensures it pays extra attention to the important minority classes even with the original imbalance. Together they're more robust than either alone."

---

### Q15: 🔴 Isn't SMOTE creating fake data? How can you trust a model trained on fake data?

**The answer:**
> "SMOTE creates synthetic *training* samples, not synthetic *users*. The distinction matters.
>
> The synthetic points are interpolations between real data points - they represent plausible regions of the feature space that the model should know about. Think of it like this: if you have only 5 examples of a rare disease, a medical simulator creates more practice scenarios *based on* those 5 cases to give students more practice. The scenarios aren't real patients, but they teach real patterns.
>
> Crucially, my test set contains *zero* SMOTE samples. Every evaluation metric - 91.4% accuracy, F1=0.89, Kappa=0.875 - is measured only on real, original data the model has never seen. If the model were overfitting to SMOTE artefacts, performance on that real test set would be poor. It wasn't."

---

## PART 3 - K-MEANS CLUSTERING

---

### Q16: What is K-Means and why did you use it alongside Random Forest?

**The answer:**
> "Random Forest answers 'how risky is this user?' - a classification problem with labels. K-Means answers a different question: 'what *type* of user is this?' - without any predefined labels.
>
> K-Means is unsupervised clustering. It groups users into k clusters based on similarity in feature space. I chose k=5, and the algorithm discovered 5 natural behavioural groupings. I then interpreted and named these clusters based on their feature patterns - 'Overconfident Clicker', 'Cautious Learner', etc.
>
> The two work together: RF tells the manager a user is 'high risk'; K-Means tells them the user is an 'Overconfident Clicker' who needs slowed-down training. That combination is far more actionable than a number alone."

---

### Q17: Walk me through the K-Means algorithm step by step.

**The answer:**
> "K-Means follows four steps, repeated until convergence:
>
> 1. **Initialise** - Place k=5 random centroid points in the 6-dimensional feature space.
> 2. **Assign** - Assign each user to their nearest centroid, measured by Euclidean distance.
> 3. **Update** - Move each centroid to the mathematical mean of all points assigned to it.
> 4. **Repeat** - Go back to step 2 and re-assign. Keep repeating until no user changes cluster (convergence).
>
> I used `n_init=10` - the algorithm runs this full process 10 times with different random starting centroids and keeps the result with the lowest total inertia (sum of squared distances from each point to its centroid). This protects against bad random initialisations."

---

### Q18: Why exactly k=5? Why not k=3 or k=7?

**The answer:**
> "I used two methods to validate k=5: the elbow method and the silhouette score.
>
> The elbow method plots inertia (total within-cluster variance) against k. Inertia always decreases as k grows - at k=n, every user is their own cluster. The 'elbow' is where the rate of decrease sharply slows. For my data, the elbow appeared around k=4 to k=5.
>
> For k=5, the silhouette score was 0.268 - meaningful cluster separation. k=4 showed slightly lower separation; k=6 started fragmenting the 'Cautious Learner' cluster without adding insight.
>
> Beyond the maths - I chose 5 because it maps to 5 *psychologically meaningful* archetypes from the security awareness literature. K-Means gave me the mathematical groupings; my domain knowledge gave them names."

---

### Q19: Your silhouette score is 0.268. Isn't that low?

**The answer:**
> "It's moderate, and it's appropriate for this type of data. Let me put it in context.
>
> The silhouette score measures how well-separated clusters are: +1 means perfect separation, 0 means points are on cluster boundaries, -1 means misclassified. For *behavioural* data - where humans exist on a spectrum rather than in discrete groups - typical silhouette scores in the literature range from 0.15 to 0.40.
>
> A score of 0.9 would actually concern me - it would suggest the features are too similar to each other or the data is artificially generated without natural overlap. Human behaviour is messy. People don't fall cleanly into boxes.
>
> 0.268 tells me: the clusters are real and meaningful, but users exist on a continuum between archetypes. That's honest and expected."

---

### Q20: 🔴 Why K-Means instead of DBSCAN or hierarchical clustering?

**The answer:**
> "Three reasons specific to my use case:
>
> First, **fixed number of clusters** - my system needs exactly 5 named archetypes to display on the manager dashboard. DBSCAN produces a variable number of clusters and can label some points as noise (no cluster). Hierarchical clustering requires cutting a dendrogram at a chosen level. K-Means directly gives me the 5 I need.
>
> Second, **interpretable centroids** - K-Means produces a centroid for each cluster - a point representing the 'average' user in that cluster. I can describe that centroid in plain English: 'fast responder, low accuracy, high session consistency.' DBSCAN has no meaningful centroid concept.
>
> Third, **scalability** - K-Means runs in O(nkt) time where n=users, k=clusters, t=iterations. For my dataset size, it's near-instant. Hierarchical clustering is O(n² log n) - problematic if the system grows.
>
> DBSCAN would be a valid alternative if I needed to detect outlier users who don't fit any archetype. That's documented as future work."

---

### Q21: Why do you use StandardScaler before K-Means?

**The answer:**
> "K-Means computes distances between points using Euclidean distance. The problem: my features live on wildly different scales.
>
> `avg_response_time_ms` ranges from 0 to 20,000. `overall_accuracy` ranges from 0 to 1. Without scaling, a tiny change in response time (say, 500ms) would look enormous compared to a massive change in accuracy (say, 0.5 points). The clustering would essentially ignore accuracy and cluster only on response time.
>
> StandardScaler rescales every feature to have mean=0 and standard deviation=1. After scaling, all features contribute equally to distance calculations. Critically, I save the fitted scaler in the model bundle - so during prediction, I apply the *same* transformation with the *same* scaling parameters as training. Using a fresh scaler on test data would be data leakage."

---

### Q22: 🔴 K-Means assumes spherical clusters. Is that valid for human behaviour?

**The answer:**
> "That's a genuine limitation of K-Means, and I document it as such. K-Means partitions space using Voronoi regions - it draws linear boundaries equidistant between centroids. This implicitly assumes clusters are roughly spherical and similar in size.
>
> Human behavioural data doesn't always satisfy this. The 'Inconsistent Performer' cluster, for example, is defined partly by high accuracy variance - which creates an elongated distribution in feature space, not a sphere.
>
> The silhouette score of 0.268 reflects this - moderate separation, not perfect. For my purpose - generating actionable management-level archetypes - this level of separation is sufficient. If I needed precise cluster boundaries (e.g., for automated interventions without human review), I'd consider Gaussian Mixture Models, which model ellipsoidal clusters, or HDBSCAN for arbitrary shapes. Both are documented as future improvements."

---

*[Continues in Part 3 - SHAP & Feature Engineering]*

---

## PART 4 - SHAP EXPLAINABILITY

---

### Q23: What is SHAP and how does it work?

**The answer:**
> "SHAP stands for SHapley Additive exPlanations. It's a method from cooperative game theory - specifically Shapley values - that fairly distributes the 'credit' for a prediction among all features.
>
> The question SHAP answers is: for this specific user's prediction, how much did each feature push the score up or down from the average?
>
> The game theory analogy: imagine 14 players (features) cooperating to win a prize (the prediction). Shapley values calculate each player's fair share of the prize by averaging their marginal contribution across all possible orderings. A feature that consistently adds value in all team combinations gets a high Shapley value.
>
> Concretely: if removing `overconfident_rate` from the calculation would drop a user's risk score from 0.85 to 0.55, SHAP assigns a large positive value to `overconfident_rate` for that user."

---

### Q24: Why SHAP instead of just looking at feature importances?

**The answer:**
> "Feature importances from Random Forest are *global* - they tell you which features matter most across the entire dataset. `overall_accuracy` is always the top feature, for every user.
>
> SHAP is *local* - it explains individual predictions. For User A, the top driver might be `overconfident_rate`. For User B, it might be `days_since_last_session`. The same model, different explanations, because different behaviours drove different predictions.
>
> This local explanability directly addresses my Research Question 2 - ethical transparency. A user asking 'why am I rated high risk?' deserves an answer about *their* behaviour, not a generic statement about what the model learned globally."

---

### Q25: 🔴 Why TreeSHAP specifically? What makes it different from KernelSHAP?

**The answer:**
> "Both compute Shapley values but with different approaches.
>
> KernelSHAP is model-agnostic - it treats the model as a black box and estimates Shapley values by sampling random feature subsets and measuring how the output changes. It's flexible but computationally expensive - O(2^n) in the worst case for n features.
>
> TreeSHAP - used by `shap.TreeExplainer` - exploits the structure of tree-based models. Because each decision tree is a deterministic sequence of splits, TreeSHAP can compute exact Shapley values in polynomial time O(TLD²) where T=trees, L=leaves, D=max depth. It's orders of magnitude faster.
>
> Since I'm using a Random Forest, TreeSHAP is the natural and efficient choice. It gives exact values rather than approximate ones, which matters for a system where users will read their explanation and potentially challenge it."

---

### Q26: 🔴 What are the limitations of SHAP?

**The answer:**
> "SHAP has three limitations I'm aware of and should acknowledge:
>
> First, **feature correlation** - SHAP assumes features can be independently toggled on/off. When features are correlated - say `overall_accuracy` and `phishing_accuracy` are both high together - SHAP can distribute the credit unintuitively between them.
>
> Second, **explanation doesn't equal causation** - SHAP tells you what features *statistically contributed* to the prediction. It doesn't tell you that changing `overconfident_rate` would *cause* the risk score to drop. I'm careful in the UI text to frame explanations as 'contributed to' rather than 'caused'.
>
> Third, **human comprehension** - even a perfect SHAP value means nothing if the user doesn't understand what `overconfident_rate` is. My system translates SHAP values into plain English template sentences to address this: 'You tend to answer questions very quickly when you get them wrong, which is a strong indicator of risky behaviour.'"

---

### Q27: Where does SHAP appear in the AHRID system?

**The answer:**
> "In `shap_explainer.py`. After every risk score recalculation, I run `shap.TreeExplainer(model).shap_values(user_features_array)`. This returns a matrix of SHAP values - one per feature, per class.
>
> I extract the values for the predicted risk class, sort them by absolute magnitude, and format the top 3 into a JSON summary that's stored in the `RiskScore.shap_summary` column.
>
> On the frontend, the `ShapExplanationPanel` component reads this JSON and renders it as a card showing: 'Your score is primarily influenced by: 1) Fast wrong answers (overconfident_rate), 2) Infrequent training (days_since_last_session), 3) Low phishing accuracy.' No jargon, no numbers - just actionable English."

---

## PART 5 - ADAPTIVE ENGINE & EVALUATION

---

### Q28: What is the Adaptive Engine? Is it ML?

**The answer:**
> "The Adaptive Engine is *not* ML - it's a deterministic rule-based system, and I'm transparent about that distinction.
>
> It uses recency-weighted mastery scores to decide what content to show next. For each security category per user, it maintains a mastery score between 0 and 1, calculated using an exponential decay model to weight recent performance higher than old performance.
>
> Based on that mastery score, it decides: promote to harder questions (if mastery > 0.8), stay at current difficulty, or demote to easier content (if mastery < 0.4). It also applies the Ebbinghaus forgetting curve - if a user hasn't practiced a topic in 21 days, their mastery for that topic decays.
>
> It's intelligent behaviour from well-designed rules, not machine learning. I'm explicit about this in the thesis to avoid overclaiming."

---

### Q29: What is the Ebbinghaus Forgetting Curve and how did you implement it?

**The answer:**
> "Ebbinghaus (1885) showed empirically that memory of learned material decays exponentially over time without reinforcement. The mathematical model is:
>
> `R(t) = e^(-t/S)`
>
> where R is retention (0-1), t is time elapsed since last review, and S is the 'stability' of the memory.
>
> I implement it as: if a user hasn't engaged with a topic in more than 7 days, their mastery decays by a factor of 0.85 per day of inactivity, but never drops below a floor of 0.30. The 21-day half-life means mastery halves every 21 days of no practice.
>
> The floor of 0.30 represents 'it's not completely forgotten' - consistent with research showing that relearning is faster than initial learning. This is called the 'savings effect' in cognitive psychology."

---

### Q30: What is Recency-Weighted Mastery? Why does it matter?

**The answer:**
> "Recency-weighted mastery means recent performance matters more than old performance when calculating a user's current skill level.
>
> The formula uses exponential decay: for each attempt in chronological order, the weight is `0.85^(n-i)` where n is the total attempts and i is the attempt index. So the most recent attempt has weight 1.0, the one before has weight 0.85, the one before that has weight 0.72, and so on.
>
> Why does this matter? Imagine a user who was consistently bad at phishing simulations six months ago, but has been improving recently. A simple average would show them as medium-skill - unfairly. Recency-weighting correctly shows their current upward trajectory and adjusts content accordingly.
>
> The opposite also applies - if a previously good user suddenly starts getting everything wrong, the system detects the drop quickly and provides remedial content."

---

### Q31: What is F1 Score and why did you use it instead of accuracy?

**The answer:**
> "Accuracy counts what fraction of all predictions are correct. The problem: with 4 risk classes, if the model correctly labels 90% of low-risk users (the majority class) but gets confused between high-risk and critical, accuracy might look like 80% even though it's failing at exactly the predictions that matter most.
>
> F1 score is the harmonic mean of Precision and Recall:
> - **Precision**: Of all users I labelled 'critical risk', how many actually were? (avoiding false alarms)
> - **Recall**: Of all actual 'critical risk' users, how many did I correctly identify? (avoiding misses)
>
> F1 penalises models that sacrifice one for the other. A model with 100% precision but 10% recall is useless - it only flags users it's certain about and misses everyone else.
>
> I report macro-F1 - the average F1 score across all 4 classes, treating each equally regardless of class size. This ensures the model performs well for *all* risk tiers, not just the common ones."

---

### Q32: What is Cohen's Kappa and why does it matter?

**The answer:**
> "Cohen's Kappa measures agreement between the model's predictions and the true labels, *adjusted for chance*.
>
> The issue with accuracy: even a random classifier that predicts by coin flip achieves some correct predictions by chance. If 54% of users are low-risk, a model that always predicts 'low risk' gets 54% accuracy - but it's learned nothing.
>
> Kappa subtracts out the expected agreement from random guessing:
>
> `κ = (Observed accuracy - Expected by chance) / (1 - Expected by chance)`
>
> My Kappa of 0.875 means 87.5% better than chance - in the 'almost perfect agreement' band on the Landis & Koch scale. This confirms that the high accuracy isn't just from predicting the majority class - the model genuinely learned all four risk tiers."

---

### Q33: 🔴 Your hypothesis H1 was that RF beats baseline by 15 F1 points. You beat it by 52. Isn't that suspicious?

**The answer:**
> "It's a fair concern - an unexpected large positive result can signal something went wrong. Let me address it directly.
>
> The gap is large because the baseline is very weak. My rule-based baseline simply inverts overall accuracy to a risk score using a threshold: above 50% accuracy → low risk, below → high risk. For four classes, this is essentially random guessing with a slight bias. The F1 of 0.37 reflects that - it's barely better than random.
>
> Meanwhile, Random Forest has 14 features and learns complex non-linear patterns. A 52-point gap over a near-trivial baseline is entirely plausible.
>
> The real validation is internal consistency: the 3-fold cross-validation F1 of 0.83 closely matches the hold-out F1 of 0.89. If the result were spurious - from data leakage or overfitting - cross-validation would reveal it. The consistency suggests the result is genuine."

---

*[Continues in Part 4 - Ethics, Data & Examiner Traps]*

---

## PART 6 - ETHICS & DATA (RQ2)

---

### Q34: Doesn't behavioural risk scoring make AHRID a surveillance tool?

**The answer:**
> "This is exactly what Research Question 2 investigates - it's not a flaw, it's the ethical core of my thesis.
>
> The distinction between training and surveillance is about *purpose*, *transparency*, and *consent*. A surveillance system monitors without knowledge and uses data for control. AHRID is the opposite on all three:
>
> **Purpose** - data is used only to personalise training content for the user's benefit, not to generate performance records for management.
>
> **Transparency** - every risk score comes with a SHAP explanation showing exactly what drove it. Users aren't just told 'you're high risk'; they're told why in plain English.
>
> **Data boundaries** - by design, managers can only see anonymised cluster-level aggregates. They cannot see individual user risk scores. This architectural choice was deliberate.
>
> The system is advisory and opt-in. It's closer to a personal trainer tracking your workout performance than an employer monitoring your productivity."

---

### Q35: What happens if the model gives someone a wrong high-risk score?

**The answer:**
> "False positives are a genuine risk, and I address them through three governance mechanisms.
>
> First, **no employment use** - the system's terms explicitly state risk scores cannot be used for hiring, firing, or performance reviews without explicit human review. Scores are advisory tools for training, not HR judgements.
>
> Second, **contestability via SHAP** - because every score has a transparent explanation, a user who believes they've been wrongly flagged can point to the explanation and say 'this doesn't reflect my actual work.' This is the principle of meaningful human oversight.
>
> Third, **decay and self-correction** - the model re-scores users as they complete new training sessions. A false positive doesn't persist; it corrects as new behavioural data accumulates. The recency-weighting in the mastery system means recent correct performance quickly outweighs historical anomalies."

---

### Q36: You used synthetic data. Doesn't that mean your evaluation is invalid?

**The answer:**
> "Synthetic data and invalid evaluation are not the same thing. Let me be precise.
>
> My evaluation is valid for the claim I make: *that a Random Forest trained on behavioural profiles achieves significantly higher classification accuracy than a rule-based baseline.* Both the RF and the baseline were trained and tested on the same synthetic dataset under the same conditions - so the comparison is internally consistent.
>
> What I cannot claim is: 'this model will achieve 91.4% accuracy on real Nepali SME employees.' That would require validation on real data, which I document as future work.
>
> The synthetic profiles are parameterised from documented SME security incident characteristics and known behavioural patterns - Hadlington (2017) specifically documents the fast-click overconfident behaviour I simulate in the critical-risk profile. So the patterns are theoretically grounded, even if not empirically validated on live users."

---

### Q37: 🔴 What about concept drift? Phishing tactics change - will your model become useless?

**The answer:**
> "Concept drift is a real and important challenge for any ML model deployed in a dynamic threat environment. Phishing techniques evolve - today's attack is different from next year's.
>
> My architecture addresses this in two ways. First, the OSINT pipeline updates the *scenario content* continuously - new phishing URLs, new lure types, new attack categories are ingested every 6 hours. So even if the model itself doesn't retrain, users are being tested on current techniques.
>
> Second, the model is designed to retrain as real user data accumulates. The `train_models.py` script can be re-run with updated data. With sufficient real users, periodic retraining would keep the behavioural patterns current.
>
> I document concept drift as a limitation and future work - specifically, implementing automated drift detection using Population Stability Index to trigger retraining when the input distribution shifts significantly."

---

### Q38: 🔴 The Nepal Privacy Act - how does your system comply?

**The answer:**
> "The Nepal Individual Privacy Act 2075 (2018) establishes rights around personal data collection, consent, and use. My system addresses compliance through three architectural decisions.
>
> First, **minimum data collection** - AHRID collects only training performance data (scenario responses, timestamps, accuracy). No biometric data, no location data, no communication monitoring. Data minimisation is a core privacy principle.
>
> Second, **purpose limitation** - the data collected is used exclusively for training personalisation. I implement this architecturally: the manager dashboard queries only aggregate cluster data, not raw user records. The individual risk data is segregated.
>
> Third, **consent** - the system is opt-in. Users register voluntarily and consent to performance tracking as part of the onboarding flow.
>
> I acknowledge that Nepal's specific AI governance framework is still developing, and formal data protection impact assessments would be required before enterprise deployment."

---

## PART 7 - EXAMINER TRAPS (HARDEST QUESTIONS)

---

### 🔴 Trap 1: "Could a simple logistic regression have done the same job?"

**The wrong answer:** "No, logistic regression is too simple."

**The right answer:**
> "That's a fair challenge. Logistic regression is a strong baseline and I should have included it in my comparison - that's a genuine gap. For linearly separable problems, it would likely perform similarly.
>
> However, the 14 features in my model have non-linear interactions. For example, the combination of fast response time AND low accuracy (overconfident_rate) is what identifies high-risk users - neither feature alone is sufficient. Logistic regression models linear relationships and would struggle with this interaction unless I manually created interaction features.
>
> Random Forest captures these interactions automatically through the tree structure. That's the theoretical justification, though I acknowledge an empirical comparison would have strengthened the methodology section."

---

### 🔴 Trap 2: "Your model was trained and tested on synthetic data generated by the same process - isn't the test set contaminated?"

**The wrong answer:** "No, I split the data properly."

**The right answer:**
> "This is a subtle and important point. You're right that both train and test sets come from the same synthetic generation process - so they share the same underlying statistical distributions and patterns. A model trained on synthetic data can look artificially good on synthetic test data because both sets reflect the same synthetic 'reality'.
>
> I can't fully escape this without real user data. What I can say is: the patterns I simulate - fast wrong answers, low category accuracy, irregular session behaviour - are documented in the empirical literature. If the model learned to recognise these patterns from synthetic data, those same patterns should appear in real data.
>
> The appropriate caveat is in the thesis: the performance numbers are valid for the synthetic validation context. Real-world performance would need to be measured empirically with live users. This is the primary limitation of my evaluation."

---

### 🔴 Trap 3: "Why do you need ML at all? What does the model learn that your rules don't capture?"

**The wrong answer:** "Because ML is better."

**The right answer:**
> "The empirical answer is in the results: F1 of 0.89 versus 0.37 for the rule-based baseline - a 52-point improvement. But let me explain *why* that gap exists.
>
> My rule-based baseline only uses one feature - overall accuracy - and applies a single threshold. It ignores 13 other features and all interactions between them.
>
> Random Forest learns that risk isn't just about accuracy. A user with 75% accuracy who answers in 800ms is different from one with 75% accuracy who answers in 4000ms. A receptionist who's poor at physical security is different from an accountant who's poor at it - the risk implications differ by role. These multi-feature, non-linear patterns are exactly what ML is good at and rule systems cannot easily capture without manually specifying every combination - which scales poorly and doesn't generalise."

---

### 🔴 Trap 4: "You say SHAP provides ethical transparency. But who validates that the SHAP explanation is actually correct?"

**The wrong answer:** "SHAP is mathematically proven to be correct."

**The right answer:**
> "This gets at a deep problem in XAI research - explanation correctness is hard to evaluate. SHAP values are mathematically correct Shapley values given the model. But 'the model said this feature was important' doesn't mean 'the feature is genuinely causal in the real world.'
>
> In my system, I validate the explanations in two ways. First, sanity-check: I manually verify that the top SHAP features for archetypal synthetic users match expectations - an overconfident clicker should have overconfident_rate as their top SHAP feature. Second, consistency: the same user with consistent behaviour should receive similar SHAP values across recalculations.
>
> Full validation - asking real users whether the explanation matches their self-perception - would require a user study. That's listed as future work and connects to the HAIS-Q evaluation that was scoped out of this version."

---

## PART 8 - LIGHTNING ROUND (30-SECOND ANSWERS)

*Practice saying each of these in under 30 seconds.*

| Question | Answer in one breath |
|---|---|
| What does AHRID stand for? | Adaptive Human Risk Intelligence Dashboard |
| What problem does it solve? | Non-technical SME employees in Kathmandu Valley have no affordable cybersecurity training |
| What are your three ML components? | Random Forest for risk prediction, K-Means for behavioural archetypes, SHAP for per-user explanations |
| What's your best metric? | Cohen's Kappa 0.875 - almost perfect agreement, well beyond chance |
| Why Random Forest? | Interpretable, works with 1,050 samples, integrates naturally with SHAP |
| Why K-Means? | Produces 5 interpretable named archetypes with meaningful centroids |
| Why SHAP? | Provides per-user local explanations - not global averages - for ethical transparency |
| What is SMOTE? | Synthetic interpolation between minority-class samples to fix class imbalance |
| What is the forgetting curve? | Ebbinghaus (1885) - mastery decays over time without practice; implemented as 21-day half-life |
| What is your biggest limitation? | ML model trained entirely on synthetic data; real-world performance requires empirical validation |
| What is Cohen's Kappa 0.875? | 87.5% better than random chance - 'almost perfect agreement' on the Landis & Koch scale |
| Why not neural network? | Black box, overfits on 1,050 samples, can't integrate with SHAP as cleanly |
| Why not logistic regression? | Can't capture non-linear feature interactions without manual feature engineering |
| What is cross-validation? | Train on 2/3 of data, test on 1/3, repeat 3 times - gives stable performance estimate |
| What is data leakage? | Test data information bleeding into training - I prevent it by splitting before SMOTE |
| Who sees individual risk scores? | Only the employee themselves - managers see only anonymised cluster-level aggregates |
| What governance protects employees? | Scores are advisory only, cannot be used for HR decisions without human review |
| How does the adaptive engine work? | Recency-weighted mastery → content weighting → difficulty promotion/demotion |

---

## PART 9 - THEORETICAL FOUNDATIONS (WHAT PAPERS BACK YOUR CHOICES)

| Concept | Paper | What it says |
|---|---|---|
| Random Forests | Breiman (2001) | Foundational paper - ensemble of unpruned trees with bootstrap sampling |
| SHAP | Lundberg & Lee (2017) | Game theory-based attribution, unified framework for explaining ML outputs |
| Cognitive failures in cybersecurity | Hadlington (2017) | Documents fast-click overconfident behaviour - validates your critical-risk profile |
| ML in cybersecurity | Buczak & Guven (2016) | Survey confirming RF as strong baseline for behavioural classification |
| SMOTE | Chawla et al. (2002) | Original SMOTE paper - interpolation-based oversampling |
| Forgetting curve | Ebbinghaus (1885) | Exponential memory decay; relearning is faster than initial learning |
| Spaced repetition | Cepeda et al. (2008) | Optimal spacing intervals for long-term retention |
| Protection Motivation Theory | Rogers (1975) | Threat appraisal + coping appraisal → behaviour change |
| Technology Acceptance Model | Davis (1989) | Perceived ease of use and usefulness predict adoption |
| Cohen's Kappa scale | Landis & Koch (1977) | 0.81-1.00 = 'almost perfect agreement' |

---

> **Final reminder:** Your examiner is not your enemy. They want to see that you built something real, understood it deeply, and can talk about it honestly - including its limitations. Confidence comes from preparation. You've built a genuinely interesting system. Own it.

---

---

# NON-TECHNICAL VIVA QUESTIONS

> These are the questions that catch students off-guard because they seem "easy." They're not technical - but they require deep, honest self-reflection about your project. Practice these just as hard as the ML questions.

---

## PART 10 - MOTIVATION & RESEARCH STORY

---

### Q39: Why did you choose this topic? What motivated you?

**The answer:**
> "The topic came from a real gap I observed in the Nepali SME landscape. Kathmandu Valley has seen rapid digital adoption - banking, fintech, government services all moved online post-COVID - but the human side of cybersecurity hasn't kept pace. SME employees are targeted constantly by phishing and social engineering, but enterprise training platforms like KnowBe4 are priced out of their reach.
>
> What interested me specifically was the combination of two problems: the training gap, and the lack of personalisation in existing solutions. Most phishing simulations are static - everyone gets the same test. I wanted to explore whether ML could make training adaptive - responding to each person's actual weaknesses in real time.
>
> Personally, I'm drawn to systems that use data to help people rather than just classify them. AHRID is both technically interesting and has a clear human benefit. That's what motivated the research."

---

### Q40: In one sentence - what is your thesis about?

**The answer:**
> "My thesis investigates whether integrating machine learning - specifically Random Forest classification, K-Means clustering, and SHAP explainability - with live threat intelligence can produce more accurate and ethically transparent cybersecurity risk predictions than rule-based approaches for non-technical SME employees."

*Practice saying this until it comes out naturally, without looking at notes.*

---

### Q41: What is the original contribution of your research?

**The answer:**
> "My contribution has three layers.
>
> First, **technical**: I demonstrate that a Random Forest trained on 14 behavioural features outperforms a rule-based risk baseline by 52 F1 points - a substantial empirical improvement that directly answers RQ1.
>
> Second, **integration**: Most cybersecurity training platforms separate threat intelligence from user training. AHRID connects them - fresh OSINT data from four sources directly populates the training scenarios users receive within 24 hours. This live threat-to-training pipeline is novel in the SME context.
>
> Third, **ethical framing**: I don't just build a risk classifier - I build a transparent one. The explicit integration of SHAP explainability as an ethical requirement, not an afterthought, contributes to the conversation about responsible AI in workplace contexts.
>
> The combination of all three - adaptive ML, live OSINT, and ethical transparency - in a single deployable system for Nepali SMEs is the specific contribution."

---

### Q42: How did your research questions evolve during the project?

**The answer:**
> "The original framing was more technical - primarily 'can ML predict phishing susceptibility?' As the project developed, I realised the ethical question was just as important, if not more so.
>
> The pivot came when I thought through who actually uses this system. A manager with access to individual employee risk scores without explanation is essentially a surveillance tool. That realisation shaped RQ2 and the entire ethical architecture - individual score privacy, SHAP transparency, the manager dashboard showing only aggregates.
>
> So the research questions didn't change dramatically, but the weight I placed on the ethical dimension grew substantially during the project. That's reflected in how much of the system design is driven by ethical constraints rather than purely technical ones."

---

### Q43: What were you surprised to find during your research?

**The answer:**
> "Two things surprised me.
>
> First, how much the baseline matters. My original hypothesis was that RF would beat rule-based by 15 F1 points - a reasonable improvement. The actual gap was 52 points. I was initially concerned this was an error, but the cross-validation results confirmed it. The lesson: a poorly designed baseline makes any ML look impressive. I've been explicit in the thesis about why the baseline is weak, so the result is honest.
>
> Second, how much of 'intelligent behaviour' doesn't require ML at all. The adaptive engine - the forgetting curve, recency-weighted mastery, difficulty progression - is entirely rule-based. I initially assumed more ML would be better. But well-designed rules were both more interpretable and more controllable for this specific use case. That shifted my thinking about when ML is actually the right tool."

---

## PART 11 - LITERATURE & THEORETICAL FRAMEWORK

---

### Q44: What is the gap in the existing literature that your thesis addresses?

**The answer:**
> "The literature has two streams that rarely intersect. First, there's substantial research on cybersecurity awareness training effectiveness - Hadlington (2017), Parsons et al. (2017) - but most of these studies use static pre/post measurement instruments rather than adaptive systems.
>
> Second, there's a growing body of ML-in-cybersecurity research - Buczak & Guven (2016) survey a range of classification approaches - but the focus is predominantly on network intrusion detection, not human behavioural risk.
>
> The gap is at the intersection: adaptive, ML-driven training personalisation for human security behaviour in the SME context, particularly in an under-studied geographical region like Nepal. No study in my literature review combined live OSINT ingestion with behavioural clustering and SHAP-based per-user explanations in a single deployable system."

---

### Q45: How does Protection Motivation Theory (PMT) connect to your system?

**The answer:**
> "PMT - Rogers (1975) - says that people's protective behaviour is driven by two appraisals: threat appraisal (how serious and likely is the threat?) and coping appraisal (do I have the ability and means to respond?).
>
> AHRID addresses both. On the threat side, the OSINT pipeline ensures training scenarios reflect real, current threats - not hypothetical examples from five years ago. When users see a training scenario based on an actual phishing campaign active this week, the threat feels real and immediate.
>
> On the coping side, the adaptive engine and SHAP explanations together give users confidence. The system doesn't just say 'you're bad at phishing' - it says 'here is specifically what you do wrong, and here is targeted practice to fix it.' That gives users a credible path to coping, which PMT predicts increases protective behaviour."

---

### Q46: How does your work relate to KnowBe4, Proofpoint, or other existing platforms?

**The answer:**
> "I did a competitive analysis of the major platforms. KnowBe4 and Proofpoint Security Awareness Training are the market leaders - they have large scenario libraries, phishing simulations, and reporting dashboards. CybSafe takes a more behavioural science approach, using psychological profiling.
>
> The key differentiators of AHRID versus these platforms are:
>
> First, **cost and access** - enterprise platforms are priced for large organisations with dedicated security teams. SMEs in Kathmandu can't access them practically or financially. AHRID is designed to be deployable on minimal infrastructure.
>
> Second, **live threat integration** - most platforms update their scenario libraries on a weekly or monthly basis via their editorial team. AHRID ingests live threat data every 6 hours automatically.
>
> Third, **per-user SHAP explanations** - I'm not aware of any commercial platform that provides per-user explainability in the sense I've implemented. Scores are given, but not explained at the feature level.
>
> I'm not claiming AHRID replaces KnowBe4. I'm claiming it addresses a different market segment with different capabilities."

---

### Q47: Which paper was most influential on your design and why?

**The answer:**
> "Lundberg & Lee (2017) - the SHAP paper - had the most direct influence, but not just for the technical reason.
>
> The paper's central argument is that explanations should satisfy specific axioms: local accuracy (they match the model's output), missingness (absent features have no impact), and consistency (features that matter more should get higher values). These aren't just mathematical properties - they're principles for trustworthy AI.
>
> Reading that paper reframed how I thought about explainability. It's not a feature you add to a model - it's a constraint on how you design the whole system. That's why SHAP isn't bolted on at the end of AHRID - the need for SHAP-compatible explanations influenced the choice of Random Forest over other models from the start."

---

## PART 12 - SYSTEM DESIGN & PROJECT DECISIONS

---

### Q48: What is the hardest design decision you made and why?

**The answer:**
> "The hardest decision was what data to show managers versus employees.
>
> The easy version: show everyone everything - individual scores, cluster assignments, detailed SHAP values. That maximises information available to managers who might want to act on it.
>
> The ethical version - what I implemented - is that employees see their own full score and SHAP explanation; managers see only anonymised cluster-level aggregates. Individual scores are completely hidden from managers.
>
> This decision significantly reduces the management utility of the system compared to what was technically possible. But it's the correct decision for the ethical framing. Once a manager can see that Employee X is 'critical risk', you've created a surveillance tool regardless of your intentions. The architectural constraint - not just a policy, but a hard data access boundary - is the only way to credibly claim the system isn't surveillance."

---

### Q49: Why Flask and not Django? Why React and not Vue?

**The answer:**
> "Flask was chosen for its minimal footprint and explicit design. Django includes an ORM, admin panel, authentication framework, and a large standard library - most of which I didn't need. Flask gave me direct control over the API structure, which mattered for integration with the ML service layer. For an SME deployment with limited server resources, Flask's smaller memory footprint is also a practical advantage.
>
> For the frontend, React was chosen primarily for TypeScript compatibility and the ecosystem maturity - component libraries, testing tools, and the Vite build system. Vue is an excellent framework, but the React ecosystem has stronger support for the accessibility and charting libraries I needed for the dashboard. This was also a case where the proposal specified the tech stack - React and Flask were in the tools section."

---

### Q50: What would you do differently if you started again?

**The answer:**
> "Three things.
>
> First, I would include at least one more algorithm in the comparison - logistic regression as a minimum. Right now I compare RF against a rule-based threshold, which is a weak baseline. A logistic regression comparison would strengthen the argument that the complexity of RF is justified.
>
> Second, I would plan the data collection earlier. The synthetic data generation is principled, but if I'd started earlier, I might have had access to a small pilot dataset of real user interactions from a willing SME - even 50 users - which would significantly strengthen the empirical claims.
>
> Third, I would invest more in evaluation of the SHAP explanations specifically. I validate the ML model thoroughly, but the explainability quality is evaluated by my own sanity check rather than by user testing. A small study asking users 'does this explanation make sense to you?' would have directly addressed the human-centricity of the XAI component."

---

## PART 13 - FUTURE WORK & REAL-WORLD DEPLOYMENT

---

### Q51: If this were deployed commercially tomorrow, what are the top 3 risks?

**The answer:**
> "First, **model performance on real users**. The model was trained on synthetic data. The first real deployment would need careful monitoring - I'd expect some performance degradation on genuinely novel user behaviour. Mitigation: deploy in shadow mode initially, comparing ML predictions against rule-based scores without using them for decisions, until enough real data accumulates to retrain.
>
> Second, **misuse of the manager dashboard**. Even with individual scores hidden, a determined manager could infer information about employees over time from cluster movements. Mitigation: formal policies governing how cluster data can be used, combined with audit logging of all dashboard access.
>
> Third, **OSINT data quality**. The threat feeds - OTX - occasionally contain false positives or low-quality entries. A scenario built on a falsely flagged URL would expose users to incorrect training. Mitigation: automated quality scoring on ingested threats before they enter the scenario pipeline."

---

### Q52: What are the top 3 directions for future work?

**The answer:**
> "First, **real user validation**. The most important next step is a pilot deployment with actual SME employees, measuring pre/post phishing susceptibility using the HAIS-Q instrument. That would directly answer the question the current thesis leaves open - does adaptive training actually improve security awareness?
>
> Second, **retraining pipeline**. Build an automated retraining trigger that activates when population drift is detected - measured by Population Stability Index on the feature distributions. This would keep the model current without manual intervention.
>
> Third, **scenario classifier upgrade**. The current scenario classifier is heuristic - keyword scoring and hash-based tiebreaking. Replacing it with a fine-tuned text classifier (BERT or similar) trained on labelled phishing examples would improve classification accuracy and handle novel phishing language patterns that keyword rules miss."

---

### Q53: 🔴 If your system went live and caused an employee to be unfairly dismissed because of a high risk score, who is responsible?

**The answer:**
> "This is the most important governance question in my thesis. The direct answer: the system as designed cannot cause that outcome, because the architectural constraints prevent managers from accessing individual risk scores. That's not a policy - it's a hard access control in the data layer.
>
> But your question gets at the deeper issue of liability in algorithmic systems. If those access controls were bypassed, or if a future version of the system relaxed them, then responsibility would sit with multiple parties: the developer who built the system (for failing to maintain the access constraints), the organisation that deployed it (for using it in a way explicitly prohibited by its terms of use), and potentially the regulatory framework for failing to govern AI in employment contexts.
>
> This is precisely why I include the human-in-the-loop governance principle - scores are explicitly advisory. The system generates an assessment; a human makes any consequential decision. That chain of accountability is essential for any AI system that touches employment."

---

## PART 14 - PERSONAL & REFLECTIVE QUESTIONS

---

### Q54: What was the most challenging part of this project?

**The answer:**
> "The hardest part was holding the ethical and technical threads together. It's easy to build a good ML model. It's easy to write an ethics chapter. What's hard is letting the ethical requirements genuinely constrain technical decisions - choosing RF over XGBoost partly because of SHAP compatibility, hiding individual scores from managers even though it reduces system utility, making SMOTE/test-split order a deliberate choice rather than an afterthought.
>
> Every time a technical shortcut looked attractive, I had to ask: does this compromise the ethical integrity of the system? That discipline is more difficult than the coding or the literature review."

---

### Q55: What did you learn from this project that you didn't expect?

**The answer:**
> "I learned that the line between an intelligent system and a surveillance tool is entirely architectural, not intentional. A system can be designed with the best intentions and still become a monitoring tool if the data access boundaries aren't enforced at the code level - not just in a policy document.
>
> I also learned to be more sceptical of impressive-looking metrics. A 91.4% accuracy number sounds excellent. Understanding *why* it's that number - the class distribution, the synthetic data, the test/train split - is what tells you whether to trust it. Learning to interrogate my own results rather than just report them was the biggest methodological growth during this project."

---

### Q56: If an examiner challenges your entire premise - "phishing training doesn't work, the research shows it" - how do you respond?

**The answer:**
> "That's a legitimate critique - there is research suggesting that static, one-time phishing simulations have limited long-term impact on user behaviour. Rocha Flores et al. (2015) and others show that awareness alone doesn't reliably translate to behaviour change.
>
> My response is: AHRID addresses exactly this limitation. The critique applies to static training - everyone gets the same scenario once a year. AHRID is designed as a continuous, adaptive system. The forgetting curve implementation ensures topics are revisited before they decay. The scenario difficulty adapts so users aren't bored with easy content they've mastered or overwhelmed by content that's too hard.
>
> Whether this adaptive approach actually performs better than static training - that's an open empirical question that requires a longitudinal study. I claim the *design* is theoretically sound based on the educational psychology literature. I'm careful not to claim proven efficacy, because that would require the kind of controlled trial that's outside the scope of this project."

---

> **Remember:** These non-technical questions feel easier, but they require the most honest self-reflection. An examiner who asks "what would you do differently?" is giving you an invitation to demonstrate academic maturity - not trap you. Take it.

---

*End of 18_VIVA_QA.md*
*Total: 56 questions across 14 sections - technical, ethical, motivational, reflective, and deployment*




