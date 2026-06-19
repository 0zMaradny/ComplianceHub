<#
.SYNOPSIS
  One-command sync: pull → commit MEMORY.md + tunnel URL → push
  PowerShell equivalent of sync.sh for Windows.
#>

$REPO_DIR = $PSScriptRoot
$URL_FILE = "$REPO_DIR\Osama\.tunnel-url"
$MEMORY_FILE = "$REPO_DIR\Osama\MEMORY.md"

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
    $matches = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Sort-Object -Property CreationTime -Descending
    if ($matches) { return $matches[0].FullName }
  }
  $cmd = Get-Command git -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  return $null
}

$GIT_PATH = Find-Git
if (-not $GIT_PATH) {
  Write-Host "Git not found. Use GitHub Desktop manually or install PortableGit." -ForegroundColor Red
  exit 1
}

Write-Host "Syncing ComplianceHub..." -ForegroundColor Cyan
Write-Host ""

# Pull latest
Write-Host "Pulling from git..."
& $GIT_PATH -C $REPO_DIR pull --rebase --autostash 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
  Write-Host "  ✓ Pulled latest" -ForegroundColor Green
} else {
  Write-Host "  ⚠ Pull had issues, trying again..." -ForegroundColor Yellow
  & $GIT_PATH -C $REPO_DIR pull 2>&1 | Out-Null
}

# Read Android tunnel URL
if (Test-Path $URL_FILE) {
  $url = Get-Content $URL_FILE -TotalCount 1
  if ($url) {
    Write-Host "  Android tunnel: $url" -ForegroundColor Green
  }
}

# Commit MEMORY.md + tunnel URL
$hasChanges = $false
& $GIT_PATH -C $REPO_DIR diff --quiet HEAD -- "Osama/MEMORY.md" 2>$null
if ($LASTEXITCODE -ne 0) { $hasChanges = $true }

& $GIT_PATH -C $REPO_DIR diff --quiet HEAD -- "Osama/.tunnel-url" 2>$null
if ($LASTEXITCODE -ne 0) { $hasChanges = $true }

if ($hasChanges) {
  & $GIT_PATH -C $REPO_DIR add "Osama/MEMORY.md" "Osama/.tunnel-url"
  & $GIT_PATH -C $REPO_DIR commit -m "sync: MEMORY.md + tunnel URL update [Windows]" 2>$null | Out-Null
  Write-Host "  ✓ Committed changes" -ForegroundColor Green
} else {
  Write-Host "  - No new changes" -ForegroundColor Gray
}

# Push
Write-Host "Pushing to git..."
& $GIT_PATH -C $REPO_DIR push 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
  Write-Host "  ✓ Pushed" -ForegroundColor Green
} else {
  Write-Host "  ⚠ Push failed — credentials may need setup" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done." -ForegroundColor Cyan
