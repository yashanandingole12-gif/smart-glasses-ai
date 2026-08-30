import pytest
import time
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_simple_query_fast_path_time():
    """Verify 'What time is it?' resolves via deterministic fast-path in <50ms without calling LLM."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Warmup app initialization
        await client.get("/api/v1/health")

        t0 = time.time()
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "test_fast_time",
            "message": "What time is it?"
        })
        dur_ms = (time.time() - t0) * 1000.0
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"].get("fast_path") is True
        assert "It's" in data["response"] or ":" in data["response"]
        assert dur_ms < 100.0  # Fast path should complete well under 100ms


@pytest.mark.asyncio
async def test_simple_query_fast_path_battery():
    """Verify 'What's my battery?' resolves via deterministic fast-path without calling LLM."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        t0 = time.time()
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "test_fast_battery",
            "message": "What's my battery?",
            "context": {
                "time": {"local_time": "12:00 PM", "period": "afternoon"},
                "location": {"is_available": False},
                "device": {"battery": 77}
            }
        })
        dur_ms = (time.time() - t0) * 1000.0
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"].get("fast_path") is True
        assert "77%" in data["response"]
        assert dur_ms < 100.0


@pytest.mark.asyncio
async def test_simple_query_fast_path_location():
    """Verify 'Where am I?' resolves via deterministic fast-path."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "test_fast_location",
            "message": "Where am I?",
            "context": {
                "time": {"local_time": "12:00 PM", "period": "afternoon"},
                "location": {"city": "Nagpur", "is_available": True},
                "device": {"battery": 80}
            }
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"].get("fast_path") is True
        assert "Nagpur" in data["response"]


@pytest.mark.asyncio
async def test_simple_query_fast_path_multilingual():
    """Verify Hindi and Marathi deterministic queries resolve via fast-path."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Hindi time
        resp_hi = await client.post("/api/v1/agent/message", json={
            "session_id": "test_fast_hi",
            "message": "कितने बजे हैं",
            "language": "hi"
        })
        assert resp_hi.status_code == 200
        data_hi = resp_hi.json()
        assert data_hi["metadata"].get("fast_path") is True
        assert "बजे" in data_hi["response"]

        # Marathi time
        resp_mr = await client.post("/api/v1/agent/message", json={
            "session_id": "test_fast_mr",
            "message": "वेळ काय झाली",
            "language": "mr"
        })
        assert resp_mr.status_code == 200
        data_mr = resp_mr.json()
        assert data_mr["metadata"].get("fast_path") is True
        assert "वाजले" in data_mr["response"]


@pytest.mark.asyncio
async def test_gmail_tool_selective_invocation():
    """Verify Gmail tools are only bound/invoked when email intent is present."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Non-email query: should NOT invoke Gmail tools
        resp_hello = await client.post("/api/v1/agent/message", json={
            "session_id": "test_no_tool",
            "message": "Hello, how are you today?"
        })
        assert resp_hello.status_code == 200
        data_hello = resp_hello.json()
        assert len(data_hello["actions"]) == 0
        assert "email" not in data_hello["response"].lower()

        # 2. Email query: should invoke Gmail tool
        resp_email = await client.post("/api/v1/agent/message", json={
            "session_id": "test_email_tool",
            "message": "Check my email."
        })
        assert resp_email.status_code == 200
        data_email = resp_email.json()
        assert "unread" in data_email["response"].lower() or "email" in data_email["response"].lower()


@pytest.mark.asyncio
async def test_health_endpoint_ultra_fast():
    """Verify GET /api/v1/health executes cleanly in <30ms without heavy dependencies."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        t0 = time.time()
        resp = await client.get("/api/v1/health")
        dur_ms = (time.time() - t0) * 1000.0
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        assert dur_ms < 50.0


@pytest.mark.asyncio
async def test_latency_metrics_metadata_structure():
    """Verify all required Phase 3B.5 profiling fields are serialized in response metadata."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        req_id = "req_prof_123456"
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "session_prof",
            "message": "Hello there",
            "request_id": req_id
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "metadata" in data
        meta = data["metadata"]
        assert meta["request_id"] == req_id
        assert "timings" in meta
        timings = meta["timings"]
        assert "context_ms" in timings
        assert "total_ms" in timings
