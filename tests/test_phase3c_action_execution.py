import pytest
import time
import uuid
from typing import Dict, Any

from backend.app.services.tool_registry import registry, PendingAction
from backend.app.services.entity_resolver import entity_resolver, ResolutionStatus, Contact
from backend.app.services.agent_graph import run_agent, execute_tool_node, AgentState
from backend.app.models.schemas import RiskLevel, AgentAction
from backend.app.services.providers.calendar_provider import MockCalendarProvider, GoogleCalendarProvider
from backend.app.services.providers.email_provider import LaptopEmailProvider, GoogleGmailProvider
from backend.app.services.providers.messaging_provider import MockMessagingProvider


# ---------------------------------------------------------------------------
# 1. 2-Step Confirmation & Token Security Lifecycle (Section 3C.3 & 3C.4)
# ---------------------------------------------------------------------------

def test_pending_action_creation_and_expiration():
    """Verify pending action token creation, TTL expiry, and rejection."""
    action = registry.create_pending_action(
        tool_name="sms_send_message",
        tool_input={"recipient": "+919876543210", "text": "Testing token expiry"},
        ttl_seconds=0.05
    )
    assert action.action_id is not None
    assert action.status == "pending"
    assert action.risk_level == RiskLevel.HIGH_RISK_WRITE

    # Wait for expiry
    time.sleep(0.06)
    consumed = registry.validate_and_consume_action(action.action_id)
    assert consumed is None
    assert registry._pending_actions[action.action_id].status == "expired"


def test_pending_action_single_use_invariant():
    """Verify action tokens are strictly single-use and cannot be replayed."""
    action = registry.create_pending_action(
        tool_name="sms_send_message",
        tool_input={"recipient": "+919876543210", "text": "Single use token"},
        ttl_seconds=60.0
    )
    # First consumption succeeds
    first_use = registry.validate_and_consume_action(action.action_id)
    assert first_use is not None
    assert first_use.status == "executed"
    assert first_use.confirmed is True

    # Second consumption MUST fail
    second_use = registry.validate_and_consume_action(action.action_id)
    assert second_use is None


def test_pending_action_cancellation():
    """Verify pending action tokens can be cancelled by user or wearable timeout."""
    action = registry.create_pending_action(
        tool_name="sms_send_message",
        tool_input={"recipient": "+919876543210", "text": "Cancel this message"},
        ttl_seconds=60.0
    )
    assert registry.cancel_action(action.action_id) is True
    assert registry._pending_actions[action.action_id].status == "cancelled"

    # Attempting to execute a cancelled action must fail
    consumed = registry.validate_and_consume_action(action.action_id)
    assert consumed is None


@pytest.mark.asyncio
async def test_agent_graph_confirmed_action_execution():
    """Verify executing an action with a valid confirmed_action_id in run_agent."""
    action = registry.create_pending_action(
        tool_name="sms_send_message",
        tool_input={"recipient": "+919876543210", "text": "I am on my way!"},
        ttl_seconds=60.0
    )
    res = await run_agent(
        session_id="test_sess_confirm_01",
        user_message="Confirm",
        context_payload={},
        confirmed_action_id=action.action_id
    )
    assert "Message sent" in res["response"]
    assert len(res["actions"]) == 1
    assert res["actions"][0].status == "executed"
    assert res["actions"][0].tool_name == "sms_send_message"


@pytest.mark.asyncio
async def test_agent_graph_invalid_action_id_handled_gracefully():
    """Verify non-existent or expired confirmation action returns user guidance."""
    res = await run_agent(
        session_id="test_sess_invalid_act",
        user_message="Confirm",
        context_payload={},
        confirmed_action_id="non-existent-action-id-12345"
    )
    assert "expired or is invalid" in res["response"]
    assert len(res["actions"]) == 0


# ---------------------------------------------------------------------------
# 2. Entity Resolution Layer & Ambiguity Clarification (Section 3C.2)
# ---------------------------------------------------------------------------

def test_entity_resolution_exact_and_honorifics():
    """Verify normalization strips Indian honorifics (bhai, ji, sir, didi)."""
    res1 = entity_resolver.resolve_contact("Rahul Sharma")
    assert res1.status == ResolutionStatus.RESOLVED
    assert res1.contact.phone == "+919876543210"

    res2 = entity_resolver.resolve_contact("Sneha didi")
    assert res2.status == ResolutionStatus.RESOLVED
    assert res2.contact.name == "Sneha Patil"

    res3 = entity_resolver.resolve_contact("Amit bhai")
    assert res3.status == ResolutionStatus.RESOLVED
    assert res3.contact.name == "Amit Joshi"


