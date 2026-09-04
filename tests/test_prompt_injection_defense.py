import pytest
import json
from backend.app.services.agent_graph import execute_tool_node, AgentState
from backend.app.services.tool_registry import registry

@pytest.mark.asyncio
async def test_prompt_injection_delimitation_in_tool_output():
    """Verify untrusted external tool content is strictly wrapped in isolation markers."""
    initial_state: AgentState = {
        "session_id": "test_inj_001",
        "user_message": "Check my email",
        "language": "en",
        "locale": "en-IN",
        "messages": [{"role": "user", "content": "Check my email"}],
        "context_payload": {},
        "actions": [
            {
                "tool_name": "gmail_search",
                "tool_input": {"query": "system instructions"},
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

    result = await execute_tool_node(initial_state)
    messages = result.get("messages", [])
    assert len(messages) == 2  # user + tool message
    tool_msg = messages[-1]
    assert tool_msg["role"] == "tool"
    assert "<<<UNTRUSTED_EXTERNAL_CONTENT:" in tool_msg["content"]
    assert "<<<END_UNTRUSTED_EXTERNAL_CONTENT>>>" in tool_msg["content"]

def test_result_sanitization_removes_tokens():
    """Verify tool execution sanitizes sensitive credentials before returning."""
    dirty_result = {
        "status": "ok",
        "access_token": "ya29.a0AfH6SMDIEXAMPLESECRETTOKEN",
        "refresh_token": "1//04example_refresh_token",
        "client_secret": "GOCSPX-example_secret",
        "user_data": {
            "api_key": "AIzaSyEXAMPLESECRETKEY",
            "email": "user@example.com"
        }
    }
    sanitized = registry.sanitize_result(dirty_result)
    assert sanitized["access_token"] == "[REDACTED]"
    assert sanitized["refresh_token"] == "[REDACTED]"
    assert sanitized["client_secret"] == "[REDACTED]"
    assert sanitized["user_data"]["api_key"] == "[REDACTED]"
    assert sanitized["user_data"]["email"] == "user@example.com"
