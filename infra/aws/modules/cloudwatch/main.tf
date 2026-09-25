# ==============================================================================
# AWS CloudWatch Observability Module
# ==============================================================================

variable "project_name" { type = string }
variable "environment" { type = string }

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/eva/${var.environment}/backend"
  retention_in_days = 30

  tags = {
    Name = "${var.project_name}-logs"
  }
}

# Metric filter to track backend errors
resource "aws_cloudwatch_log_metric_filter" "error_filter" {
  name           = "${var.project_name}-backend-errors"
  pattern        = "{ $.event_type = \"BACKEND_ERROR\" || $.level = \"ERROR\" }"
  log_group_name = aws_cloudwatch_log_group.backend.name

  metric_transformation {
    name      = "BackendErrorCount"
    namespace = "EVA/SmartGlasses"
    value     = "1"
  }
}

output "log_group_name" { value = aws_cloudwatch_log_group.backend.name }
output "log_group_arn" { value = aws_cloudwatch_log_group.backend.arn }
