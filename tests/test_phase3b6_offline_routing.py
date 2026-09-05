import pytest
import asyncio
from backend.app.config import settings
from backend.app.services.context_engine import context_engine
from backend.app.models.schemas import FullContextPayload, TemporalContext, LocationContext, DeviceContext, TimePeriod
from backend.app.services.temporal_resolver import temporal_resolver
from backend.app.services.llm_router import llm_router, RoutingTier, FailureCategory

def test_deterministic_queries_fast_path():
    ctx = FullContextPayload(
        time=TemporalContext(local_time="12:42 PM", period=TimePeriod.AFTERNOON, timezone="Asia/Kolkata", date_str="Saturday, September 05, 2026", iso_timestamp="2026-09-05T12:42:00"),
        location=LocationContext(city="Nagpur", country="India", is_available=True),
        device=DeviceContext(battery=84, esp32_connected=True)
    )

    # Time
    time_resp = context_engine.resolve_deterministic_query("What time is it?", ctx)
    assert time_resp is not None
    assert "12:42 PM" in time_resp

    # Battery
    bat_resp = context_engine.resolve_deterministic_query("What's my battery?", ctx)
    assert bat_resp is not None
    assert "84%" in bat_resp

    # Location
    loc_resp = context_engine.resolve_deterministic_query("Where am I?", ctx)
    assert loc_resp is not None
    assert "Nagpur" in loc_resp

    # Date
    date_resp = context_engine.resolve_deterministic_query("What is today's date?", ctx)
    assert date_resp is not None
    assert "September" in date_resp or "Saturday" in date_resp

def test_temporal_reasoning_multi_turn_continuity():
    # Turn 1: "What do I have tomorrow?"
    intent1 = temporal_resolver.resolve_intent("What do I have tomorrow?")
    assert intent1.is_calendar_query is True
    assert intent1.date_target == "tomorrow"

    # Turn 2: "What about 8 AM?" with conversation history referencing tomorrow
    history = [
        {"role": "user", "content": "What do I have tomorrow?"},
        {"role": "assistant", "content": "You have Machine Learning at 10:30 AM."}
    ]
    intent2 = temporal_resolver.resolve_intent("What about 8 AM?", conversation_history=history)
    assert intent2.is_calendar_query is True
    assert intent2.date_target == "tomorrow"
    assert intent2.start_time_filter == "08:00 AM"

def test_calendar_zero_fabrication():
    intent = temporal_resolver.resolve_intent("What do I have tomorrow?")
    empty_events = []
    resp = temporal_resolver.format_calendar_response(intent, empty_events)
    assert "no events scheduled" in resp.lower()

@pytest.mark.asyncio
async def test_llm_router_secondary_provider_support():
    messages = [{"role": "user", "content": "Tell me a short joke."}]
    resp = await llm_router.generate_with_budget(
        messages=messages,
        per_attempt_timeout=1.0,
        global_deadline_seconds=2.0
    )
    assert resp is not None
    assert resp.content is not None
    assert resp.tier_used in [RoutingTier.FAST, RoutingTier.PRIMARY, RoutingTier.SECONDARY, RoutingTier.FALLBACK]
