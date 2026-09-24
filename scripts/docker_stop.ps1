# ==============================================================================
# EVA Smart Glasses AI — Graceful Docker Stopper (Windows PowerShell)
# ==============================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Stopping EVA Smart Glasses Docker Services...       " -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Cyan

docker compose down

Write-Host ""
Write-Host " [*] All EVA Docker containers stopped safely. Persistent volumes preserved." -ForegroundColor Green
