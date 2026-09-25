# ==============================================================================
# EVA Smart Glasses AI — AWS Infrastructure Variables
# ==============================================================================

variable "aws_region" {
  description = "AWS deployment region (e.g. ap-south-1, us-east-1)"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment name (production, staging, dev)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name prefix for AWS resources"
  type        = string
  default     = "eva-smart-glasses"
}

variable "device_id" {
  description = "Primary IoT Thing device identifier"
  type        = string
  default     = "EVA-GLS-01"
}

variable "vpc_cidr" {
  description = "CIDR block for the dedicated EVA VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "database_name" {
  description = "PostgreSQL RDS database name"
  type        = string
  default     = "eva_db"
}

variable "database_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "eva_admin"
}

variable "database_instance_class" {
  description = "RDS instance class (e.g., db.t4g.micro for cost efficiency)"
  type        = string
  default     = "db.t4g.micro"
}

variable "container_cpu" {
  description = "CPU units for ECS Fargate task (256 = 0.25 vCPU, 512 = 0.5 vCPU)"
  type        = number
  default     = 512
}

variable "container_memory" {
  description = "Memory (MB) for ECS Fargate task (1024 = 1 GB)"
  type        = number
  default     = 1024
}

variable "app_port" {
  description = "FastAPI backend container port"
  type        = number
  default     = 8001
}
