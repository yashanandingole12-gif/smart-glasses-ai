# ==============================================================================
# AWS Secrets Manager Module for Runtime API Keys and Credentials
# ==============================================================================

variable "project_name" { type = string }
variable "environment" { type = string }

resource "aws_secretsmanager_secret" "eva_secrets" {
  name                    = "${var.project_name}-secrets-${var.environment}"
  description             = "Production runtime API keys and secrets for EVA AI backend"
  recovery_window_in_days = 0

  tags = {
    Name = "${var.project_name}-secrets"
  }
}

resource "aws_secretsmanager_secret_version" "initial_placeholders" {
  secret_id = aws_secretsmanager_secret.eva_secrets.id
  secret_string = jsonencode({
    GEMINI_API_KEY       = "PLACEHOLDER_SET_IN_AWS_CONSOLE"
    DEEPSEEK_API_KEY     = "PLACEHOLDER_SET_IN_AWS_CONSOLE"
    OPENAI_API_KEY       = "PLACEHOLDER_SET_IN_AWS_CONSOLE"
    GROQ_API_KEY         = "PLACEHOLDER_SET_IN_AWS_CONSOLE"
    TAVILY_API_KEY       = "PLACEHOLDER_SET_IN_AWS_CONSOLE"
    GITHUB_TOKEN         = "PLACEHOLDER_SET_IN_AWS_CONSOLE"
    GOOGLE_CLIENT_ID     = "PLACEHOLDER_SET_IN_AWS_CONSOLE"
    GOOGLE_CLIENT_SECRET = "PLACEHOLDER_SET_IN_AWS_CONSOLE"
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

output "secrets_name" { value = aws_secretsmanager_secret.eva_secrets.name }
output "secrets_arn" { value = aws_secretsmanager_secret.eva_secrets.arn }
