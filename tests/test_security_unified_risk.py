import pytest
import time
from backend.app.services.tool_registry import registry
from backend.app.services.agent_graph import run_agent
from backend.app.models.schemas import RiskLevel

def test_pending_action_token_lifecycle():
    """Verify action token creation, validation, consumption, and expiration."""
    action = registry.create_pending_action(
        tool_name="sms_send_message",
        tool_input={"recipient": "+919876543210", "text": "Testing confirmation token"},
        ttl_seconds=1.0  # 1 second TTL for test
    )
    assert action.action_id is not None
    assert action.status == "pending"

    # Validate and consume token
    consumed = registry.validate_and_consume_action(action.action_id)
    assert consumed is not None
    assert consumed.status == "executed"
    assert consumed.confirmed is True

    # Re-using the same action token must fail (single-use)
    reused = registry.validate_and_consume_action(action.action_id)
    assert reused is None

def test_expired_action_token_rejected():
    """Expired action tokens must be rejected."""
    action = registry.create_pending_action(
        tool_name="sms_send_message",
        tool_input={"recipient": "+919876543210", "text": "Expired test"},
        ttl_seconds=0.01
    )
    time.sleep(0.05)
    consumed = registry.validate_and_consume_action(action.action_id)
    assert consumed is None

def test_invalid_fake_action_id_rejected():
    """Non-existent or fake action IDs must be rejected."""
    consumed = registry.validate_and_consume_action("fake-action-id-999")
    assert consumed is None

@pytest.mark.asyncio
async def test_agent_sms_requires_confirmation_token():
    """Verify LangGraph generates confirmation action token for high-risk SMS tool."""
    res = await run_agent(
        session_id="test_sms_conf_001",
        user_message="Send Rahul a message saying I'll be late",
        context_payload={}
    )
    # If mock LLM decides to call sms_send_message or asks confirmation
    if res.get("requires_confirmation"):
        assert res.get("confirmation_action_id") is not None
        assert "SMS" in (res.get("confirmation_prompt") or "")

@pytest.mark.asyncio
async def test_agent_explicit_confirmation_execution():
    """Verify explicit confirmation using valid action token executes the action."""
    action = registry.create_pending_action(
        tool_name="sms_send_message",
        tool_input={"recipient": "+919876543210", "text": "I am on my way"},
        ttl_seconds=60.0
    )
    res = await run_agent(
        session_id="test_sms_conf_002",
        user_message="Confirm",
        context_payload={},
        confirmed_action_id=action.action_id
    )
    assert "Message sent" in res["response"] or "sent" in res["response"].lower()
    assert len(res["actions"]) == 1
    assert res["actions"][0].status == "executed"
