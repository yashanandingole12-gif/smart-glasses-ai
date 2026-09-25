# ==============================================================================
# Amazon RDS PostgreSQL Database Module
# ==============================================================================

variable "project_name" { type = string }
variable "environment" { type = string }
variable "database_name" { type = string }
variable "database_username" { type = string }
variable "database_instance_class" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "ecs_security_group_id" { type = string }

resource "random_password" "db_password" {
  length  = 24
  special = false
}

resource "aws_db_subnet_group" "db_subnets" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = { Name = "${var.project_name}-db-subnets" }
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Allow inbound PostgreSQL traffic from ECS backend only"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-rds-sg" }
}

resource "aws_db_instance" "postgres" {
  identifier             = "${var.project_name}-db-${var.environment}"
  engine                 = "postgres"
  engine_version         = "16.1"
  instance_class         = var.database_instance_class
  allocated_storage      = 20
  max_allocated_storage  = 50
  storage_type           = "gp3"
  db_name                = var.database_name
  username               = var.database_username
  password               = random_password.db_password.result
  db_subnet_group_name   = aws_db_subnet_group.db_subnets.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot    = true
  publicly_accessible    = false

  tags = { Name = "${var.project_name}-postgres" }
}

output "rds_endpoint" { value = aws_db_instance.postgres.endpoint }
output "database_url_placeholder" {
  value     = "postgresql://${var.database_username}:${random_password.db_password.result}@${aws_db_instance.postgres.endpoint}/${var.database_name}"
  sensitive = true
}
