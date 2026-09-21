import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_atmosphere_endpoint():
    """Verify GET /api/v1/atmosphere returns active preset and full preset list."""
    resp = client.get("/api/v1/atmosphere")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "current_mode" in data
    assert "current" in data
    assert "presets" in data
    assert len(data["presets"]) >= 8

def test_set_atmosphere_presets():
    """Verify switching across all canonical atmosphere modes."""
    modes = ["GROUNDED", "FOCUSED", "CREATIVE", "CURIOUS", "REFLECTIVE", "ENERGETIC", "NIGHT"]
    for mode in modes:
        resp = client.post("/api/v1/atmosphere/set", json={"mode": mode})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["mode"] == mode
        assert "accent" in data["atmosphere"]
        assert "highlight" in data["atmosphere"]

def test_set_custom_atmosphere():
    """Verify POST /api/v1/atmosphere/custom configures custom tone shifting."""
    resp = client.post("/api/v1/atmosphere/custom", json={
        "foundation": "#0C0805",
        "accent": "#703912",
        "highlight": "#D3A95B",
        "emotion": "adaptive curiosity",
        "glow_opacity": 0.3,
        "motion_scale": 1.1
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["mode"] == "CUSTOM"
    assert data["atmosphere"]["accent"] == "#703912"
    assert data["atmosphere"]["highlight"] == "#D3A95B"

def test_wearable_atmosphere_state():
    """Verify GET /api/v1/atmosphere/wearable returns lightweight BLE payload."""
    resp = client.get("/api/v1/atmosphere/wearable")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "atmosphere" in data
    assert "accent" in data
    assert "highlight" in data
    assert "foundation" in data

def test_invalid_atmosphere_mode():
    """Verify 400 error on invalid atmosphere mode."""
    resp = client.post("/api/v1/atmosphere/set", json={"mode": "INVALID_MODE"})
    assert resp.status_code == 400
    data = resp.json()
    assert "Invalid atmosphere mode" in data["message"] or "Invalid atmosphere mode" in data["detail"]
