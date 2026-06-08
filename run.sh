#!/usr/bin/env bash
set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
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
LOCAL_MODEL_NAME=""

for arg in "$@"; do
  case "$arg" in
    --local-ai)
      START_LOCAL=true
      LOCAL_MODEL_NAME=""
      ;;
    --local-model=*)
      START_LOCAL=true
      LOCAL_MODEL_NAME="${arg#*=}"
      ;;
    --no-local-ai)
      START_LOCAL=false
      LOCAL_MODEL_NAME=""
      ;;
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
  if [ -n "$LOCAL_MODEL_NAME" ]; then
    MODEL="$MODEL_DIR/$LOCAL_MODEL_NAME.gguf"
  else
    # Auto-detect: prefer qwen-0.5b (only model that's fast enough on CPU ARM)
    if [ -f "$MODEL_DIR/qwen-0.5b.gguf" ]; then
      MODEL="$MODEL_DIR/qwen-0.5b.gguf"
      echo -e "  ${CYAN}Auto-selected: qwen-0.5b (~20s/doc)${NC}"
    fi
  fi

  if [ -z "$MODEL" ] || [ ! -f "$MODEL" ]; then
    model_name="${LOCAL_MODEL_NAME:-qwen-0.5b}"
    echo -e "  ${YELLOW}Model not found: $MODEL_DIR/$model_name.gguf${NC}"
    echo -e "  ${YELLOW}Available models:${NC}"
    if ls "$MODEL_DIR"/*.gguf >/dev/null 2>&1; then
      ls -1 "$MODEL_DIR"/*.gguf | sed 's/^/  /'
    else
      echo "  (none)"
    fi
    echo -e "  ${YELLOW}Skipping local AI.${NC}"
  else
    echo -e "${YELLOW}[2/4] Starting local AI on port $LOCAL_AI_PORT ...${NC}"
    MODEL_NAME="$(basename "$MODEL")"
    echo -e "  Model: $MODEL_NAME ($(du -h "$MODEL" | cut -f1))"
    /opt/llama-server/llama-server \
      -m "$MODEL" -c 4096 -t 4 -b 2048 --mlock \
      --host 0.0.0.0 --port $LOCAL_AI_PORT --temp 0.3 \
      > /tmp/llama-server.log 2>&1 &
    LOCAL_AI_PID=$!
    sleep 2

    # Readiness check: poll /health up to 3 times (5s timeout each)
    READY=false
    for i in 1 2 3; do
      if curl -sf http://127.0.0.1:$LOCAL_AI_PORT/health > /dev/null 2>&1; then
        READY=true
        break
      fi
      echo -e "  Waiting for model to load... (attempt $i/3)"
      sleep 3
    done

    if [ "$READY" = true ]; then
      echo -e "  ${GREEN}✓ Local AI ready (PID $LOCAL_AI_PID)${NC}"
    else
      echo -e "  ${RED}✗ Local AI failed to respond. Check /tmp/llama-server.log${NC}"
    fi
  fi
else
  echo -e "${YELLOW}[2/4] Local AI: disabled (use --local-ai or --local-model=<name>)${NC}"
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
echo -e "${BOLD}${GREEN}║  • Local AI: --local-model=<name>               ║${NC}"
echo -e "${BOLD}${GREEN}║  • Cloud AI: enter Gemini/OpenAI key in UI      ║${NC}"
if grep -q "^HF_API_KEY=hf_" backend/.env 2>/dev/null; then
  echo -e "${BOLD}${GREEN}║  • HF Free Tier: active (Llama-3-8B via API)    ║${NC}"
fi
echo -e "${BOLD}${GREEN}║                                                  ║${NC}"
echo -e "${BOLD}${GREEN}║  Models:                                         ║${NC}"
if ls "$MODEL_DIR"/*.gguf >/dev/null 2>&1; then
  for m in "$MODEL_DIR"/*.gguf; do
    name="$(basename "$m")"
    size="$(du -h "$m" | cut -f1)"
    echo -e "${BOLD}${GREEN}║    $name ($size)              ║${NC}"
  done
fi
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
