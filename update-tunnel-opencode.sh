#!/usr/bin/env bash
# Auto-update opencode.jsonc with current tunnel URL.
# Called by tunnel watchdog on URL change.
# Usage: update-tunnel-opencode.sh [new-tunnel-url]

set -euo pipefail

URL="${1:-}"
CONFIG="$HOME/.config/opencode/opencode.jsonc"
URL_FILE="/root/Documents/ComplianceHub/.tunnel-url"

if [[ -z "$URL" && -f "$URL_FILE" ]]; then
  URL=$(cat "$URL_FILE")
fi

if [[ -z "$URL" ]]; then
  echo "No tunnel URL available"
  exit 1
fi

# Strip trailing slash
URL="${URL%/}"

# Write machine-readable URL file for Windows scripts
echo -n "$URL" > /tmp/tunnel-url.txt

if ! grep -q "$URL" "$CONFIG" 2>/dev/null; then
  # URL changed — rewrite the api field
  sed -i "s|\"api\": \"https://[a-z0-9.-]*\.trycloudflare\.com/v1\"|\"api\": \"${URL}/v1\"|" "$CONFIG"
  echo "Updated opencode.jsonc tunnel URL to $URL"
  echo "$URL" > /tmp/tunnel-url-changed
else
  echo "Tunnel URL unchanged"
fi
