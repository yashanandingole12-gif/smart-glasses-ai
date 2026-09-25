"""
AWS S3 Storage Service:
Handles private object storage for camera snapshots, vision captures,
resumes/documents, and generated assets with Presigned URL generation.
Falls back seamlessly to local storage when AWS_ENABLED=false.
"""

import os
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, BinaryIO

from backend.app.config import settings, PROJECT_ROOT
from backend.app.services.storage_service import storage_service

logger = logging.getLogger("SmartGlasses.AwsS3Service")


class AwsS3Service:
    """
    S3 client abstraction with fallback to local filesystem storage.
    Enforces private bucket permissions and presigned URL access.
    """

    def __init__(self, bucket_name: Optional[str] = None, region: Optional[str] = None):
        self.bucket_name = bucket_name or settings.AWS_S3_BUCKET_NAME
        self.region = region or settings.AWS_REGION
        self._s3_client = None

        if settings.AWS_ENABLED and self.bucket_name:
            self._init_s3_client()

    def _init_s3_client(self):
        try:
            import boto3
            from botocore.config import Config
            self._s3_client = boto3.client(
                "s3",
                region_name=self.region,
                config=Config(signature_version="s3v4")
            )
            logger.info(f"AwsS3Service initialized with bucket: {self.bucket_name} (region: {self.region})")
        except ImportError:
            logger.info("boto3 not installed; S3 service operating in local fallback mode.")
            self._s3_client = None
        except Exception as e:
            logger.warning(f"S3 client initialization notice: {e}")
            self._s3_client = None

    def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
        prefix: str = "uploads",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Uploads file to S3 (if AWS_ENABLED) or local storage directory.
        Returns file ID, storage key/path, and access URL.
        """
        file_id = f"s3_{uuid.uuid4().hex[:12]}"
        s3_key = f"{prefix}/{file_id}_{filename}"

        # 1. AWS S3 Upload if enabled and configured
        if settings.AWS_ENABLED and self._s3_client and self.bucket_name:
            try:
                extra_args = {
                    "ContentType": content_type,
                    "ServerSideEncryption": "AES256"
                }
                if metadata:
                    extra_args["Metadata"] = metadata

                self._s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_bytes,
                    **extra_args
                )

                presigned_url = self.generate_presigned_url(s3_key, expires_in=3600)
                logger.info(f"Uploaded {filename} to S3: s3://{self.bucket_name}/{s3_key}")
                return {
                    "success": True,
                    "storage_provider": "AWS_S3",
                    "bucket": self.bucket_name,
                    "key": s3_key,
                    "file_id": file_id,
                    "filename": filename,
                    "content_type": content_type,
                    "size_bytes": len(file_bytes),
                    "url": presigned_url,
                    "is_presigned": True
                }
            except Exception as e:
                logger.error(f"S3 upload error: {e}. Falling back to local storage.")

        # 2. Fallback to local storage
        local_res = storage_service.save_file(
            file_bytes=file_bytes,
            filename=filename,
            content_type=content_type,
            source=prefix
        )
        local_url = f"http://{settings.HOST}:{settings.PORT}/api/v1/files/{local_res['file_id']}/download"
        return {
            "success": True,
            "storage_provider": "LOCAL_STORAGE",
            "file_id": local_res["file_id"],
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(file_bytes),
            "url": local_url,
            "is_presigned": False
        }

    def generate_presigned_url(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        """Generates a secure temporary presigned GET URL for an S3 object."""
        if not self._s3_client or not self.bucket_name:
            return None
        try:
            url = self._s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL for {s3_key}: {e}")
            return None

    def delete_file(self, s3_key: str) -> bool:
        """Deletes object from S3."""
        if self._s3_client and self.bucket_name:
            try:
                self._s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
                return True
            except Exception as e:
                logger.error(f"Error deleting S3 object {s3_key}: {e}")
                return False
        return False


aws_s3_service = AwsS3Service()
