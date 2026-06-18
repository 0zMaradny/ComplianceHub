#!/usr/bin/env bash
set -euo pipefail

# ─── Configuration ───
THRESHOLD_YELLOW=80
THRESHOLD_RED=85
THRESHOLD_CRITICAL=90
WATCH_INTERVAL=1800
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
ALERTS_FILE="$ROOT_DIR/Osama/DISK_ALERTS.md"
STATE_DIR="/tmp/compliancehub-disk"
ESCALATION_FILE="$STATE_DIR/last_level"
TELEGRAM_CONFIG="$HOME/.codex/telegram-bridge.json"

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

check_cmd() { command -v "$1" >/dev/null 2>&1; }

get_disk_pct() {
  df / | awk 'NR==2 {print $5}' | tr -d '%'
}

get_disk_avail() {
  df -h / | awk 'NR==2 {print $4}'
}

list_large_items() {
  local total=0
  echo ""
  local targets=(
    "/opt/llama-server/models:GGUF models"
    "$HOME/.npm:NPM cache"
    "$HOME/.bun/install/cache:Bun cache"
    "$HOME/.cache/uv:UV cache"
    "$HOME/.cache/pip:PIP cache"
    "$HOME/.local/share/pnpm:PNPM store"
    "/tmp:Temp files"
    "$HOME/.cache:Other caches"
  )
  for entry in "${targets[@]}"; do
    local path="${entry%%:*}"
    local label="${entry#*:}"
    if [ -d "$path" ] || [ -f "$path" ]; then
      local size
      size=$(du -sh "$path" 2>/dev/null | awk '{print $1}')
      if [ -n "$size" ]; then
        printf "  ${CYAN}%-30s${NC} %s\n" "$label" "$size"
      fi
    fi
  done
}

auto_clean_caches() {
  local freed=0
  echo -e "  ${YELLOW}Auto-cleaning caches...${NC}"

  local b1 b2 b3 b4 b5
  b1=$(du -sb "$HOME/.npm" 2>/dev/null | awk '{print $1}' || echo 0)
  check_cmd npm && npm cache clean --force 2>/dev/null && echo -e "    ${GREEN}✓${NC} npm cache cleaned" || true
  local a1
  a1=$(du -sb "$HOME/.npm" 2>/dev/null | awk '{print $1}' || echo 0)
  freed=$((freed + (b1 - a1)))

  b2=$(du -sb "$HOME/.cache/pip" 2>/dev/null | awk '{print $1}' || echo 0)
  pip cache purge 2>/dev/null && echo -e "    ${GREEN}✓${NC} pip cache cleaned" || true
  a2=$(du -sb "$HOME/.cache/pip" 2>/dev/null | awk '{print $1}' || echo 0)
  freed=$((freed + (b2 - a2)))

  b3=$(du -sb "$HOME/.cache/uv" 2>/dev/null | awk '{print $1}' || echo 0)
  if check_cmd uv; then
    uv cache clean 2>/dev/null && echo -e "    ${GREEN}✓${NC} uv cache cleaned" || true
  elif [ -x "$HOME/.local/bin/uv" ]; then
    "$HOME/.local/bin/uv" cache clean 2>/dev/null && echo -e "    ${GREEN}✓${NC} uv cache cleaned" || true
  fi
  a3=$(du -sb "$HOME/.cache/uv" 2>/dev/null | awk '{print $1}' || echo 0)
  freed=$((freed + (b3 - a3)))

  b4=$(du -sb "$HOME/.bun/install/cache" 2>/dev/null | awk '{print $1}' || echo 0)
  if check_cmd bun; then
    bun pm cache rm 2>/dev/null || true
  elif [ -x "$HOME/.bun/bin/bun" ]; then
    "$HOME/.bun/bin/bun" pm cache rm 2>/dev/null || true
  fi
  rm -rf "$HOME/.bun/install/cache/@"* "$HOME/.bun/install/cache/"* 2>/dev/null || true
  a4=$(du -sb "$HOME/.bun/install/cache" 2>/dev/null | awk '{print $1}' || echo 0)
  freed=$((freed + (b4 - a4)))
  echo -e "    ${GREEN}✓${NC} bun cache cleaned"

  b5=$(du -sb "$HOME/.local/share/pnpm" 2>/dev/null | awk '{print $1}' || echo 0)
  if check_cmd pnpm; then
    pnpm store prune 2>/dev/null || true
  fi
  rm -rf /tmp/pip-* /tmp/BTrA* /tmp/build-env* 2>/dev/null || true
  find /tmp -maxdepth 1 -name "*.log" -delete 2>/dev/null || true
  a5=$(du -sb "$HOME/.local/share/pnpm" 2>/dev/null | awk '{print $1}' || echo 0)
  freed=$((freed + (b5 - a5)))
  echo -e "    ${GREEN}✓${NC} pnpm + tmp cleaned"

  local freed_mb=$((freed / 1048576))
  echo -e "  ${GREEN}Freed ~${freed_mb} MB${NC}"
  echo "$freed_mb"
}

send_telegram() {
  local message="$1"
  if [ ! -f "$TELEGRAM_CONFIG" ]; then
    return 0
  fi
  local bot_token chat_id
  bot_token=$(python3 -c "import json; print(json.load(open('$TELEGRAM_CONFIG'))['botToken'])" 2>/dev/null || echo "")
  chat_id=$(python3 -c "import json; print(json.load(open('$TELEGRAM_CONFIG'))['chatIds'][0])" 2>/dev/null || echo "")
  if [ -z "$bot_token" ] || [ -z "$chat_id" ]; then
    return 0
  fi
  curl -sf -X POST "https://api.telegram.org/bot${bot_token}/sendMessage" \
    -d "chat_id=${chat_id}" \
    -d "text=${message}" \
    -d "parse_mode=Markdown" >/dev/null 2>&1 || true
}

