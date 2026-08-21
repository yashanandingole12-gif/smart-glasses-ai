from typing import Dict, Any, Optional
from datetime import datetime
import pytz
from backend.app.config import settings
from backend.app.models.schemas import (
    FullContextPayload,
    TemporalContext,
    LocationContext,
    CalendarContext,
    CalendarEvent,
    DeviceContext,
    ConversationContext,
    TimePeriod
)
from backend.app.tools.calendar_tools import calendar_get_events

class ContextEngine:
    def __init__(self):
        pass

    def compute_temporal_context(self, timezone_str: Optional[str] = None) -> TemporalContext:
        tz_name = timezone_str or settings.DEFAULT_TIMEZONE
        try:
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
        except Exception:
            now = datetime.now()
            tz_name = "Local"

        hour = now.hour
        if 5 <= hour < 12:
            period = TimePeriod.MORNING
        elif 12 <= hour < 17:
            period = TimePeriod.AFTERNOON
        elif 17 <= hour < 22:
            period = TimePeriod.EVENING
        else:
            period = TimePeriod.NIGHT

        return TemporalContext(
            local_time=now.strftime("%I:%M %p").lstrip("0"),
            period=period,
            timezone=tz_name,
            date_str=now.strftime("%A, %B %d, %Y"),
            iso_timestamp=now.isoformat()
        )

    def get_relevant_context(
        self,
        user_message: str,
        client_context: Optional[FullContextPayload] = None,
        session_id: Optional[str] = None
    ) -> FullContextPayload:
        """
        Builds a tailored context payload merging client telemetry, temporal calculation,
        calendar status, and relevant context.
        """
        # 1. Temporal context (prefer client if provided, else calculate)
        if client_context and client_context.time:
            time_ctx = client_context.time
        else:
            time_ctx = self.compute_temporal_context()

        # 2. Location context
        if client_context and client_context.location and client_context.location.city != "Unknown":
            loc_ctx = client_context.location
        else:
            loc_ctx = LocationContext(
                latitude=settings.DEFAULT_LOCATION_LATITUDE,
                longitude=settings.DEFAULT_LOCATION_LONGITUDE,
                city=settings.DEFAULT_LOCATION_CITY,
                country=settings.DEFAULT_LOCATION_COUNTRY,
                place_type="college campus"
            )

        # 3. Calendar context
        if client_context and client_context.calendar and client_context.calendar.next_event:
            cal_ctx = client_context.calendar
        else:
            cal_data = calendar_get_events()
            events = [
                CalendarEvent(
                    id=e["id"],
                    title=e["title"],
                    start_time=e["start_time"],
                    end_time=e.get("end_time"),
                    location=e.get("location"),
                    description=e.get("description")
                )
                for e in cal_data["events"]
            ]
            cal_ctx = CalendarContext(
                current_event=None,
                next_event=events[0] if events else None,
                today_events=events
            )

        # 4. Device context
        if client_context and client_context.device:
            dev_ctx = client_context.device
        else:
            dev_ctx = DeviceContext(
                battery=85,
                camera_available=True,
                microphone_available=True,
                network="WIFI",
                connection_type="SIMULATOR"
            )

        # 5. Conversation context
        if client_context and client_context.conversation:
            conv_ctx = client_context.conversation
        else:
            conv_ctx = ConversationContext(
                recent_topic=None,
                referenced_entities={}
            )

        return FullContextPayload(
            time=time_ctx,
            location=loc_ctx,
            calendar=cal_ctx,
            device=dev_ctx,
            conversation=conv_ctx,
            vision=client_context.vision if client_context else None
        )

context_engine = ContextEngine()
