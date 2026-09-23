#!/usr/bin/env bash
# ==============================================================================
# EVA Smart Glasses — Automated AWS EC2 One-Click Provisioning Script
# Target: AWS Ubuntu 22.04 / 24.04 LTS (t4g.small ARM64 or t3.small x86_64)
# Budget: ~$10-$14/month (Fully covered by $100 AWS Builder Credit for 7+ months)
# ==============================================================================

set -e

echo "=========================================================="
echo "   EVA SMART GLASSES — AWS CLOUD BACKEND PROVISIONING    "
echo "=========================================================="

# 1. Update System Packages
echo "[1/5] Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y

# 2. Install Docker & Docker Compose
echo "[2/5] Installing Docker Engine & Docker Compose Plugin..."
if ! command -v docker &> /dev/null; then
    sudo apt-get install -y ca-certificates curl gnupg lsb-release git
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker $USER
    echo "Docker installed successfully."
fi

# 3. Clone / Update Repository
REPO_DIR="/home/$USER/smart-glasses-ai"
if [ ! -d "$REPO_DIR" ]; then
    echo "[3/5] Cloning repository into $REPO_DIR..."
    git clone https://github.com/yashanandingole12-gif/smart-glasses-ai.git "$REPO_DIR"
else
    echo "[3/5] Repository already exists. Pulling latest main..."
    cd "$REPO_DIR" && git pull origin main
fi

cd "$REPO_DIR"

# 4. Configure Environment Variables
echo "[4/5] Setting up environment variables..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat <<EOF > .env
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
TAVILY_API_KEY=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
# Insert other API keys below as desired
# OPENAI_API_KEY=
# GEMINI_API_KEY=
# GROQ_API_KEY=
EOF
    echo ".env created. Please add any required API keys."
fi

# 5. Build and Launch Containers via Docker Compose
echo "[5/5] Building and launching EVA containers..."
sudo docker compose down --remove-orphans || true
sudo docker compose build --pull
sudo docker compose up -d

echo "=========================================================="
echo "   EVA BACKEND IS NOW RUNNING LIVE IN THE CLOUD!         "
echo "   Endpoint: http://$(curl -s http://checkip.amazonaws.com):8000"
echo "   Dashboard: http://$(curl -s http://checkip.amazonaws.com)/"
echo "=========================================================="
