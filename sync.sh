#!/usr/bin/env bash
# sync.sh — Pull latest, commit local changes, push
# Run anytime: bash sync.sh
# Or before/after a session to sync MEMORY.md + tunnel URL

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "==> Syncing ComplianceHub..."

# Pull with autostash
if ! git diff --quiet 2>/dev/null; then
  echo "  Stashing local changes..."
  git stash push -m "auto-stash before sync $(date +%s)"
  STASHED=true
fi

echo "  Pulling from origin..."
git pull --rebase origin main 2>/dev/null || echo "  ⚠ Pull failed (no remote or offline)"

if [ "${STASHED:-false}" = true ]; then
  echo "  Restoring local changes..."
  git stash pop 2>/dev/null || true
fi

# Commit MEMORY.md and tunnel URL if changed
COMMIT_MSG=""
if ! git diff --quiet -- "Osama/MEMORY.md" 2>/dev/null; then
  git add "Osama/MEMORY.md"
  COMMIT_MSG="sync: MEMORY.md"
fi
if ! git diff --quiet -- "Osama/.tunnel-url" 2>/dev/null; then
  git add "Osama/.tunnel-url"
  COMMIT_MSG="${COMMIT_MSG}${COMMIT_MSG:+, }tunnel URL"
fi

if [ -n "$COMMIT_MSG" ]; then
  git commit -m "$COMMIT_MSG" 2>/dev/null || true
  git push origin main 2>/dev/null && echo "  ✓ Pushed: $COMMIT_MSG" || echo "  ⚠ Push failed"
fi

echo "  ✓ Done"

# Show tunnel URL if available
if [ -f "Osama/.tunnel-url" ] && [ -s "Osama/.tunnel-url" ]; then
  URL=$(head -1 "Osama/.tunnel-url")
  if echo "$URL" | grep -q "^https\?://"; then
    echo ""
    echo "  Android tunnel URL: $URL"
  fi
fi
