<#
.SYNOPSIS
  ComplianceHub — Native Windows Setup (No Admin Required)
  Run in PowerShell. Installs deps, configures claude-mem, clones repo.

.NOTES
  Requires: Git portable, Node.js portable manually installed first
  (see WINDOWS_SETUP.md for download links)
#>

$BOLD = [char]27 + "[1m"
$GREEN = [char]27 + "[32m"
$YELLOW = [char]27 + "[33m"
$CYAN = [char]27 + "[36m"
$RED = [char]27 + "[31m"
$NC = [char]27 + "[0m"

Write-Host "${BOLD}${GREEN}"
Write-Host "  ╔══════════════════════════════════════╗"
Write-Host "  ║   ComplianceHub — Windows Setup      ║"
Write-Host "  ╚══════════════════════════════════════╝"
Write-Host "${NC}"

# ── Find Git (auto-detect portable, GitHub Desktop, or PATH) ──
function Find-Git {
  $locations = @(
    "$env:LOCALAPPDATA\GitHubDesktop\app-*\resources\app\git\cmd\git.exe",
    "$env:USERPROFILE\Downloads\PortableGit\cmd\git.exe",
    "$env:USERPROFILE\PortableGit\cmd\git.exe",
    "$env:ProgramFiles\Git\cmd\git.exe",
    "${env:ProgramFiles(x86)}\Git\cmd\git.exe"
  )
  foreach ($pattern in $locations) {
    $matches = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    if ($matches) { return $matches[0].FullName }
  }
  $cmd = Get-Command git -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  return $null
}

# ── 1. Check prerequisites ──
$GIT_PATH = Find-Git
$missing = @()
if (-not $GIT_PATH) { $missing += "Git" }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { $missing += "Node.js" }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { $missing += "Python" }

if ($missing.Count -gt 0) {
  Write-Host "${RED}Missing prerequisites: $($missing -join ', ')${NC}"
  Write-Host "Install these first, then re-run this script."
  Write-Host "  Git portable:     https://github.com/git-for-windows/git/releases"
  Write-Host "  Node.js portable: https://nodejs.org/ (download .zip, not .msi)"
  Write-Host "  Python: Already installed ✓"
  exit 1
}

$gitVersion = & $GIT_PATH --version
Write-Host "${GREEN}  ✓ Git: $gitVersion${NC}"
Write-Host "${GREEN}  ✓ Node: $(node --version)${NC}"
Write-Host "${GREEN}  ✓ Python: $(python --version)${NC}"

# ── 2. Locate or clone repo ──
$REPO_DIR = "$env:USERPROFILE\ComplianceHub"

if (Test-Path "$REPO_DIR\backend\app\main.py") {
  Write-Host "${GREEN}  ✓ Repo found at $REPO_DIR${NC}"
} else {
  Write-Host "${CYAN}  Cloning ComplianceHub...${NC}"
  & $GIT_PATH clone https://github.com/0zMaradny/ComplianceHub.git $REPO_DIR
  if ($LASTEXITCODE -ne 0) {
    Write-Host "${RED}  ✗ Clone failed. Check network or URL.${NC}"
    exit 1
  }
  Write-Host "${GREEN}  ✓ Repo cloned${NC}"
}

Set-Location $REPO_DIR

# ── 3. Backend Python deps ──
Write-Host "${CYAN}  Installing Python deps...${NC}"
try {
  $env:PIP_USER = "true"
  python -m pip install -q -r backend\requirements.txt 2>&1 | Out-Null
  Write-Host "${GREEN}  ✓ Python deps installed${NC}"
} catch {
  Write-Host "${YELLOW}  ⚠ pip install had issues — try: pip install -r backend\requirements.txt${NC}"
}

# ── 4. Frontend deps ──
Write-Host "${CYAN}  Installing frontend deps...${NC}"
Set-Location "$REPO_DIR\frontend"
npm install 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
  Write-Host "${GREEN}  ✓ Frontend deps installed${NC}"
} else {
  Write-Host "${YELLOW}  ⚠ npm install had issues${NC}"
}

# ── 5. .env file ──
if (-not (Test-Path "$REPO_DIR\backend\.env")) {
  Copy-Item "$REPO_DIR\backend\.env.example" "$REPO_DIR\backend\.env"
  Write-Host "${YELLOW}  ⚠ Created backend\.env — add your API keys:${NC}"
  Write-Host "     ANTIGRAVITY_CLIENT_ID=      # OAuth client ID"
  Write-Host "     ANTIGRAVITY_CLIENT_SECRET=  # OAuth client secret"
  Write-Host "     ANTIGRAVITY_REFRESH=        # OAuth refresh token"
  Write-Host "     OPENROUTER_API_KEY=sk-or-..."
  Write-Host "     GROQ_API_KEY=gsk_..."
}

