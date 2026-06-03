#!/usr/bin/env bash
set -e

echo "============================================"
echo "  ComplianceHub"
echo "  Audit & Compliance Platform"
echo "============================================"
echo ""

DIR="$(cd "$(dirname "$0")" && pwd)"

# Backend setup
echo "[1/3] Setting up Python backend..."
cd "$DIR/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# Frontend setup
echo "[2/3] Setting up React frontend..."
cd "$DIR/frontend"
npm install --silent 2>/dev/null

# Start services
echo "[3/3] Starting services..."
echo ""

# Start backend
cd "$DIR/backend"
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
