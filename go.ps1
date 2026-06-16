<#
.SYNOPSIS
  Launch ComplianceHub from Windows via WSL.
  Thin wrapper around go.sh running inside WSL (Ubuntu).

.PARAMETER ai
  Start with local AI
.PARAMETER cloudflare
  Cloudflare tunnel only
.PARAMETER serveo
  Serveo tunnel only
.PARAMETER serveoSubdomain
  Fixed Serveo subdomain (use with -serveo)
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

# ── Help ──
if ($help) {
  Write-Host "Usage: .\go.ps1 [-ai] [-cloudflare|-serveo|-noTunnel] [-serveoSubdomain NAME]"
  Write-Host "  Default: auto tunnel, no AI"
  exit 0
}

# ── Detect WSL distro ──
$WSL_DISTRO = "Ubuntu"
$wslList = wsl -l -q 2>$null
if ($wslList -match "Ubuntu") {
  $WSL_DISTRO = "Ubuntu"
} elseif ($wslList -match "docker-desktop") {
  # Skip docker-desktop, try first real distro
  $first = ($wslList -split "`n" | Where-Object { $_ -ne "" -and $_ -notlike "*docker*" -and $_ -notlike "*Windows*" } | Select-Object -First 1)
  if ($first) { $WSL_DISTRO = $first.Trim() }
}

# ── Resolve repo path ──
$WIN_PATH = $PSScriptRoot
$WSL_REPO = ""
$wslPath = wsl -d $WSL_DISTRO -e wslpath "$WIN_PATH" 2>$null
if ($LASTEXITCODE -eq 0 -and $wslPath) {
  $WSL_REPO = $wslPath.Trim()
}
if (-not $WSL_REPO) {
  # Fallback: assume mounted at /mnt/c/...
  $drive = $WIN_PATH.Substring(0,1).ToLower()
  $rest = $WIN_PATH.Substring(2) -replace '\\', '/'
  $WSL_REPO = "/mnt/$drive$rest"
}

# ── Build args ──
$ARGS = @()
if ($ai) { $ARGS += "--ai" }
if ($cloudflare) { $ARGS += "--cloudflare" }
if ($serveo) { $ARGS += "--serveo" }
if ($serveoSubdomain) { $ARGS += "--serveo-subdomain=$serveoSubdomain" }
if ($noTunnel) { $ARGS += "--no-tunnel" }

$CMD = "cd '$WSL_REPO' && bash go.sh $($ARGS -join ' ')"

Write-Host "ComplianceHub — launching via WSL ($WSL_DISTRO)" -ForegroundColor Cyan
Write-Host "  Repo: $WSL_REPO" -ForegroundColor Gray
if ($ARGS.Count -gt 0) {
  Write-Host "  Args: $($ARGS -join ' ')" -ForegroundColor Gray
}
Write-Host ""

# ── Launch ──
wsl -d $WSL_DISTRO -e bash -c $CMD

# ── Read back tunnel URL ──
$URL = wsl -d $WSL_DISTRO -e sh -c "cat /tmp/compliancehub-url.txt 2>/dev/null || cat $WSL_REPO/Osama/.tunnel-url 2>/dev/null" 2>$null
if ($URL) {
  Write-Host ""
  Write-Host "Tunnel URL: $URL" -ForegroundColor Green
}
