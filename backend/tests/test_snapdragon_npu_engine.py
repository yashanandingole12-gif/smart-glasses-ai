import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.snapdragon_npu_engine import snapdragon_npu_engine

client = TestClient(app)

def test_snapdragon_hardware_status_endpoint():
    """Verify GET /api/v1/snapdragon/status returns NPU telemetry and loaded models."""
    resp = client.get("/api/v1/snapdragon/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "Snapdragon X Elite" in data["telemetry"]["soc_name"]
    assert "Hexagon NPU" in data["telemetry"]["npu_name"]
    assert data["telemetry"]["npu_tops"] == 45.0
    assert "HP PC" in data["telemetry"]["host_platform"]
    assert len(data["models"]) >= 4
    assert "whisper_stt" in data["models"]
    assert "local_llm" in data["models"]

def test_snapdragon_benchmarks_endpoint():
    """Verify GET /api/v1/snapdragon/benchmarks provides comparative NPU vs CPU data."""
    resp = client.get("/api/v1/snapdragon/benchmarks")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["benchmarks"]) >= 3
    first_b = data["benchmarks"][0]
    assert first_b["snapdragon_npu_ms"] < first_b["standard_cpu_ms"]
    assert first_b["power_joules_npu"] < first_b["power_joules_cpu"]

def test_snapdragon_on_device_stt_inference():
    """Verify POST /api/v1/snapdragon/infer/stt executes Whisper on NPU."""
    resp = client.post("/api/v1/snapdragon/infer/stt")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "Hexagon NPU" in data["engine"]
    assert data["is_on_device"] is True
    assert "transcript" in data

def test_snapdragon_on_device_vision_inference():
    """Verify POST /api/v1/snapdragon/infer/vision runs spatial perception on NPU."""
    resp = client.post("/api/v1/snapdragon/infer/vision?task=detect_objects")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "Hexagon NPU" in data["engine"]
    assert data["fps_capability"] >= 60.0
    assert len(data["detected_objects"]) >= 1

def test_snapdragon_on_device_llm_inference():
    """Verify POST /api/v1/snapdragon/infer/llm performs INT4 reasoning on NPU."""
    resp = client.post("/api/v1/snapdragon/infer/llm", json={
        "prompt": "Where is the Sitabuldi Metro station?",
        "max_tokens": 64
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "Hexagon NPU" in data["engine"]
    assert "response" in data
    assert len(data["oled_lines"]) >= 2
    assert "100% locally" in data["privacy_guarantee"]
