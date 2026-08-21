from datetime import datetime
import pytz
from typing import Dict, Any
from simulator.config import (
    DEFAULT_CITY,
    DEFAULT_COUNTRY,
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
    DEFAULT_TIMEZONE
)

class SimulatorContextEngine:
    """Provides local laptop system time and location for simulator payload."""
    def __init__(
        self,
        city: str = DEFAULT_CITY,
        country: str = DEFAULT_COUNTRY,
        latitude: float = DEFAULT_LATITUDE,
        longitude: float = DEFAULT_LONGITUDE,
        timezone_str: str = DEFAULT_TIMEZONE
    ):
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.timezone_str = timezone_str

    def get_current_time(self) -> Dict[str, Any]:
        try:
            tz = pytz.timezone(self.timezone_str)
            now = datetime.now(tz)
        except Exception:
            now = datetime.now()

        hour = now.hour
        if 5 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 17:
            period = "afternoon"
        elif 17 <= hour < 22:
            period = "evening"
        else:
            period = "night"

        return {
            "local_time": now.strftime("%I:%M %p").lstrip("0"),
            "period": period,
            "timezone": self.timezone_str,
            "date_str": now.strftime("%A, %B %d, %Y"),
            "iso_timestamp": now.isoformat()
        }

    def get_location(self) -> Dict[str, Any]:
        return {
            "city": self.city,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "place_type": "college campus"
        }

    def get_full_context_dict(self, battery: int = 82) -> Dict[str, Any]:
        return {
            "time": self.get_current_time(),
            "location": self.get_location(),
            "calendar": {
                "next_event": {
                    "title": "Class",
                    "start_time": "10:30 AM"
                },
                "today_events": []
            },
            "device": {
                "battery": battery,
                "camera_available": True,
                "microphone_available": True,
                "network": "WIFI",
                "connection_type": "SIMULATOR"
            },
            "conversation": {
                "recent_topic": None,
                "referenced_entities": {}
            }
        }
