#!/usr/bin/env bash
# ComplianceHub — Windows WSL2 Setup Script
# Run inside WSL Ubuntu. Installs everything needed to work on ComplianceHub.
set -euo pipefail

BOLD='\033[1m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${CYAN}==>${NC} $1"; }
ok()    { echo -e "${GREEN}  ✓${NC} $1"; }
warn()  { echo -e "${YELLOW}  ⚠${NC} $1"; }
err()   { echo -e "${RED}  ✗${NC} $1"; }

echo -e "${BOLD}${GREEN}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║   ComplianceHub — WSL Setup          ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

# ── 1. Detect WSL ──
if ! grep -qi microsoft /proc/version 2>/dev/null; then
  warn "Not detected as WSL. Script works on Linux too but assumes Ubuntu package names."
  echo "  Continue? [Y/n]"
  read -r ans
  [[ "$ans" =~ ^[Nn] ]] && exit 1
else
  ok "WSL detected"
fi

# ── 2. Locate repo ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/backend/app/main.py" ]; then
  REPO_DIR="$SCRIPT_DIR"
  ok "Repo found at $REPO_DIR"
else
  warn "Not inside ComplianceHub repo. Where is it cloned?"
  echo "  Enter path (e.g., /home/username/ComplianceHub):"
  read -r REPO_DIR
  REPO_DIR="${REPO_DIR/#\~/$HOME}"
  if [ ! -f "$REPO_DIR/backend/app/main.py" ]; then
    err "Not a valid repo path. Clone it first:"
    echo "    cd ~ && git clone https://github.com/YOUR-ORG/ComplianceHub.git"
    exit 1
  fi
fi
cd "$REPO_DIR"

# ── 3. System packages ──
info "Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq curl wget git python3 python3-pip python3-venv \
  build-essential libssl-dev pkg-config 2>&1 | tail -1
ok "System packages installed"

# ── 4. Node.js via nvm ──
if ! command -v node &>/dev/null; then
  info "Installing Node.js 22 via nvm..."
  export NVM_DIR="$HOME/.nvm"
  if [ ! -d "$NVM_DIR" ]; then
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  fi
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  nvm install 22 2>&1 | tail -1
  nvm alias default 22
  echo 'export NVM_DIR="$HOME/.nvm"' >> "$HOME/.bashrc"
  echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> "$HOME/.bashrc"
  ok "Node.js $(node -v) installed"
else
  ok "Node.js $(node -v) already installed"
fi

# ── 5. opencode-ai ──
if ! command -v opencode &>/dev/null; then
  info "Installing opencode-ai..."
  npm install -g opencode-ai 2>&1 | tail -1
  ok "opencode installed"
else
  ok "opencode already installed"
fi

# ── 6. cloudflared ──
if ! command -v cloudflared &>/dev/null; then
  info "Installing cloudflared..."
  curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb \
    -o /tmp/cloudflared.deb
  sudo dpkg -i /tmp/cloudflared.deb 2>&1 | tail -1
  rm /tmp/cloudflared.deb
  ok "cloudflared installed"
else
  ok "cloudflared already installed"
fi

# ── 7. Backend Python deps ──
info "Setting up Python virtual environment..."
cd "$REPO_DIR/backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt 2>&1 | tail -1
ok "Python deps installed"

# ── 8. Frontend deps ──
info "Installing frontend dependencies..."
cd "$REPO_DIR/frontend"
npm install 2>&1 | tail -1
ok "Frontend deps installed"

# ── 9. .env file ──
if [ ! -f "$REPO_DIR/backend/.env" ]; then
  info "Creating backend/.env from template..."
  cp "$REPO_DIR/backend/.env.example" "$REPO_DIR/backend/.env"
  warn ">> Edit backend/.env and add your API keys:"
  echo "     ANTHROPIC_API_KEY=sk-ant-..."
  echo "     OPENROUTER_API_KEY=sk-or-..."
  echo "     GROQ_API_KEY=gsk_..."
  echo ""
fi

# ── 10. claude-mem ──
if ! npx -y claude-mem --version &>/dev/null 2>&1; then
  info "Installing claude-mem..."
  npx -y claude-mem install --ide opencode 2>&1 | tail -3
  ok "claude-mem installed"
else
  ok "claude-mem already installed"
fi

# ── 11. Tree-sitter CLI binary ──
info "Installing tree-sitter CLI for smart tools..."
# Find all tree-sitter-cli directories and install the binary
find ~/.claude/plugins -path "*/tree-sitter-cli" -type d 2>/dev/null | while read -r dir; do
  if [ -f "$dir/package.json" ] && [ ! -f "$dir/tree-sitter" ]; then
    (cd "$dir" && node install.js 2>/dev/null) && ok "tree-sitter binary in $dir"
  fi
done

