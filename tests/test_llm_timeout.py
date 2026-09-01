import pytest
import asyncio
import time
from unittest.mock import patch
from backend.app.services.llm_router import llm_router, RoutingTier, FailureCategory
from backend.app.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_hard_llm_timeout_cancellation_and_fallback():
    """Verify slow LLM provider is cancelled upon reaching timeout budget and immediately falls back."""
    messages = [
        {"role": "user", "content": "Explain quantum computing in detail."}
    ]

    async def mock_slow_generate(*args, **kwargs):
        # Simulate 10-second hang
        await asyncio.sleep(10.0)
        return None

    with patch.object(LLMService, "generate", side_effect=mock_slow_generate):
        t0 = time.time()
        resp = await llm_router.generate_with_budget(
            messages=messages,
            per_attempt_timeout=0.15,
            global_deadline_seconds=1.0
        )
        total_time_ms = (time.time() - t0) * 1000.0

        # Must finish well under the simulated 10s delay
        assert total_time_ms < 1500.0
        assert resp is not None
        assert resp.content is not None
        assert resp.tier_used == RoutingTier.FALLBACK
        assert any(f.get("error") == "LLM_TIMEOUT" for f in resp.fallback_chain)
