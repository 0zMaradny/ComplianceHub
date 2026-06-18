#!/usr/bin/env bash
set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_DIR="$ROOT_DIR/backend"
PID_DIR="/tmp/compliancehub-pids"
URL_FILE="/tmp/compliancehub-url.txt"
PERSISTENT_URL_FILE="$ROOT_DIR/.tunnel-url"
GIT_URL_FILE="$ROOT_DIR/Osama/.tunnel-url"
mkdir -p "$PID_DIR"

START_AI=false
TUNNEL_MODE="auto"
SERVEO_SUBDOMAIN=""

for arg in "$@"; do
  case "$arg" in
    --ai|--local-ai) START_AI=true ;;
    --tunnel=cloudflare|--cloudflare) TUNNEL_MODE="cloudflare" ;;
    --tunnel=serveo|--serveo) TUNNEL_MODE="serveo" ;;
    --tunnel=auto) TUNNEL_MODE="auto" ;;
    --tunnel=none|--no-tunnel) TUNNEL_MODE="none" ;;
    --serveo-subdomain=*) SERVEO_SUBDOMAIN="${arg#*=}" ;;
    --help|-h)
      echo "Usage: ./go.sh [--ai] [--cloudflare|--serveo|--auto|--no-tunnel] [--serveo-subdomain=NAME]"
      echo "  Default: auto (Cloudflare with Serveo fallback), no local AI"
      echo "  --ai                    Start local AI"
      echo "  --cloudflare            Cloudflare tunnel only (no fallback)"
      echo "  --serveo                Serveo tunnel only (no fallback)"
      echo "  --auto                  Cloudflare → Serveo → loop (default)"
      echo "  --no-tunnel             Local access only"
      exit 0 ;;
  esac
done

# ── Git sync helpers ──
GIT_REMOTE="origin"
GIT_BRANCH="main"

git_sync_pull() {
  local stash_msg=""
  # Stash any local changes before pull
  if ! git -C "$ROOT_DIR" diff --quiet 2>/dev/null; then
    stash_msg=$(git -C "$ROOT_DIR" stash push -m "auto-stash before sync $(date +%s)" 2>&1)
  fi
  git -C "$ROOT_DIR" pull --rebase "$GIT_REMOTE" "$GIT_BRANCH" 2>/dev/null || echo -e "  ${YELLOW}⚠ git pull failed (no remote or offline)${NC}"
  # Pop stash if we stashed
  if [ -n "$stash_msg" ] && echo "$stash_msg" | grep -q "Saved"; then
    git -C "$ROOT_DIR" stash pop 2>/dev/null || true
  fi
}

