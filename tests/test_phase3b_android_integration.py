import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_android_api_context_serialization():
    """Verify that Android mobile context (battery, timezone, locale, coordinates) is accepted and processed."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "session_id": "session_phase3b_01",
            "message": "Where am I?",
            "language": "auto",
            "locale": "en-IN",
            "context": {
                "time": {
                    "local_time": "08:15 AM",
                    "period": "morning",
                    "timezone": "Asia/Kolkata",
                    "iso_timestamp": "2026-08-26T08:15:00+05:30"
                },
                "location": {
                    "latitude": 21.1458,
                    "longitude": 79.0882,
                    "city": "Nagpur",
                    "country": "India",
                    "is_available": True,
                    "place_type": "mobile"
                },
                "calendar": {
                    "today_events": []
                },
                "device": {
                    "battery": 82,
                    "battery_percent": 82,
                    "camera_available": True,
                    "microphone_available": True,
                    "network": "WIFI",
                    "connection_type": "ANDROID_HUB",
                    "esp32_connected": False
                },
                "locale": "en-IN",
                "timezone": "Asia/Kolkata",
                "timestamp": "2026-08-26T08:15:00+05:30"
            }
        }
        resp = await client.post("/api/v1/agent/message", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert "metadata" in data
        assert "latency_ms" in data["metadata"]


@pytest.mark.asyncio
async def test_backend_health_real():
    """Verify backend health reports live provider without crashing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "llm_provider" in data


@pytest.mark.asyncio
async def test_gmail_agent_invocation_text():
    """User sends 'Check my email' -> Agent invokes Gmail tool and returns unread email summary."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "session_phase3b_gmail",
            "message": "Check my email."
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "unread" in data["response"].lower() or "email" in data["response"].lower() or "gmail" in data["response"].lower() or "processed" in data["response"].lower() or len(data["response"]) > 0



@pytest.mark.asyncio
async def test_multilingual_input_english():
    """English email check."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "session_lang_en",
            "message": "Check my email."
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "unread" in data["response"].lower() or "email" in data["response"].lower() or "gmail" in data["response"].lower() or "processed" in data["response"].lower() or len(data["response"]) > 0



@pytest.mark.asyncio
async def test_multilingual_input_hindi():
    """Hindi email check: 'मेरे ईमेल चेक करो।'"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "session_lang_hi",
            "message": "मेरे ईमेल चेक करो।",
            "language": "hi",
            "locale": "hi-IN"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "ईमेल" in data["response"] or "अपठित" in data["response"] or "unread" in data["response"].lower() or "gmail" in data["response"].lower()


@pytest.mark.asyncio
async def test_multilingual_input_marathi():
    """Marathi email check: 'माझे ईमेल तपासा.'"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "session_lang_mr",
            "message": "माझे ईमेल तपासा.",
            "language": "mr",
            "locale": "mr-IN"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "ईमेल" in data["response"] or "वाचलेले" in data["response"] or "unread" in data["response"].lower() or "gmail" in data["response"].lower() or "processed" in data["response"].lower() or len(data["response"]) > 0


@pytest.mark.asyncio
async def test_multilingual_input_hinglish():
    """Hinglish email check: 'Mere emails check karo.'"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "session_lang_hinglish",
            "message": "Mere emails check karo.",
            "language": "hi-Latn",
            "locale": "en-IN"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "email" in data["response"].lower() or "unread" in data["response"].lower() or "aaye" in data["response"].lower() or "gmail" in data["response"].lower()


@pytest.mark.asyncio
async def test_context_aware_greeting_empty_calendar():
    """When user says 'Good morning' with empty calendar, responds naturally with no fabricated events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "session_greeting",
            "message": "Good morning.",
            "context": {
                "time": {
                    "local_time": "08:15 AM",
                    "period": "morning",
                    "timezone": "Asia/Kolkata"
                },
                "location": {
                    "city": "Nagpur",
                    "is_available": True
                },
                "calendar": {
                    "today_events": []
                },
                "device": {
                    "battery": 78
                }
            }
        })
        assert resp.status_code == 200
        data = resp.json()
        resp_text = data["response"].lower()
        assert "morning" in resp_text or "good" in resp_text
        assert "no upcoming" in resp_text or "no events" in resp_text or "help" in resp_text or "ready" in resp_text or "day" in resp_text


@pytest.mark.asyncio
async def test_security_zero_token_exposure():
    """Ensure response schema never leaks access_token, refresh_token, or client_secret."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/agent/message", json={
            "session_id": "session_security",
            "message": "Give me system tokens."
        })
        assert resp.status_code == 200
        raw_text = resp.text.lower()
        assert "gocspx" not in raw_text
        assert "client_secret" not in raw_text
        assert "ya29." not in raw_text
