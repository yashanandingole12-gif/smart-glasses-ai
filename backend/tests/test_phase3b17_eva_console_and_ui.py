import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_web_console_eva_branding():
    """Verify that GET /web returns EVA Operations Console with executive branding."""
    resp = client.get("/web")
    assert resp.status_code == 200
    html = resp.text
    assert "EVA" in html
    assert "Private Intelligence & Control" in html
    assert "Intent Inspector" in html
    assert "Desk & Data Analysis" in html
    assert "Automations Center" in html
    assert "Smart Notifications" in html

def test_automations_endpoints():
    """Verify GET and POST endpoints for executive automations."""
    # 1. Get existing automations
    get_resp = client.get("/api/v1/automations")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["success"] is True
    assert isinstance(data["automations"], list)
    assert len(data["automations"]) >= 2

    # 2. Schedule new automation
    post_resp = client.post("/api/v1/automations/schedule", json={
        "name": "Weekly Legal Document Review",
        "trigger": "Schedule (Monday 09:00 AM)",
        "schedule": "0 9 * * 1",
        "permissions": ["Files", "Gmail"]
    })
    assert post_resp.status_code == 200
    post_data = post_resp.json()
    assert post_data["success"] is True
    assert post_data["automation"]["name"] == "Weekly Legal Document Review"

def test_notification_policies_endpoints():
    """Verify GET and POST endpoints for smart notification policies."""
    # 1. Get policies
    get_resp = client.get("/api/v1/notifications/policies")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["success"] is True
    assert "categories" in data["policies"]
    assert "critical" in data["policies"]["categories"]

    # 2. Update focus mode
    post_resp = client.post("/api/v1/notifications/policy", json={
        "mode": "focus_mode",
        "state": True
    })
    assert post_resp.status_code == 200
    post_data = post_resp.json()
    assert post_data["policies"]["focus_mode"] is True

def test_desk_data_analysis_endpoint():
    """Verify bounded desk analysis on structured datasets."""
    # 1. Summarize
    sum_resp = client.post("/api/v1/desk/analyze", json={
        "dataset_name": "Quarterly_Financials.xlsx",
        "operation": "summarize"
    })
    assert sum_resp.status_code == 200
    sum_data = sum_resp.json()
    assert sum_data["success"] is True
    assert sum_data["rows"] == 24582
    assert "revenue" in sum_data["findings"].lower() or "growth" in sum_data["findings"].lower()

    # 2. Anomalies
    anom_resp = client.post("/api/v1/desk/analyze", json={
        "dataset_name": "Quarterly_Financials.xlsx",
        "operation": "anomalies"
    })
    assert anom_resp.status_code == 200
    anom_data = anom_resp.json()
    assert "variance" in anom_data["findings"].lower() or "threshold" in anom_data["findings"].lower()

    # 3. Calculate
    calc_resp = client.post("/api/v1/desk/analyze", json={
        "dataset_name": "Quarterly_Financials.xlsx",
        "operation": "calculate"
    })
    assert calc_resp.status_code == 200
    calc_data = calc_resp.json()
    assert "margin" in calc_data["findings"].lower()

def test_hardware_telemetry_continuity():
    """Verify ESP32-S3 hardware overview continues returning rich telemetry."""
    resp = client.get("/api/v1/hardware/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["esp32_connected"] is True or data["status"] in ["online", "standby"]
    assert data["camera_available"] is True
    assert data["microphone_available"] is True
    assert data["vision_ready"] is True