# ── 12. Generate opencode.json for this device ──
info "Generating opencode.json for WSL..."
if [ -f "$REPO_DIR/opencode.json.template" ]; then
  # Find claude-mem MCP server path
  MCP_SERVER=""
  MCP_NODE_PATH=""
  for candidate in ~/.claude/plugins/marketplaces/*/plugin/scripts/mcp-server.cjs; do
    if [ -f "$candidate" ]; then
      MCP_SERVER="$candidate"
      # Derive NODE_PATH — find the cache node_modules
      PLUGIN_NAME=$(echo "$candidate" | sed 's|.*/marketplaces/\(.*\)/plugin/scripts/mcp-server.cjs|\1|')
      CACHE_PATH="$HOME/.claude/plugins/cache/$PLUGIN_NAME"
      if [ -d "$CACHE_PATH" ]; then
        MCP_NODE_PATH=$(find "$CACHE_PATH" -maxdepth 2 -name "node_modules" -type d | head -1)
      fi
      break
    fi
  done

  if [ -n "$MCP_SERVER" ]; then
    cat > "$REPO_DIR/opencode.json" <<CONFIGEOF
{
  "\$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md", "HUMANIZE.md"],
  "permission": {
    "read": "allow",
    "edit": "allow",
    "bash": "allow",
    "glob": "allow",
    "grep": "allow",
    "list": "allow",
    "task": "allow",
    "webfetch": "ask",
    "websearch": "ask"
  },
  "skills": {
    "paths": [".opencode/skills"]
  },
  "agent": {
    "humanizer": {
      "description": "Reviews output for AI-sounding patterns and rewrites in natural human voice",
      "file": ".opencode/agents/humanizer.md"
    }
  },
  "mcp": {
    "claude-mem": {
      "type": "local",
      "command": ["node", "${MCP_SERVER}"],
      "environment": {
        "NODE_PATH": "${MCP_NODE_PATH}",
        "CLAUDE_MEM_CHROMA_ENABLED": "false"
      },
      "enabled": true,
      "timeout": 10000
    }
  }
}
CONFIGEOF
    ok "opencode.json generated with claude-mem MCP"
  else
    warn "claude-mem MCP server not found. Generating minimal opencode.json."
    cat > "$REPO_DIR/opencode.json" <<CONFIGEOF
{
  "\$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md", "HUMANIZE.md"],
  "permission": {
    "read": "allow",
    "edit": "allow",
    "bash": "allow",
    "glob": "allow",
    "grep": "allow",
    "list": "allow",
    "task": "allow",
    "webfetch": "ask",
    "websearch": "ask"
  },
  "skills": {
    "paths": [".opencode/skills"]
  }
}
CONFIGEOF
    warn "Run 'npx claude-mem install --ide opencode' then re-run this script"
  fi
else
  warn "opencode.json.template not found. Using minimal config."
fi

# ── 13. Git auth ──
info "Setting up Git..."
git config --global user.name "Osama"
git config --global user.email "osama@compliancehub.dev" 2>/dev/null || true

# Try GCM first (Windows shared)
GCM_PATH="/mnt/c/Program Files/Git/mingw64/bin/git-credential-manager.exe"
if [ -f "$GCM_PATH" ]; then
  git config --global credential.helper "$GCM_PATH"
  ok "Using Windows Git Credential Manager"
else
  # Check if already configured
  CURRENT_HELPER=$(git config --global credential.helper 2>/dev/null || true)
  if [ -z "$CURRENT_HELPER" ]; then
    warn "No credential helper found. Set up a PAT:"
    echo "    git config --global credential.helper store"
    echo "    git pull (will prompt for username/PAT)"
    echo ""
  fi
fi

# ── 14. Cherry Studio reference ──
echo ""
info "Cherry Studio assistants config:"
echo "  Open 'Osama/CHERRY_STUDIO_ASSISTANTS.md' and create 9 assistants in Cherry Studio."
echo "  Same config works on both devices — knowledge base files are in the repo."
echo ""

# ── 15. Summary ──
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║        Setup Complete!                         ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${YELLOW}Start the app:${NC}"
echo -e "    ${CYAN}bash go.sh${NC}"
echo -e "    ${CYAN}http://localhost:8000${NC}"
echo ""
echo -e "  ${YELLOW}Start with AI:${NC}"
echo -e "    ${CYAN}bash go.sh --ai${NC}"
echo ""
echo -e "  ${YELLOW}Start opencode:${NC}"
echo -e "    ${CYAN}cd $REPO_DIR && opencode${NC}"
echo ""
echo -e "  ${YELLOW}Edit API keys:${NC}"
echo -e "    ${CYAN}nano backend/.env${NC}"
echo ""
echo -e "  ${YELLOW}See Android tunnel URL (sync first):${NC}"
echo -e "    ${CYAN}git pull && cat Osama/.tunnel-url${NC}"
echo ""

# Check Android tunnel URL if available
if [ -f "$REPO_DIR/Osama/.tunnel-url" ] && [ -s "$REPO_DIR/Osama/.tunnel-url" ]; then
  ANDROID_URL=$(head -1 "$REPO_DIR/Osama/.tunnel-url")
  if echo "$ANDROID_URL" | grep -q "^https\?://"; then
    echo -e "  ${YELLOW}Android tunnel URL (from last sync):${NC}"
    echo -e "    ${CYAN}$ANDROID_URL${NC}"
    echo ""
  fi
fi

echo -e "  ${YELLOW}Tip: run ${CYAN}bash go.sh${YELLOW} and it auto-syncs from git on start/stop${NC}"
echo ""
