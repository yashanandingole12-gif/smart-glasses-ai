"""
Central Integration Registry & Configuration Provider for EVA
Authoritative configuration model for LLMs, Google Workspace, GitHub, LinkedIn,
Academic Research (arXiv, OpenAlex, Semantic Scholar, Crossref), and Web Search.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class IntegrationStatus(BaseModel):
    name: str
    status: str  # "CONNECTED", "NOT_CONFIGURED", "AUTH_REQUIRED", "RATE_LIMITED", "UNAVAILABLE", "INVALID_CONFIGURATION"
    auth_type: str  # "API_KEY", "OAUTH2", "TOKEN", "PUBLIC", "NONE"
    is_optional: bool
    details: Dict[str, Any] = Field(default_factory=dict)

class IntegrationSettings(BaseSettings):
    # =========================================================================
    # 1. LLM Providers
    # =========================================================================
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: Optional[str] = None

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-flash-lite-latest"

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-latest"

    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    FAST_LLM_PROVIDER: str = "gemini"
    PRIMARY_LLM_PROVIDER: str = "gemini"
    SECONDARY_LLM_PROVIDER: str = "deepseek"
    FALLBACK_LLM_PROVIDER: str = "mock"

    # =========================================================================
    # 2. Google Workspace & OAuth 2.0
    # =========================================================================
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8001/api/v1/auth/google/callback"
    GOOGLE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    GOOGLE_REVOKE_URI: str = "https://oauth2.googleapis.com/revoke"

    GOOGLE_OAUTH_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/contacts.readonly",
        "https://www.googleapis.com/auth/userinfo.email"
    ]

    # =========================================================================
    # 3. GitHub Integration
    # =========================================================================
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_APP_ID: Optional[str] = None
    GITHUB_PRIVATE_KEY: Optional[str] = None
    GITHUB_API_BASE_URL: str = "https://api.github.com"

    # =========================================================================
    # 4. LinkedIn Integration
    # =========================================================================
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8001/api/v1/auth/linkedin/callback"
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None
    LINKEDIN_API_BASE_URL: str = "https://api.linkedin.com/v2"

    # =========================================================================
    # 5. Academic Research Providers
    # =========================================================================
    ARXIV_ENABLED: bool = True
    ARXIV_BASE_URL: str = "https://export.arxiv.org/api/query"

    OPENALEX_API_KEY: Optional[str] = None
    OPENALEX_EMAIL: Optional[str] = None
    OPENALEX_BASE_URL: str = "https://api.openalex.org"

    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None
    SEMANTIC_SCHOLAR_BASE_URL: str = "https://api.semanticscholar.org/graph/v1"

    CROSSREF_EMAIL: Optional[str] = None
    CROSSREF_BASE_URL: str = "https://api.crossref.org"

    # =========================================================================
    # 6. Web Search Providers
    # =========================================================================
    WEB_SEARCH_API_KEY: Optional[str] = None
    WEB_SEARCH_ENGINE: str = "tavily"  # "tavily", "serpapi", "duckduckgo", "mock"
    WEB_SEARCH_BASE_URL: Optional[str] = None

    # =========================================================================
    # 7. Opportunity & Job Providers
    # =========================================================================
    LINKEDIN_OPPORTUNITY_ENABLED: bool = True
    INTERNSHALA_ENABLED: bool = False
    INDEED_ENABLED: bool = False
    OTHER_JOB_PROVIDER_ENABLED: bool = False

    # =========================================================================
    # 8. WiFi & Hardware Network Configuration
    # =========================================================================
    GLASSES_WIFI_SSID: str = "EVA 3693"
    GLASSES_WIFI_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

integration_settings = IntegrationSettings()
