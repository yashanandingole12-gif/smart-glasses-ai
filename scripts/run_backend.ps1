# Set Working Directory and PYTHONPATH to Project Root automatically
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot
$env:PYTHONPATH = $ProjectRoot

# Auto-clean existing stale processes on port 8001 to prevent WinError 10013
$existingConnections = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($existingConnections) {
    $pids = $existingConnections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($p in $pids) {
        if ($p -and $p -ne 0 -and $p -ne $PID) {
            Write-Host "Releasing port 8001 occupied by previous process ($p)..." -ForegroundColor DarkYellow
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Milliseconds 500
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting Smart Glasses AI FastAPI Backend" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " Open in your Laptop Browser:" -ForegroundColor Yellow
Write-Host " 👉 http://localhost:8001/" -ForegroundColor White
Write-Host ""
Write-Host " Open on your Android Phone:" -ForegroundColor Yellow

$activeIps = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" }
foreach ($netIp in $activeIps) {
    Write-Host (" 👉 http://" + $netIp.IPAddress + ":8001/ (" + $netIp.InterfaceAlias + ")") -ForegroundColor White
}

Write-Host ""
Write-Host " (Note: Do NOT type 0.0.0.0 into web browsers; use localhost or your LAN/Hotspot IP above)" -ForegroundColor DarkGray
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload
