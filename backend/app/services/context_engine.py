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
        user_message: str = "",
        client_context: Optional[FullContextPayload] = None,
        session_id: Optional[str] = None,
        include_remote: bool = False
    ) -> FullContextPayload:
        """
        Builds a tailored context payload merging client telemetry, temporal calculation,
        and optionally remote calendar status. When include_remote=False, returns in <1ms.
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

        # 3. Calendar context (Real Google Calendar, zero mock fallback)
        if client_context and client_context.calendar and client_context.calendar.next_event:
            cal_ctx = client_context.calendar
        elif include_remote:
            cal_data = calendar_get_events()
            raw_events = cal_data.get("events", []) if isinstance(cal_data, dict) else []
            events = [
                CalendarEvent(
                    id=e.get("id", f"evt_{idx}"),
                    title=e.get("title", "Event"),
                    start_time=e.get("start_time", ""),
                    end_time=e.get("end_time"),
                    location=e.get("location"),
                    description=e.get("description")
                )
                for idx, e in enumerate(raw_events)
            ]
            cal_ctx = CalendarContext(
                current_event=None,
                next_event=events[0] if events else None,
                today_events=events
            )
        else:
            cal_ctx = CalendarContext(
                current_event=None,
                next_event=None,
                today_events=[]
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

    def resolve_deterministic_query(
        self,
        user_message: str,
        context: FullContextPayload,
        language: str = "auto"
    ) -> Optional[str]:
        """
        Fast-path evaluation for trivial deterministic queries.
        Returns immediate response without invoking LangGraph or LLM.
        """
        msg = user_message.strip().lower().rstrip("?.,! ")
        if not msg:
            return None

        # 1. Time queries
        time_patterns = [
            "what time is it", "what's the time", "what is the time", "time please",
            "tell me the time", "current time", "what time", "time now",
            "कितने बजे हैं", "समय क्या है", "टाइम क्या हुआ", "टाइम क्या है",
            "किती वाजले", "वेळ काय झाली", "आता किती वाजले",
            "time kya hua", "kitne baje", "kya time hai"
        ]
        if any(p in msg for p in time_patterns) or msg in ["time", "समय", "वेळ"]:
            t = context.time.local_time
            if any(h in msg for h in ["बजे", "समय", "हुआ", "टाइम"]):
                return f"अभी {t} बजे हैं।"
            elif any(m in msg for m in ["वाजले", "झाली", "वेळ"]):
                return f"आता {t} वाजले आहेत."
            elif any(hg in msg for h in ["kya", "hua", "kitne"] for hg in [h]):
                return f"Abhi {t} hue hain."
            return f"It's {t}."

        # 2. Battery queries
        battery_patterns = [
            "what's my battery", "what is my battery", "battery percentage", "battery level",
            "battery status", "check battery", "how much battery", "my battery",
            "बैटरी कितनी है", "बैटरी स्टेटस", "बैटरी लेवल",
            "बॅटरी किती आहे", "बॅटरी पातळी",
            "battery kitni hai", "battery kitna hai", "battery percent"
        ]
        if any(p in msg for p in battery_patterns) or msg in ["battery", "बैटरी", "बॅटरी"]:
            bat = context.device.battery if context.device.battery is not None else 85
            if any(h in msg for h in ["बैटरी", "कितनी"]):
                return f"आपकी बैटरी {bat}% है।"
            elif any(m in msg for m in ["बॅटरी", "किती"]):
                return f"तुमची बॅटरी {bat}% आहे."
            elif "kitni" in msg or "kitna" in msg:
                return f"Aapki battery {bat}% hai."
            return f"Your battery is at {bat}%."

        # 3. Location queries
        location_patterns = [
            "where am i", "what is my location", "what's my location", "current location",
            "my location", "where are we",
            "मैं कहाँ हूँ", "मेरी लोकेशन क्या है", "स्थान क्या है",
            "मी कुठे आहे", "माझे स्थान काय आहे",
            "main kahan hoon", "meri location", "kahan hoon"
        ]
        if any(p in msg for p in location_patterns) or msg in ["location", "लोकेशन"]:
            loc_avail = context.location.is_available
            city = context.location.city
            if loc_avail and city and city not in ["Unavailable", "Unknown"]:
                if any(h in msg for h in ["कहाँ", "लोकेशन"]):
                    return f"आप अभी {city} में हैं।"
                elif any(m in msg for m in ["कुठे", "स्थान"]):
                    return f"तुम्ही आता {city} मध्ये आहात."
                elif "kahan" in msg:
                    return f"Aap abhi {city} mein hain."
                return f"You are currently in {city}."
            else:
                if any(h in msg for h in ["कहाँ", "लोकेशन"]):
                    return "लोकेशन अभी उपलब्ध नहीं है।"
                elif any(m in msg for m in ["कुठे", "स्थान"]):
                    return "स्थान सध्या उपलब्ध नाही."
                elif "kahan" in msg:
                    return "Location abhi available nahi hai."
                return "Location is currently unavailable."

        # 4. Date queries
        date_patterns = [
            "what's today's date", "what is the date", "what's the date", "today's date",
            "what day is it", "आज कौन सी तारीख है", "आजची तारीख काय आहे", "aaj konsi date hai"
        ]
        if any(p in msg for p in date_patterns) or msg in ["date", "तारीख"]:
            d_str = context.time.date_str or "Today"
            return f"Today is {d_str}."

        # 5. Greetings & Status
        if msg in ["good morning", "morning", "good morning.", "सुप्रभात", "शुभ सकाळ"]:
            cal_info = ""
            if context.calendar and hasattr(context.calendar, "today_events"):
                if not context.calendar.today_events:
                    cal_info = " You have no upcoming events scheduled for today."
                else:
                    cal_info = f" You have {len(context.calendar.today_events)} events today."
            return f"Good morning!{cal_info} How can I help you today?"

        return None

context_engine = ContextEngine()
