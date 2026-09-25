from datetime import datetime, timezone, timedelta
from typing import Dict, Any

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

try:
    import pytz
except ImportError:
    pytz = None

def get_time(timezone_str: str = "Asia/Kolkata") -> Dict[str, Any]:
    """
    Get current local time, date, period (morning, afternoon, evening, night), and timezone.
    """
    now = None
    if ZoneInfo:
        try:
            tz = ZoneInfo(timezone_str)
            now = datetime.now(tz)
        except Exception:
            pass
            
    if now is None and pytz:
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
        except Exception:
            pass

    if now is None:
        if timezone_str == "Asia/Kolkata" or "Kolkata" in timezone_str or "IST" in timezone_str:
            tz = timezone(timedelta(hours=5, minutes=30))
            now = datetime.now(tz)
        else:
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
