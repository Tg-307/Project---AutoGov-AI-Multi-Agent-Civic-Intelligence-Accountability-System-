#!/usr/bin/env bash
# AutoGov AI — Setup & Run Script
set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   AutoGov AI — Setup & Launch        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# 1. Install deps
echo "[1/4] Installing dependencies..."
pip install -r requirements.txt -q

# 2. Migrations
echo "[2/4] Running database migrations..."
python manage.py migrate --run-syncdb 2>&1 | grep -v "^$"

# 3. Seed departments
echo "[3/4] Seeding departments..."
python manage.py seed_departments

# 4. Start server
echo ""
echo "[4/4] Starting server at http://127.0.0.1:8000"
echo "      Press Ctrl+C to stop."
echo ""
python manage.py runserver 127.0.0.1:8000
