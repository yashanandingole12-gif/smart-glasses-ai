# ==============================================================================
# EVA Smart Glasses AI - Permanent Docker Production Launcher (Windows PowerShell)
# ==============================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host '======================================================' -ForegroundColor Cyan
Write-Host '  EVA Smart Glasses AI - Permanent Docker Launcher    ' -ForegroundColor Green
Write-Host '======================================================' -ForegroundColor Cyan
Write-Host ''

# 1. Verify Docker CLI is available
$dockerCli = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCli) {
    Write-Host ' [ERROR] Docker is not installed or not in system PATH.' -ForegroundColor Red
    Write-Host ' Please install Docker Desktop from https://www.docker.com/products/docker-desktop/' -ForegroundColor Yellow
    exit 1
}

# 2. Check if Docker daemon is running, start Docker Desktop if needed
Write-Host ' [*] Checking Docker Daemon status...' -ForegroundColor Gray
$dockerRunning = $false
try {
    $null = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerRunning = $true
    }
} catch {
    $dockerRunning = $false
}

if (-not $dockerRunning) {
    Write-Host ' [!] Docker Desktop is not running. Attempting to start Docker Desktop...' -ForegroundColor Yellow
    $dockerDesktopPath = 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
    if (Test-Path $dockerDesktopPath) {
        Start-Process $dockerDesktopPath
        Write-Host ' [*] Waiting for Docker Desktop engine to initialize (up to 45 seconds)...' -ForegroundColor Gray
        $retries = 0
        while ($retries -lt 30) {
            Start-Sleep -Seconds 2
            try {
                $null = docker info 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $dockerRunning = $true
                    break
                }
            } catch {}
            $retries++
            Write-Host '.' -NoNewline -ForegroundColor Gray
        }
        Write-Host ''
    }
}

if (-not $dockerRunning) {
    Write-Host ' [WARNING] Docker Daemon is still initializing or Docker Desktop requires manual start.' -ForegroundColor Yellow
    Write-Host ' Please ensure Docker Desktop is running, then re-run this script.' -ForegroundColor White
    exit 1
}

# 3. Create persistent directories if they do not exist
New-Item -ItemType Directory -Force -Path "$ProjectRoot\storage\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProjectRoot\data" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProjectRoot\logs" | Out-Null

# 4. Check if standalone uvicorn is currently holding port 8001
$occupied = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($occupied) {
    $pids = $occupied | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($p in $pids) {
        if ($p -and $p -ne 0 -and $p -ne $PID) {
            Write-Host " [*] Releasing port 8001 from process ID $p..." -ForegroundColor DarkYellow
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Milliseconds 500
}

# 5. Build and run permanent container stack
Write-Host ' [*] Building and launching permanent Docker container stack (restart=unless-stopped)...' -ForegroundColor Cyan
docker compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ''
    Write-Host '======================================================' -ForegroundColor Green
    Write-Host '  EVA Docker Stack is ACTIVE and RUNNING PERMANENTLY! ' -ForegroundColor Green
    Write-Host '======================================================' -ForegroundColor Green
    Write-Host ''
    Write-Host ' Web Console URL:        http://localhost:8001/' -ForegroundColor White
    Write-Host ' Caddy Reverse Proxy:    http://localhost:80/ (or HTTPS on port 443)' -ForegroundColor White
    Write-Host ' Healthcheck Endpoint:   http://localhost:8001/api/v1/health' -ForegroundColor White
    Write-Host ' Swagger API Docs:       http://localhost:8001/docs' -ForegroundColor White
    Write-Host ''
    Write-Host ' To view live container logs:   docker compose logs -f eva-backend' -ForegroundColor Yellow
    Write-Host ' To stop containers gracefully: .\scripts\docker_stop.ps1' -ForegroundColor Yellow
    Write-Host '======================================================' -ForegroundColor Green
} else {
    Write-Host ' [ERROR] Docker Compose failed to start containers. Check logs with docker compose logs.' -ForegroundColor Red
}
