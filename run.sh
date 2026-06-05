#!/usr/bin/env bash
set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║         ComplianceHub — Launch Script           ║${NC}"
echo -e "${BOLD}${GREEN}║     Audit & Compliance Document Generator       ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
MODEL_DIR="$ROOT_DIR/models"
LOCAL_AI_PORT=8080

# ── Parse args ─────────────────────────────────────────────────────────────
START_LOCAL=false
for arg in "$@"; do
  case "$arg" in
    --local-ai) START_LOCAL=true ;;
  esac
done

# ── Step 1: Clean up old servers ──────────────────────────────────────────
echo -e "${YELLOW}[1/4] Stopping old servers...${NC}"
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true
fuser -k $LOCAL_AI_PORT/tcp 2>/dev/null || true
sleep 1
echo -e "  Done"

# ── Step 2 (optional): Start local AI server ──────────────────────────────
LOCAL_AI_PID=""
if [ "$START_LOCAL" = true ]; then
  if [ -f "$MODEL_DIR/qwen-1.5b.gguf" ]; then
    echo -e "${YELLOW}[2/4] Starting local AI model on port $LOCAL_AI_PORT ...${NC}"
    MODEL="$MODEL_DIR/qwen-1.5b.gguf"
  elif [ -f "$MODEL_DIR/qwen-0.5b.gguf" ]; then
    echo -e "${YELLOW}[2/4] Starting local AI model on port $LOCAL_AI_PORT ...${NC}"
    MODEL="$MODEL_DIR/qwen-0.5b.gguf"
  else
    echo -e "  ${YELLOW}No model found in $MODEL_DIR. Skipping local AI.${NC}"
    echo -e "  ${YELLOW}Download one: curl -L -o $MODEL_DIR/qwen-1.5b.gguf <url>${NC}"
  fi

  if [ -n "$MODEL" ]; then
    /opt/llama-server/llama-server \
      -m "$MODEL" -c 4096 -t 8 --host 0.0.0.0 --port $LOCAL_AI_PORT --temp 0.3 \
      > /tmp/llama-server.log 2>&1 &
    LOCAL_AI_PID=$!
    sleep 2
    echo -e "  ${GREEN}✓ Local AI starting (PID $LOCAL_AI_PID)${NC}"
  fi
else
  echo -e "${YELLOW}[2/4] Local AI: disabled (use --local-ai to enable)${NC}"
fi

# ── Step 3: Start backend ──────────────────────────────────────────────────
echo -e "${YELLOW}[3/4] Starting backend on http://localhost:8000 ...${NC}"
cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level warning &
BACKEND_PID=$!
sleep 2

if kill -0 $BACKEND_PID 2>/dev/null; then
  echo -e "  ${GREEN}✓ Backend running (PID $BACKEND_PID)${NC}"
else
  echo -e "  ${BOLD}❌ Backend failed to start. Check port 8000.${NC}"
  [ -n "$LOCAL_AI_PID" ] && kill $LOCAL_AI_PID 2>/dev/null || true
  exit 1
fi

# ── Step 4: Start frontend ─────────────────────────────────────────────────
echo -e "${YELLOW}[4/4] Starting frontend on http://localhost:5173 ...${NC}"
cd "$FRONTEND_DIR"
npx vite --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
sleep 3
echo -e "  ${GREEN}✓ Frontend running (PID $FRONTEND_PID)${NC}"

# ── Done ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║  🚀 ComplianceHub is ready!                     ║${NC}"
echo -e "${BOLD}${GREEN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
echo -e "${BOLD}${GREEN}║  ${CYAN}http://localhost:5173${GREEN}                     ║${NC}"
echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
echo -e "${BOLD}${GREEN}║  Content modes:                                  ║${NC}"
echo -e "${BOLD}${GREEN}║  • Offline (default): no API key needed         ║${NC}"
echo -e "${BOLD}${GREEN}║  • Local AI: run with --local-ai                ║${NC}"
echo -e "${BOLD}${GREEN}║  • Cloud AI: enter Gemini/OpenAI key in UI      ║${NC}"
echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
echo -e "${BOLD}${GREEN}║  Press Ctrl+C to stop all servers               ║${NC}"
echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ── Trap ───────────────────────────────────────────────────────────────────
cleanup() {
  echo ""
  echo -e "${YELLOW}Shutting down...${NC}"
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  [ -n "$LOCAL_AI_PID" ] && kill $LOCAL_AI_PID 2>/dev/null || true
  echo -e "${GREEN}Servers stopped.${NC}"
  exit 0
}
trap cleanup SIGINT SIGTERM

wait
