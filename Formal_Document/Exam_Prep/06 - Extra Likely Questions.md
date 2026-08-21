---
tags: [exam, ST6047CEM, AHRID, extra-questions]
---

# Extra Likely Questions

Related: [[00 - Exam Prep Hub]]

Pulled from common capstone/viva written-exam patterns (general project overview, literature justification, scalability, limitations, individual contribution) layered onto AHRID's actual content. Use this after you've drilled Sections A–C.

## General Project Overview

> [!question] "Summarise your project in under 2 minutes of writing."
> > [!success]- Answer
> > AHRID is an adaptive cybersecurity awareness platform for non-technical SME employees in Kathmandu Valley, Nepal. It integrates live OSINT phishing intelligence (Phishing.Database, AlienVault OTX), a three-stage ML pipeline (K-Means behavioural clustering → Random Forest risk classification → SHAP explainability), and adaptive spaced-repetition training. Built using Design Science Research over 15 Agile sprints, it addresses two questions: RQ1 (can this architecture outperform a rule-based baseline? — yes, F1 0.889 vs 0.387) and RQ2 (can it comply with Nepal's IPA 2075 while remaining ethical? — yes, via privacy-by-design and non-punitive governance).

> [!question] "What existing system/approach does AHRID improve on, and how?"
> > [!success]- Answer
> > Commercial platforms (KnowBe4, CybSafe, Proofpoint) assume enterprise budgets, dedicated security teams, and mature governance — none hold for resource-constrained Nepali SMEs. They also rely on opaque, proprietary risk scoring with no explainability. AHRID replaces static, generic training with adaptive, explainable, OSINT-grounded, non-punitive training at effectively zero licensing cost.

> [!question] "What was your individual role and contribution?" *(relevant since this is a solo BSc project)*
> > [!success]- Answer
> > Sole researcher and developer across the entire pipeline: requirements analysis, literature review, system architecture, full-stack implementation (Flask backend, React frontend, PostgreSQL), OSINT pipeline, ML model design/training (K-Means, Random Forest, SHAP integration), evaluation, and ethical compliance verification — all under supervisor (Manoj Shrestha) guidance across 15 sprints.

## Literature & Theory

> [!question] "Which behavioural theories inform your training design, and how, specifically?"
> > [!success]- Answer
> > - **Protection Motivation Theory** (Rogers, 1975/1983): threat appraisal via live OSINT phishing scenarios + personalised risk scores; coping appraisal via SHAP-guided actionable feedback.
> > - **Prospect Theory** (Kahneman & Tversky, 1979): scenarios frame consequences as losses (data breach, credential theft) since loss framing produces stronger behavioural response than gain framing.
> > - **Technology Acceptance Model** (Davis, 1989): SHAP explanations target perceived usefulness; simple UI targets perceived ease of use.
> > - **Compliance Budget** (Beautement et al., 2008): adaptive difficulty prevents cognitive overload by only surfacing role-relevant scenarios, respecting employees' limited security-task bandwidth.

> [!question] "What is the single biggest gap in the literature your project fills?"
> > [!success]- Answer
> > No identified system combines OSINT-driven live threat content, unsupervised behavioural clustering + supervised risk classification, SHAP-based explainability, and privacy-by-design specifically calibrated for a developing-economy SME context — each component is validated individually in prior work, but not integrated together for this population.

## Scalability & Generalisability

> [!question] "Would AHRID scale to a 500-employee organisation?"
> > [!success]- Answer
> > Architecturally yes — Flask + Gunicorn multi-worker + PostgreSQL scale well beyond SME size; RF/SHAP inference cost is per-request and modest. The bigger open question is **behavioural generalisability**, not infrastructure: the model was calibrated on SME-scale synthetic data, so retraining/revalidation would be needed before trusting predictions at a different organisational scale or culture.

> [!question] "Would your findings generalise outside Kathmandu Valley?"
> > [!success]- Answer
> > Not without further validation — explicitly out of scope. Regional expansion to other parts of Nepal and South Asia is listed as future work, since behavioural archetypes and threat patterns may shift with different regulatory, linguistic, and organisational contexts.

## Limitations & Future Work

> [!question] "What is the single most important next step if you continued this research?"
> > [!success]- Answer
> > A real-world pilot deployment with a consenting Kathmandu Valley SME — collecting real (not synthetic) behavioural data under proper ethics approval, to validate whether the archetypes and reported classification performance hold outside controlled synthetic conditions.

> [!question] "Name three limitations you'd tell an examiner unprompted."
> > [!success]- Answer
> > 1. Synthetic-only evaluation — no real employee data or deployment.
> > 2. Moderate silhouette score (~0.2645) reflecting inherent overlap in behavioural clusters.
> > 3. No longitudinal study — can't yet show sustained behavioural change over months, only point-in-time classification performance.

> [!question] "What would you do differently if starting over?"
> > [!success]- Answer
> > Two honest options: (a) formalise adversarial/gaming-resistance testing earlier rather than as a noted future-work gap, or (b) begin ethics-approval conversations in parallel from sprint 1 in case a real-SME partnership became feasible later in the project — currently the desk-based/synthetic decision was made early and irreversibly.

## Compliance & Regulation

> [!question] "Besides IPA 2075, are there other regulatory frameworks relevant to AHRID?"
> > [!success]- Answer
> > Article 28 of the Constitution of Nepal (privacy as a fundamental right) underpins IPA 2075. GDPR is referenced conceptually (transparency/explainability principles) even though it isn't the binding jurisdiction, since AHRID's SHAP-based approach aligns with the "right to explanation" spirit found in GDPR-adjacent frameworks — useful if the platform were ever adapted for a jurisdiction with stricter automated-decision rules.

> [!question] "How would you evaluate success if you deployed this for real?"
> > [!success]- Answer
> > Beyond the technical metrics already reported, real deployment would add: reduction in actual phishing click-through rate over time, SUS (System Usability Scale) scores from real users (designed but not yet administered), and longitudinal retention of security behaviour measured across repeated training cycles — none of which synthetic evaluation can provide.
