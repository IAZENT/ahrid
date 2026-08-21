---
tags: [exam, ST6047CEM, AHRID, ethics, priority]
---

# Ethics Deep Dive — Priority Topic

Related: [[00 - Exam Prep Hub]] | [[03 - Section C Critical Ethical]]

> [!danger] Teacher signal: focus on ETHICS over technical detail.
> Treat this note as the highest-priority material in the whole vault. RQ2 is your ethical research question, and "ethical considerations and potential impact on stakeholders" is its own line item in the marking rubric. If exam time is tight, answer the ethics questions thoroughly and the technical ones adequately — not the reverse.

---

## 1. The Core Ethical Framing

> [!question] Why is ethics treated as a "design requirement" rather than a compliance checklist in your thesis?
> > [!success]- Answer
> > Because AHRID continuously analyses employee behaviour to generate automated risk assessments — technical performance alone is insufficient if the system can't also protect privacy, ensure fairness, and prevent misuse. Ethics was embedded into every Design Science Research iteration (reviewed at every development phase/sprint), not bolted on after the platform was built. This matters because a system built first and audited for ethics afterward tends to have ethics "designed around" rather than "designed in" — AHRID's architecture (zero-PII pipeline, RBAC boundaries, non-punitive workflow) physically cannot easily violate its own principles, whereas a policy-only approach could be overridden by a manager or admin decision.

> [!question] What ethical framework did you draw on beyond IPA 2075 itself?
> > [!success]- Answer
> > **AI4People** (Floridi et al., 2018) — an ethical framework built on five principles: beneficence, non-maleficence, autonomy, justice, and explicability. Map AHRID to each:
> > - **Beneficence:** improves employee cyber-risk awareness through personalised training.
> > - **Non-maleficence:** non-punitive governance — elevated risk never triggers disciplinary consequences.
> > - **Autonomy:** employees retain control (consent, withdrawal, visibility into their own SHAP explanations).
> > - **Justice:** feature audit excludes protected-characteristic proxies (age, gender, nationality); SMOTE prevents majority-class bias.
> > - **Explicability:** SHAP-based per-prediction explanation for every risk score.
> > Also **Jobin, Ienca & Vayena (2019)** — the global landscape of AI ethics guidelines, used to argue that transparency and accountability are now baseline expectations for any AI system that classifies individuals, not optional extras.

---

## 2. IPA 2075 — Go Deep, Not Just Surface-Level

> [!question] Walk through all four IPA 2075 principles in detail, with the exact technical mechanism for each.
> > [!success]- Answer
> > | Principle | Requirement | AHRID's technical mechanism |
> > |---|---|---|
> > | **Purpose limitation** | Data used only for the stated purpose | Behavioural scores and cluster assignments are stored in dedicated database structures, architecturally isolated from any HR/performance system; never transmitted to third-party analytics or external APIs |
> > | **Data minimisation** | Collect only what's necessary | Exactly 18 engineered behavioural features feed the ML pipeline; biometric data, national ID numbers, financial records, precise location, communication content, and device telemetry are explicitly excluded from both training and inference |
> > | **Right to information** | Explain automated decisions | Every risk prediction is accompanied by a SHAP TreeExplainer-generated, plain-language explanation naming the specific behavioural factors that drove the score |
> > | **Informed consent** | Obtain consent before collection | Consent-first onboarding — behavioural data collection cannot begin until the user explicitly acknowledges the privacy disclosure; users can withdraw consent, triggering deletion of associated records and invalidation of active JWTs |
> > A fifth control worth naming even though it's not a named IPA principle: **Accountability** — append-only audit logging of administrative actions on employee data, plus JWT revocation on logout/withdrawal.

> [!question] Is IPA 2075 compliance the same as GDPR compliance? Why does this distinction matter?
> > [!success]- Answer
> > No — IPA 2075 is the binding jurisdiction (Nepal), but it is a comparatively young privacy law without as extensive case law or explicit "automated decision-making" provisions as GDPR's Article 22. AHRID's design *exceeds* the explicit letter of IPA 2075 by voluntarily adopting GDPR-adjacent principles like a "right to explanation," which future-proofs the platform if Nepali regulation matures, or if the platform were ever extended to organisations with EU-linked compliance obligations. This is framed honestly as compliance **by design**, not a formal legal certification — appropriate scope for a BSc technical project, not a legal audit.

> [!question] What happens, technically, when an employee withdraws consent or leaves the company?
> > [!success]- Answer
> > Withdrawal triggers deletion of the associated behavioural records and invalidates any active JWT authentication tokens for that user (via the server-side revocation/blocklist mechanism) — so access is cut immediately, not just at next token expiry. This operationalises the "right to be forgotten"-adjacent expectation under data protection principles even though IPA 2075 doesn't use that exact phrase.

---

## 3. Algorithmic Fairness

> [!question] How do you know the model isn't discriminating against protected groups, given you never tested it on real diverse employees?
> > [!success]- Answer
> > Two-part answer — be honest about the limit:
> > 1. **What was done:** a feature audit before training confirmed none of the 18 features are direct or proxy variables for protected characteristics (age, gender, nationality, disability) — the model literally cannot use demographic information it was never given.
> > 2. **What wasn't and can't yet be done:** fairness across *real* demographic subgroups (e.g. do certain roles/genders get systematically misclassified?) cannot be verified without real deployment data, since synthetic profiles weren't generated with demographic fairness testing in mind. This is a genuine open question for Future Work — name it directly rather than claiming fairness was "proven."

