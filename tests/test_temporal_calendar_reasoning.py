import pytest
import time
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.temporal_resolver import temporal_resolver, TemporalResolver
from backend.app.services.providers.calendar_provider import MockCalendarProvider


def test_stt_normalization_layer():
    """Verify STT normalization transforms speech artifacts with high confidence."""
    resolver = TemporalResolver()
    
    # "Whatever tomorrow."
    norm, conf = resolver.normalize_stt("Whatever tomorrow.")
    assert norm == "what about tomorrow"
    assert conf >= 0.9

    # "What ever tomorrow"
    norm, conf = resolver.normalize_stt("What ever tomorrow")
    assert norm == "what about tomorrow"

    # "whover tomorrow"
    norm, conf = resolver.normalize_stt("whover tomorrow")
    assert norm == "what about tomorrow"

    # "anything after three"
    norm, conf = resolver.normalize_stt("anything after three")
    assert norm == "anything after 3"

    # "what about eight a m"
    norm, conf = resolver.normalize_stt("what about eight a m")
    assert norm == "what about 8 am"


def test_temporal_intent_structured_logging():
    """Verify structured diagnostic logging has required fields and zero sensitive tokens."""
    resolver = TemporalResolver()
    intent = resolver.resolve_intent("What do I have tomorrow?")
    log_dict = intent.to_log_dict()

    assert "date" in log_dict
    assert "start_time" in log_dict
    assert "end_time" in log_dict
    assert "timezone" in log_dict
    assert "confidence" in log_dict
    assert log_dict["date_target"] == "tomorrow"
    
    # Ensure no token or credential exposure
    for key in ["token", "secret", "password", "auth", "access_token"]:
        assert key not in log_dict


def test_conversational_context_multi_turn_resolution():
    """
    Verify:
    Turn 1: 'What do I have tomorrow?'
    Turn 2: 'What about 8 am?' -> correctly resolves against tomorrow's context!
    """
    resolver = TemporalResolver()

    # Turn 1: Tomorrow
    intent_t1 = resolver.resolve_intent("What do I have tomorrow?")
    assert intent_t1.date_target == "tomorrow"

    # Simulate conversation history after Turn 1
    history = [
        {"role": "user", "content": "What do I have tomorrow?"},
        {"role": "assistant", "content": "You have 3 events tomorrow: Operating Systems Lab at 9:00 AM, Database Systems at 11:30 AM, and AI Seminar at 4:00 PM."}
    ]

    # Turn 2: Relative time query 'What about 8 am?'
    intent_t2 = resolver.resolve_intent("What about 8 am?", conversation_history=history)
    assert intent_t2.filter_mode == "exact"
    assert intent_t2.start_time_filter == "08:00 AM"
    assert intent_t2.date_target == "tomorrow"
    assert intent_t2.target_date_iso == intent_t1.target_date_iso


def test_calendar_provider_multi_event_filtering():
    """Verify MockCalendarProvider returns all events for tomorrow and today without single-event truncation."""
    provider = MockCalendarProvider()
    resolver = TemporalResolver()

    # Query today
    today_res = provider.get_events(date_target="today")
    assert today_res["count"] == 3
    assert any("Machine Learning" in e["title"] for e in today_res["events"])

    # Query tomorrow
    tmrw_res = provider.get_events(date_target="tomorrow")
    assert tmrw_res["count"] == 3
    assert any("Operating Systems" in e["title"] for e in tmrw_res["events"])
    assert any("AI Seminar" in e["title"] for e in tmrw_res["events"])

    # Filter tomorrow for 8:00 AM (Zero fabrication test)
    intent_8am = resolver.resolve_intent("What about 8 am?", conversation_history=[
        {"role": "user", "content": "What do I have tomorrow?"}
    ])
    matched_8am = resolver.filter_events(tmrw_res["events"], intent_8am)
    assert len(matched_8am) == 0  # No events at 8 AM

    reply_8am = resolver.format_calendar_response(intent_8am, matched_8am)
    assert "no events scheduled for 08:00 am tomorrow" in reply_8am.lower() or "no events" in reply_8am.lower()



# =========================================================================
# Acceptance Tests for the 7 Required User Queries via Backend API
# =========================================================================

@pytest.fixture(autouse=True)
def mock_calendar_events(monkeypatch):
    """Provide a predictable test schedule for temporal reasoning verification."""
    test_today = [
        {"id": "evt_1", "title": "Machine Learning Class", "start_time": "10:30 AM", "day_tag": "today", "date_iso": "2026-09-05"},
        {"id": "evt_2", "title": "Project Team Sync", "start_time": "03:00 PM", "day_tag": "today", "date_iso": "2026-09-05"},
        {"id": "evt_3", "title": "Gym / Workout", "start_time": "06:30 PM", "day_tag": "today", "date_iso": "2026-09-05"}
    ]
    test_tomorrow = [
        {"id": "evt_4", "title": "Operating Systems Lab", "start_time": "09:00 AM", "day_tag": "tomorrow", "date_iso": "2026-09-06"},
        {"id": "evt_5", "title": "Database Systems Lecture", "start_time": "11:30 AM", "day_tag": "tomorrow", "date_iso": "2026-09-06"},
        {"id": "evt_6", "title": "AI Seminar", "start_time": "04:00 PM", "day_tag": "tomorrow", "date_iso": "2026-09-06"}
    ]

    def mock_get(query=None, user_id="default_user", date_target=None):
        if date_target == "tomorrow":
            ev = test_tomorrow
        else:
            ev = test_today
        return {"count": len(ev), "events": ev, "next_event": ev[0]}

    monkeypatch.setattr("backend.app.main.calendar_get_events", mock_get)

