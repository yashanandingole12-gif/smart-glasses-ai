"""
AWS Cloud Services Package for EVA Smart Glasses AI.
Encapsulates AWS IoT Core, S3, Secrets Manager, and CloudWatch Logging.
"""

from .aws_iot_service import aws_iot_service, AwsIotService
from .aws_s3_service import aws_s3_service, AwsS3Service
from .aws_secrets_service import aws_secrets_service, AwsSecretsService
from .aws_cloudwatch_service import aws_cloudwatch_service, AwsCloudWatchService

__all__ = [
    "aws_iot_service",
    "AwsIotService",
    "aws_s3_service",
    "AwsS3Service",
    "aws_secrets_service",
    "AwsSecretsService",
    "aws_cloudwatch_service",
    "AwsCloudWatchService"
]
