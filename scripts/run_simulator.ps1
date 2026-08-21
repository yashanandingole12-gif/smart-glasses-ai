Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting Smart Glasses Laptop Simulator" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

$env:PYTHONPATH = (Get-Location).Path
python simulator/main.py
