import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_root_dashboard():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "CONTEXT-AWARE SMART GLASSES AI" in resp.text
        assert "text/html" in resp.headers.get("content-type", "")

@pytest.mark.asyncio
async def test_api_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"

@pytest.mark.asyncio
async def test_api_session_creation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/session", json={"device_type": "SIMULATOR"})
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert data["device_type"] == "SIMULATOR"

@pytest.mark.asyncio
async def test_api_agent_message():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "session_id": "test_endpoint_session",
            "message": "Good morning."
        }
        resp = await client.post("/api/v1/agent/message", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert "Nagpur" in data["response"] or "morning" in data["response"].lower()
        assert "metadata" in data
        assert "latency_ms" in data["metadata"]

@pytest.mark.asyncio
async def test_api_vision_analyze():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "session_id": "test_vision_session",
            "image_base64": "dummy_base64_data"
        }
        resp = await client.post("/api/v1/vision/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "description" in data
        assert data["category"] == "pants"
