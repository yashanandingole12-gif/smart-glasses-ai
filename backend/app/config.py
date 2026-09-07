from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from pathlib import Path

# Find project root .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    # LLM Settings & Multi-Tier Router
    LLM_PROVIDER: str = "gemini"  # "mock", "openai", "gemini", "anthropic", "deepseek", "ollama"
    LLM_MODEL: str = "gemini-flash-lite-latest"
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: Optional[str] = "gemini-flash-lite-latest"

    # Multi-Tier Routing & Secondary Cloud Provider (Phase 3B.6)
    FAST_LLM_PROVIDER: str = "gemini"
    FAST_LLM_MODEL: str = "gemini-flash-lite-latest"
    PRIMARY_LLM_PROVIDER: str = "gemini"
    PRIMARY_LLM_MODEL: str = "gemini-flash-lite-latest"
    SECONDARY_LLM_PROVIDER: Optional[str] = "deepseek"  # "deepseek", "openai", "groq", "anthropic", "ollama", "mock"
    SECONDARY_LLM_MODEL: Optional[str] = "deepseek-chat"
    SECONDARY_LLM_API_KEY: Optional[str] = None
    SECONDARY_LLM_BASE_URL: Optional[str] = "https://api.deepseek.com"

    # DeepSeek Specific Configuration
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: Optional[str] = "deepseek-chat"
    DEEPSEEK_BASE_URL: Optional[str] = "https://api.deepseek.com"

    FALLBACK_LLM_PROVIDER: str = "mock"
    FALLBACK_LLM_MODEL: str = "mock-glasses-v1"

    # Latency Budget & Hard Deadlines (Phase 3B.6 / 3B.10)
    CLOUD_TIMEOUT_SECONDS: float = 10.0
    LLM_TIMEOUT_SECONDS: float = 10.0
    REQUEST_DEADLINE_SECONDS: float = 15.0
    MAX_OUTPUT_TOKENS: int = 180
    MAX_INPUT_TOKENS: int = 2048
    VOICE_RESPONSE_MODE: bool = True

    # Agent Limits
    MAX_AGENT_STEPS: int = 4
    RECENT_MESSAGES_LIMIT: int = 10

    # Server Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8001
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Context & Location Fallbacks
    DEFAULT_LOCATION_CITY: str = "Nagpur"
    DEFAULT_LOCATION_COUNTRY: str = "India"
    DEFAULT_LOCATION_LATITUDE: float = 21.1458
    DEFAULT_LOCATION_LONGITUDE: float = 79.0882
    DEFAULT_TIMEZONE: str = "Asia/Kolkata"

    # Memory Database
    DATABASE_URL: str = "sqlite:///./smart_glasses.db"

    # Audio & Voice Settings
    STT_ENGINE: str = "faster_whisper"  # "faster_whisper", "mock", "auto"
    TTS_ENGINE: str = "sapi5"           # "sapi5", "pyttsx3", "silent"

    # Google OAuth 2.0 Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8001/api/v1/auth/google/callback"
    GOOGLE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    GOOGLE_REVOKE_URI: str = "https://oauth2.googleapis.com/revoke"
    GOOGLE_USERINFO_URI: str = "https://www.googleapis.com/oauth2/v2/userinfo"

    # Minimum Necessary Scopes
    GOOGLE_OAUTH_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/userinfo.email"
    ]

    # External Integrations (Backwards compatibility)
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CALENDAR_CLIENT_ID: Optional[str] = None
    GOOGLE_CALENDAR_CLIENT_SECRET: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    SERPAPI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Normalize Google Client ID / Secret if provided under alias
if not settings.GOOGLE_CLIENT_ID and settings.GMAIL_CLIENT_ID:
    settings.GOOGLE_CLIENT_ID = settings.GMAIL_CLIENT_ID
if not settings.GOOGLE_CLIENT_SECRET and settings.GMAIL_CLIENT_SECRET:
    settings.GOOGLE_CLIENT_SECRET = settings.GMAIL_CLIENT_SECRET

# Normalize DeepSeek Secondary API key
if not settings.SECONDARY_LLM_API_KEY and settings.DEEPSEEK_API_KEY:
    settings.SECONDARY_LLM_API_KEY = settings.DEEPSEEK_API_KEY

# If no Gemini key is configured or default is mock, align FAST/PRIMARY to mock
if not settings.GEMINI_API_KEY and settings.LLM_PROVIDER == "mock":
    settings.FAST_LLM_PROVIDER = "mock"
    settings.PRIMARY_LLM_PROVIDER = "mock"
