# System Architecture

> High-level overview of AHRID's architecture before diving into details.

---

## Architecture Diagram
<!-- Insert or link your architecture diagram here -->

## Stack Summary
| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, TypeScript, Tailwind CSS v4, Recharts, Framer Motion |
| **Backend** | Python 3.11, Flask 3, PostgreSQL (prod) / SQLite (dev) |
| **ML Pipeline** | scikit-learn (Random Forest, K-Means), SMOTE, SHAP |
| **OSINT Feeds** | AlienVault OTX, Phishing.Database |
| **Infrastructure** | Supabase (DB), Render (API), Vercel (frontend) |

## Key Components
1. **Scenario Engine** - 450 hand-crafted scenarios across 8 categories
2. **Risk Scoring** - 14-feature Random Forest classifier (91.4% accuracy)
3. **Behavioral Clustering** - K-Means (5 clusters)
4. **Explainability** - SHAP value generation per prediction
5. **Adaptive Engine** - Adjusts scenario difficulty based on user performance
6. **OSINT Integration** - Live phishing URL ingestion via APScheduler

## Notes
- 
