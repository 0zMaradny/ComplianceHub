#!/usr/bin/env bash
# Stop all ComplianceHub processes (graceful shutdown)

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PID_DIR="/tmp/compliancehub-pids"
URL_FILE="/tmp/compliancehub-url.txt"

echo -e "${YELLOW}Stopping ComplianceHub...${NC}"

# Kill by PID files — SIGTERM first, then SIGKILL
if [ -d "$PID_DIR" ]; then
  for f in "$PID_DIR"/*.pid; do
    if [ -f "$f" ]; then
      pid=$(cat "$f")
      name=$(basename "$f" .pid)
      if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null && echo -e "  ${GREEN}✓ SIGTERM sent to $name (PID $pid)${NC}" || true
      else
        echo -e "  ${YELLOW}  $name (PID $pid) not running${NC}"
      fi
      rm -f "$f"
    fi
  done

  # Wait for graceful shutdown
  sleep 2

  # Force kill anything still alive
  for f in "$PID_DIR"/*.pid; do
    if [ -f "$f" ]; then
      pid=$(cat "$f")
      name=$(basename "$f" .pid)
      kill -9 "$pid" 2>/dev/null && echo -e "  ${RED}✗ Force killed $name (PID $pid)${NC}" || true
      rm -f "$f"
    fi
  done

  rmdir "$PID_DIR" 2>/dev/null || true
fi

# Kill by port (catch anything leftover)
fuser -k -TERM 8000/tcp 8080/tcp 2>/dev/null || true
sleep 1
fuser -k -KILL 8000/tcp 8080/tcp 2>/dev/null || true

# Kill tunnel processes
pkill -f "cloudflared tunnel" 2>/dev/null || true
pkill -f "serveo.net" 2>/dev/null || true
pkill -f "localtunnel" 2>/dev/null || true

rm -f "$URL_FILE"

echo -e "${GREEN}✓ ComplianceHub stopped${NC}"
