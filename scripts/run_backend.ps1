Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting Smart Glasses AI FastAPI Backend" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " Open in your Laptop Browser:" -ForegroundColor Yellow
Write-Host " 👉 http://localhost:8001/" -ForegroundColor White
Write-Host ""
Write-Host " Open on your Android Phone (Wi-Fi LAN):" -ForegroundColor Yellow
Write-Host " 👉 http://192.168.243.120:8001/" -ForegroundColor White
Write-Host ""
Write-Host " (Note: Do NOT type 0.0.0.0 into web browsers; use localhost or your LAN IP above)" -ForegroundColor DarkGray
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload
