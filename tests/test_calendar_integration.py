import pytest
from unittest.mock import patch, MagicMock
from backend.app.services.providers.calendar_provider import (
    MockCalendarProvider,
    GoogleCalendarProvider,
    get_calendar_provider
)
from backend.app.tools.calendar_tools import calendar_get_events, calendar_find_free_time
from backend.app.services.tool_registry import registry
from backend.app.models.schemas import RiskLevel

@pytest.fixture
def mock_calendar():
    return MockCalendarProvider()

def test_calendar_provider_get_events(mock_calendar):
    """Test standard event retrieval with query filtering."""
    res = mock_calendar.get_events()
    assert res["count"] == 3
    assert len(res["events"]) == 3
    assert res["next_event"]["title"] == "Machine Learning Class"

    # Search by query
    res_filtered = mock_calendar.get_events(query="Gym")
    assert res_filtered["count"] == 1
    assert res_filtered["events"][0]["title"] == "Gym / Workout"

def test_calendar_provider_empty_calendar():
    """Empty calendar is a valid state and must NOT fabricate events."""
    empty_provider = MockCalendarProvider(custom_events=[])
    res = empty_provider.get_events()
    assert res["count"] == 0
    assert res["events"] == []
    assert res["next_event"] is None
    assert "No calendar events found" in res["message"]

def test_calendar_find_free_time(mock_calendar):
    """Test free time slot calculation."""
    res = mock_calendar.find_free_time()
    assert "free_slots" in res
    assert len(res["free_slots"]) > 0

def test_calendar_tools_route_through_provider():
    """Verify calendar_get_events tool queries active provider."""
    res = calendar_get_events()
    assert res["count"] >= 0
    assert "events" in res

def test_calendar_tool_risk_level():
    """Calendar read tools must be categorized as RiskLevel.READ with no confirmation."""
    tool = registry.get_tool("calendar_get_events")
    assert tool is not None
    assert tool.risk_level == RiskLevel.READ
    assert tool.requires_confirmation is False

def test_google_calendar_provider_unauthenticated():
    """GoogleCalendarProvider must handle unauthenticated/token-expired state safely."""
    provider = GoogleCalendarProvider(user_id="unauth_user")
    res = provider.get_events()
    assert res["count"] == 0
    assert res["events"] == []
    assert "Google Calendar is not connected" in res["message"]