write_alert() {
  local level="$1" pct="$2" detail="$3"
  mkdir -p "$ROOT_DIR/Osama"
  {
    echo ""
    echo "## $(date '+%Y-%m-%d %H:%M UTC+3') — Disk ${level} (${pct}%)"
    echo "$detail"
  } >> "$ALERTS_FILE"
}

read_last_level() {
  if [ -f "$ESCALATION_FILE" ]; then
    cat "$ESCALATION_FILE"
  else
    echo "ok"
  fi
}

write_last_level() {
  mkdir -p "$STATE_DIR"
  echo "$1" > "$ESCALATION_FILE"
}

get_level() {
  local pct=$1
  if [ "$pct" -ge "$THRESHOLD_CRITICAL" ]; then
    echo "critical"
  elif [ "$pct" -ge "$THRESHOLD_RED" ]; then
    echo "red"
  elif [ "$pct" -ge "$THRESHOLD_YELLOW" ]; then
    echo "yellow"
  else
    echo "ok"
  fi
}

main() {
  local pct
  pct=$(get_disk_pct)
  local avail
  avail=$(get_disk_avail)
  local level
  level=$(get_level "$pct")
  local last_level
  last_level=$(read_last_level)

  if [ "$level" = "ok" ]; then
    echo -e "${GREEN}Disk: ${pct}% used (${avail} free) — OK${NC}"
    write_last_level "ok"
    return 0
  fi

  local large_items
  large_items=$(list_large_items)

  case "$level" in
    yellow)
      echo -e "${YELLOW}${BOLD}⚠ Disk: ${pct}% used (${avail} free) — YELLOW${NC}"
      echo -e "${YELLOW}Large items:${NC}$large_items"
      if [ "$last_level" != "yellow" ] && [ "$last_level" != "red" ] && [ "$last_level" != "critical" ]; then
        write_alert "YELLOW" "$pct" "**Large items:**\n\`\`\`\n$large_items\n\`\`\`\n**Available:** $avail"
      fi
      write_last_level "yellow"
      ;;

    red)
      echo -e "${RED}${BOLD}🔴 Disk: ${pct}% used (${avail} free) — RED${NC}"
      echo -e "${RED}Large items:${NC}$large_items"
      local freed_mb=0
      local clean_result
      clean_result=$(auto_clean_caches)
      freed_mb=$(echo "$clean_result" | tail -1)
      local detail="**Large items:**\n\`\`\`\n$large_items\n\`\`\`\n**Auto-cleaned:** ~${freed_mb} MB\n**Available:** $avail"
      if [ "$last_level" != "red" ] && [ "$last_level" != "critical" ]; then
        write_alert "RED" "$pct" "$detail"
        send_telegram "🚨 *ComplianceHub Disk Alert — RED*\nDisk usage: ${pct}%\nAvailable: $avail\nFreed: ~${freed_mb} MB from caches\n\nCheck \`Osama/DISK_ALERTS.md\` for details."
      elif [ "$last_level" = "ok" ] || [ "$last_level" = "yellow" ]; then
        write_alert "RED (escalated)" "$pct" "$detail"
        send_telegram "🚨 *ComplianceHub Disk Alert — RED (escalated)*\nDisk usage: ${pct}%\nAvailable: $avail\nFreed: ~${freed_mb} MB from caches"
      fi
      write_last_level "red"
      ;;

    critical)
      echo -e "${RED}${BOLD}🚨 Disk: ${pct}% used (${avail} free) — CRITICAL${NC}"
      echo -e "${RED}Large items:${NC}$large_items"
      local cfreed_mb=0
      local cclean_result
      cclean_result=$(auto_clean_caches)
      cfreed_mb=$(echo "$cclean_result" | tail -1)
      local gguf_msg=""
      if [ -d "/opt/llama-server/models" ]; then
        local gguf_size
        gguf_size=$(du -sh /opt/llama-server/models 2>/dev/null | awk '{print $1}')
        gguf_msg="\n**GGUF models:** ${gguf_size} — consider deleting unused ones with \`rm /opt/llama-server/models/*.gguf\`"
      fi
      local cdetail="**Large items:**\n\`\`\`\n$large_items\n\`\`\`\n**GGUF models:** $(du -sh /opt/llama-server/models 2>/dev/null | awk '{print $1}')\n**Auto-cleaned:** ~${cfreed_mb} MB\n**Available:** $avail"
      if [ "$last_level" != "critical" ]; then
        write_alert "CRITICAL" "$pct" "$cdetail"
        send_telegram "🚨🚨 *ComplianceHub Disk Alert — CRITICAL*\nDisk usage: ${pct}% — URGENT\nAvailable: $avail\nFreed: ~${cfreed_mb} MB from caches${gguf_msg}\n\nTake action immediately!"
      fi
      write_last_level "critical"
      ;;
  esac
}

case "${1:-}" in
  watch)
    shift
    mkdir -p "$STATE_DIR"
    echo "$$" > "$STATE_DIR/watch.pid"
    echo -e "${CYAN}Disk monitor started (PID $$) — checking every ${WATCH_INTERVAL}s${NC}"
    while true; do
      main "$@"
      sleep "$WATCH_INTERVAL"
    done
    ;;
  check|"")
    main
    ;;
  *)
    echo "Usage: $0 [check|watch]"
    echo "  check    Run once (default)"
    echo "  watch    Run every 30 min"
    exit 1
    ;;
esac
