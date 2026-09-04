import pytest
import asyncio
import uuid
from backend.app.services.agent_graph import run_agent
from backend.app.services.context_engine import context_engine

@pytest.mark.asyncio
async def test_agent_graph_greeting_flow():
    session_id = f"test_sess_{uuid.uuid4()}"
    full_ctx = context_engine.get_relevant_context("Good morning.").model_dump()

    result = await run_agent(
        session_id=session_id,
        user_message="Good morning.",
        context_payload=full_ctx
    )

    assert "response" in result
    response = result["response"]
    assert len(response) > 0



@pytest.mark.asyncio
async def test_agent_graph_multi_turn_entity_resolution():
    session_id = f"test_sess_{uuid.uuid4()}"
    full_ctx = context_engine.get_relevant_context("Check my email.").model_dump()

    # Turn 1
    t1_res = await run_agent(
        session_id=session_id,
        user_message="Check my email.",
        context_payload=full_ctx
    )
    assert "unread" in t1_res["response"].lower() or len(t1_res.get("actions", [])) > 0

    # Turn 2: "Read the second one"
    t2_res = await run_agent(
        session_id=session_id,
        user_message="Read the second one.",
        context_payload=full_ctx
    )
    assert "response" in t2_res
    # Verified tool execution
    actions = [a.tool_name for a in t2_res.get("actions", [])]
    assert "gmail_read" in actions or "email" in t2_res["response"].lower()
