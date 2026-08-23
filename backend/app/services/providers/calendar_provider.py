from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class CalendarProvider(ABC):
    """Abstract provider interface for calendar services (Laptop Mock / Google Calendar API)."""

    @abstractmethod
    def get_events(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve scheduled events for today or matching search query."""
        pass

    @abstractmethod
    def find_free_time(self) -> Dict[str, Any]:
        """Calculate and return free time slots in the user's schedule."""
        pass


class MockCalendarProvider(CalendarProvider):
    """Deterministic development calendar provider for laptop simulation."""

    def __init__(self):
        self._mock_events = [
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

    def get_events(self, query: Optional[str] = None) -> Dict[str, Any]:
        events = self._mock_events
        if query:
            q = query.lower()
            events = [e for e in events if q in e["title"].lower() or q in (e.get("description") or "").lower()]
        return {
            "count": len(events),
            "events": events,
            "next_event": events[0] if events else None
        }

    def find_free_time(self) -> Dict[str, Any]:
        return {
            "free_slots": [
                {"from": "12:00 PM", "to": "03:00 PM", "duration": "3 hours"},
                {"from": "04:00 PM", "to": "06:30 PM", "duration": "2.5 hours"},
                {"from": "07:30 PM", "to": "10:00 PM", "duration": "2.5 hours"}
            ]
        }
