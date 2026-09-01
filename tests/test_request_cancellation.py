import pytest
import asyncio
from backend.app.services.llm_router import llm_router

@pytest.mark.asyncio
async def test_request_cancellation_event():
    """Verify active cancellation event aborts generation cleanly."""
    messages = [
        {"role": "user", "content": "Tell me a story."}
    ]

    cancel_event = asyncio.Event()
    cancel_event.set()  # Cancelled before / during start

    resp = await llm_router.generate_with_budget(
        messages=messages,
        cancellation_event=cancel_event,
        global_deadline_seconds=2.0
    )

    assert resp is not None
    assert "cancelled" in resp.content.lower()
    assert resp.provider == "cancelled"
