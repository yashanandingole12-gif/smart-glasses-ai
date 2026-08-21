from datetime import datetime
import pytz
from typing import Dict, Any

def get_time(timezone_str: str = "Asia/Kolkata") -> Dict[str, Any]:
    """
    Get current local time, date, period (morning, afternoon, evening, night), and timezone.
    """
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()
        timezone_str = "Local"

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
        "time": now.strftime("%I:%M %p").lstrip("0"),
        "time_24h": now.strftime("%H:%M"),
        "period": period,
        "date": now.strftime("%A, %B %d, %Y"),
        "timezone": timezone_str,
        "iso": now.isoformat()
    }
