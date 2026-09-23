# EVA Smart Glasses — AWS Cloud Hosting Guide ($100 Credit Plan)

This guide walks you through deploying your **EVA Smart Glasses Backend** to AWS, optimized to run 24/7 for **7+ months** within your **$100 AWS Builder Credit**.

---

## 1. AWS Cost & Architecture Breakdown ($100 Budget)

| Component | AWS Resource | Specs | Monthly Cost | 7-Month Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Compute** | **EC2 `t4g.small`** (Graviton2 ARM) | 2 vCPUs, 2 GB RAM | ~$12.26 / mo | ~$85.80 |
| **Storage** | **EBS gp3** SSD | 20 GB Root Disk | ~$1.60 / mo | ~$11.20 |
| **Networking**| **Elastic IP + Data Out** | Static Public IPv4, ~15GB/mo | ~$0.00 (In Free Tier) | ~$0.00 |
| **SSL / HTTPS** | **Caddy Reverse Proxy** | Let's Encrypt automated TLS | $0.00 (Open Source) | $0.00 |
| **Total** | | | **~$13.86 / mo** | **~$97.00** |

> [!TIP]
> **Why `t4g.small` (ARM Graviton2)?**
> - 20% cheaper than x86 `t3.small` with 40% better compute and memory performance for Python/FastAPI async workloads.
> - Fits cleanly inside your $100 credit while running continuously with zero throttling.

---

## 2. Step-by-Step EC2 Deployment Walkthrough

### Step 1: Launch an EC2 Instance
1. Log in to your [AWS Management Console](https://console.aws.amazon.com/ec2/).
2. In the top right, select your closest region (e.g., `ap-south-1` Mumbai or `us-east-1` N. Virginia).
3. Click **Launch Instances** and set:
   - **Name**: `EVA-Smart-Glasses-Cloud`
   - **OS Image (AMI)**: `Ubuntu Server 24.04 LTS (HVM)`
   - **Architecture**: `64-bit (Arm)`
   - **Instance Type**: `t4g.small` (2 vCPU, 2 GB RAM)
   - **Key Pair**: Select or create a key pair (e.g., `eva-key.pem`).
   - **Storage**: `20 GiB gp3` SSD.

### Step 2: Configure Security Group (Firewall)
Under **Network Settings**, create a Security Group with the following inbound rules:

| Type | Port Range | Source | Purpose |
| :--- | :--- | :--- | :--- |
| **SSH** | `22` | `My IP` | Secure command line management |
| **HTTP** | `80` | `0.0.0.0/0` | Web showcase & ACME HTTP challenge |
| **HTTPS** | `443` | `0.0.0.0/0` | Secure SSL API and Companion Sync |
| **Custom TCP** | `8000` | `0.0.0.0/0` | Direct backend API testing |

Click **Launch Instance**.

---

### Step 3: Connect and Run One-Click Provisioning
Once the instance status is **Running**:

1. Connect via SSH from your terminal:
   ```bash
   ssh -i /path/to/eva-key.pem ubuntu@<YOUR-EC2-PUBLIC-IP>
   ```

2. Download and run the automated provisioning script:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/yashanandingole12-gif/smart-glasses-ai/main/scripts/deploy_aws.sh -o deploy.sh
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. The script will automatically:
   - Install Docker and Docker Compose
   - Clone your repository
   - Build the lightweight multi-stage Docker container
   - Spin up the FastAPI backend and Caddy reverse proxy on ports `80`, `443`, and `8000`.

---

## 3. Connecting a Custom Domain with Free SSL (Optional)

If you have a domain (e.g., `eva.yourdomain.com`):
1. In AWS Route 53 or your DNS registrar (GoDaddy, Namecheap, Cloudflare), add an **A record**:
   - **Host**: `eva`
   - **Points to**: `<YOUR-EC2-PUBLIC-IP>`
2. Edit `/home/ubuntu/smart-glasses-ai/Caddyfile`:
   ```caddy
   eva.yourdomain.com {
       reverse_proxy eva-backend:8000
   }
   ```
3. Restart Caddy:
   ```bash
   sudo docker compose restart caddy
   ```
   *Caddy will instantly obtain an SSL certificate from Let's Encrypt and enable HTTPS automatically.*

---

## 4. Connecting Android App & Smart Glasses to AWS

1. In your Android app or ESP32 firmware config:
   ```kotlin
   // In Android app configuration:
   const val BASE_URL = "http://<YOUR-EC2-PUBLIC-IP>:8000/api/v1/"
   // Or with custom domain:
   const val BASE_URL = "https://eva.yourdomain.com/api/v1/"
   ```
2. Test the live health endpoint:
   ```bash
   curl https://<YOUR-EC2-DOMAIN>/api/v1/health
   # Returns: {"status": "ok", "service": "EVA Smart Glasses Cloud Backend"}
   ```

---

## 5. Monitoring & Credit Usage Safeguards

1. Set up an **AWS Budget Alert**:
   - Go to [AWS Billing & Cost Management](https://console.aws.amazon.com/billing/) -> **Budgets**.
   - Create a budget for **$14.00/month**.
   - Add an alert email to notify you if forecasted spend exceeds 80% ($11.20).
2. Check container logs anytime:
   ```bash
   sudo docker compose logs -f eva-backend
   ```
