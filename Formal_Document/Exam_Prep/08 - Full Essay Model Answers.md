---
tags: [exam, ST6047CEM, AHRID, essays, priority]
---

# Full Essay Model Answers (300–650 words each)

Related: [[00 - Exam Prep Hub]] | [[07 - Ethics Deep Dive]] | [[05 - Mock Exam Paper]]

> [!danger] Why this note exists
> A 2–3 hour written exam producing ~2000 words means the real paper will ask **4–6 substantial essay questions**, not 20 short-answer prompts. The other notes in this vault give you accurate *content* — this note shows you what **exam-ready length and structure** actually looks like, so you can pace yourself and internalise the shape of a strong answer, not just the facts inside it.

> [!tip] Structure every long answer the same way
> 1. **Opening claim** (1–2 sentences — directly answer the question)
> 2. **Development** (2–4 paragraphs — mechanism, evidence, numbers, alternatives considered and rejected)
> 3. **Honest limitation** (1 paragraph — what this doesn't prove, what would strengthen it)
> 4. **Closing tie-back** (1–2 sentences — link explicitly back to RQ1/RQ2)
> Examiners mark down answers that are accurate-but-list-like. A flowing argument with the same facts scores higher than bullet points dressed as prose.

---

## Essay 1 — "Explain how AHRID satisfies RQ2, and evaluate how convincing this satisfaction actually is." (Ethics-priority, ~600 words)

> [!success]- Model Answer
> AHRID satisfies RQ2 — how automated behavioural risk assessment can protect employee privacy, promote transparency, support non-punitive learning, and comply with Nepal's Individual Privacy Act 2075 — by treating ethics as an architectural constraint embedded from the earliest design phase, rather than a compliance audit performed after the platform was built. This distinction matters because a system designed first and checked for ethics afterward tends to have ethical properties that can be quietly overridden by a later business decision, whereas AHRID's key protections are enforced at the data and API layer, where they are much harder to circumvent informally.
>
> The clearest evidence is the mapping between IPA 2075's core principles and specific technical mechanisms. Purpose limitation is enforced by architecturally isolating behavioural scores and cluster assignments from any HR or performance-management data structure, and by never transmitting this data to third-party services. Data minimisation is enforced by restricting the entire machine learning pipeline to eighteen engineered behavioural features — response time, per-category accuracy, session consistency, and similar signals — while excluding biometric data, national identification numbers, financial records, and any other information not strictly necessary for risk prediction. The right to information is satisfied through SHAP TreeExplainer, which generates a plain-language explanation for every single risk classification, naming the specific behavioural factors that contributed to the score, rather than presenting employees with an unexplained number. Informed consent is enforced through a consent-first onboarding flow: no behavioural data collection can begin until the employee has explicitly acknowledged the privacy disclosure, and withdrawing consent triggers deletion of associated records and immediate invalidation of active authentication tokens.
>
> Beyond the four named IPA 2075 principles, AHRID also embeds a non-punitive governance model that goes beyond what the law strictly requires. Role-based access control ensures that managers can only view aggregate, team-level risk trends through the platform's API — individual SHAP explanations and granular behavioural detail are visible only to the employee and, for audit purposes, administrators. Critically, an elevated risk classification triggers additional adaptive training content for that employee; there is no code path connecting a risk score to any disciplinary or performance-review process. This was a deliberate architectural choice, not merely a written policy, precisely because policies can be ignored while access-control boundaries cannot be as easily bypassed.
>
> However, this satisfaction of RQ2 should be evaluated honestly rather than presented as complete. First, IPA 2075 is a comparatively young privacy law without the depth of case law or explicit automated-decision-making provisions found in frameworks like GDPR Article 22 — AHRID's compliance is architectural alignment with the spirit of the law, not a formal legal certification, which is appropriate scope for a technical BSc project but should not be overstated. Second, algorithmic fairness was only partially verified: a feature audit confirmed that no protected-characteristic proxies exist among the eighteen features, but fairness across real demographic subgroups could not be tested, since all evaluation used synthetic data not designed with demographic fairness testing in mind. Third, technical controls cannot fully prevent organisational misuse — a determined bad-faith manager or administrator could still draw inferences informally, even if RBAC prevents them from directly querying individual behavioural detail through the platform.
>
> In summary, AHRID answers RQ2 convincingly at the level of architectural design: privacy, transparency, and non-punitive governance are demonstrably built into the system rather than asserted about it. What remains open is empirical validation under real organisational conditions, real demographic diversity, and sustained real-world governance — precisely why real-world SME deployment is identified as the highest-priority direction for future work.

---

## Essay 2 — "Justify the design of your three-stage machine learning pipeline and explain how it answers RQ1." (Technical-with-ethical-framing, ~550 words)

> [!success]- Model Answer
> AHRID's three-stage pipeline — K-Means behavioural clustering, Random Forest risk classification, and SHAP explainability — was designed specifically to answer RQ1: whether an adaptive platform integrating behavioural machine learning, live OSINT threat intelligence, and explainable AI can outperform a conventional rule-based awareness approach for non-technical SME employees.
>
> The first stage, K-Means clustering with k=5, groups employees into behavioural archetypes based on six standardised interaction features, without requiring labelled training data. This unsupervised step was chosen because it can surface latent behavioural patterns — such as the "Overconfident Clicker" archetype, characterised by fast responses and inconsistent judgement, or the "Disengaged Completer" archetype, characterised by low participation — that a supervised model alone would not explicitly represent. The resulting cluster label is then fed into the second stage as one of eighteen input features, allowing long-run behavioural identity to inform, rather than solely determine, an individual prediction.
>
> The second stage, a Random Forest classifier, was selected over alternatives including XGBoost, Support Vector Machines, and deep neural networks for three concrete reasons tied to this specific project. First, Random Forest natively supports SHAP TreeExplainer, which computes exact Shapley values for tree ensembles rather than the approximated explanations required for arbitrary black-box models — this directly serves the explainability requirement central to RQ1 and RQ2 alike. Second, the dataset — 1,050 statistically calibrated synthetic behavioural profiles — is far too small to train a deep neural network without substantial overfitting risk, whereas Random Forest's ensemble-of-trees structure is well suited to moderate tabular datasets. Third, after balancing the four risk classes with SMOTE, Random Forest handles the resulting feature space robustly without the extensive hyperparameter tuning that XGBoost or SVMs typically require to perform comparably.
>
> The third stage, SHAP TreeExplainer, converts each Random Forest prediction into a plain-language explanation identifying which behavioural factors — for example, below-threshold phishing-category accuracy, or unusually fast response times suggesting insufficient scrutiny — contributed most strongly to that employee's risk classification. This was prioritised over a simpler global feature-importance display because global importance describes what matters on average across the whole model, not why a specific individual received their specific score, which is what genuinely actionable, personalised feedback requires.
>
> The empirical result directly answers RQ1: the pipeline achieved 90.95% accuracy, a macro F1-score of 0.889, and a PR-AUC of 0.9399, compared with a rule-based baseline that achieved only 0.3868 macro F1 — an improvement of just over fifty percentage points. Cohen's Kappa of 0.8684 indicates almost perfect agreement between predicted and actual risk classifications, and three-fold cross-validation, producing a mean F1 of 0.8604 with a standard deviation of only 0.0094, demonstrates that this performance is stable rather than an artefact of one lucky data split.
>
> The honest limitation is that this evaluation, while methodologically sound, was conducted entirely on synthetic data calibrated against real Nepal Police Cyber Bureau statistics rather than on real employee behaviour. This means RQ1 is answered convincingly at the level of architectural capability — the pipeline demonstrably can integrate these three stages and outperform a rule-based alternative — while the magnitude of that improvement in a genuine deployment remains an open empirical question for future work.

---

## Essay 3 — "An examiner claims AHRID is workplace surveillance regardless of your intentions. Respond fully." (Ethics-priority, ~500 words)

> [!success]- Model Answer
> This is a fair concern to raise about any system that continuously analyses employee behaviour, and it deserves a direct response grounded in what AHRID's architecture actually does, rather than a defensive appeal to good intentions alone.
>
> It is true that AHRID collects behavioural interaction data — response times, per-category quiz accuracy, session engagement patterns — and uses it to classify employees into risk tiers. In isolation, this description does resemble workplace monitoring. What distinguishes AHRID from a punitive surveillance system is not the presence of behavioural data collection, but three specific, enforced properties of what happens to that data afterward.
>
> First, role-based access control restricts what a manager can see through the platform to aggregate, team-level risk trends only. A manager cannot query an individual employee's SHAP explanation or granular behavioural history through AHRID's API — that visibility is restricted to the employee themselves, and to administrators for audit purposes. This is enforced at the authorisation layer of the system, not merely hidden in the user interface, meaning it cannot be casually bypassed by a manager who simply asks for more detail.
>
> Second, and most importantly, there is no code path connecting a risk classification to any disciplinary or performance-management outcome. When an employee is classified as High or Critical Risk, the only system response is that the adaptive training engine surfaces additional, targeted training scenarios for that employee. Nothing is written to a performance record, nothing is flagged for HR review, and no manager receives an alert naming that individual. This is a deliberate architectural decision, reflecting the thesis's non-punitive governance model, which is designed to make elevated risk a trigger for support rather than consequence.
>
> Third, employees retain meaningful agency over their own data: consent is required before any collection begins, withdrawal is supported and triggers deletion of records, and every risk score is accompanied by a SHAP-generated explanation the employee can read and act on themselves — this is fundamentally different from opaque monitoring, where a subject has no visibility into what is being inferred about them or why.
>
> I want to be honest about the limit of this defence, however. Technical controls cannot fully prevent organisational misuse. A manager who is determined to informally judge an employee's performance could still form impressions through means outside the platform, and RBAC cannot prevent that. This is why the thesis explicitly frames privacy-by-design as a necessary but not sufficient condition — the technical architecture must be paired with organisational policy that reinforces, rather than undermines, the non-punitive intent designed into the system.
>
> So my position is not that AHRID is somehow immune from surveillance risk by virtue of good intentions, but that it is architecturally distinguishable from a punitive monitoring system through concrete, verifiable mechanisms: access-control boundaries, the absence of any disciplinary data path, and enforced employee transparency and consent. That is a stronger claim than "we didn't intend it to be used that way," and it is the claim the evidence actually supports.

---

## Essay 4 — "Trace the complete lifecycle of a single employee's data through AHRID, from collection to deletion." (Technical + ethical integration, ~500 words)

> [!success]- Model Answer
> Tracing a single employee's data through AHRID illustrates how the platform's technical architecture and ethical commitments are implemented as one integrated system rather than as separate concerns.
>
> The lifecycle begins at onboarding, where the employee must explicitly acknowledge a privacy disclosure before any behavioural data collection can begin — this consent-first design satisfies IPA 2075's informed consent principle at the very first point of contact. Once training begins, the employee completes scenario-based exercises, and the platform records eighteen behavioural interaction features per prediction cycle: metrics such as response time, per-category accuracy across the platform's phishing, social engineering, and password-hygiene categories, and session consistency. Deliberately excluded from this collection are any biometric identifiers, financial data, precise location information, or communication content — this is the enforced boundary of data minimisation.
>
> These behavioural features feed two machine learning stages. First, K-Means clustering assigns the employee to one of five behavioural archetypes based on their accumulated interaction pattern, producing a cluster label that is periodically recalculated as new data arrives. Second, this cluster label, combined with the seventeen other behavioural features, is passed into the Random Forest classifier, which outputs a risk tier — Low, Medium, High, or Critical — along with a confidence score. Immediately following classification, SHAP TreeExplainer computes the exact feature-level contribution to that specific prediction, and this is translated into a plain-language explanation delivered to the employee, satisfying the right-to-information principle at the point where it matters most: the moment a decision affecting the employee is made.
>
> If the resulting classification is Medium, High, or Critical, the only downstream system action is that the adaptive training engine reprioritises which scenarios the employee sees next, weighted toward their weakest categories and informed by a spaced-repetition mechanism that resurfaces content the employee has not practised recently. At no point in this lifecycle does a risk classification write to any record accessible by a manager beyond aggregate team statistics, and at no point does it trigger any workflow outside the training platform itself.
>
> Should the employee choose to withdraw consent, or leave the organisation, this triggers deletion of their behavioural records from the database and immediate invalidation of any active authentication tokens through the server-side JWT revocation mechanism — meaning access is severed at that moment, not merely at the next natural token expiry up to thirty days later. This closes the lifecycle in a manner consistent with a right-to-be-forgotten expectation, even though IPA 2075 does not use that exact terminology.
>
> Throughout this entire lifecycle, no data leaves the platform to any third-party service, and no personally identifiable information — as opposed to behavioural interaction data — is ever collected in the first place, since all model development and evaluation for this thesis used statistically calibrated synthetic profiles rather than real employee data. This end-to-end trace demonstrates that AHRID's ethical commitments are not a separate policy layer sitting alongside the technical system, but are implemented as specific, verifiable steps within the data's actual path through the platform.
