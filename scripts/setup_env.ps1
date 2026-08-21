Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Setting up Smart Glasses AI Assistant" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

pip install -r backend/requirements.txt
pip install -r simulator/requirements.txt

Write-Host "`nEnvironment setup complete! Run .\scripts\run_backend.ps1 to start." -ForegroundColor Green
