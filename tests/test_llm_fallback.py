import pytest
from unittest.mock import patch
from backend.app.services.llm_router import llm_router, RoutingTier
from backend.app.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_llm_fallback_on_provider_error():
    """Verify provider errors immediately trigger fallback without returning empty text."""
    messages = [
        {"role": "user", "content": "What is the weather?"}
    ]

    async def mock_failing_generate(*args, **kwargs):
        raise RuntimeError("Cloud provider 500 Internal Server Error")

    with patch.object(LLMService, "generate", side_effect=mock_failing_generate):
        resp = await llm_router.generate_with_budget(
            messages=messages,
            per_attempt_timeout=1.0,
            global_deadline_seconds=2.0
        )
        assert resp is not None
        assert resp.content is not None
        assert len(resp.content.strip()) > 0
        assert resp.tier_used == RoutingTier.FALLBACK
        assert len(resp.fallback_chain) > 0
