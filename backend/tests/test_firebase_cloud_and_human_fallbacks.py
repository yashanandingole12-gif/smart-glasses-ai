import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.personality_engine import personality_engine
from backend.app.services.llm_service import llm_service
from backend.app.services.firebase_sync_service import firebase_sync_service

client = TestClient(app)

def test_human_fallback_response_no_echo():
    """Verify that fallbacks never echo 'I am listening... you asked:' and provide concise human replies."""
    # 1. Check prompt core instructions
    prompt = personality_engine.SYSTEM_PROMPT_CORE
    assert "Never echo the user's question" in prompt
    assert "I don’t have that information right now" in prompt
    assert "under 2 short sentences" in prompt

    # 2. Check API endpoint response
    resp = client.post("/api/v1/agent/message", json={
        "session_id": "test-session-fallback",
        "message": "What is the secret flight code for alien spaceship XYZ999?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data
    # Ensure no echo pattern exists
    assert "you asked" not in data["response"].lower()
    assert "listening on your smart glasses" not in data["response"].lower()

def test_firebase_device_sync_and_heartbeat():
    """Verify Firebase device registration, state heartbeat, and retrieval."""
    device_payload = {
        "device_id": "ESP32-S3-TEST-001",
        "device_name": "My Smart Glasses",
        "user_id": "user_eva_prime",
        "status": "ONLINE",
        "battery_level": 92,
        "current_mode": "PTT_VOICE_AI",
        "mic_status": "READY (INMP441)",
        "speaker_status": "READY (MAX98357A)",
        "firmware_version": "v1.0.0"
    }
    sync_resp = client.post("/api/v1/cloud/device/sync", json=device_payload)
    assert sync_resp.status_code == 200
    synced_data = sync_resp.json()
    assert synced_data["success"] is True
    assert synced_data["device"]["device_id"] == "ESP32-S3-TEST-001"
    assert synced_data["device"]["battery_level"] == 92

    # Query device state
    get_resp = client.get("/api/v1/cloud/device/ESP32-S3-TEST-001")
    assert get_resp.status_code == 200
    assert get_resp.json()["device"]["status"] == "ONLINE"

def test_firebase_remote_command_lifecycle():
    """Verify queuing remote commands and reporting completion."""
    cmd_payload = {
        "user_id": "user_eva_prime",
        "device_id": "ESP32-S3-TEST-001",
        "command_type": "SAY_TEXT",
        "payload": {"text": "Incoming meeting in 5 minutes."}
    }
    queue_resp = client.post("/api/v1/cloud/command/queue", json=cmd_payload)
    assert queue_resp.status_code == 200
    cmd_data = queue_resp.json()
    cmd_id = cmd_data["command"]["command_id"]
    assert cmd_data["command"]["status"] == "PENDING"

    # Poll pending commands
    pending_resp = client.get("/api/v1/cloud/command/pending/ESP32-S3-TEST-001")
    assert pending_resp.status_code == 200
    pending_data = pending_resp.json()
    assert pending_data["count"] >= 1
    assert any(c["command_id"] == cmd_id for c in pending_data["commands"])

    # Mark complete
    complete_resp = client.post(f"/api/v1/cloud/command/{cmd_id}/complete", json={
        "success": True,
        "result": {"played_duration_ms": 1400}
    })
    assert complete_resp.status_code == 200
    assert complete_resp.json()["command"]["status"] == "EXECUTED"
