<#
.SYNOPSIS
  Launch ComplianceHub from Windows.
  Uses WSL if available, falls back to native Python backend.

.PARAMETER ai
  Start with local AI (WSL mode only)
.PARAMETER cloudflare
  Start Cloudflare tunnel (requires cloudflared.exe in PATH or repo)
.PARAMETER serveo
  Serveo tunnel (WSL mode only)
.PARAMETER serveoSubdomain
  Fixed Serveo subdomain (WSL mode only)
.PARAMETER noTunnel
  Localhost only
.PARAMETER help
  Show help
#>

param(
  [switch]$ai,
  [switch]$cloudflare,
  [switch]$serveo,
  [string]$serveoSubdomain = "",
  [switch]$noTunnel,
  [switch]$help
)

$BOLD = [char]27 + "[1m"
$GREEN = [char]27 + "[32m"
$YELLOW = [char]27 + "[33m"
$CYAN = [char]27 + "[36m"
$RED = [char]27 + "[31m"
$NC = [char]27 + "[0m"

$ROOT_DIR = $PSScriptRoot
$URL_FILE = "$ROOT_DIR\Osama\.tunnel-url"
$MEMORY_FILE = "$ROOT_DIR\Osama\MEMORY.md"

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

# ── Git sync helpers ──
function Git-Sync-Pull {
  param([string]$gitPath)
  Write-Host "${CYAN}Syncing from git...${NC}"
  & $gitPath -C $ROOT_DIR stash 2>&1 | Out-Null
  & $gitPath -C $ROOT_DIR pull --rebase --autostash 2>&1 | Out-Null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "${GREEN}  ✓ Pulled latest${NC}"
  } else {
    & $gitPath -C $ROOT_DIR pull 2>&1 | Out-Null
    Write-Host "${YELLOW}  ⚠ Pull had issues (offline or no remote)${NC}"
  }
}

function Git-Sync-Exit {
  param([string]$gitPath)
  Write-Host "${YELLOW}Syncing changes to git...${NC}"
  $hasChanges = $false
  & $gitPath -C $ROOT_DIR diff --quiet HEAD -- "Osama/MEMORY.md" 2>$null
  if ($LASTEXITCODE -ne 0) { $hasChanges = $true }
  & $gitPath -C $ROOT_DIR diff --quiet HEAD -- "Osama/.tunnel-url" 2>$null
  if ($LASTEXITCODE -ne 0) { $hasChanges = $true }

  if ($hasChanges) {
    & $gitPath -C $ROOT_DIR add "Osama/MEMORY.md" "Osama/.tunnel-url"
    & $gitPath -C $ROOT_DIR commit -m "sync: MEMORY.md + tunnel URL [Windows]" 2>$null | Out-Null
    & $gitPath -C $ROOT_DIR push 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
      Write-Host "${GREEN}  ✓ Synced to git${NC}"
    } else {
      Write-Host "${YELLOW}  ⚠ Push failed (credentials may need setup)${NC}"
    }
  } else {
    Write-Host "  - No new changes${NC}"
  }
}

# ── Help ──
if ($help) {
  Write-Host "Usage: .\go.ps1 [-cloudflare|-noTunnel]"
  Write-Host "  Default: no tunnel, localhost only"
  Write-Host "  WSL mode: also supports -ai -serveo -serveoSubdomain"
  exit 0
}

# ── Check for WSL ──
$HAS_WSL = $false
try {
  $wslCheck = wsl --status 2>&1
  if ($LASTEXITCODE -eq 0) { $HAS_WSL = $true }
} catch {}

# ── WSL MODE: delegate to go.sh ──
if ($HAS_WSL) {
  $WSL_DISTRO = "Ubuntu"
  $wslList = wsl -l -q 2>$null
  if ($wslList -match "Ubuntu") {
    $WSL_DISTRO = "Ubuntu"
  } elseif ($wslList -match "docker-desktop") {
    $first = ($wslList -split "`n" | Where-Object { $_ -ne "" -and $_ -notlike "*docker*" -and $_ -notlike "*Windows*" } | Select-Object -First 1)
    if ($first) { $WSL_DISTRO = $first.Trim() }
  }

  $WSL_REPO = ""
  $wslPath = wsl -d $WSL_DISTRO -e wslpath "$ROOT_DIR" 2>$null
  if ($LASTEXITCODE -eq 0 -and $wslPath) {
    $WSL_REPO = $wslPath.Trim()
  } else {
    $drive = $ROOT_DIR.Substring(0,1).ToLower()
    $rest = $ROOT_DIR.Substring(2) -replace '\\', '/'
    $WSL_REPO = "/mnt/$drive$rest"
  }

  $ARGS = @()
  if ($ai) { $ARGS += "--ai" }
  if ($cloudflare -and -not $serveo) { $ARGS += "--cloudflare" }
  if ($serveo) { $ARGS += "--serveo" }
  if ($serveoSubdomain) { $ARGS += "--serveo-subdomain=$serveoSubdomain" }
  if ($noTunnel) { $ARGS += "--no-tunnel" }

  $CMD = "cd '$WSL_REPO' && bash go.sh $($ARGS -join ' ')"

  Write-Host "${CYAN}ComplianceHub — WSL mode ($WSL_DISTRO)${NC}"
  Write-Host "  Repo: $WSL_REPO"
  if ($ARGS.Count -gt 0) { Write-Host "  Args: $($ARGS -join ' ')" }
  Write-Host ""

  wsl -d $WSL_DISTRO -e bash -c $CMD

  $URL = wsl -d $WSL_DISTRO -e sh -c "cat /tmp/compliancehub-url.txt 2>/dev/null || cat $WSL_REPO/Osama/.tunnel-url 2>/dev/null" 2>$null
  if ($URL) {
    Write-Host ""
    Write-Host "Tunnel URL: $URL" -ForegroundColor Green
  }
  exit 0
}