> [!question] Why SMOTE for class balance, and does it have fairness implications?
> > [!success]- Answer
> > SMOTE balances the four *risk* classes (Low/Medium/High/Critical), not demographic groups — its purpose is preventing the classifier from defaulting to the majority risk class, not a fairness intervention across people. It's applied only to the training set (test set stays untouched) and uses k=5 nearest-neighbour interpolation, which keeps synthetic points behaviourally plausible rather than arbitrary. No known negative fairness implication for this specific balancing axis, but worth clarifying the distinction if an examiner conflates "class imbalance" with "demographic bias" — they're different problems.

---

## 4. Non-Punitive Governance — The Mechanism, Not the Slogan

> [!question] "Non-punitive governance" sounds like a policy statement. What's the actual enforced mechanism?
> > [!success]- Answer
> > - **RBAC scope:** the manager role's API access is limited to aggregate team-level risk trends. Individual SHAP explanations and granular behavioural detail are visible only to the employee themselves (and admins, for audit purposes) — this is enforced at the API authorisation layer, not just a UI hiding decision.
> > - **No disciplinary data path:** an elevated risk classification triggers the adaptive engine to surface additional training scenarios. There is no code path from a risk score to any HR/performance-review-adjacent record.
> > - **Explicit acknowledged limit:** this is a *technical* safeguard, not a guarantee against organisational misuse — a determined bad-faith admin could still misuse aggregate data informally. That's why the thesis frames this as requiring **organisational policy alongside the technical control**, not architecture alone.

> [!question] Could a manager still misuse this system even with RBAC in place?
> > [!success]- Answer
> > Yes — worth admitting proactively. RBAC prevents a manager from *querying* individual behavioural detail through the platform, but it can't prevent a manager who has other means of observing an employee (e.g. informal conversation, overall team ranking inference) from drawing conclusions. This is why the thesis frames privacy-by-design as necessary-but-not-sufficient — organisational culture and policy have to reinforce the technical boundary.

---

## 5. Ethical Trade-offs — Show You Understand the Tension, Not Just the Solution

> [!question] What's the central ethical trade-off in choosing synthetic data over real data?
> > [!success]- Answer
> > **Privacy vs. validity.** Synthetic data eliminates the risk of processing real PII (satisfying IPA 2075 cleanly, avoiding the need for IRB approval, informed consent infrastructure, and organisational access), but it also means the reported performance (F1=0.889) cannot yet be claimed to reflect real-world behaviour. This is a deliberate, disclosed trade-off — not an oversight — appropriate for a desk-based BSc project, with the validity gap explicitly reserved for future real-deployment research.

> [!question] Is there a tension between "explainability" (SHAP) and "employee autonomy"? Could detailed explanations make employees feel more surveilled, not less?
> > [!success]- Answer
> > Genuine tension worth naming if asked: transparency is usually framed as empowering (employees understand *why* they were classified, and can act on it), but a very detailed behavioural explanation could also feel invasive — "the system knows I answer questions in under 10 seconds when overconfident" is informative but also uncomfortably specific. AHRID's mitigation is translating SHAP values into plain-language, actionable, developmental language ("your phishing accuracy is below the threshold — here's what to review") rather than exposing raw behavioural telemetry, but this is a genuine design tension rather than a fully solved problem.

> [!question] Does making training "adaptive" and "personalised" risk feeling like individualised profiling rather than support?
> > [!success]- Answer
> > Yes, and the mitigation is precisely the non-punitive governance model: personalisation is framed and technically implemented as *developmental* (more relevant training content) rather than *evaluative* (a score that follows you). The distinction between "profiling for support" and "profiling for judgement" is primarily enforced by what happens *downstream* of the classification — and AHRID's downstream action is always training content, never a performance record.

---

## 6. Stakeholder Impact — Think Beyond "the Employee"

> [!question] Who are all the stakeholders affected by AHRID, and how does each one's interest get protected?
> > [!success]- Answer
> > - **Employees:** protected via data minimisation, consent, SHAP transparency, and non-punitive framing.
> > - **Managers:** given useful aggregate insight without individual surveillance capability — protects them too, since they're never put in a position to (mis)use granular personal data they shouldn't have.
> > - **The organisation (SME):** benefits from improved awareness at near-zero cost, but bears responsibility for organisational policy that reinforces (not undermines) the technical non-punitive design.
> > - **Nepali regulatory environment:** AHRID is designed to model what responsible AI deployment under IPA 2075 could look like — a kind of reference implementation, not just a one-off product.
> > - **Future researchers:** benefit from a documented, ethically-reasoned architecture pattern (OSINT + XAI + privacy-by-design) that could be reused or critiqued in future developing-economy cybersecurity research.

---

## 7. If the Exam Asks You to Choose: Ethics vs Technical Depth

> [!tip] Answer strategy under time pressure
> If a question could be answered either technically or ethically (e.g. "why did you use SHAP?"), **lead with the ethical justification** (right to explanation, IPA 2075, employee autonomy) and use the technical detail (TreeExplainer, exact Shapley values) as *supporting evidence*, not the headline. This matches the signal that ethics is the priority axis for this exam.
