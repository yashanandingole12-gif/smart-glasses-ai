#!/usr/bin/env bash
# ==============================================================================
# EVA Smart Glasses AI — Graceful Docker Stopper (Linux/macOS/EC2)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "======================================================"
echo "  Stopping EVA Smart Glasses Docker Services...       "
echo "======================================================"

docker compose down

echo " [*] All EVA Docker containers stopped. Volumes preserved."
