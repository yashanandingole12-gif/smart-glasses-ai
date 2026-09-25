# EVA Smart Glasses AI — AWS Production Deployment Architecture

## 1. AWS Architecture Overview

EVA employs a secure, scalable, and cost-controlled cloud architecture:

```mermaid
flowchart TD
    subgraph Edge["ESP32-S3 Smart Glasses (Fleet)"]
        G1["EVA-GLS-01\nX.509 Device Certificate"]
        G2["EVA-GLS-02\nX.509 Device Certificate"]
    end

    subgraph AWSIoT["AWS IoT Core (MQTT / TLS 8883)"]
        Topics["MQTT Topics\neva/{device_id}/telemetry\neva/{device_id}/status\neva/{device_id}/events\neva/{device_id}/commands"]
        Shadow["Device Shadow (desired/reported state)"]
    end

    subgraph BackendCluster["Amazon ECS Fargate (Private Subnet)"]
        ALB["Application Load Balancer\n(Public HTTPS Port 443)"]
        FastAPI["FastAPI Orchestration Core\n(Port 8001)"]
    end

    subgraph AWSServices["AWS Managed Services"]
        S3[("Amazon S3 (Private Bucket)\nMedia, Captures, Documents")]
        RDS[("Amazon RDS PostgreSQL\nRelational Database")]
        Secrets["AWS Secrets Manager\nRuntime Credentials"]
        CW["Amazon CloudWatch Logs\nStructured Audit Events"]
    end

    subgraph Clients["User Endpoints"]
        Android["📱 Android Companion App"]
        Web["💻 Liquid Glass Web Console"]
    end

    Edge -->|MQTT / TLS| AWSIoT
    AWSIoT -->|IoT Rules / Events| FastAPI
    FastAPI -->|Downlink Commands| AWSIoT
    ALB --> FastAPI
    FastAPI --> S3
    FastAPI --> RDS
    FastAPI --> Secrets
    FastAPI --> CW
    Android -->|HTTPS / WSS| ALB
    Web -->|HTTPS / SSE| ALB
```

---

## 2. Required AWS Services

| Service | Purpose | Recommended Free / Low-Cost Tier |
| :--- | :--- | :--- |
| **AWS IoT Core** | Device fleet identity (`EVA-GLS-01`), MQTT messaging, Device Shadows | Free tier (2.25M msgs/mo) |
| **Amazon S3** | Encrypted storage for vision frames, documents, and assets | 5 GB Free Tier |
| **Amazon RDS (PostgreSQL)** | Persistent relational database | `db.t4g.micro` / `db.t3.micro` |
| **AWS Secrets Manager** | Centralized server-side credential management | ~$0.40/secret/mo |
| **Amazon CloudWatch** | Structured JSON logging and alarm metrics | 5 GB ingestion Free Tier |
| **Amazon ECS Fargate** | Serverless backend container runtime | 0.25–0.5 vCPU, 1 GB RAM |
| **Amazon ECR** | Docker image registry | 500 MB Free Tier |
| **Application Load Balancer**| Public SSL termination and traffic routing | 750 hrs Free Tier |

---

## 3. Required IAM Permissions

For automated deployment via Terraform or CI/CD, the deployment IAM role requires:
- `iot:*`
- `s3:*`
- `rds:*`
- `secretsmanager:*`
- `logs:*`
- `ecs:*`
- `ecr:*`
- `elasticloadbalancing:*`
- `iam:PassRole`, `iam:CreateRole`, `iam:AttachRolePolicy`

---

## 4. Environment Variables Configuration

Create a `.env` file for local development or configure Secrets Manager in production:

```ini
# Core Environment
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8001

# AWS Activation (Default is false for local development)
AWS_ENABLED=true
AWS_REGION=ap-south-1
AWS_IOT_ENDPOINT=xxxxxx-ats.iot.ap-south-1.amazonaws.com
AWS_IOT_CLIENT_ID=eva_backend_service
AWS_S3_BUCKET_NAME=eva-smart-glasses-assets-production-xxxx
AWS_SECRETS_NAME=eva-smart-glasses-secrets-production
AWS_CLOUDWATCH_LOG_GROUP=/eva/production/backend
DEFAULT_DEVICE_ID=EVA-GLS-01

# Database Configuration (PostgreSQL in production, SQLite in local dev)
DATABASE_URL=postgresql://eva_admin:PASSWORD@rds-endpoint:5432/eva_db

# LLM & AI Providers
GEMINI_API_KEY=your_gemini_key
DEEPSEEK_API_KEY=your_deepseek_key
```

---

## 5. IoT Setup & Device Provisioning

### 5.1 Device Naming Convention
- Current primary device: `EVA-GLS-01`
- Scalable fleet naming: `EVA-GLS-02`, `EVA-GLS-03`, `EVA-GLS-04`

### 5.2 X.509 Certificate Generation
```bash
# Generate device certificate and private key
aws iot create-keys-and-certificate \
    --set-as-active \
    --certificate-pem-outfile "eva-gls-01.cert.pem" \
    --public-key-outfile "eva-gls-01.public.key" \
    --private-key-outfile "eva-gls-01.private.key"
```

### 5.3 Attach IoT Policy & Thing
```bash
# Attach policy to certificate
aws iot attach-policy \
    --policy-name "eva-smart-glasses-device-policy-production" \
    --target "<CERTIFICATE_ARN>"

# Attach certificate to Thing
aws iot attach-thing-principal \
    --thing-name "EVA-GLS-01" \
    --principal "<CERTIFICATE_ARN>"
```

---

## 6. MQTT Topic Hierarchy

| Topic Pattern | Direction | Purpose |
| :--- | :---: | :--- |
| `eva/{device_id}/telemetry` | Device &rarr; Cloud | Battery, temperature, heap, BLE/Wi-Fi status |
| `eva/{device_id}/status` | Device &rarr; Cloud | Online/offline heartbeat |
| `eva/{device_id}/events` | Device &rarr; Cloud | Wake-word triggers, button taps, low battery |
| `eva/{device_id}/commands` | Cloud &rarr; Device | Downlink instructions (e.g. `CAPTURE_FRAME`, `SET_AUDIO`) |
| `eva/{device_id}/diagnostics`| Device &rarr; Cloud | Audio RMS, mic health, sensor logs |
| `$aws/things/{device_id}/shadow/update` | Bidirectional | Sync desired & reported configuration |

---

## 7. Terraform Deployment Procedure

```bash
cd infra/aws

# 1. Initialize Terraform
terraform init

# 2. Review infrastructure execution plan
terraform plan -var-file="terraform.tfvars.example"

# 3. Apply infrastructure to AWS (once credentials provided)
terraform apply -var-file="terraform.tfvars.example"
```

---

## 8. Rollback Procedure

If a deployed task definition encounters errors:
1. Rollback ECS service to previous task definition:
   ```bash
   aws ecs update-service \
       --cluster eva-smart-glasses-cluster-production \
       --service eva-smart-glasses-service-production \
       --task-definition eva-smart-glasses-task-production:<PREVIOUS_REVISION>
   ```
2. Destroy Terraform resources cleanly if tearing down:
   ```bash
   cd infra/aws && terraform destroy
   ```

---

## 9. Local Development vs. AWS Production

| Feature | Local Development (`AWS_ENABLED=false`) | AWS Production (`AWS_ENABLED=true`) |
| :--- | :--- | :--- |
| **Transport** | In-Memory `LocalMqttTransport` / WebSockets | AWS IoT Core (`AwsIotTransport` TLS 8883) |
| **Storage** | Local Filesystem (`storage/uploads/`) | Amazon S3 (Private with Presigned URLs) |
| **Database** | SQLite (`smart_glasses.db`, `eva_memory.db`) | Amazon RDS PostgreSQL |
| **Secrets** | Local `.env` file | AWS Secrets Manager (with cache) |
| **Logging** | Standard Console JSON | Amazon CloudWatch Logs Group |
