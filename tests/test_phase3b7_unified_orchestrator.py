import pytest
from datetime import datetime
from backend.app.config import settings
from backend.app.services.providers.calendar_provider import get_calendar_provider, GoogleCalendarProvider
from backend.app.services.providers.email_provider import get_email_provider, GoogleGmailProvider
from backend.app.tools.calendar_tools import calendar_get_events
from backend.app.tools.gmail_tools import gmail_search, gmail_read
from backend.app.services.temporal_resolver import temporal_resolver, TemporalIntent
from backend.app.services.llm_service import llm_service
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_production_calendar_provider_is_google(monkeypatch):
    """Verify that get_calendar_provider() returns GoogleCalendarProvider and never MockCalendarProvider in production."""
    monkeypatch.delenv("USE_MOCK_CALENDAR", raising=False)
    provider = get_calendar_provider("test_user_no_auth")
    assert isinstance(provider, GoogleCalendarProvider)

def test_unauthenticated_calendar_returns_honest_error_zero_mock(monkeypatch):
    """Verify that querying calendar when unauthenticated returns honest error and zero mock events."""
    monkeypatch.delenv("USE_MOCK_CALENDAR", raising=False)
    res = calendar_get_events(user_id="unauthenticated_user_xyz")
    assert res.get("count") == 0
    assert len(res.get("events", [])) == 0
    assert "error" in res or "not connected" in res.get("message", "").lower()
    
    # Assert no mock data strings exist in the result
    res_str = str(res).lower()
    assert "machine learning class" not in res_str
    assert "project team sync" not in res_str
    assert "gym / workout" not in res_str

def test_production_email_provider_is_google(monkeypatch):
    """Verify that get_email_provider() returns GoogleGmailProvider."""
    monkeypatch.delenv("USE_MOCK_EMAIL", raising=False)
    provider = get_email_provider("test_user_no_auth")
    assert isinstance(provider, GoogleGmailProvider)

def test_unauthenticated_gmail_returns_honest_error_zero_mock(monkeypatch):
    """Verify that searching emails when unauthenticated returns honest error and zero mock emails."""
    monkeypatch.delenv("USE_MOCK_EMAIL", raising=False)
    provider = get_email_provider("unauthenticated_user_xyz")
    res = provider.search()
    assert res.get("count") == 0
    assert len(res.get("messages", [])) == 0
    assert "error" in res or "not connected" in res.get("message", "").lower()

    # Assert no mock emails exist
    res_str = str(res).lower()
    assert "college.admin@university.edu" not in res_str
    assert "rahul.sharma@techcorp.com" not in res_str

def test_temporal_resolver_error_handling():
    """Verify that temporal resolver respects error message from calendar provider."""
    intent = TemporalIntent(
        is_calendar_query=True,
        date_target="today",
        target_date_iso="2026-09-05",
        filter_mode="all"
    )
    # With explicit error
    resp = temporal_resolver.format_calendar_response(intent, [], error_message="I can't access your calendar right now.")
    assert resp == "I can't access your calendar right now."

    # With empty events (connected but clear schedule)
    resp_empty = temporal_resolver.format_calendar_response(intent, [])
    assert "no events scheduled" in resp_empty.lower()
    assert "machine learning" not in resp_empty.lower()

def test_diagnostics_integrations_endpoint():
    """Verify GET /api/v1/diagnostics/integrations returns safe integration status."""
    response = client.get("/api/v1/diagnostics/integrations")
    assert response.status_code == 200
    data = response.json()
    assert "gemini" in data
    assert "google" in data
    assert "gmail" in data
    assert "calendar" in data
    
    # Verify no tokens or keys are leaked
    data_str = str(data).lower()
    assert "token" not in data_str
    assert "secret" not in data_str
    assert "key" not in data_str

def test_mock_fallback_has_no_echo():
    """Verify that mock fallback response does not contain (Echo: ...) artifacts."""
    import asyncio
    resp = asyncio.run(llm_service._generate_mock([{"role": "user", "content": "Tell me something random 12345"}]))
    assert "(Echo:" not in resp.content
    assert "Echo:" not in resp.content
