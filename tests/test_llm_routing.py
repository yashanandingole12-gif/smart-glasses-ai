import pytest
from backend.app.services.llm_router import llm_router, RoutingTier
from backend.app.config import settings

@pytest.mark.asyncio
async def test_routing_tier_selection_simple():
    """Verify simple conversational query defaults to FAST tier."""
    tier = llm_router.select_starting_tier("Hello there", has_tools=False)
    assert tier == RoutingTier.FAST

@pytest.mark.asyncio
async def test_routing_tier_selection_with_tools():
    """Verify tool-bearing query defaults to PRIMARY tier."""
    tier = llm_router.select_starting_tier("Check my email", has_tools=True)
    assert tier == RoutingTier.PRIMARY

@pytest.mark.asyncio
async def test_generate_with_budget_fast_tier():
    """Verify execution through router returns valid RoutingTier and content."""
    messages = [
        {"role": "system", "content": "You are a smart glasses assistant."},
        {"role": "user", "content": "Hello"}
    ]
    resp = await llm_router.generate_with_budget(
        messages=messages,
        starting_tier=RoutingTier.FAST,
        global_deadline_seconds=5.0
    )
    assert resp is not None
    assert resp.content is not None
    assert len(resp.content.strip()) > 0
    assert resp.tier_used in [RoutingTier.FAST, RoutingTier.PRIMARY, RoutingTier.FALLBACK]
    assert resp.duration_ms < 5000.0
