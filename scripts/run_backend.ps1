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

$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload
