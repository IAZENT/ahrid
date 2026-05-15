#!/usr/bin/env bash
# AHRID one-command cold-start bootstrap.
#
# Brings a fresh checkout from "git clone" → "fully demoable system" with one
# command. Idempotent: safe to re-run any time.
#
# Steps performed (in order):
#   1.  Sanity check the Python environment.
#   2.  Apply alembic migrations (creates / upgrades the SQLite schema).
#   3.  Seed the demo organisation, scenarios, and admin user (`seed.py`).
#   4.  Seed synthetic ML bootstrap data (`seed_ml_data.py`).
#   5.  Run the threat-feed and cyber-news ingestion pipelines once so the
#       admin and dashboard pages have content to display.
#   6.  Train the Random Forest + KMeans models and persist metrics.json.
#
# Run from the project root or the backend directory:
#   $ ./backend/bootstrap.sh
#   $ cd backend && ./bootstrap.sh
#
# Environment variables honoured:
#   SKIP_INGESTION=1   skip step 5 (useful when offline)
#   SKIP_TRAIN=1       skip step 6
set -euo pipefail

# Resolve script dir so the script works from any cwd.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

# Colours for nicer output (degrades gracefully if not a TTY).
if [ -t 1 ]; then
    BOLD=$(tput bold) DIM=$(tput dim) GREEN=$(tput setaf 2)
    YELLOW=$(tput setaf 3) RED=$(tput setaf 1) RESET=$(tput sgr0)
else
    BOLD="" DIM="" GREEN="" YELLOW="" RED="" RESET=""
fi

step() { echo "${BOLD}→ $*${RESET}"; }
ok()   { echo "${GREEN}✓ $*${RESET}"; }
warn() { echo "${YELLOW}⚠ $*${RESET}"; }
die()  { echo "${RED}✗ $*${RESET}" >&2; exit 1; }

# ---------- 1. Python sanity ----------
step "Step 1/6: Python sanity check"
command -v python3 >/dev/null || die "python3 not found on PATH."
PY_VER=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
echo "  Python: $PY_VER"
if [ ! -d ".venv" ] && [ ! -n "${VIRTUAL_ENV:-}" ]; then
    warn "No .venv detected and VIRTUAL_ENV is empty. Continuing with system python3."
fi
ok "Python OK"

# ---------- 2. Migrations ----------
step "Step 2/6: Apply alembic migrations"
if [ -f "migrations/alembic.ini" ]; then
    flask --app app:create_app db upgrade || die "Alembic upgrade failed."
    ok "Migrations applied"
else
    warn "No migrations/alembic.ini — falling back to db.create_all() inside seed.py."
fi

# ---------- 3. Domain seed ----------
step "Step 3/6: Seed organisation, scenarios, and admin user"
python3 seed.py || die "seed.py failed."
ok "Domain seed complete"

# ---------- 4. ML bootstrap ----------
step "Step 4/6: Seed synthetic ML data (idempotent)"
python3 seed_ml_data.py || die "seed_ml_data.py failed."
ok "ML bootstrap data seeded"

# ---------- 5. OSINT + news ingestion ----------
if [ "${SKIP_INGESTION:-0}" = "1" ]; then
    warn "SKIP_INGESTION=1 — skipping threat + news fetch."
else
    step "Step 5/6: Run threat-feed + cyber-news ingestion (one-shot)"
    python3 - <<'PY' || warn "Ingestion had non-fatal errors (network?). Continuing."
from app import create_app
from app.services.threat_ingestion import ThreatIngestionService
from app.services.cyber_news_ingestion import ingest_news
app = create_app()
with app.app_context():
    print("  threat ingestion:", ThreatIngestionService().run_ingestion())
    print("  news ingestion  :", ingest_news())
PY
    ok "Ingestion complete (or skipped on error)"
fi

# ---------- 6. ML training ----------
if [ "${SKIP_TRAIN:-0}" = "1" ]; then
    warn "SKIP_TRAIN=1 — skipping ML model training."
else
    step "Step 6/6: Train Random Forest + KMeans (saves metrics.json)"
    python3 train_models.py || die "train_models.py failed."
    ok "ML models trained"
fi

echo
echo "${GREEN}${BOLD}════════════════════════════════════════════════════════${RESET}"
echo "${GREEN}${BOLD}  AHRID bootstrap complete.${RESET}"
echo "${GREEN}${BOLD}════════════════════════════════════════════════════════${RESET}"
echo
echo "  Next steps:"
echo "    1. Start backend : ${DIM}flask --app app:create_app run --debug${RESET}"
echo "    2. Start frontend: ${DIM}cd ../frontend && npm run dev${RESET}"
echo "    3. Visit         : ${DIM}http://localhost:5173${RESET}"
echo
echo "  Inspect ML metrics: ${DIM}cat backend/ml_models/rf_metrics.json${RESET}"
echo "                     ${DIM}cat backend/ml_models/kmeans_metrics.json${RESET}"
