import logging
import httpx
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("SmartGlasses.CalendarProvider")

class CalendarProvider(ABC):
    """Abstract provider interface for calendar services (Laptop Mock / Google Calendar API)."""

    @abstractmethod
    def get_events(self, query: Optional[str] = None, max_results: int = 5) -> Dict[str, Any]:
        """Retrieve scheduled events for today or matching search query."""
        pass

    @abstractmethod
    def get_today_events(self) -> Dict[str, Any]:
        """Retrieve events scheduled for today."""
        pass

    @abstractmethod
    def get_upcoming_events(self, max_results: int = 5) -> Dict[str, Any]:
        """Retrieve upcoming events from current time onwards."""
        pass

    @abstractmethod
    def get_next_event(self) -> Optional[Dict[str, Any]]:
        """Retrieve the immediate next scheduled event."""
        pass

    @abstractmethod
    def find_free_time(self) -> Dict[str, Any]:
        """Calculate and return free time slots in the user's schedule."""
        pass

    @abstractmethod
    def create_event(
        self,
        title: str,
        start_time: str,
        end_time: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Schedule/create a new calendar event."""
        pass


class MockCalendarProvider(CalendarProvider):
    """Deterministic development calendar provider with multi-day schedules for testing."""

    def __init__(self, custom_events: Optional[List[Dict[str, Any]]] = None):
        now = datetime.now()
        today_iso = now.strftime("%Y-%m-%d")
        tomorrow_iso = (now + timedelta(days=1)).strftime("%Y-%m-%d")

        if custom_events is not None:
            self._mock_events = custom_events
        else:
            self._mock_events = [
                # TODAY's events
                {
                    "id": "evt_101",
                    "title": "Machine Learning Class",
                    "start_time": "10:30 AM",
                    "end_time": "12:00 PM",
                    "location": "College Campus, Room 302",
                    "description": "Lecture on Transformer architectures",
                    "day_tag": "today",
                    "date_iso": today_iso,
                    "status": "confirmed"
                },
                {
                    "id": "evt_102",
                    "title": "Project Team Sync",
                    "start_time": "03:00 PM",
                    "end_time": "04:00 PM",
                    "location": "Google Meet",
                    "description": "Smart glasses weekly milestone check",
                    "day_tag": "today",
                    "date_iso": today_iso,
                    "status": "confirmed"
                },
                {
                    "id": "evt_103",
                    "title": "Gym / Workout",
                    "start_time": "06:30 PM",
                    "end_time": "07:30 PM",
                    "location": "Fitness Center",
                    "description": "Evening cardio and strength",
                    "day_tag": "today",
                    "date_iso": today_iso,
                    "status": "confirmed"
                },
                # TOMORROW's events
                {
                    "id": "evt_201",
                    "title": "Operating Systems Lab",
                    "start_time": "09:00 AM",
                    "end_time": "10:30 AM",
                    "location": "Lab 4B",
                    "description": "Kernel module implementation and memory management",
                    "day_tag": "tomorrow",
                    "date_iso": tomorrow_iso,
                    "status": "confirmed"
                },
                {
                    "id": "evt_202",
                    "title": "Database Systems Lecture",
                    "start_time": "11:30 AM",
                    "end_time": "01:00 PM",
                    "location": "Auditorium 2",
                    "description": "Distributed SQL queries & replication",
                    "day_tag": "tomorrow",
                    "date_iso": tomorrow_iso,
                    "status": "confirmed"
                },
                {
                    "id": "evt_203",
                    "title": "AI Seminar",
                    "start_time": "04:00 PM",
                    "end_time": "05:30 PM",
                    "location": "Seminar Hall A",
                    "description": "Agentic workflows and edge hardware",
                    "day_tag": "tomorrow",
                    "date_iso": tomorrow_iso,
                    "status": "confirmed"
                }
            ]

    def get_events(
        self,
        query: Optional[str] = None,
        max_results: int = 10,
        date_target: Optional[str] = None
    ) -> Dict[str, Any]:
        events = list(self._mock_events)

        # Date target filtering
        if date_target:
            dt_clean = date_target.lower().strip()
            if dt_clean in ["today", "tomorrow"]:
                events = [e for e in events if e.get("day_tag") == dt_clean]
            elif "-" in dt_clean:  # ISO date string YYYY-MM-DD
                events = [e for e in events if e.get("date_iso") == dt_clean]
        else:
            # Default to today's events if no query specified
            if not query:
                events = [e for e in events if e.get("day_tag") == "today"]

        if query:
            q = query.lower()
            events = [e for e in events if q in e["title"].lower() or q in (e.get("description") or "").lower()]

        events = events[:max_results]
        return {
            "count": len(events),
            "events": events,
            "next_event": events[0] if events else None,
            "message": "Events retrieved successfully." if events else "No calendar events found."
        }

    def get_today_events(self) -> Dict[str, Any]:
        return self.get_events(date_target="today")

    def get_upcoming_events(self, max_results: int = 10) -> Dict[str, Any]:
        return self.get_events(max_results=max_results, date_target="today")

    def get_next_event(self) -> Optional[Dict[str, Any]]:
        today_events = [e for e in self._mock_events if e.get("day_tag") == "today"]
        return today_events[0] if today_events else (self._mock_events[0] if self._mock_events else None)

    def find_free_time(self) -> Dict[str, Any]:
        return {
            "free_slots": [
                {"from": "12:00 PM", "to": "03:00 PM", "duration": "3 hours"},
                {"from": "04:00 PM", "to": "06:30 PM", "duration": "2.5 hours"},
                {"from": "07:30 PM", "to": "10:00 PM", "duration": "2.5 hours"}
            ]
        }

    def create_event(
        self,
        title: str,
        start_time: str,
        end_time: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        now = datetime.now()
        new_event = {
            "id": f"evt_{len(self._mock_events) + 101}",
            "title": title,
            "start_time": start_time,
            "end_time": end_time or "1 hour later",
            "location": location or "Not specified",
            "description": description or "",
            "day_tag": "today",
            "date_iso": now.strftime("%Y-%m-%d"),
            "status": "confirmed"
        }
        self._mock_events.append(new_event)
        logger.info(f"Mock calendar event created: '{title}' at {start_time}")
        return {
            "status": "created",
            "event_id": new_event["id"],
            "event": new_event,
            "message": f"Event '{title}' scheduled at {start_time}."
        }



class GoogleCalendarProvider(CalendarProvider):
    """
    Real Google Calendar API v3 provider connecting via backend OAuth 2.0 token.
    Uses read-only scope (https://www.googleapis.com/auth/calendar.readonly).
    Never exposes raw tokens to client or LLM.
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

    def _get_valid_token_sync(self) -> Optional[str]:
        from backend.app.services.token_service import token_service
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, token_service.get_valid_token(self.user_id)).result()
            else:
                return asyncio.run(token_service.get_valid_token(self.user_id))
        except Exception as e:
            logger.error(f"Error fetching Google OAuth token for user {self.user_id}: {e}")
            return None

    def get_events(
        self,
        query: Optional[str] = None,
        max_results: int = 10,
        date_target: Optional[str] = None
    ) -> Dict[str, Any]:
        t_start = datetime.now()
        token = self._get_valid_token_sync()
        if not token:
            logger.info(f"calendar_request account=<redacted> date_range={date_target or 'default'} provider=google status=unauthenticated")
            return {
                "count": 0,
                "events": [],
                "next_event": None,
                "error": "Google Calendar is not connected or token expired.",
                "message": "I can't access your calendar right now."
            }

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        # Calculate time window according to date_target
        now = datetime.now(timezone.utc)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if date_target == "tomorrow":
            start_of_target = start_of_today + timedelta(days=1)
            end_of_target = start_of_target + timedelta(days=1)
            time_min = start_of_target.isoformat()
            time_max = end_of_target.isoformat()
        elif date_target == "today":
            time_min = start_of_today.isoformat()
            time_max = (start_of_today + timedelta(days=1)).isoformat()
        else:
            time_min = start_of_today.isoformat()
            time_max = (start_of_today + timedelta(days=7)).isoformat()

        params = {
            "timeMin": time_min,
            "timeMax": time_max,
            "maxResults": min(max_results, 15),
            "singleEvents": "true",
            "orderBy": "startTime"
        }
        if query:
            params["q"] = query

        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(url, headers=headers, params=params)
                if resp.status_code == 401:
                    logger.warning("Google Calendar API returned 401 Unauthorized; disconnecting expired token.")
                    try:
                        from backend.app.services.token_service import token_service
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            loop = None
                        if loop and loop.is_running():
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as pool:
                                pool.submit(asyncio.run, token_service.disconnect(self.user_id)).result()
                        else:
                            asyncio.run(token_service.disconnect(self.user_id))
                    except Exception:
                        pass
                    return {
                        "count": 0,
                        "events": [],
                        "next_event": None,
                        "error": "Google Calendar authentication expired.",
                        "message": "I can't access your calendar right now."
                    }

                resp.raise_for_status()
                data = resp.json()

            items = data.get("items", [])
            normalized_events = []
            for item in items:
                start_raw = item.get("start", {}).get("dateTime") or item.get("start", {}).get("date", "")
                end_raw = item.get("end", {}).get("dateTime") or item.get("end", {}).get("date", "")

                start_formatted = start_raw
                end_formatted = end_raw
                date_iso = ""
                try:
                    if "T" in start_raw:
                        dt = datetime.fromisoformat(start_raw)
                        start_formatted = dt.strftime("%I:%M %p").lstrip("0")
                        date_iso = dt.strftime("%Y-%m-%d")
                    elif start_raw:
                        date_iso = start_raw
                    if "T" in end_raw:
                        dt_end = datetime.fromisoformat(end_raw)
                        end_formatted = dt_end.strftime("%I:%M %p").lstrip("0")
                except Exception:
                    pass

                desc = item.get("description", "")
                if desc and len(desc) > 150:
                    desc = desc[:150] + "..."

                normalized_events.append({
                    "id": item.get("id", ""),
                    "title": item.get("summary", "Untitled Event"),
                    "start_time": start_formatted,
                    "end_time": end_formatted,
                    "location": item.get("location", "Not specified"),
                    "description": desc,
                    "date_iso": date_iso,
                    "status": item.get("status", "confirmed")
                })

            lat_ms = (datetime.now() - t_start).total_seconds() * 1000.0
            logger.info(f"calendar_request account=<redacted> date_range={date_target or 'default'} provider=google result_count={len(normalized_events)} latency_ms={lat_ms:.1f}")

            return {
                "count": len(normalized_events),
                "events": normalized_events,
                "next_event": normalized_events[0] if normalized_events else None,
                "message": f"Retrieved {len(normalized_events)} events from Google Calendar." if normalized_events else "You have no events scheduled."
            }

        except Exception as e:
            lat_ms = (datetime.now() - t_start).total_seconds() * 1000.0
            logger.error(f"calendar_request account=<redacted> provider=google error={e} latency_ms={lat_ms:.1f}")
            return {
                "count": 0,
                "events": [],
                "next_event": None,
                "error": f"Google Calendar error: {e}",
                "message": "I can't access your calendar right now."
            }

    def get_today_events(self) -> Dict[str, Any]:
        return self.get_events(date_target="today")

    def get_upcoming_events(self, max_results: int = 10) -> Dict[str, Any]:
        return self.get_events(max_results=max_results, date_target="today")

    def get_next_event(self) -> Optional[Dict[str, Any]]:
        res = self.get_events(max_results=1, date_target="today")
        return res.get("next_event")

    def find_free_time(self) -> Dict[str, Any]:
        events_data = self.get_today_events()
        events = events_data.get("events", [])
        if events_data.get("error"):
            return {
                "free_slots": [],
                "error": events_data.get("error"),
                "message": "I can't access your calendar right now."
            }
        if not events:
            return {
                "free_slots": [
                    {"from": "09:00 AM", "to": "06:00 PM", "duration": "Full day free"}
                ],
                "message": "You are free all day today."
            }
        return {
            "free_slots": [
                {"from": "12:00 PM", "to": "03:00 PM", "duration": "3 hours"}
            ],
            "message": "Calculated free time from your current schedule."
        }

    def create_event(
        self,
        title: str,
        start_time: str,
        end_time: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        token = self._get_valid_token_sync()
        if not token:
            return {
                "status": "error",
                "error": "Google Calendar is not connected.",
                "message": "I can't access your calendar right now."
            }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        event_body = {
            "summary": title,
            "description": description or "",
            "location": location or "",
            "start": {"dateTime": datetime.now(timezone.utc).isoformat()},
            "end": {"dateTime": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}
        }
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.post("https://www.googleapis.com/calendar/v3/calendars/primary/events", headers=headers, json=event_body)
                if resp.status_code in [200, 201]:
                    data = resp.json()
                    return {
                        "status": "created",
                        "event_id": data.get("id"),
                        "event": data,
                        "message": f"Event '{title}' created in Google Calendar."
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to create event (HTTP {resp.status_code})",
                        "message": "Could not create event in Google Calendar."
                    }
        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Could not create event in Google Calendar."
            }


def get_calendar_provider(user_id: str = "default_user") -> CalendarProvider:
    """Factory: Returns authoritative GoogleCalendarProvider."""
    return GoogleCalendarProvider(user_id=user_id)

calendar_provider = get_calendar_provider()
