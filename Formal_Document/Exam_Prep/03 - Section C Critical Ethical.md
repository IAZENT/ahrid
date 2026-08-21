---
tags: [exam, ST6047CEM, AHRID, ethics, critical]
---

# Section C — Critical / Ethical Pushback Question Bank

Related: [[00 - Exam Prep Hub]] | [[02 - Section B Design Justification]]

> [!tip] These simulate an examiner actively trying to poke holes. Never get defensive — acknowledge the valid part of the criticism, then show the specific evidence that limits its force.

> [!question] C1. "This is still workplace surveillance regardless of your intentions. How is AHRID different from a system that punishes low performers?"
> > [!success]- Answer
> > - **Concede the surface concern:** yes, any behavioural-monitoring system carries surveillance risk in principle — that's why governance was treated as an architectural requirement, not an afterthought.
> > - **RBAC evidence:** managers see only aggregate team metrics; individual SHAP explanations are visible only to the employee and admins for audit, never routed into a performance-management workflow.
> > - **Workflow evidence:** elevated risk triggers *additional adaptive training content*, not a flag in any HR-adjacent data structure — there is no code path connecting a risk score to disciplinary action.
> > - **Honest limit:** technical controls cannot fully prevent a *determined, malicious* admin from misusing the platform. This is explicitly acknowledged as a limitation — the answer is architectural safeguard *plus* organisational policy, not architecture alone.

> [!question] C2. "You report 90.95% accuracy and claim this shows AHRID improves cybersecurity awareness. But you never measured awareness in a real person — isn't that an overstatement?"
> > [!success]- Answer
> > - **Separate what was measured from what wasn't, explicitly.** Measured: classification accuracy, macro F1, PR-AUC, Cohen's κ, per-class precision/recall, on a held-out **synthetic** test set — this demonstrates the *architecture's technical capability*, i.e. RQ1's answer.
> > - **Not measured:** real employee behavioural change, real-world phishing susceptibility reduction, long-term retention. These require live deployment, explicitly reserved for Future Work.
> > - The thesis's own conclusion is careful to frame results as "technical feasibility and effectiveness of the proposed approach," not as a demonstrated real-world behavioural outcome — this distinction is what makes the claim scientifically defensible rather than an overstatement.
> > - If pressed further: "Claiming operational impact from synthetic-data evaluation would be the overstatement I'm avoiding — that's precisely why real-world deployment is Future Work Priority #1, not a completed claim."

> [!question] C3. "Your synthetic data was calibrated by you. Isn't that circular — you designed the test to pass?"
> > [!success]- Answer
> > - Calibration used **external, independently-published sources** (Nepal Police Cyber Bureau statistics, international breach reports like Verizon DBIR), not parameters tuned to guarantee a target F1 score.
> > - The **rule-based baseline was evaluated on the identical dataset** — if the data were rigged to flatter the Random Forest specifically, the baseline's poor performance (F1=0.3868) wouldn't be explainable, since both models see the same data.
> > - 3-fold cross-validation (std=0.0094) shows performance is *stable across different data partitions*, which would be unlikely if results depended on one lucky calibration.

> [!question] C4. "Why should we trust SHAP explanations shown to non-technical employees? Couldn't they be misleading or manipulated?"
> > [!success]- Answer
> > - TreeExplainer computes **exact** Shapley values for tree ensembles — not an approximation, so there's no "gaming" risk from sampling variance the way there can be with KernelSHAP on black-box models.
> > - Explanations are translated into **plain-language labels** (e.g. "your phishing accuracy is below threshold") rather than raw numeric SHAP values, reducing the risk of misinterpretation by non-technical users — though this translation step is itself a design choice that trades some mathematical precision for comprehensibility, which is an honest trade-off, not a flaw to hide.
> > - Genuine limitation: SHAP values reflect **correlation-based** feature contribution within the trained model, not causal truth about the employee's actual security posture — worth stating proactively if asked "does this prove causation?"

> [!question] C5. "You claim IPA 2075 compliance, but you're not a legal expert. How can you be sure?"
> > [!success]- Answer
> > - The claim is **architectural alignment** with the four principles most relevant to a behavioural ML system — purpose limitation, data minimisation, right to information, informed consent — verified via a compliance matrix mapping each principle to a specific technical control, not a formal legal certification.
> > - This is explicitly framed as compliance **by design**, i.e. built to satisfy the principle, not a claim of formal legal sign-off — which is appropriate scope for a BSc technical project.
> > - The thesis also states that IPA 2075 alignment "provides an important legal foundation but should not be interpreted as sufficient for long-term AI governance" — showing awareness of the limits of a technical-only compliance claim.

> [!question] C6. "Nepal Police statistics and international breach reports come from very different contexts. Isn't your calibration inconsistent?"
> > [!success]- Answer
> > - Nepal Police Cyber Bureau data grounds the **incident volume and category distribution** (e.g. financial fraud share) specific to the Nepali threat landscape, while international breach reports (Verizon DBIR etc.) inform **generalisable behavioural patterns** (e.g. the well-established finding that human error accounts for the majority of breaches) that aren't Nepal-specific by nature.
> > - The two sources are used for **different parameters**, not blended into a single number — local data anchors the local context claims, general research anchors the general ML-design assumptions.
> > - Acknowledged limitation: without a real Nepali SME dataset, some behavioural assumptions inevitably borrow from non-Nepali literature — this is exactly why real deployment validation is future work.

> [!question] C7. "What stops an employee from gaming the system — e.g., deliberately answering slowly to appear more 'cautious'?"
> > [!success]- Answer
> > - Genuine, currently-unaddressed limitation — worth naming directly rather than deflecting.
> > - The adaptive mastery/forgetting-curve mechanism uses **recency-weighted accuracy over many attempts** (not a single session), making short-term gaming less impactful than sustained behaviour.
> > - This is a legitimate direction for future work: anomaly detection on suspiciously "too-perfect" behavioural patterns, or triangulating self-reported behaviour against harder-to-game signals.

> [!question] C8. "If this were deployed tomorrow in a real SME, what's the single biggest risk?"
> > [!success]- Answer
> > - **Distribution shift:** real employee behaviour may not match the statistically calibrated synthetic distributions the model was trained on, meaning reported performance (F1=0.889) could be optimistic for real deployment until re-validated on real data.
> > - Directly connects to why the **first priority in Future Work** is a real-SME pilot with consenting employees — this isn't a hypothetical risk, it's the explicit next research step.