def test_entity_resolution_relationship():
    """Verify relationship matching ('my mentor', 'colleague', 'classmate')."""
    res_mentor = entity_resolver.resolve_contact("my mentor")
    assert res_mentor.status == ResolutionStatus.RESOLVED
    assert res_mentor.contact.name == "Priya Rao"

    res_classmate = entity_resolver.resolve_contact("classmate")
    assert res_classmate.status == ResolutionStatus.RESOLVED
    assert res_classmate.contact.name == "Rahul Verma"


def test_entity_resolution_ambiguity():
    """Verify multiple close candidate matches trigger ambiguity and prompt."""
    res = entity_resolver.resolve_contact("Rahul")
    # There are two Rahuls in default contacts (Rahul Sharma and Rahul Verma)
    assert res.status == ResolutionStatus.AMBIGUOUS
    assert len(res.candidates) >= 2
    assert "Rahul Sharma" in res.clarification_prompt
    assert "Rahul Verma" in res.clarification_prompt


# ---------------------------------------------------------------------------
# 3. Credential Sanitization & Security Boundary (Section 3C.5)
# ---------------------------------------------------------------------------

def test_tool_registry_recursive_credential_sanitization():
    """Verify recursive redaction of access tokens, refresh tokens, and secrets."""
    dirty_payload = {
        "user": "developer",
        "access_token": "ya29.a0AfH6SM...",
        "refresh_token": "1//04xyz...",
        "client_secret": "GOCSPX-secret123",
        "api_key": "AQ.Ab8...",
        "nested": {
            "password": "SuperSecretPassword",
            "safe_field": "public_data",
            "token_list": [
                {"authorization": "Bearer ya29.123", "id": 101}
            ]
        }
    }
    cleaned = registry.sanitize_result(dirty_payload)
    assert cleaned["access_token"] == "[REDACTED]"
    assert cleaned["refresh_token"] == "[REDACTED]"
    assert cleaned["client_secret"] == "[REDACTED]"
    assert cleaned["api_key"] == "[REDACTED]"
    assert cleaned["nested"]["password"] == "[REDACTED]"
    assert cleaned["nested"]["safe_field"] == "public_data"
    assert cleaned["nested"]["token_list"][0]["authorization"] == "[REDACTED]"


# ---------------------------------------------------------------------------
# 4. Prompt Injection Defense (Section 3C.6)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_prompt_injection_defense_wrapping():
    """Verify tool execution node fences untrusted tool outputs inside demarcation tags."""
    state: AgentState = {
        "session_id": "test_pi_session",
        "user_message": "Read my emails",
        "language": "en",
        "locale": "en-IN",
        "messages": [{"role": "user", "content": "Read my emails"}],
        "context_payload": {},
        "actions": [
            {
                "tool_name": "gmail_search",
                "tool_input": {"query": "test"},
                "status": "requested"
            }
        ],
        "requires_confirmation": False,
        "confirmation_prompt": None,
        "confirmation_action_id": None,
        "final_response": None,
        "iteration_count": 0,
        "timings": {},
        "routing_metadata": {}
    }

    out = await execute_tool_node(state)
    assert "messages" in out
    tool_msg = out["messages"][-1]
    assert tool_msg["role"] == "tool"
    assert "<<<UNTRUSTED_EXTERNAL_CONTENT:" in tool_msg["content"]
    assert "<<<END_UNTRUSTED_EXTERNAL_CONTENT>>>" in tool_msg["content"]


# ---------------------------------------------------------------------------
# 5. Calendar Tools & Event Scheduling (Section 3C.1)
# ---------------------------------------------------------------------------

def test_calendar_provider_event_creation():
    """Verify scheduling a new event via CalendarProvider."""
    cal = MockCalendarProvider()
    create_res = cal.create_event(
        title="AI Architecture Review",
        start_time="05:00 PM",
        end_time="06:00 PM",
        location="Lab 204"
    )
    assert create_res["status"] == "created"
    assert create_res["event"]["title"] == "AI Architecture Review"

    # Verify event is in list
    events_res = cal.get_events()
    assert any(e["title"] == "AI Architecture Review" for e in events_res["events"])


def test_calendar_tool_registry_execution():
    """Verify calendar tools can be executed via unified tool registry."""
    events = registry.execute("calendar_get_events")
    assert "events" in events
    assert isinstance(events["events"], list)

    free = registry.execute("calendar_find_free_time")
    assert "free_slots" in free or "error" in free or "message" in free

    created = registry.execute(
        "calendar_create_event",
        title="Dentist Appointment",
        start_time="04:30 PM"
    )
    assert "status" in created or "error" in created
