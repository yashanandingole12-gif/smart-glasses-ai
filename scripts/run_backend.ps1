Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting Smart Glasses AI FastAPI Backend" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload
