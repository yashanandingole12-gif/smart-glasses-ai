# AWS Cloud Deployment Readiness Checklist

This checklist tracks the readiness and operational status for deploying EVA to AWS.

### 1. Account & Security Foundations
- [ ] AWS account selected & root MFA enabled
- [ ] Deployment IAM user/role created with least privilege
- [ ] AWS Region selected (e.g., `ap-south-1` or `us-east-1`)
- [ ] Zero static credentials in code or repository confirmed

### 2. Infrastructure as Code (Terraform)
- [ ] Terraform CLI installed (`>= 1.5.0`)
- [ ] `infra/aws/variables.tf` configured
- [ ] `terraform plan` executed with clean zero-drift output
- [ ] `terraform apply` completed

### 3. AWS IoT Core & Device Identity
- [ ] AWS IoT Core enabled in target region
- [ ] Thing Group `eva-smart-glasses-fleet` created
- [ ] Thing `EVA-GLS-01` created
- [ ] Device Policy `eva-smart-glasses-device-policy` attached
- [ ] X.509 Device Certificate generated & activated
- [ ] Endpoint verified via `aws iot describe-endpoint --endpoint-type iot:Data-ATS`

### 4. Storage & Database
- [ ] S3 Bucket created with Public Access Block enabled
- [ ] S3 Server-Side Encryption (AES-256) enabled
- [ ] RDS PostgreSQL instance provisioned (`eva_db`)
- [ ] Database migrations executed against RDS

### 5. Secrets & Observability
- [ ] Secrets Manager secret populated with runtime API keys
- [ ] CloudWatch Log Group `/eva/production/backend` created
- [ ] CloudWatch error metric filters and alarms established

### 6. Backend Deployment (ECS Fargate)
- [ ] Amazon ECR repository created
- [ ] Production Docker image built and pushed to ECR
- [ ] ECS Fargate task definition registered
- [ ] Application Load Balancer health check passing (`/api/v1/health` &rarr; `200 OK`)

### 7. End-to-End Client Connectivity
- [ ] Web Console connected over ALB HTTPS domain
- [ ] Android App connected via In-App Server URL
- [ ] ESP32 Smart Glasses connected via X.509 cert to AWS IoT Core
- [ ] Bidirectional telemetry and command execution verified
