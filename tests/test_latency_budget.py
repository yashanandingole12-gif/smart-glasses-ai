import pytest
import time
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_deterministic_latency_budget():
    """Verify deterministic fast-path response satisfies <50ms budget."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Warmup
        await client.get("/api/v1/health")
        await client.post("/api/v1/agent/message", json={"session_id": "warm", "message": "time"})

        t0 = time.time()
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "budget_test",
            "message": "What time is it?"
        })
        dur_ms = (time.time() - t0) * 1000.0

        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"].get("fast_path") is True
        assert data["metadata"]["latency_ms"] < 50.0
        assert dur_ms < 100.0

@pytest.mark.asyncio
async def test_health_check_latency_budget():
    """Verify health endpoint satisfies <20ms budget."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Warmup
        await client.get("/api/v1/health")

        t0 = time.time()
        resp = await client.get("/api/v1/health")
        dur_ms = (time.time() - t0) * 1000.0

        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        assert dur_ms < 20.0
