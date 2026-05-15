# AHRIP v2  Adaptive Human Risk Intelligence Platform

A role-aware human-risk dashboard for security awareness training: phishing,
vishing, smishing, physical security, password hygiene, USB baiting, social
engineering, and data handling  with adaptive scenario selection, sentiment
analysis, Random Forest risk prediction, K-Means behavioural clustering, and
gamification.

## Stack
- **Backend:** Python 3.11 · Flask 3 · PostgreSQL · scikit-learn · APScheduler
- **Frontend:** React 18 · Vite · TypeScript · Tailwind CSS v4 · Recharts · Framer Motion
- **OSINT:** PhishTank · OpenPhish · AlienVault OTX · URLScan.io

## Repository Layout
```
backend/    Flask API, ML services, threat ingestion
frontend/   React + Vite SPA
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
python wsgi.py
```

### Frontend
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
