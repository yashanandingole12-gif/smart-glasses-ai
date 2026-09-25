# ==============================================================================
# EVA Smart Glasses AI — AWS Terraform Outputs
# ==============================================================================

output "aws_region" {
  description = "Configured AWS Region"
  value       = var.aws_region
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS Name (Backend API Endpoint)"
  value       = module.ecs.alb_dns_name
}

output "ecr_repository_url" {
  description = "Amazon ECR Docker Repository URL"
  value       = module.ecs.ecr_repository_url
}

output "iot_endpoint_command" {
  description = "CLI command to retrieve AWS IoT Core endpoint"
  value       = "aws iot describe-endpoint --endpoint-type iot:Data-ATS"
}

output "s3_bucket_name" {
  description = "Private S3 Bucket Name for EVA Assets & Documents"
  value       = module.s3.bucket_name
}

output "rds_endpoint" {
  description = "Amazon RDS PostgreSQL Database Endpoint"
  value       = module.rds.rds_endpoint
}

output "secrets_manager_arn" {
  description = "AWS Secrets Manager Secret ARN"
  value       = module.secrets.secrets_arn
}

output "cloudwatch_log_group" {
  description = "CloudWatch Log Group Name"
  value       = module.cloudwatch.log_group_name
}
