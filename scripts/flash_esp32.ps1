# XIAO ESP32-S3 Sense One-Click Flash & Monitor Script

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " 👓 Flashing Seeed Studio XIAO ESP32-S3 Sense" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Locate project root and firmware dir dynamically
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$firmwareDir = Join-Path $projectRoot "firmware\esp32-s3"

# Check if board is plugged in
$comPorts = [System.IO.Ports.SerialPort]::GetPortNames()
if ($comPorts.Count -eq 0) {
    Write-Host "⚠️ Warning: No active COM ports detected. Please ensure your XIAO ESP32-S3 is plugged into USB." -ForegroundColor Yellow
} else {
    Write-Host "🔍 Detected COM Port(s): $($comPorts -join ', ')" -ForegroundColor Green
}

Write-Host "`n🚀 Building and uploading firmware..." -ForegroundColor Yellow
python -m platformio run -e seeed_xiao_esp32s3 -d "$firmwareDir" -t upload

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Firmware successfully uploaded to XIAO ESP32-S3 Sense!" -ForegroundColor Green
    Write-Host "Opening live Serial Monitor (Press Ctrl+C to exit)..." -ForegroundColor Cyan
    python -m platformio device monitor -d "$firmwareDir" -b 115200
} else {
    Write-Host "`n❌ Upload failed. Please check if:" -ForegroundColor Red
    Write-Host "  1. The USB-C cable is securely connected and supports data." -ForegroundColor Yellow
    Write-Host "  2. If the board is busy or not responding, hold the 'B' (BOOT) button, tap 'R' (RESET), then release 'B'." -ForegroundColor Yellow
}
