import re
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, time as dtime
from typing import Optional, List, Dict, Any, Tuple
import pytz

logger = logging.getLogger("SmartGlasses.TemporalResolver")


@dataclass
class TemporalIntent:
    is_calendar_query: bool
    date_target: str               # "today" | "tomorrow" | "specific" | "upcoming"
    target_date_iso: str           # e.g. "2026-09-01"
    start_time_filter: Optional[str] = None  # e.g. "08:00 AM", "03:00 PM"
    end_time_filter: Optional[str] = None
    filter_mode: str = "all"       # "all" | "exact" | "after" | "before" | "next" | "first"
    confidence: float = 1.0
    normalized_query: str = ""
    timezone: str = "Asia/Kolkata"
    requires_clarification: bool = False
    clarification_prompt: Optional[str] = None

    def to_log_dict(self) -> Dict[str, Any]:
        """Diagnostic log representation without sensitive data."""
        return {
            "date": self.target_date_iso,
            "date_target": self.date_target,
            "start_time": self.start_time_filter or "all_day",
            "end_time": self.end_time_filter or "all_day",
            "filter_mode": self.filter_mode,
            "timezone": self.timezone,
            "confidence": round(self.confidence, 2)
        }


class TemporalResolver:
    """
    Deterministic Conversational Temporal Reasoning Engine.
    
    Responsibilities:
    1. STT Error Normalization (e.g. "Whatever tomorrow" -> "what about tomorrow").
    2. Multi-turn Temporal Context Resolution ("What about 8 am?" resolves against prior turn's target date).
    3. Exact calendar query window extraction.
    4. Structured Intent Logging without sensitive data exposure.
    5. Zero event fabrication.
    """

    STT_NORMALIZATION_MAP = [
        (r"\bwhatever tomorrow\b", "what about tomorrow"),
        (r"\bwhat ever tomorrow\b", "what about tomorrow"),
        (r"\bwhover tomorrow\b", "what about tomorrow"),
        (r"\bwht about tomorrow\b", "what about tomorrow"),
        (r"\bwhat about tmrw\b", "what about tomorrow"),
        (r"\bwhat do i hav\b", "what do i have"),
        (r"\bwhats my\b", "what's my"),
        (r"\bwhat is my\b", "what is my"),
        (r"\bafter three\b", "after 3"),
        (r"\bafter 3 pm\b", "after 3"),
        (r"\bafter 3:00\b", "after 3"),
        (r"\beight a m\b", "8 am"),
        (r"\beight am\b", "8 am"),
        (r"\b8:00 am\b", "8 am"),
        (r"\b8:00\b", "8 am"),
    ]

    def normalize_stt(self, text: str) -> Tuple[str, float]:
        """Cleans speech recognition transcription artifacts."""
        if not text:
            return "", 1.0
        normalized = text.strip().lower()
        confidence = 1.0

        for pattern, replacement in self.STT_NORMALIZATION_MAP:
            if re.search(pattern, normalized):
                normalized = re.sub(pattern, replacement, normalized)
                confidence = 0.95

        normalized = normalized.rstrip("?.!, ")
        return normalized, confidence


    def resolve_intent(
        self,
        query: str,
        current_dt: Optional[datetime] = None,
        tz_name: str = "Asia/Kolkata",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> TemporalIntent:
        """
        Extracts temporal intent from user query with conversational context.
        """
        tz = pytz.timezone(tz_name) if tz_name else pytz.timezone("Asia/Kolkata")
        now = current_dt or datetime.now(tz)
        if now.tzinfo is None:
            now = tz.localize(now)

        today_iso = now.strftime("%Y-%m-%d")
        tomorrow_dt = now + timedelta(days=1)
        tomorrow_iso = tomorrow_dt.strftime("%Y-%m-%d")

        norm_query, conf = self.normalize_stt(query)
        q = norm_query.rstrip("?.! ")

        # Check if this is a calendar query
        calendar_keywords = [
            "calendar", "event", "events", "meeting", "meetings", "schedule", "agenda",
            "tomorrow", "today", "next event", "first event", "after 3", "after 3 pm",
            "at 8 am", "about 8 am", "free time", "what do i have", "what's on my",
            "anything after", "what about", "what's next"
        ]
        is_calendar = any(kw in q for kw in calendar_keywords)

        if not is_calendar:
            return TemporalIntent(
                is_calendar_query=False,
                date_target="none",
                target_date_iso=today_iso,
                confidence=1.0,
                normalized_query=norm_query,
                timezone=tz_name
            )

        # 1. Determine Date Target (Explicit vs Conversational Context)
        date_target = "today"
        target_date_iso = today_iso

        has_explicit_tomorrow = "tomorrow" in q or "tmrw" in q
        has_explicit_today = "today" in q

        if has_explicit_tomorrow:
            date_target = "tomorrow"
            target_date_iso = tomorrow_iso
        elif has_explicit_today:
            date_target = "today"
            target_date_iso = today_iso
        else:
            # Check conversation context if relative query (e.g. "What about 8 am?", "Do I have anything after 3?")
            prior_date = self._extract_date_from_history(conversation_history, today_iso, tomorrow_iso)
            if prior_date:
                target_date_iso = prior_date
                date_target = "tomorrow" if prior_date == tomorrow_iso else "today"
            else:
                date_target = "today"
                target_date_iso = today_iso

        # 2. Filter mode & specific time parsing
        filter_mode = "all"
        start_time_filter = None
        end_time_filter = None

        # Mode: "next"
        if "next event" in q or "what's next" in q or "next meeting" in q:
            filter_mode = "next"
            date_target = "upcoming"
            target_date_iso = today_iso

        # Mode: "first"
        elif "first event" in q or "first meeting" in q or "first schedule" in q:
            filter_mode = "first"

        # Time filter: "after X" (e.g. "after 3", "after 3 pm", "after 3:00")
        elif "after 3" in q or "after 3pm" in q or "after 3:00" in q:
            filter_mode = "after"
            start_time_filter = "03:00 PM"

        elif re.search(r"after\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", q):
            m = re.search(r"after\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", q)
            hour = int(m.group(1))
            minute = int(m.group(2) or 0)
            meridiem = m.group(3)
            if not meridiem:
                meridiem = "pm" if hour < 12 and hour >= 1 else "am"
            filter_mode = "after"
            start_time_filter = f"{hour:02d}:{minute:02d} {meridiem.upper()}"

        # Time filter: "at / about X am/pm" (e.g. "what about 8 am?", "at 8 am", "for 8 am")
        elif "8 am" in q or "8:00 am" in q or "8am" in q or "8:00" in q and "8" in q:
            filter_mode = "exact"
            start_time_filter = "08:00 AM"

        elif re.search(r"(?:at|about|for)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", q):
            m = re.search(r"(?:at|about|for)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", q)
            hour = int(m.group(1))
            minute = int(m.group(2) or 0)
            meridiem = m.group(3)
            if not meridiem:
                meridiem = "am" if hour in [8, 9, 10, 11] else "pm"
            filter_mode = "exact"
            start_time_filter = f"{hour:02d}:{minute:02d} {meridiem.upper()}"

        intent = TemporalIntent(
            is_calendar_query=True,
            date_target=date_target,
            target_date_iso=target_date_iso,
            start_time_filter=start_time_filter,
            end_time_filter=end_time_filter,
            filter_mode=filter_mode,
            confidence=conf,
            normalized_query=norm_query,
            timezone=tz_name
        )

        # Structured internal logging
        logger.info(f"TEMPORAL_INTENT_RESOLVED: {json.dumps(intent.to_log_dict())}")
        return intent

    def _extract_date_from_history(
        self,
        history: Optional[List[Dict[str, str]]],
        today_iso: str,
        tomorrow_iso: str
    ) -> Optional[str]:
        """Examines recent conversational turns to resolve contextual date references."""
        if not history:
            return None

        # Check last 4 messages in reverse chronological order
        for msg in reversed(history[-4:]):
            content = (msg.get("content") or "").lower()
            if "tomorrow" in content or tomorrow_iso in content:
                return tomorrow_iso
            if "today" in content or today_iso in content:
                return today_iso

        return None

    def filter_events(
        self,
        events: List[Dict[str, Any]],
        intent: TemporalIntent,
        current_dt: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Filters a list of calendar events according to the resolved temporal intent."""
        if not events:
            return []

        target_date = intent.target_date_iso
        mode = intent.filter_mode

        # 1. Filter by target date if event has date information
        matching_date_events = []
        for e in events:
            e_date = e.get("date_iso")
            # If event has explicit date_iso, match it
            if e_date:
                if e_date == target_date:
                    matching_date_events.append(e)
            else:
                # If mock/provider didn't attach date_iso, treat based on date_target
                e_tag = e.get("day_tag", "today")
                if intent.date_target == "tomorrow" and e_tag == "tomorrow":
                    matching_date_events.append(e)
                elif intent.date_target == "today" and e_tag == "today":
                    matching_date_events.append(e)
                elif intent.date_target == "upcoming":
                    matching_date_events.append(e)

        # Fallback if tags not present: use events as-is
        candidate_events = matching_date_events if matching_date_events else events

        # 2. Filter by mode & time
        if mode == "next":
            # Return earliest upcoming event
            return candidate_events[:1]

        elif mode == "first":
            # Return first event of the day
            return candidate_events[:1]

        elif mode == "exact" and intent.start_time_filter:
            target_time_clean = intent.start_time_filter.upper().strip()
            exact_matches = [
                e for e in candidate_events
                if self._times_match(e.get("start_time", ""), target_time_clean)
            ]
            return exact_matches

        elif mode == "after" and intent.start_time_filter:
            target_min = self._parse_time_to_minutes(intent.start_time_filter)
            after_matches = [
                e for e in candidate_events
                if self._parse_time_to_minutes(e.get("start_time", "")) >= target_min
            ]
            return after_matches

        return candidate_events

    def _times_match(self, time_str_a: str, time_str_b: str) -> bool:
        """Compares two time strings flexibly (e.g. '08:00 AM' == '8:00 AM' == '8 AM')."""
        min_a = self._parse_time_to_minutes(time_str_a)
        min_b = self._parse_time_to_minutes(time_str_b)
        return min_a == min_b and min_a >= 0

    def _parse_time_to_minutes(self, time_str: str) -> int:
        """Converts a time string like '10:30 AM' or '3:00 PM' to minutes since midnight."""
        if not time_str:
            return -1
        s = time_str.strip().upper()
        try:
            # Handle formats: "10:30 AM", "03:00 PM", "8 AM", "15:00"
            if "AM" in s or "PM" in s:
                parts = s.replace("AM", "").replace("PM", "").strip().split(":")
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
                if "PM" in s and hour < 12:
                    hour += 12
                if "AM" in s and hour == 12:
                    hour = 0
                return hour * 60 + minute
            elif ":" in s:
                parts = s.split(":")
                return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            pass
        return -1

    def format_calendar_response(
        self,
        intent: TemporalIntent,
        events: List[Dict[str, Any]]
    ) -> str:
        """
        Generates a concise, voice-optimized wearable response without event fabrication.
        """
        day_label = "tomorrow" if intent.date_target == "tomorrow" else "today"

        # Case 1: Filter mode is 'exact' (e.g. "What about 8 am?")
        if intent.filter_mode == "exact":
            time_str = intent.start_time_filter or "that time"
            if not events:
                return f"You have no events scheduled for {time_str} {day_label}."
            e = events[0]
            return f"At {time_str} {day_label}, you have {e['title']} at {e['start_time']}."

        # Case 2: Filter mode is 'first' (e.g. "What's my first event tomorrow?")
        if intent.filter_mode == "first":
            if not events:
                return f"You have no events scheduled for {day_label}."
            e = events[0]
            return f"Your first event {day_label} is {e['title']} at {e['start_time']}."

        # Case 3: Filter mode is 'next' (e.g. "What is my next event?")
        if intent.filter_mode == "next":
            if not events:
                return "You have no upcoming events on your schedule."
            e = events[0]
            return f"Your next event is {e['title']} at {e['start_time']}."

        # Case 4: Filter mode is 'after' (e.g. "Do I have anything after 3?")
        if intent.filter_mode == "after":
            time_str = intent.start_time_filter or "that time"
            if not events:
                return f"You have nothing scheduled after {time_str} {day_label}."
            if len(events) == 1:
                e = events[0]
                return f"After {time_str} {day_label}, you have {e['title']} at {e['start_time']}."
            event_strs = [f"{e['title']} at {e['start_time']}" for e in events]
            joined = ", ".join(event_strs[:-1]) + f", and {event_strs[-1]}"
            return f"After {time_str} {day_label}, you have {len(events)} events: {joined}."

        # Case 5: Standard Day Schedule ('all') (e.g. "What do I have tomorrow?", "What do I have today?")
        if not events:
            return f"You have no events scheduled for {day_label}."

        if len(events) == 1:
            e = events[0]
            return f"You have 1 event {day_label}: {e['title']} at {e['start_time']}."

        event_strs = [f"{e['title']} at {e['start_time']}" for e in events]
        if len(event_strs) == 2:
            joined = f"{event_strs[0]} and {event_strs[1]}"
        else:
            joined = ", ".join(event_strs[:-1]) + f", and {event_strs[-1]}"

        return f"You have {len(events)} events {day_label}: {joined}."


# Global singleton instance
temporal_resolver = TemporalResolver()
