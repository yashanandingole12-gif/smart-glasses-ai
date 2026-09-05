from typing import List, Dict, Any, Optional
from backend.app.services.providers.calendar_provider import get_calendar_provider

def calendar_get_events(
    query: Optional[str] = None,
    user_id: str = "default_user",
    date_target: Optional[str] = None,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    user_tz: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve today's, tomorrow's, or specific date's scheduled calendar events or search events by query string.
    """
    provider = get_calendar_provider(user_id=user_id)
    return provider.get_events(
        query=query,
        date_target=date_target,
        time_min=time_min,
        time_max=time_max,
        user_tz=user_tz
    )


def calendar_find_free_time(user_id: str = "default_user") -> Dict[str, Any]:
    """
    Find available free time slots in the user's schedule today.
    """
    provider = get_calendar_provider(user_id=user_id)
    return provider.find_free_time()

def calendar_create_event(
    title: str,
    start_time: str,
    end_time: Optional[str] = None,
    location: Optional[str] = None,
    description: Optional[str] = None,
    user_id: str = "default_user"
) -> Dict[str, Any]:
    """
    Create/schedule a new event on the user's calendar.
    """
    provider = get_calendar_provider(user_id=user_id)
    return provider.create_event(
        title=title,
        start_time=start_time,
        end_time=end_time,
        location=location,
        description=description
    )

