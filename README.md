# AHRID - Adaptive Human Risk Intelligence Dashboard

A role-aware human-risk dashboard for cybersecurity awareness training across
8 categories (phishing, vishing, smishing, physical security, password hygiene,
USB baiting, social engineering, data handling) with adaptive scenario selection,
Random Forest risk prediction (91.4% accuracy), K-Means behavioural clustering,
and SHAP explainability.

## Key Numbers
- **450** hand-crafted, length-balanced training scenarios
- **91.4%** RF accuracy · **0.89** F1 · **0.92** PR-AUC · **0.875** Cohen's Kappa
- **52.2** F1-point gap over rule-based baseline (hypothesis target: 15)
- **1,050** synthetic users across 5 risk profiles for ML training

## Stack
- **Backend:** Python 3.11 · Flask 3 · PostgreSQL · scikit-learn · APScheduler
- **Frontend:** React 18 · Vite · TypeScript · Tailwind CSS v4 · Recharts · Framer Motion
- **ML:** Random Forest (14 features) · K-Means (5 clusters) · SMOTE · SHAP
- **OSINT:** Phishing.Database · AlienVault OTX · Phishing.Database · Phishing.Database
- **Infra:** Supabase (DB) · Render (API) · Vercel (frontend)

## Repository Layout
```
backend/              Flask API, ML services, threat ingestion
frontend/             React + Vite SPA
ML_Learning_Guide/    Defense prep & ML concept guides (16 chapters)
ML_Sandbox/           Standalone ML training pipeline scripts
Formal_Document/      Thesis DOCX and proposal PDF
docs/
  ├── build_prompts/  AI-assistant build specifications
  ├── planning/       Feature lists, progress, backlogs, bug trackers
  ├── design_thinking/ Design thinking deliverables & analysis
  └── thesis_report/  Main system report (REPORT.md)
credentials/          Secrets & user credentials (gitignored)
```

## Local Setup

### Backend
```bash
cd backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # fill in secrets
python -m textblob.download_corpora   # one-time
flask --app wsgi:app db upgrade
python seed_scenarios.py              # 450 scenarios
python seed_synthetic_ml_data.py      # 1,050 users + attempts
python train_models.py                # RF + KMeans
python wsgi.py
```

### Frontend
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```