# ── NATIVE MODE (no WSL) ──
Write-Host "${CYAN}ComplianceHub — native mode${NC}"
Write-Host ""

# ── Auto-sync on start ──
$GIT_PATH = Find-Git
if ($GIT_PATH) {
  Git-Sync-Pull -gitPath $GIT_PATH
} else {
  Write-Host "${YELLOW}  ⚠ Git not found — skipping sync${NC}"
}

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host "${RED}Python not found. Install Python and add to PATH.${NC}"
  exit 1
}

$BACKEND_DIR = "$ROOT_DIR\backend"
if (-not (Test-Path "$BACKEND_DIR\app\main.py")) {
  Write-Host "${RED}Backend not found at $BACKEND_DIR. Run from ComplianceHub repo root.${NC}"
  exit 1
}

# ── Start backend ──
Write-Host "Starting backend on http://localhost:8000 ..."
$pythonArgs = @("-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000")
$backendProcess = Start-Process -FilePath "python" -ArgumentList $pythonArgs -WorkingDirectory $BACKEND_DIR -WindowStyle Hidden -PassThru -RedirectStandardOutput "$ROOT_DIR\.backend.log" -RedirectStandardError "$ROOT_DIR\.backend.err.log"
Start-Sleep -Seconds 2

# Check if it started
$backendRunning = Get-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
if (-not $backendRunning) {
  Write-Host "${RED}Backend failed to start. Check .backend.err.log${NC}"
  exit 1
}
Write-Host "${GREEN}  ✓ Backend started (PID: $($backendProcess.Id))${NC}"

# ── Cloudflare tunnel (optional) ──
$CLOUDFLARED = "cloudflared.exe"
if (-not (Get-Command $CLOUDFLARED -ErrorAction SilentlyContinue)) {
  $CLOUDFLARED = "$ROOT_DIR\cloudflared.exe"
}

$TUNNEL_URL = ""
if ($cloudflare -and (Test-Path $CLOUDFLARED)) {
  Write-Host "Starting Cloudflare tunnel..."
  $tunnelArgs = @("tunnel", "--url", "http://localhost:8000", "--protocol", "http2")
  $tunnelProcess = Start-Process -FilePath $CLOUDFLARED -ArgumentList $tunnelArgs -WindowStyle Hidden -PassThru -RedirectStandardOutput "$ROOT_DIR\.tunnel.log" -RedirectStandardError "$ROOT_DIR\.tunnel.err.log"
  Start-Sleep -Seconds 3
  
  $TUNNEL_URL = "http://localhost:8000"
  Write-Host "${GREEN}  ✓ Tunnel starting... Check .tunnel.log for URL${NC}"
  Write-Host "${YELLOW}  Run 'type $ROOT_DIR\.tunnel.log | findstr try' to get the URL${NC}"
} elseif ($cloudflare) {
  Write-Host "${YELLOW}  ⚠ cloudflared.exe not found. Download from:${NC}"
  Write-Host "     https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
  Write-Host "     Save to $ROOT_DIR\cloudflared.exe"
}

# ── Save URL ──
if ($TUNNEL_URL) {
  Set-Content -Path $URL_FILE -Value $TUNNEL_URL -NoNewline
}

# ── Print info ──
Write-Host ""
Write-Host "${GREEN}${BOLD}ComplianceHub is running${NC}"
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  Status:   http://localhost:8000/api/health"
Write-Host "  PID:      $($backendProcess.Id)"
Write-Host ""
Write-Host "${YELLOW}Git sync:${NC}"
Write-Host "  bash sync.sh   (or manually: git pull, git push)"
Write-Host ""
Write-Host "${YELLOW}Android tunnel URL (after sync):${NC}"
if (Test-Path $URL_FILE) {
  $url = Get-Content $URL_FILE -TotalCount 1
  Write-Host "  $url"
} else {
  Write-Host "  Run 'git pull' then 'type Osama\.tunnel-url'"
}
Write-Host ""
Write-Host "Press Enter to stop the backend..."
Read-Host

# ── Cleanup ──
Write-Host "Stopping..."
# Auto-sync on exit
if ($GIT_PATH) {
  Git-Sync-Exit -gitPath $GIT_PATH
}
Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
if ($tunnelProcess) { Stop-Process -Id $tunnelProcess.Id -Force -ErrorAction SilentlyContinue }
Write-Host "${GREEN}Done${NC}"
