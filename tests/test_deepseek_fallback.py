import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from backend.app.config import settings
from backend.app.services.llm_service import LLMService, LLMResponse, ToolCall
from backend.app.services.llm_router import LLMRouter, RoutingTier

def test_deepseek_config_loaded():
    assert settings.DEEPSEEK_API_KEY == "sk-2929005b2c1c4ff18abc78b7e5fc693d"
    assert settings.SECONDARY_LLM_PROVIDER == "deepseek"
    assert settings.SECONDARY_LLM_MODEL == "deepseek-chat"
    assert settings.SECONDARY_LLM_BASE_URL == "https://api.deepseek.com"

def test_deepseek_llm_service_properties():
    service = LLMService(provider="deepseek", model="deepseek-chat", api_key="sk-test-123")
    assert service.provider == "deepseek"
    assert service.model == "deepseek-chat"
    assert service.api_key == "sk-test-123"
    assert "api.deepseek.com" in service.base_url

@pytest.mark.asyncio
async def test_deepseek_generation_mocked():
    service = LLMService(provider="deepseek", model="deepseek-chat", api_key="sk-test-123")
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = lambda: None
        mock_resp.json = lambda: {
            "choices": [
                {
                    "message": {
                        "content": "DeepSeek response: Weather is clear and 28C.",
                        "tool_calls": None
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp
        
        resp = await service.generate([{"role": "user", "content": "What is the weather?"}])
        assert resp.provider == "deepseek"
        assert resp.model == "deepseek-chat"
        assert "DeepSeek response" in resp.content

@pytest.mark.asyncio
async def test_llm_router_cascades_to_secondary_deepseek():
    router = LLMRouter()
    
    with patch.object(LLMService, "generate") as mock_gen:
        # First 2 calls (Primary & Fast Gemini) fail
        # Third call (Secondary DeepSeek) succeeds
        async def side_effect(messages, tools=None, context_payload=None):
            if mock_gen.call_count <= 2:
                raise Exception("429 Quota Exceeded on Gemini")
            return LLMResponse(
                content="DeepSeek fallback successful.",
                provider="deepseek",
                model="deepseek-chat"
            )
        
        mock_gen.side_effect = side_effect
        
        result = await router.generate_with_budget(
            messages=[{"role": "user", "content": "Tell me a fun fact about quantum physics."}],
            starting_tier=RoutingTier.PRIMARY
        )
        
        assert result.content == "DeepSeek fallback successful."
        assert result.provider == "deepseek"
        assert result.tier_used == RoutingTier.SECONDARY
        assert len(result.fallback_chain) >= 2
