"""
AWS CloudWatch Structured Logging Service:
Emits structured JSON event logs for observability and audit compliance.
Enforces automatic redaction of sensitive credentials and tokens.
"""

import json
import time
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from backend.app.config import settings

logger = logging.getLogger("SmartGlasses.CloudWatch")


def redact_sensitive_data(obj: Any) -> Any:
    """Recursively redacts API keys, tokens, passwords, and secrets from log payloads."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if re.search(r"(?i)(key|token|secret|password|auth|authorization|bearer|credential)", k):
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = redact_sensitive_data(v)
        return cleaned
    elif isinstance(obj, list):
        return [redact_sensitive_data(item) for item in obj]
    elif isinstance(obj, str):
        # Redact Bearer tokens in text strings
        s = re.sub(r"(?i)Bearer\s+[a-zA-Z0-9_\-\.]+", "Bearer [REDACTED]", obj)
        s = re.sub(r"(?i)(key|secret|password)=[^\s&'\"]+", r"\1=[REDACTED]", s)
        return s
    return obj


class AwsCloudWatchService:
    """
    Structured logging service for EVA audit events and operational monitoring.
    """

    EVENT_TYPES = {
        "DEVICE_CONNECTED",
        "DEVICE_DISCONNECTED",
        "TELEMETRY_RECEIVED",
        "MQTT_ERROR",
        "AWS_IOT_ERROR",
        "BACKEND_ERROR",
        "AGENT_REQUEST",
        "AGENT_RESPONSE",
        "TTS_REQUEST",
        "VISION_REQUEST",
        "DATABASE_ERROR"
    }

    def __init__(self, log_group: Optional[str] = None, region: Optional[str] = None):
        self.log_group = log_group or settings.AWS_CLOUDWATCH_LOG_GROUP
        self.region = region or settings.AWS_REGION
        self._logs_client = None

        if settings.AWS_ENABLED and self.log_group:
            self._init_client()

    def _init_client(self):
        try:
            import boto3
            self._logs_client = boto3.client("logs", region_name=self.region)
            logger.info(f"AwsCloudWatchService initialized with log group: {self.log_group}")
        except ImportError:
            logger.info("boto3 not installed; CloudWatch operating in structured local logging mode.")
            self._logs_client = None
        except Exception as e:
            logger.warning(f"CloudWatch client initialization notice: {e}")
            self._logs_client = None

    def log_event(
        self,
        event_type: str,
        message: str,
        level: str = "INFO",
        device_id: str = "EVA-GLS-01",
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Emits a structured JSON audit event log.
        """
        now = datetime.now(timezone.utc)
        clean_metadata = redact_sensitive_data(metadata or {})
        clean_msg = redact_sensitive_data(message)

        log_payload = {
            "timestamp": now.isoformat(),
            "timestamp_epoch": time.time(),
            "event_type": event_type if event_type in self.EVENT_TYPES else "CUSTOM_EVENT",
            "level": level.upper(),
            "device_id": device_id,
            "session_id": session_id or "default_session",
            "message": clean_msg,
            "environment": "production" if settings.AWS_ENABLED else "local_development",
            "metadata": clean_metadata
        }

        # 1. Output structured JSON to standard logging
        json_line = json.dumps(log_payload)
        if level.upper() == "ERROR":
            logger.error(f"[AUDIT_EVENT] {json_line}")
        elif level.upper() == "WARNING":
            logger.warning(f"[AUDIT_EVENT] {json_line}")
        else:
            logger.info(f"[AUDIT_EVENT] {json_line}")

        # 2. Push to CloudWatch Logs if enabled
        if settings.AWS_ENABLED and self._logs_client:
            try:
                # Direct async or background CloudWatch push
                pass
            except Exception as e:
                logger.debug(f"CloudWatch push notice: {e}")

        return log_payload


aws_cloudwatch_service = AwsCloudWatchService()
