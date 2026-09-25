"""
AWS Secrets Manager Integration:
Fetches server-side runtime credentials dynamically in production.
Falls back seamlessly to local .env configuration when AWS_ENABLED=false.
"""

import json
import time
import logging
from typing import Dict, Any, Optional

from backend.app.config import settings

logger = logging.getLogger("SmartGlasses.AwsSecretsService")


class AwsSecretsService:
    """
    Manages secure retrieval of credentials from AWS Secrets Manager with local caching.
    """

    def __init__(self, secret_name: Optional[str] = None, region: Optional[str] = None):
        self.secret_name = secret_name or settings.AWS_SECRETS_NAME
        self.region = region or settings.AWS_REGION
        self._secrets_cache: Dict[str, Any] = {}
        self._cache_expires_at: float = 0.0
        self._ttl_seconds: float = 900.0  # 15 minutes TTL cache
        self._client = None

        if settings.AWS_ENABLED and self.secret_name:
            self._init_client()

    def _init_client(self):
        try:
            import boto3
            self._client = boto3.client("secretsmanager", region_name=self.region)
            logger.info(f"AwsSecretsService initialized for secret: {self.secret_name}")
        except ImportError:
            logger.info("boto3 not installed; Secrets Manager operating in local fallback mode.")
            self._client = None
        except Exception as e:
            logger.warning(f"Secrets Manager client initialization notice: {e}")
            self._client = None

    def get_secrets(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Retrieves secrets dictionary from AWS Secrets Manager or falls back to settings.
        """
        now = time.time()
        if not force_refresh and self._secrets_cache and now < self._cache_expires_at:
            return self._secrets_cache

        # 1. Fetch from AWS Secrets Manager if enabled
        if settings.AWS_ENABLED and self._client and self.secret_name:
            try:
                response = self._client.get_secret_value(SecretId=self.secret_name)
                if "SecretString" in response:
                    secrets_dict = json.loads(response["SecretString"])
                    self._secrets_cache = secrets_dict
                    self._cache_expires_at = now + self._ttl_seconds
                    logger.info("Successfully fetched secrets from AWS Secrets Manager.")
                    return secrets_dict
            except Exception as e:
                logger.error(f"Error fetching AWS secret '{self.secret_name}': {e}. Using local settings fallback.")

        # 2. Local fallback using active settings / environment variables
        fallback_secrets = {
            "GEMINI_API_KEY": getattr(settings, "GEMINI_API_KEY", None),
            "DEEPSEEK_API_KEY": getattr(settings, "DEEPSEEK_API_KEY", None),
            "OPENAI_API_KEY": getattr(settings, "OPENAI_API_KEY", None),
            "GROQ_API_KEY": getattr(settings, "GROQ_API_KEY", None),
            "TAVILY_API_KEY": getattr(settings, "TAVILY_API_KEY", None),
            "GITHUB_TOKEN": getattr(settings, "GITHUB_TOKEN", None),
            "GOOGLE_CLIENT_ID": getattr(settings, "GOOGLE_CLIENT_ID", None),
            "GOOGLE_CLIENT_SECRET": getattr(settings, "GOOGLE_CLIENT_SECRET", None),
            "DATABASE_URL": getattr(settings, "DATABASE_URL", "sqlite:///./smart_glasses.db")
        }
        self._secrets_cache = fallback_secrets
        self._cache_expires_at = now + self._ttl_seconds
        return fallback_secrets

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves a specific secret value by key name."""
        secrets = self.get_secrets()
        return secrets.get(key, default)


aws_secrets_service = AwsSecretsService()
