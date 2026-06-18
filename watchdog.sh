#!/usr/bin/env bash
# ComplianceHub Watchdog — runs from crontab every 10 min
# Ensures backend + tunnel stay alive even after reboot or crash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
PID_DIR="/tmp/compliancehub-pids"
LOG_FILE="/tmp/watchdog.log"
URL_FILE="/tmp/compliancehub-url.txt"
GIT_URL_FILE="$ROOT_DIR/Osama/.tunnel-url"

mkdir -p "$PID_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M')] $*" >> "$LOG_FILE"; }

# ── Check backend health ──
check_backend() {
  curl -sf http://127.0.0.1:8000/api/health > /dev/null 2>&1
}

# ── Check if tunnel has a URL ──
check_tunnel_url() {
  [ -f "$URL_FILE" ] && [ -s "$URL_FILE" ]
}

# ── Start backend only ──
start_backend() {
  log "Backend down — starting..."
  cd "$BACKEND_DIR"
  FRONTEND_STATIC_DIR="$FRONTEND_DIR/dist" setsid python -m uvicorn app.main:app \
    --host 0.0.0.0 --port 8000 --log-level warning > /tmp/backend.log 2>&1 &
  echo $! > "$PID_DIR/backend.pid"
  for i in 1 2 3 4 5 6; do
    if curl -sf http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
      log "Backend ready (PID $(cat $PID_DIR/backend.pid))"
      return 0
    fi
    sleep 2
  done
  log "Backend failed to start"
  return 1
}

# ── Start tunnel only ──
start_tunnel() {
  log "Tunnel down — starting..."
  setsid "$ROOT_DIR/tunnel.sh" auto > /tmp/tunnel.log 2>&1 &
  echo $! > "$PID_DIR/tunnel.pid"
  # Wait for URL
  for i in 1 2 3 4 5 6 7 8; do
    if [ -f "$URL_FILE" ] && [ -s "$URL_FILE" ]; then
      local url
      url=$(cat "$URL_FILE")
      log "Tunnel ready: $url"
      # Sync to git-tracked file
      echo "$url" > "$GIT_URL_FILE"
      return 0
    fi
    sleep 3
  done
  log "Tunnel failed — will retry next cycle"
  return 1
}

# ── Sync tunnel URL to git ──
sync_tunnel_url() {
  if [ -f "$URL_FILE" ] && [ -s "$URL_FILE" ]; then
    local url
    url=$(cat "$URL_FILE")
    echo "$url" > "$GIT_URL_FILE"
    cd "$ROOT_DIR"
    git add "$GIT_URL_FILE" 2>/dev/null || true
    git commit -m "watchdog: tunnel URL sync" 2>/dev/null || true
    git push origin main 2>/dev/null || true
  fi
}

# ── Main ──
BACKEND_UP=false
TUNNEL_UP=false

if check_backend; then
  BACKEND_UP=true
fi

if check_tunnel_url; then
  TUNNEL_UP=true
fi

if $BACKEND_UP && $TUNNEL_UP; then
  # Everything fine — silent exit
  exit 0
fi

if ! $BACKEND_UP; then
  log "Backend is DOWN — restarting stack"
  start_backend || true
  sleep 3
  start_tunnel || true
  sync_tunnel_url
  exit 0
fi

# Backend up, tunnel down
if ! $TUNNEL_UP; then
  log "Tunnel is DOWN — restarting"
  start_tunnel || true
  sync_tunnel_url
fi
