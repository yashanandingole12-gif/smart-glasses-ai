# ==============================================================================
# Private S3 Storage Module for EVA Media, Vision Captures & Documents
# ==============================================================================

variable "project_name" { type = string }
variable "environment" { type = string }

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "assets" {
  bucket        = "${var.project_name}-assets-${var.environment}-${random_id.bucket_suffix.hex}"
  force_destroy = false

  tags = {
    Name = "${var.project_name}-assets"
  }
}

# 1. Enforce strict private bucket access
resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 2. Server-side encryption with AES-256
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 3. Lifecycle rules for temporary vision cache
resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {
  bucket = aws_s3_bucket.assets.id

  rule {
    id     = "expire_temp_captures"
    status = "Enabled"

    filter {
      prefix = "temp_captures/"
    }

    expiration {
      days = 30
    }
  }
}

output "bucket_name" { value = aws_s3_bucket.assets.id }
output "bucket_arn" { value = aws_s3_bucket.assets.arn }
