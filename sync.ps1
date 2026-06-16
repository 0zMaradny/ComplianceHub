<#
.SYNOPSIS
  One-command sync: pull → commit MEMORY.md + tunnel URL → push
  PowerShell equivalent of sync.sh for Windows.
#>

$REPO_DIR = $PSScriptRoot
$URL_FILE = "$REPO_DIR\Osama\.tunnel-url"
$MEMORY_FILE = "$REPO_DIR\Osama\MEMORY.md"

Write-Host "Syncing ComplianceHub..." -ForegroundColor Cyan
Write-Host ""

# Pull latest
Write-Host "Pulling from git..."
git -C $REPO_DIR pull --rebase --autostash 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
  Write-Host "  ✓ Pulled latest" -ForegroundColor Green
} else {
  Write-Host "  ⚠ Pull had issues, trying again..." -ForegroundColor Yellow
  git -C $REPO_DIR pull 2>&1 | Out-Null
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
git -C $REPO_DIR diff --quiet HEAD -- "Osama/MEMORY.md" 2>$null
if ($LASTEXITCODE -ne 0) { $hasChanges = $true }

git -C $REPO_DIR diff --quiet HEAD -- "Osama/.tunnel-url" 2>$null
if ($LASTEXITCODE -ne 0) { $hasChanges = $true }

if ($hasChanges) {
  git -C $REPO_DIR add "Osama/MEMORY.md" "Osama/.tunnel-url"
  git -C $REPO_DIR commit -m "sync: MEMORY.md + tunnel URL update [Windows]" 2>$null | Out-Null
  Write-Host "  ✓ Committed changes" -ForegroundColor Green
} else {
  Write-Host "  - No new changes" -ForegroundColor Gray
}

# Push
Write-Host "Pushing to git..."
git -C $REPO_DIR push 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
  Write-Host "  ✓ Pushed" -ForegroundColor Green
} else {
  Write-Host "  ⚠ Push failed — credentials may need setup" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done." -ForegroundColor Cyan
