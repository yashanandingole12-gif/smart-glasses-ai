from typing import Dict, Any
from backend.app.config import settings

def get_location(custom_city: str = None, custom_country: str = None) -> Dict[str, Any]:
    """
    Get current location information.
    In simulator mode, returns configured default location with dynamic overrides.
    """
    city = custom_city or settings.DEFAULT_LOCATION_CITY
    country = custom_country or settings.DEFAULT_LOCATION_COUNTRY
    return {
        "city": city,
        "country": country,
        "latitude": settings.DEFAULT_LOCATION_LATITUDE,
        "longitude": settings.DEFAULT_LOCATION_LONGITUDE,
        "source": "SIMULATOR_CONFIG"
    }
