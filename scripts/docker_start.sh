#!/usr/bin/env bash
# ==============================================================================
# EVA Smart Glasses AI — Permanent Docker Production Launcher (Linux/macOS/EC2)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "======================================================"
echo "  EVA Smart Glasses AI — Permanent Docker Launcher   "
echo "======================================================"

# Ensure directories exist
mkdir -p storage/uploads data logs

echo " [*] Launching permanent Docker container stack..."
docker compose up -d --build

echo ""
echo "======================================================"
echo "  EVA Docker Stack is ACTIVE & RUNNING PERMANENTLY!  "
echo "======================================================"
echo " Web Console URL:        http://localhost:8001/"
echo " Caddy Reverse Proxy:    http://localhost:80/"
echo " Healthcheck:            http://localhost:8001/api/v1/health"
echo " Live logs command:      docker compose logs -f"
echo "======================================================"
