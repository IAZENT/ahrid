---
tags: [exam, ST6047CEM, AHRID, hub]
date: 2026-08-20
exam-date: 2026-08-23
---

# ST6047CEM Written Examination — Prep Hub

> [!danger] Exam Logistics
> - **Date:** Sunday, 23 August 2026
> - **Time:** likely 2–3 hours (notice said 09:00–11:00, but expect the real duration/format to allow substantial writing — confirm on the day)
> - **Report by:** 08:45 (mandatory, late = no entry)
> - **Venue:** Block E, A, or C — **check your room assignment on campus announcements**
> - **Format:** Written exam, essay-style — expect to produce roughly **~2000 words total** across a handful of substantial questions testing understanding of your submitted coursework and your ability to **justify design decisions** at length, not just state them

> [!bug]+ PRIORITY SIGNAL FROM TEACHER
> Recalled guidance: **focus on ethics over technical detail.** RQ2 is your ethical research question, and "ethical considerations and impact on stakeholders" is its own line in the marking rubric. Read [[07 - Ethics Deep Dive]] **first**, then [[09 - Ethics Approval Form (Primary Source)]] — the second one gives you exact, officially-filed wording you can quote verbatim, since your formal ethics application is now embedded in the thesis as Appendix E. When a question could go either technical or ethical, lead with the ethical justification and use technical detail as supporting evidence, not the headline.

> [!info] Content verified against your live thesis document
> All facts in this vault were cross-checked directly against `Coursework/Rupesh_Kumar_Thakur_230548.docx` (not just memory). Appendix ordering has changed since earlier drafts: **A** SWOT, **B** Roles & Responsibilities, **C** Budget, **D** Code Explanation File, **E** Ethical Form, **F** Gantt Chart, **G** ML Model Performance, **H** OSINT Pipeline, then API Reference / Glossary / GUI / DB Schema. If you cite an appendix letter in the exam, use this order.

## What this exam actually tests
Per the assignment brief and marking rubric, the exam maps directly onto:
1. **Clarity and completeness** — can you describe AHRID accurately without notes?
2. **Relevance of RQs/objectives** — can you connect every component back to RQ1/RQ2?
3. **Implementation of methodology** — can you justify *why*, not just *what*?
4. **Technical competence** — do you actually understand the ML/security internals, or did you just copy explanations?
5. **Writing quality** — even under exam pressure, structure your answers (claim → evidence → justification).

## How to use this vault section
Each note below uses **foldable callouts**. Click the arrow to reveal the answer — use this for active recall, not passive reading.

| Note | Covers | Priority |
|---|---|---|
| [[07 - Ethics Deep Dive]] | IPA 2075 in depth, AI4People framework, fairness, non-punitive governance mechanism, stakeholder impact, ethical trade-offs | 🔴 **Read first** |
| [[09 - Ethics Approval Form (Primary Source)]] | Exact official wording from your approved ethics application (thesis Appendix E) — quotable verbatim, strongest possible evidence | 🔴 **Read second** |
| [[08 - Full Essay Model Answers]] | 4 complete, exam-length (400–650 word) model essays showing what "thorough" actually looks like at this word count | 🔴 High |
| [[03 - Section C Critical Ethical]] | Examiner pushback scenarios — defending against skepticism, mostly ethics-flavoured | 🔴 High |
| [[02 - Section B Design Justification]] | "Why did you choose X over Y" — mix of technical and ethical; lead ethical where possible | 🟠 Medium |
| [[01 - Section A Short Answer]] | Facts, numbers, definitions — the stuff you must never fumble | 🟡 Baseline |
| [[04 - Numbers Cheat Sheet]] | Every metric, every count, in one glance-able table | 🟡 Baseline |
| [[06 - Extra Likely Questions]] | Broader question bank; includes a dedicated Compliance & Regulation section | 🟠 Medium |
| [[05 - Mock Exam Paper]] | The timed essay-format practice paper (~2000 words target) — do this under real conditions first | Use Day 1 |

## Suggested 3-day plan (ethics-weighted, essay-length)
- [ ] **Day 1 (today):** Read [[07 - Ethics Deep Dive]] slowly, then [[08 - Full Essay Model Answers]] to see the target length/structure. Attempt [[05 - Mock Exam Paper]] cold, timed for 2–3 hours, aiming for ~2000 words total — notice whether your essays lead with ethics and include an honest limitation.
- [ ] **Day 1 evening:** Mark your mock essays against [[08 - Full Essay Model Answers]] directly (same question numbers). Check: did you concede before defending in Section C? Did every essay tie back to RQ1/RQ2 in its closing line?
- [ ] **Day 2:** Re-drill [[07 - Ethics Deep Dive]] until you can reconstruct the IPA 2075 table from memory and expand each row into 2–3 sentences unprompted. Then [[01 - Section A Short Answer]] and [[04 - Numbers Cheat Sheet]] for baseline facts you'll weave into essays as evidence.
- [ ] **Day 2 evening:** Rewrite one essay from [[08 - Full Essay Model Answers]] in your own words from memory, timed to ~10 minutes per 100 words, to build writing speed at exam pace.
- [ ] **Day 3 (day before):** Light review only. Re-read [[07 - Ethics Deep Dive]] and skim [[08 - Full Essay Model Answers]] once more. Sleep well. Confirm your room assignment and actual exam duration.

## Golden rule for written exam answers
> [!tip] Structure every answer as: **Claim → Evidence (a real number or mechanism) → Justification (why this beats the alternative)**
> Weak answer: *"I used Random Forest because it's accurate and interpretable."*
> Strong answer: *"I used Random Forest because it natively supports SHAP TreeExplainer for exact, fast explainability, which XGBoost and deep learning would require approximation for; it achieved macro F1 = 0.889, and my dataset size (1,050 synthetic profiles) doesn't justify a deep learning approach that needs far more data to avoid overfitting."*
