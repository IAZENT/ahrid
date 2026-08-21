# Research Methodology

> Maps to **Objective 4** (Design & Develop)

---

## Methodology Approach

### Design Science Research (DSR)
- Hevner et al. (2004) - Design Science in Information Systems Research
- Build an artifact (AHRID) → Evaluate → Contribute knowledge
- Iterative design-build-evaluate cycles

### Why DSR?
- The goal is to build and evaluate a system, not just observe phenomena
- DSR is the standard methodology for IS/CS system-building theses
- Maps naturally to: Design → Develop → Evaluate → Document

## Data Collection
- **Scenarios:** 450 hand-crafted, length-balanced training scenarios across 8 categories
- **Synthetic Users:** 1,050 users across 5 risk profiles for ML training
- **OSINT Data:** Live feeds from AlienVault OTX, Phishing.Database

## Evaluation Framework
| Metric | Target | Achieved |
|--------|--------|----------|
| RF Accuracy | > 80% | 91.4% |
| F1 Score | > 0.80 | 0.89 |
| PR-AUC | > 0.85 | 0.92 |
| Cohen's Kappa | > 0.80 | 0.875 |
| F1 Gap over Baseline | > 15 pts | 52.2 pts |

## Notes
- 