git_sync_push() {
  local message="$1"
  shift
  if [ $# -ge 1 ]; then
    git -C "$ROOT_DIR" add "$@" 2>/dev/null
  fi
  if ! git -C "$ROOT_DIR" diff --cached --quiet 2>/dev/null; then
    git -C "$ROOT_DIR" commit -m "$message" 2>/dev/null || true
    git -C "$ROOT_DIR" push "$GIT_REMOTE" "$GIT_BRANCH" 2>/dev/null || echo -e "  ${YELLOW}⚠ git push failed${NC}"
  fi
}

git_sync_tunnel_url() {
  if [ -n "$1" ]; then
    echo "$1" > "$GIT_URL_FILE"
    git_sync_push "sync: tunnel URL" "$GIT_URL_FILE"
  fi
}

git_sync_exit() {
  local changed=false
  if ! git -C "$ROOT_DIR" diff --quiet -- "Osama/MEMORY.md" 2>/dev/null; then
    git_sync_push "sync: MEMORY.md" "Osama/MEMORY.md"
    changed=true
  fi
  if ! git -C "$ROOT_DIR" diff --quiet -- "$GIT_URL_FILE" 2>/dev/null; then
    git_sync_push "sync: tunnel URL" "$GIT_URL_FILE"
    changed=true
  fi
  if [ "$changed" = true ]; then
    echo -e "  ${GREEN}✓ Changes synced to git${NC}"
  fi
}

# ── Auto-sync on start ──
echo -e "${CYAN}Syncing from git...${NC}"
git_sync_pull
# Restore device-specific opencode.json if template exists
if [ -f "$ROOT_DIR/opencode.json.template" ] && [ ! -f "$ROOT_DIR/opencode.json" ]; then
  cp "$ROOT_DIR/opencode.json.template" "$ROOT_DIR/opencode.json"
  echo -e "  ${GREEN}✓ Created opencode.json from template${NC}"
fi
echo -e "  ${GREEN}✓ Git sync complete${NC}"
echo ""

# ── Disk audit pre-flight ──
if [ -f "$ROOT_DIR/audit-disk.sh" ]; then
  "$ROOT_DIR/audit-disk.sh"
fi
echo ""

cleanup_all() {
  echo ""
  echo -e "${YELLOW}Syncing changes to git...${NC}"
  git_sync_exit
  echo -e "${YELLOW}Stopping all processes...${NC}"
  for f in "$PID_DIR"/*.pid; do
    if [ -f "$f" ]; then
      pid=$(cat "$f")
      kill "$pid" 2>/dev/null || true
      sleep 1
      kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
      rm -f "$f"
    fi
  done
  # Stop disk monitor watcher
  if [ -f "/tmp/compliancehub-disk/watch.pid" ]; then
    kill "$(cat /tmp/compliancehub-disk/watch.pid)" 2>/dev/null || true
    rm -f /tmp/compliancehub-disk/watch.pid
  fi
  fuser -k 8000/tcp 8080/tcp 2>/dev/null || true
  echo -e "${GREEN}All stopped.${NC}"
}

# Trap signals for graceful shutdown
trap cleanup_all EXIT SIGINT SIGTERM

# ──────────────────────────────────────────────
echo -e "${BOLD}${GREEN}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║      ComplianceHub — Self-Hosted     ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[1/4] Stopping old servers...${NC}"
cleanup_all
sleep 1

echo -e "${YELLOW}[2/4] Building frontend...${NC}"
cd "$FRONTEND_DIR"
npm run build 2>&1 | tail -1
echo -e "  ${GREEN}✓ Frontend built${NC}"

echo -e "${YELLOW}[3/4] Starting backend...${NC}"
cd "$BACKEND_DIR"
FRONTEND_STATIC_DIR="$FRONTEND_DIR/dist" setsid python -m uvicorn app.main:app \
  --host 0.0.0.0 --port 8000 --log-level warning > /tmp/backend.log 2>&1 &
echo $! > "$PID_DIR/backend.pid"

for i in 1 2 3 4 5 6; do
  if curl -sf http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Backend ready (PID $(cat $PID_DIR/backend.pid))${NC}"
    break
  fi
  if [ $i -eq 6 ]; then
    echo -e "  ${RED}✗ Backend failed to start. Check /tmp/backend.log${NC}"
    cleanup_all; exit 1
  fi
  sleep 2
done

# ── Start local AI (auto-select best available model) ──
if [ "$START_AI" = true ]; then
  MODEL=""
  MODEL_CTX=""
  MODEL_NAME=""
  for candidate in "qwen3-4b.gguf:32768:Qwen3-4B" "qwen-3b.gguf:8192:Qwen2.5-3B" "qwen-0.5b.gguf:4096:Qwen2.5-0.5B"; do
    f="${candidate%%:*}"
    rest="${candidate#*:}"
    ctx="${rest%%:*}"
    name="${rest##*:}"
    p="/opt/llama-server/models/$f"
    if [ -f "$p" ]; then
      MODEL="$p"
      MODEL_CTX="$ctx"
      MODEL_NAME="$name"
      break
    fi
  done
  if [ -n "$MODEL" ]; then
    echo -e "${YELLOW}[3b/4] Starting $MODEL_NAME (${MODEL_CTX} ctx)...${NC}"
    setsid /opt/llama-server/llama-server \
      -m "$MODEL" -c "$MODEL_CTX" -t 4 -b 2048 --mlock \
      --host 0.0.0.0 --port 8080 --temp 0.3 \
      > /tmp/llama-server.log 2>&1 &
    echo $! > "$PID_DIR/llama.pid"
    for i in 1 2 3 4 5 6; do
      if curl -sf http://127.0.0.1:8080/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓ $MODEL_NAME ready (attempt $i)${NC}"
        break
      fi
      if [ $i -eq 6 ]; then
        echo -e "  ${RED}✗ $MODEL_NAME failed to load. Check /tmp/llama-server.log${NC}"
      fi
      sleep 3
    done
  else
    echo -e "  ${RED}✗ No AI model found in /opt/llama-server/models/${NC}"
    ls /opt/llama-server/models/ 2>/dev/null || echo "  (directory empty or missing)"
  fi
fi

echo -e "${YELLOW}[4/4] Starting tunnel...${NC}"

rm -f "$URL_FILE"

# Restore last-known URL for immediate feedback
if [ -f "$PERSISTENT_URL_FILE" ] && [ -s "$PERSISTENT_URL_FILE" ]; then
  cp "$PERSISTENT_URL_FILE" "$URL_FILE"
fi

case "$TUNNEL_MODE" in
  cloudflare|serveo|auto)
    setsid "$ROOT_DIR/tunnel.sh" "$TUNNEL_MODE" "$SERVEO_SUBDOMAIN" > /tmp/tunnel.log 2>&1 &
    echo $! > "$PID_DIR/tunnel.pid"
    ;;
  none)
    echo -e "  ${YELLOW}Tunnel disabled — access via localhost only${NC}"
    ;;
esac

# ── Wait for URL ──
URL=""
if [ "$TUNNEL_MODE" != "none" ]; then
  for i in 1 2 3 4 5 6 7 8; do
    if [ -f "$URL_FILE" ] && [ -s "$URL_FILE" ]; then
      URL=$(cat "$URL_FILE")
      if [ -n "$URL" ]; then
        # Got a live URL, not just stale
        break
      fi
    fi
    sleep 3
  done
fi

# If no live URL but we have a stale one, show it
if [ -z "$URL" ] && [ -f "$PERSISTENT_URL_FILE" ] && [ -s "$PERSISTENT_URL_FILE" ]; then
  URL="$(cat "$PERSISTENT_URL_FILE") (last known — tunnel connecting)"
fi

# Sync tunnel URL to git (so other devices can see it)
if [ -n "$URL" ] && echo "$URL" | grep -qv "last known"; then
  git_sync_tunnel_url "$URL"
fi

# ── Background disk monitor ──
if [ -f "$ROOT_DIR/audit-disk.sh" ]; then
  if ! pgrep -f "audit-disk.sh watch" >/dev/null 2>&1; then
    nohup "$ROOT_DIR/audit-disk.sh watch" >/dev/null 2>&1 &
    echo -e "  ${CYAN}✓ Disk monitor started (PID $!)${NC}"
  fi
fi

# ── Display results ──
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║        ComplianceHub is running!               ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

if [ -n "$URL" ]; then
  echo -e "  ${GREEN}🌐 Public URL:${NC}"
  echo -e "  ${BOLD}${CYAN}  $URL${NC}"
  echo ""
fi

echo -e "  ${YELLOW}Local access:${NC}"
echo -e "  ${CYAN}  http://localhost:8000${NC}"
echo ""

echo -e "  ${YELLOW}Health check:${NC}"
echo -e "  ${CYAN}  curl http://localhost:8000/api/health${NC}"
echo ""

if [ "$START_AI" = true ]; then
  echo -e "  ${YELLOW}AI status:${NC}"
  curl -sf http://127.0.0.1:8080/health > /dev/null 2>&1 \
    && echo -e "  ${GREEN}✓ Qwen2.5-3B running on port 8080${NC}" \
    || echo -e "  ${RED}✗ Qwen2.5-3B not responding${NC}"
  echo ""
fi

echo -e "  ${YELLOW}Commands:${NC}"
echo -e "  ${CYAN}  bash stop.sh${NC}        — Stop all servers"
echo -e "  ${CYAN}  bash go.sh --ai${NC}      — Restart with AI"
echo -e "  ${CYAN}  bash go.sh --serveo --serveo-subdomain=NAME${NC} — Serveo tunnel"
echo -e "  ${CYAN}  cat $URL_FILE${NC}        — Get current URL"
echo ""

if [ -z "$URL" ] && [ "$TUNNEL_MODE" != "none" ]; then
  echo -e "  ${YELLOW}⏳ Tunnel still connecting... Check back:${NC}"
  echo -e "  ${CYAN}  cat $URL_FILE${NC}"
  echo -e "  ${CYAN}  tail -f /tmp/tunnel.log${NC}"
  echo ""
fi
