#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# LARA Smart Glasses AI — Docker Deploy Script (Linux/macOS/VPS)
# -----------------------------------------------------------------------------
set -e

echo "=================================================="
echo "  LARA Smart Glasses AI — Docker Deployment"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[!] Docker not found. Installing Docker engine..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
fi

# Ensure storage directories exist
mkdir -p storage captures scratch

echo "[*] Building and starting LARA container..."
docker compose up -d --build

echo ""
echo "[SUCCESS] LARA Smart Glasses AI is hosted and running on Docker!"
echo "  Web Console: http://localhost:8001/web"
echo "  API Docs:    http://localhost:8001/docs"
echo "  Health:      http://localhost:8001/api/v1/health"
