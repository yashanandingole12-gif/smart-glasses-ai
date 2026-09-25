# -----------------------------------------------------------------------------
# EVA Smart Glasses AI - Docker Deploy Script (PowerShell)
# -----------------------------------------------------------------------------
param (
    [switch]$Rebuild,
    [switch]$Logs
)

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  EVA Smart Glasses AI - Docker Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Auto-detect and include Docker Desktop paths in PATH if not already present
$possibleDockerPaths = @(
    "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin",
    "$env:ProgramFiles\Docker\Docker\resources\bin",
    "$env:ProgramFiles\Docker\Docker",
    "C:\Program Files\Docker\Docker\resources\bin"
)

foreach ($dir in $possibleDockerPaths) {
    if (Test-Path "$dir\docker.exe") {
        if ($env:PATH -notlike "*$dir*") {
            $env:PATH = "$dir;$env:PATH"
            Write-Host "[*] Added Docker path to environment: $dir" -ForegroundColor DarkGray
        }
    }
}

# Check if Docker is available
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Host ""
    Write-Host "[ERROR] Docker is installed but could not be located in system PATH." -ForegroundColor Red
    Write-Host "Please ensure Docker Desktop is running." -ForegroundColor Yellow
    Exit 1
}

# Create storage and capture directories
if (-not (Test-Path "storage")) { New-Item -ItemType Directory -Path "storage" | Out-Null }
if (-not (Test-Path "captures")) { New-Item -ItemType Directory -Path "captures" | Out-Null }

Write-Host "[*] Docker Engine detected: $(docker --version)" -ForegroundColor Green

if ($Rebuild) {
    Write-Host "[*] Building and starting container with fresh cache..." -ForegroundColor Yellow
    docker compose up -d --build
} else {
    Write-Host "[*] Launching container via Docker Compose..." -ForegroundColor Green
    docker compose up -d
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] EVA Smart Glasses AI is running on Docker!" -ForegroundColor Green
    Write-Host "  Web Console: http://localhost:8001/web" -ForegroundColor Cyan
    Write-Host "  API Docs:    http://localhost:8001/docs" -ForegroundColor Cyan
    Write-Host "  Health:      http://localhost:8001/api/v1/health" -ForegroundColor Cyan
    
    if ($Logs) {
        docker compose logs -f
    }
} else {
    Write-Host "[ERROR] Docker Compose failed to start the container." -ForegroundColor Red
}
