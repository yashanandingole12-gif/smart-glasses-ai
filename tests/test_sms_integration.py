import pytest
from backend.app.services.providers.messaging_provider import MockMessagingProvider, get_messaging_provider
from backend.app.tools.sms_tools import sms_read_recent, sms_search, sms_send_message
from backend.app.services.tool_registry import registry
from backend.app.models.schemas import RiskLevel

@pytest.fixture
def messaging_provider():
    return MockMessagingProvider()

def test_sms_read_recent(messaging_provider):
    """Test reading recent SMS messages with data minimization."""
    res = messaging_provider.get_recent_messages(limit=2)
    assert res["count"] == 2
    assert len(res["messages"]) == 2
    assert res["messages"][0]["sender"] == "Rahul"

def test_sms_search_by_query_and_contact(messaging_provider):
    """Test searching SMS by query text or sender contact name."""
    res_query = messaging_provider.search_messages(query="presentation")
    assert res_query["count"] == 1
    assert res_query["messages"][0]["sender"] == "Sneha"

    res_sender = messaging_provider.search_messages(sender="Rahul")
    assert res_sender["count"] == 1
    assert res_sender["messages"][0]["sender"] == "Rahul"

def test_sms_send_execution(messaging_provider):
    """Test verified SMS dispatch via provider."""
    res = messaging_provider.send_message(recipient="+919876543210", text="I'll be late by 10 mins")
    assert res["status"] == "sent"
    assert res["recipient"] == "+919876543210"
    assert len(res["text"]) <= 160

def test_sms_tool_risk_levels():
    """sms_read_recent is READ, sms_send_message is HIGH_RISK_WRITE requiring confirmation."""
    read_tool = registry.get_tool("sms_read_recent")
    assert read_tool.risk_level == RiskLevel.READ
    assert read_tool.requires_confirmation is False

    send_tool = registry.get_tool("sms_send_message")
    assert send_tool.risk_level == RiskLevel.HIGH_RISK_WRITE
    assert send_tool.requires_confirmation is True
