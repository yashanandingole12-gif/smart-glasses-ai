import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.hardware_bridge import hardware_bridge
from backend.app.services.providers.messaging_provider import messaging_provider
from backend.app.services.device_security_service import device_security_service

client = TestClient(app)

def test_web_ui_endpoint():
    """Verify Web Dashboard loads with status 200 and valid JS structure."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text
    assert "LARA Smart Glasses" in html
    assert "ESP32 Smart Glasses & Android Hub" in html
    assert "updateHardwareStatus" in html
    assert "simulateIncomingSmsPrompt" in html
    assert "triggerMultimodalCapture" in html


def test_hardware_status_overview_endpoint():
    """Verify GET /api/v1/hardware/status returns consolidated ESP32 device status."""
    resp = client.get("/api/v1/hardware/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["device_model"] == "Seeed Studio XIAO ESP32-S3 Sense"
    assert data["ble_device_name"] == "SmartGlasses-S3"
    assert "camera" in data
    assert data["camera"]["status"] == "READY"
    assert "640x480" in data["camera"]["resolution"]
    assert "microphone" in data
    assert data["microphone"]["status"] == "READY"
    assert data["microphone"]["sample_rate"] == 16000
    assert "system" in data
    assert "battery_pct" in data["system"]


def test_sms_receive_webhook_endpoint():
    """Verify POST /api/v1/sms/receive receives Android SMS and injects into messaging provider."""
    payload = {
        "sender": "Vikram Malhotra",
        "phone": "+919876500001",
        "body": "Hi, please review the smart glasses circuit diagram when free."
    }
    resp = client.post("/api/v1/sms/receive", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "Vikram Malhotra" in data["message"]

    # Verify message is now queryable via messaging provider
    recent = messaging_provider.get_recent_messages(limit=5)
    matching = [m for m in recent["messages"] if m.get("sender") == "Vikram Malhotra"]
    assert len(matching) > 0
    assert matching[0]["text"] == payload["body"]


def test_device_overview_method():
    """Verify XiaoSenseHardwareBridge.get_device_overview() structure."""
    overview = hardware_bridge.get_device_overview()
    assert "device_model" in overview
    assert "camera" in overview
    assert "microphone" in overview
    assert "system" in overview
