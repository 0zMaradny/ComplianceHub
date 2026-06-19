#!/bin/bash
# Start ComplianceHub backend with setsid (survives shell timeout kills)
set -euo pipefail

cd "$(dirname "$0")"
PORT=${PORT:-8000}
FRONTEND_DIR="$(dirname "$0")/../frontend"

# Kill previous instance
if [ -f /tmp/backend.pid ]; then
  OLD=$(cat /tmp/backend.pid 2>/dev/null)
  kill "$OLD" 2>/dev/null || true
  sleep 1
fi

FRONTEND_STATIC_DIR="$FRONTEND_DIR/dist" \
setsid python3 -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --log-level warning \
  > /tmp/backend.log 2>&1 < /dev/null &

PID=$!
echo $PID > /tmp/backend.pid

# Wait for healthy
for i in 1 2 3 4 5 6; do
  if curl -sf "http://127.0.0.1:$PORT/api/health" > /dev/null 2>&1; then
    echo "Backend up (PID $PID) on port $PORT"
    exit 0
  fi
  sleep 2
done

echo "Backend failed to start — check /tmp/backend.log" >&2
exit 1
