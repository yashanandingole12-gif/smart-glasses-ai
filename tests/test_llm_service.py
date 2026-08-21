import pytest
import asyncio
from backend.app.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_llm_service_mock_greeting():
    service = LLMService(provider="mock")
    messages = [{"role": "user", "content": "Good morning."}]
    context_payload = {
        "time": {"local_time": "08:15 AM", "period": "morning"},
        "location": {"city": "Nagpur"},
        "calendar": {"next_event": {"title": "Machine Learning Class", "start_time": "10:30 AM"}}
    }

    resp = await service.generate(messages, context_payload=context_payload)
    assert resp.content is not None
    assert "Nagpur" in resp.content or "morning" in resp.content.lower()
    assert "10:30" in resp.content

@pytest.mark.asyncio
async def test_llm_service_mock_tool_triggering():
    service = LLMService(provider="mock")
    messages = [{"role": "user", "content": "Check my email."}]
    resp = await service.generate(messages)
    assert resp.tool_calls is not None
    assert len(resp.tool_calls) > 0
    assert resp.tool_calls[0].name == "gmail_search"
