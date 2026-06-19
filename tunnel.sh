#!/usr/bin/env bash
# ComplianceHub Tunnel Watchdog
# Usage: tunnel.sh cloudflare|serveo|auto [subdomain]
# Runs forever, reconnecting on failure with exponential backoff.
# Saves URL to /tmp/compliancehub-url.txt and $ROOT_DIR/.tunnel-url
# Auto-fallback: cloudflare → serveo → loop if consecutive failures exceed threshold

MODE="${1:-auto}"
SUBDOMAIN="${2:-}"
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
URL_FILE="/tmp/compliancehub-url.txt"
PERSISTENT_URL_FILE="$ROOT_DIR/.tunnel-url"
CLOUD="/tmp/cloudflared"
TUNNEL_SECRET="${TUNNEL_SECRET:-compliancehub-tunnel-secret}"
LOG_DIR="/tmp"
LOG_FILE="$LOG_DIR/tunnel.log"
HEALTH_LOG="$LOG_DIR/tunnel-health.log"

# Track state for fallback
CONSECUTIVE_FAILURES=0
FAILURE_THRESHOLD=3
BACKOFF=5
MAX_BACKOFF=60
CURRENT_TUNNEL="$MODE"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_FILE"; }

rotate_log() {
  local f="$1"
  if [ -f "$f" ] && [ "$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null)" -gt 1048576 ]; then
    mv "$f" "${f}.1" 2>/dev/null
    [ -f "${f}.1" ] && mv "${f}.1" "${f}.2" 2>/dev/null
    [ -f "${f}.2" ] && mv "${f}.2" "${f}.3" 2>/dev/null
  fi
}

save_url() {
  local url="$1"
  if [ -n "$url" ]; then
    echo "$url" > "$URL_FILE"
    echo "$url" > "$PERSISTENT_URL_FILE"
    # Also write to git-tracked location for cross-device sync
    echo "$url" > "$ROOT_DIR/Osama/.tunnel-url"
    log "URL: $url"
    post_url "$url"
  fi
}

post_url() {
  local url="$1"
  if [ -n "$url" ]; then
    curl -s -X POST http://localhost:8000/api/tunnel-url \
      -H "Content-Type: application/json" \
      -H "X-Tunnel-Secret: $TUNNEL_SECRET" \
      -d "{\"tunnel_url\":\"$url\"}" > /dev/null 2>&1 || true
  fi
}

backoff_wait() {
  sleep "$BACKOFF"
  BACKOFF=$((BACKOFF * 2))
  [ "$BACKOFF" -gt "$MAX_BACKOFF" ] && BACKOFF=$MAX_BACKOFF
}

reset_backoff() {
  BACKOFF=5
  CONSECUTIVE_FAILURES=0
}

# ── Cloudflare Tunnel ──
cloudflare_connect() {
  if [ ! -f "$CLOUD" ]; then
    log "Downloading cloudflared ARM64..."
    curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o "$CLOUD"
    chmod +x "$CLOUD"
    log "cloudflared downloaded"
  fi

  rotate_log "$LOG_FILE"
  log "Connecting Cloudflare tunnel..."
  rm -f "$URL_FILE"
  local url=""

  $CLOUD tunnel --url http://localhost:8000 --protocol http2 2>&1 | while read -r line; do
    echo "$line" >> "$LOG_FILE"
    local parsed
    parsed=$(echo "$line" | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com')
    if [ -n "$parsed" ] && [ -z "$url" ]; then
      url="$parsed"
      save_url "$url"
      reset_backoff
      CONSECUTIVE_FAILURES=0
    fi
  done

  return 1
}

# ── Serveo Tunnel ──
serveo_connect() {
  rotate_log "$LOG_FILE"
  local serveo_arg="80:localhost:8000"
  if [ -n "$SUBDOMAIN" ]; then
    serveo_arg="${SUBDOMAIN}:80:localhost:8000"
    log "Using fixed subdomain: $SUBDOMAIN.serveo.net"
  fi

  log "Connecting Serveo tunnel..."
  rm -f "$URL_FILE"
  local url=""

  ssh -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes \
    -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
    -R "$serveo_arg" serveo.net 2>&1 | while read -r line; do
    echo "$line" >> "$LOG_FILE"
    local parsed=""
    if [ -n "$SUBDOMAIN" ]; then
      parsed="https://${SUBDOMAIN}.serveo.net"
    else
      parsed=$(echo "$line" | grep -oE 'https://[^[:space:]]+')
    fi
    if [ -n "$parsed" ] && [ -z "$url" ]; then
      url="$parsed"
      save_url "$url"
      reset_backoff
      CONSECUTIVE_FAILURES=0
    fi
  done

  return 1
}

# ── Main watchdog with fallback ──
# Restore last known URL on startup
if [ -f "$PERSISTENT_URL_FILE" ] && [ -s "$PERSISTENT_URL_FILE" ]; then
  log "Last known URL: $(cat "$PERSISTENT_URL_FILE")"
fi

while true; do
  # Determine which tunnel to try next
  local_try_mode=""
  case "$CURRENT_TUNNEL" in
    cloudflare) local_try_mode="cloudflare" ;;
    serveo) local_try_mode="serveo" ;;
    auto)
      if [ $((CONSECUTIVE_FAILURES % 2)) -eq 0 ]; then
        local_try_mode="cloudflare"
      else
        local_try_mode="serveo"
      fi
      ;;
  esac

  log "Starting tunnel: $local_try_mode (failure count: $CONSECUTIVE_FAILURES, backoff: ${BACKOFF}s)"
  local rc=1
  case "$local_try_mode" in
    cloudflare) cloudflare_connect; rc=$? ;;
    serveo) serveo_connect; rc=$? ;;
  esac

  CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))

  # Auto switch mode on consecutive failures
  if [ "$CONSECUTIVE_FAILURES" -ge "$FAILURE_THRESHOLD" ]; then
    if [ "$CURRENT_TUNNEL" = "auto" ]; then
      log "Switching tunnel mode after $CONSECUTIVE_FAILURES failures"
    else
      log "Primary tunnel ($CURRENT_TUNNEL) failed $CONSECUTIVE_FAILURES times, switching mode"
      CURRENT_TUNNEL="auto"
    fi
    CONSECUTIVE_FAILURES=0
    reset_backoff
  fi

  log "Tunnel disconnected. Reconnecting in ${BACKOFF}s..."
  backoff_wait
done
