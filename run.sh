#!/usr/bin/env bash
set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║         ComplianceHub — Launch Script           ║${NC}"
echo -e "${BOLD}${GREEN}║     Audit & Compliance Document Generator       ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# ── Step 1: Clean up any old servers ──────────────────────────────────────
echo -e "${YELLOW}[1/4] Stopping any old servers...${NC}"
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true
sleep 1
echo "  Done"

# ── Step 2: Start backend ──────────────────────────────────────────────────
echo -e "${YELLOW}[2/4] Starting backend on http://localhost:8000 ...${NC}"
cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level warning &
BACKEND_PID=$!
sleep 2

if kill -0 $BACKEND_PID 2>/dev/null; then
  echo -e "  ${GREEN}✓ Backend running (PID $BACKEND_PID)${NC}"
else
  echo -e "  ${BOLD}❌ Backend failed to start. Check port 8000.${NC}"
  exit 1
fi

# ── Step 3: Start frontend ─────────────────────────────────────────────────
echo -e "${YELLOW}[3/4] Starting frontend on http://localhost:5173 ...${NC}"
cd "$FRONTEND_DIR"
npx vite --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
sleep 3
echo -e "  ${GREEN}✓ Frontend running (PID $FRONTEND_PID)${NC}"

# ── Step 4: Done ──────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║  🚀 ComplianceHub is ready!                     ║${NC}"
echo -e "${BOLD}${GREEN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
echo -e "${BOLD}${GREEN}║  Open in your browser:                          ║${NC}"
echo -e "${BOLD}${GREEN}║  ${CYAN}http://localhost:5173${GREEN}                     ║${NC}"
echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
echo -e "${BOLD}${GREEN}║  Dashboard → Audit Generator                    ║${NC}"
echo -e "${BOLD}${GREEN}║  1. Select ISO standard(s)                      ║${NC}"
echo -e "${BOLD}${GREEN}║  2. Upload audit notes (.docx or .txt)          ║${NC}"
echo -e "${BOLD}${GREEN}║  3. Upload Manday calculation (.docx)           ║${NC}"
echo -e "${BOLD}${GREEN}║  4. Enter your API key                          ║${NC}"
echo -e "${BOLD}${GREEN}║  5. Click Generate                              ║${NC}"
echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
echo -e "${BOLD}${GREEN}║  Press Ctrl+C to stop all servers               ║${NC}"
echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ── Trap Ctrl+C to clean up ───────────────────────────────────────────────
cleanup() {
  echo ""
  echo -e "${YELLOW}Shutting down...${NC}"
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  echo -e "${GREEN}Servers stopped. Goodbye!${NC}"
  exit 0
}
trap cleanup SIGINT SIGTERM

# ── Keep running until Ctrl+C ──────────────────────────────────────────────
wait
