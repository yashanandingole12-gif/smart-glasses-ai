from typing import List, Dict, Any, Optional
from datetime import datetime

# Sample repository state (extensible with Google Calendar OAuth in Phase 5)
_MOCK_EVENTS = [
    {
        "id": "evt_101",
        "title": "Machine Learning Class",
        "start_time": "10:30 AM",
        "end_time": "12:00 PM",
        "location": "College Campus, Room 302",
        "description": "Lecture on Transformer architectures"
    },
    {
        "id": "evt_102",
        "title": "Project Team Sync",
        "start_time": "03:00 PM",
        "end_time": "04:00 PM",
        "location": "Google Meet",
        "description": "Smart glasses weekly milestone check"
    },
    {
        "id": "evt_103",
        "title": "Gym / Workout",
        "start_time": "06:30 PM",
        "end_time": "07:30 PM",
        "location": "Fitness Center",
        "description": "Evening cardio and strength"
    }
]

def calendar_get_events(query: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve today's scheduled calendar events.
    """
    events = _MOCK_EVENTS
    if query:
        q = query.lower()
        events = [e for e in events if q in e["title"].lower() or q in (e.get("description") or "").lower()]
    return {
        "count": len(events),
        "events": events,
        "next_event": events[0] if events else None
    }

def calendar_find_free_time() -> Dict[str, Any]:
    """
    Find free time slots in the user's schedule today.
    """
    return {
        "free_slots": [
            {"from": "12:00 PM", "to": "03:00 PM", "duration": "3 hours"},
            {"from": "04:00 PM", "to": "06:30 PM", "duration": "2.5 hours"},
            {"from": "07:30 PM", "to": "10:00 PM", "duration": "2.5 hours"}
        ]
    }
