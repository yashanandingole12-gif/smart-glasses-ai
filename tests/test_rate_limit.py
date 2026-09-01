import pytest
import httpx
from unittest.mock import patch
from backend.app.services.llm_router import llm_router, RoutingTier, FailureCategory
from backend.app.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_rate_limit_429_immediate_fallback():
    """Verify HTTP 429 rate limiting triggers immediate fallback without long retry sleep."""
    messages = [
        {"role": "user", "content": "Tell me a joke."}
    ]

    async def mock_429_generate(*args, **kwargs):
        req = httpx.Request("POST", "https://api.test.com/v1/chat")
        resp = httpx.Response(status_code=429, request=req, headers={"Retry-After": "60"})
        raise httpx.HTTPStatusError("429 Too Many Requests", request=req, response=resp)

    with patch.object(LLMService, "generate", side_effect=mock_429_generate):
        resp = await llm_router.generate_with_budget(
            messages=messages,
            per_attempt_timeout=1.0,
            global_deadline_seconds=2.0
        )
        assert resp is not None
        assert resp.content is not None
        assert resp.tier_used == RoutingTier.FALLBACK
        assert resp.failure_category == FailureCategory.LLM_RATE_LIMIT