@pytest.mark.asyncio
async def test_acceptance_query_1_what_do_i_have_today():
    """Acceptance Query 1: 'What do I have today?'"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        t0 = time.time()
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "test_accept_today",
            "message": "What do I have today?"
        })
        dur_ms = (time.time() - t0) * 1000.0
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"].get("fast_path") is True
        assert "3 events today" in data["response"] or "Machine Learning Class" in data["response"]
        assert dur_ms < 100.0


@pytest.mark.asyncio
async def test_acceptance_query_2_what_do_i_have_tomorrow():
    """Acceptance Query 2: 'What do I have tomorrow?'"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        t0 = time.time()
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "test_accept_tmrw",
            "message": "What do I have tomorrow?"
        })
        dur_ms = (time.time() - t0) * 1000.0
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"].get("fast_path") is True
        # Must return all tomorrow's events, not only one
        assert "Operating Systems" in data["response"]
        assert "AI Seminar" in data["response"]
        assert dur_ms < 100.0


@pytest.mark.asyncio
async def test_acceptance_query_3_what_is_my_next_event():
    """Acceptance Query 3: 'What is my next event?'"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        t0 = time.time()
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "test_accept_next",
            "message": "What is my next event?"
        })
        dur_ms = (time.time() - t0) * 1000.0
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"].get("fast_path") is True
        assert "next event is" in data["response"].lower()
        assert dur_ms < 100.0


@pytest.mark.asyncio
async def test_acceptance_query_4_multi_turn_what_about_8_am():
    """
    Acceptance Query 4:
    Turn 1: 'What do I have tomorrow?'
    Turn 2: 'What about 8 am?' -> correctly resolves against tomorrow without guessing or fabricating.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        session_id = "test_accept_multi_turn_8am"

        # Turn 1
        resp1 = await client.post("/api/v1/agent/message", json={
            "session_id": session_id,
            "message": "What do I have tomorrow?"
        })
        assert resp1.status_code == 200

        # Turn 2
        t0 = time.time()
        resp2 = await client.post("/api/v1/agent/message", json={
            "session_id": session_id,
            "message": "What about 8 am?"
        })
        dur_ms = (time.time() - t0) * 1000.0
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["metadata"].get("fast_path") is True
        # Verified: no events at 8 am tomorrow
        assert "no events scheduled for 08:00 AM tomorrow" in data2["response"].lower() or "no events" in data2["response"].lower()
        assert dur_ms < 100.0


@pytest.mark.asyncio
async def test_acceptance_query_5_what_about_tomorrow():
    """Acceptance Query 5: 'What about tomorrow?' and STT variant 'Whatever tomorrow.'"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Standard
        resp1 = await client.post("/api/v1/agent/message", json={
            "session_id": "test_accept_about_tmrw_1",
            "message": "What about tomorrow?"
        })
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert "Operating Systems Lab" in data1["response"]
        assert "Database Systems" in data1["response"]

        # STT Error artifact: "Whatever tomorrow."
        resp2 = await client.post("/api/v1/agent/message", json={
            "session_id": "test_accept_about_tmrw_2",
            "message": "Whatever tomorrow."
        })
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert "Operating Systems Lab" in data2["response"]


@pytest.mark.asyncio
async def test_acceptance_query_6_do_i_have_anything_after_3():
    """Acceptance Query 6: 'Do I have anything after 3?'"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        t0 = time.time()
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "test_accept_after_3",
            "message": "Do I have anything after 3?"
        })
        dur_ms = (time.time() - t0) * 1000.0
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"].get("fast_path") is True
        # Events today at or after 3 PM: Project Team Sync (3:00 PM) and Gym (6:30 PM)
        assert "Project Team Sync" in data["response"] or "Gym / Workout" in data["response"]
        assert dur_ms < 100.0


@pytest.mark.asyncio
async def test_acceptance_query_7_whats_my_first_event_tomorrow():
    """Acceptance Query 7: 'What's my first event tomorrow?'"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        t0 = time.time()
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "test_accept_first_tmrw",
            "message": "What's my first event tomorrow?"
        })
        dur_ms = (time.time() - t0) * 1000.0
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"].get("fast_path") is True
        # Tomorrow's first event is Operating Systems Lab at 9:00 AM
        assert "Operating Systems Lab" in data["response"]
        assert "09:00 AM" in data["response"] or "9:00 AM" in data["response"]
        assert dur_ms < 100.0
