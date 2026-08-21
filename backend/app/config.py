from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path

# Find project root .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    # LLM Settings
    LLM_PROVIDER: str = "mock"  # "mock", "openai", "gemini", "anthropic", "ollama"
    LLM_MODEL: str = "gemini-flash-latest"
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: Optional[str] = None

    # Server Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
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

    # External Integrations
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