# ── 6. claude-mem ──
$claudeMemCheck = Get-Command claude-mem -ErrorAction SilentlyContinue
if (-not $claudeMemCheck) {
  Write-Host "${CYAN}  Installing claude-mem...${NC}"
  npx -y claude-mem install --ide opencode 2>&1 | Out-Null
  Write-Host "${GREEN}  ✓ claude-mem installed${NC}"
} else {
  Write-Host "${GREEN}  ✓ claude-mem already installed${NC}"
}

# ── 7. Tree-sitter CLI for smart tools ──
Write-Host "${CYAN}  Installing tree-sitter CLI...${NC}"
$pluginDirs = @()
$claudePlugins = "$env:LOCALAPPDATA\claude\plugins"
if (Test-Path $claudePlugins) {
  $dirs = Get-ChildItem -Path $claudePlugins -Recurse -Directory -Filter "tree-sitter-cli" -ErrorAction SilentlyContinue
  foreach ($d in $dirs) {
    $installJs = Join-Path $d.FullName "install.js"
    $treeSitterBin = Join-Path $d.FullName "tree-sitter.exe"
    if ((Test-Path $installJs) -and (-not (Test-Path $treeSitterBin))) {
      Push-Location $d.FullName
      node install.js 2>$null
      Pop-Location
    }
  }
}
Write-Host "${GREEN}  ✓ tree-sitter CLI setup done${NC}"

# ── 8. Generate opencode.json ──
$templatePath = "$REPO_DIR\opencode.json.template"
if (Test-Path $templatePath) {
  $mcpServer = ""
  $mcpNodePath = ""
  $marketplaceDirs = Get-ChildItem -Path "$env:LOCALAPPDATA\claude\plugins\marketplaces" -Recurse -Filter "mcp-server.cjs" -ErrorAction SilentlyContinue
  foreach ($f in $marketplaceDirs) {
    if ($f.FullName -match "scripts\\mcp-server\.cjs$") {
      $mcpServer = $f.FullName
      $cachePath = $f.FullName -replace 'marketplaces\\.+?\\plugin\\scripts\\mcp-server\.cjs', 'cache'
      $cachePath = $cachePath -replace '([A-Z]):.*?claude\\plugins', "$env:LOCALAPPDATA\claude\plugins"
      # Find the actual cache node_modules
      $cacheDir = $f.FullName -replace 'marketplaces\\(.+?)\\plugin\\scripts\\mcp-server\.cjs', "cache\`$1"
      $globalCache = Join-Path $env:LOCALAPPDATA "claude\plugins\cache"
      if (Test-Path $globalCache) {
        $nmDirs = Get-ChildItem -Path $globalCache -Recurse -Directory -Filter "node_modules" -ErrorAction SilentlyContinue
        foreach ($nm in $nmDirs) {
          if (Test-Path (Join-Path $nm.FullName "claude-mem")) {
            $mcpNodePath = $nm.FullName
            break
          }
        }
      }
      break
    }
  }

  if ($mcpServer) {
    $mcpServerJson = $mcpServer -replace '\\', '/'
    $mcpNodePathJson = $mcpNodePath -replace '\\', '/'
    $json = @"
{
  "`$schema": "https://opencode.ai/config.json",
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
      "command": ["node", "${mcpServerJson}"],
      "environment": {
        "NODE_PATH": "${mcpNodePathJson}",
        "CLAUDE_MEM_CHROMA_ENABLED": "false"
      },
      "enabled": true,
      "timeout": 10000
    }
  }
}
"@
    Set-Content -Path "$REPO_DIR\opencode.json" -Value $json
    Write-Host "${GREEN}  ✓ opencode.json generated${NC}"
  } else {
    Write-Host "${YELLOW}  ⚠ claude-mem MCP server not found — copy opencode.json.template manually${NC}"
  }
}

# ── 9. Summary ──
Write-Host "${BOLD}${GREEN}"
Write-Host "╔══════════════════════════════════════════════════╗"
Write-Host "║        Setup Complete!                         ║"
Write-Host "╚══════════════════════════════════════════════════╝${NC}"
Write-Host ""
Write-Host "${YELLOW}Next steps:${NC}"
Write-Host "  1. Add API keys:   notepad $REPO_DIR\backend\.env"
Write-Host "  2. Start backend:  python $REPO_DIR\backend\app\main.py"
Write-Host "  3. Open browser:   http://localhost:8000"
Write-Host ""
Write-Host "${YELLOW}opencode Desktop config:${NC}"
Write-Host "  4. Settings → Custom Instructions → Add AGENTS.md + HUMANIZE.md"
Write-Host "  5. Settings → MCP → Add Server → path to claude-mem MCP"
Write-Host "  6. Working directory: $REPO_DIR"
Write-Host ""
Write-Host "${YELLOW}See Android tunnel URL (after git pull):${NC}"
Write-Host "  type $REPO_DIR\Osama\.tunnel-url"
Write-Host ""

Set-Location $REPO_DIR
