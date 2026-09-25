# ==============================================================================
# AWS IoT Core Module for EVA Smart Glasses Fleet & Thing Architecture
# ==============================================================================

variable "project_name" { type = string }
variable "environment" { type = string }
variable "device_id" { type = string }

# 1. Thing Group for Fleet Management (EVA-GLS-01, EVA-GLS-02, etc.)
resource "aws_iot_thing_group" "fleet" {
  name = "${var.project_name}-fleet-${var.environment}"

  tags = {
    Name = "${var.project_name}-fleet"
  }
}

# 2. Individual IoT Thing (EVA-GLS-01)
resource "aws_iot_thing" "glasses" {
  name = var.device_id

  attributes = {
    model       = "ESP32-S3-Sense"
    firmware    = "1.0.0"
    fleet_group = "eva_smart_glasses"
  }
}

# 3. Associate Thing with Thing Group
resource "aws_iot_thing_group_membership" "glasses_membership" {
  thing_group_name = aws_iot_thing_group.fleet.name
  thing_name       = aws_iot_thing.glasses.name
}

# 4. Strict Least-Privilege IoT Policy
resource "aws_iot_policy" "device_policy" {
  name = "${var.project_name}-device-policy-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["iot:Connect"]
        Resource = ["arn:aws:iot:*:*:client/$${iot:Connection.Thing.ThingName}"]
      },
      {
        Effect = "Allow"
        Action = ["iot:Publish"]
        Resource = [
          "arn:aws:iot:*:*:topic/eva/$${iot:Connection.Thing.ThingName}/telemetry",
          "arn:aws:iot:*:*:topic/eva/$${iot:Connection.Thing.ThingName}/status",
          "arn:aws:iot:*:*:topic/eva/$${iot:Connection.Thing.ThingName}/events",
          "arn:aws:iot:*:*:topic/eva/$${iot:Connection.Thing.ThingName}/diagnostics",
          "arn:aws:iot:*:*:topic/$aws/things/$${iot:Connection.Thing.ThingName}/shadow/*"
        ]
      },
      {
        Effect = "Allow"
        Action = ["iot:Subscribe"]
        Resource = [
          "arn:aws:iot:*:*:topicfilter/eva/$${iot:Connection.Thing.ThingName}/commands",
          "arn:aws:iot:*:*:topicfilter/$aws/things/$${iot:Connection.Thing.ThingName}/shadow/*"
        ]
      },
      {
        Effect = "Allow"
        Action = ["iot:Receive"]
        Resource = [
          "arn:aws:iot:*:*:topic/eva/$${iot:Connection.Thing.ThingName}/commands",
          "arn:aws:iot:*:*:topic/$aws/things/$${iot:Connection.Thing.ThingName}/shadow/*"
        ]
      }
    ]
  })
}

output "thing_name" { value = aws_iot_thing.glasses.name }
output "thing_arn" { value = aws_iot_thing.glasses.arn }
output "thing_group_name" { value = aws_iot_thing_group.fleet.name }
output "policy_name" { value = aws_iot_policy.device_policy.name }
