import os
from pathlib import Path
from dotenv import load_dotenv

# Load root .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

BACKEND_URL = os.getenv("SIMULATOR_BACKEND_URL", "http://127.0.0.1:8000")
SAMPLE_RATE = int(os.getenv("SIMULATOR_AUDIO_SAMPLE_RATE", "16000"))
DEFAULT_CITY = os.getenv("DEFAULT_LOCATION_CITY", "Nagpur")
DEFAULT_COUNTRY = os.getenv("DEFAULT_LOCATION_COUNTRY", "India")
DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LOCATION_LATITUDE", "21.1458"))
DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LOCATION_LONGITUDE", "79.0882"))
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")
STT_ENGINE = os.getenv("STT_ENGINE", "faster_whisper")  # "faster_whisper", "mock", "auto"
TTS_ENGINE = os.getenv("TTS_ENGINE", "sapi5")           # "sapi5", "pyttsx3", "silent"

