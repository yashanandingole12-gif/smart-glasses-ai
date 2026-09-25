# ==============================================================================
# EVA Smart Glasses AI — Master AWS Infrastructure (Terraform)
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      System      = "EVA-Smart-Glasses-AI"
    }
  }
}

# ------------------------------------------------------------------------------
# 1. Networking (VPC, Subnets, Security Groups)
# ------------------------------------------------------------------------------
module "networking" {
  source       = "./modules/networking"
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
  app_port     = var.app_port
}

# ------------------------------------------------------------------------------
# 2. AWS IoT Core (Thing EVA-GLS-01, Fleet Group, IoT Policy, Rules)
# ------------------------------------------------------------------------------
module "iot_core" {
  source       = "./modules/iot_core"
  project_name = var.project_name
  environment  = var.environment
  device_id    = var.device_id
}

# ------------------------------------------------------------------------------
# 3. Private S3 Storage (Documents, Vision Captures, Assets)
# ------------------------------------------------------------------------------
module "s3" {
  source       = "./modules/s3"
  project_name = var.project_name
  environment  = var.environment
}

# ------------------------------------------------------------------------------
# 4. Amazon RDS PostgreSQL Database
# ------------------------------------------------------------------------------
module "rds" {
  source                  = "./modules/rds"
  project_name            = var.project_name
  environment             = var.environment
  database_name           = var.database_name
  database_username       = var.database_username
  database_instance_class = var.database_instance_class
  vpc_id                  = module.networking.vpc_id
  private_subnet_ids      = module.networking.private_subnet_ids
  ecs_security_group_id   = module.networking.ecs_security_group_id
}

# ------------------------------------------------------------------------------
# 5. AWS Secrets Manager (API Keys & Credentials)
# ------------------------------------------------------------------------------
module "secrets" {
  source       = "./modules/secrets"
  project_name = var.project_name
  environment  = var.environment
}

# ------------------------------------------------------------------------------
# 6. CloudWatch Observability & Logging
# ------------------------------------------------------------------------------
module "cloudwatch" {
  source       = "./modules/cloudwatch"
  project_name = var.project_name
  environment  = var.environment
}

# ------------------------------------------------------------------------------
# 7. ECS Fargate Backend Deployment & ECR
# ------------------------------------------------------------------------------
module "ecs" {
  source                = "./modules/ecs"
  project_name          = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  app_port              = var.app_port
  container_cpu         = var.container_cpu
  container_memory      = var.container_memory
  vpc_id                = module.networking.vpc_id
  public_subnet_ids     = module.networking.public_subnet_ids
  private_subnet_ids    = module.networking.private_subnet_ids
  alb_security_group_id = module.networking.alb_security_group_id
  ecs_security_group_id = module.networking.ecs_security_group_id
  s3_bucket_arn         = module.s3.bucket_arn
  secrets_arn           = module.secrets.secrets_arn
  log_group_name        = module.cloudwatch.log_group_name
}
